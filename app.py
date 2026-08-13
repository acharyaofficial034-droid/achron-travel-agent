import random
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for
from database.database import initialize_database
from auth.signup import create_user
from auth.login import login_user
from auth.profile import get_user, update_user
from auth.password import hash_password, verify_password, update_password
from email_system.email_service import send_welcome_email, send_booking_confirmation
from booking.booking_service import save_booking
from booking.booking_service import get_user_bookings, save_booking

app = Flask(__name__)
app.secret_key = "ACHRON_SECRET_KEY_2026"

@app.route("/")
def home():
    return """
    <h1>Welcome to ACHRON Travel Agent</h1>
    <h3>Version 1.0</h3>

    <br>

    <a href="/login">
        <button>Login</button>
    </a>

    <a href="/signup">
        <button>Sign Up</button>
    </a>
    """

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        success, message = create_user(
            full_name,
            email,
            phone,
            password
        )

        if not success:
            return f"❌ {message}"

        try:
            send_welcome_email(email, full_name)
        except Exception as e:
            print("WELCOME EMAIL ERROR:", e)

        return "✅ Account Created Successfully!"

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        success, message = login_user(email, password)

        if success:
            session["user"] = email
            return redirect(url_for("dashboard"))
        else:
            return message

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    user = get_user(session["user"])

    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (session["user"],)
    )

    user_id = cursor.fetchone()[0]

    connection.close()

    bookings = get_user_bookings(user_id)

    return render_template(
        "dashboard.html",
        name=user[0],
        bookings=bookings
    )

@app.route("/booking", methods=["GET", "POST"])
def booking():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        destination = request.form["destination"]
        travel_date = request.form["travel_date"]
        travellers = int(request.form["travellers"])

        hotel_id = request.form.get("hotel_id") or None
        flight_id = request.form.get("flight_id") or None

        seat_number = request.form.get("seat_number") or None
        total_amount = float(request.form["total_amount"])

        connection = sqlite3.connect("achron.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE email = ?",
            (session["user"],)
        )

        user = cursor.fetchone()
        connection.close()

        if user is None:
            return "User not found"

        user_id = user[0]

        booking_id = "ACH" + str(random.randint(10000, 99999))
        pnr = str(random.randint(100000, 999999))

        save_booking(
            booking_id,
            user_id,
            hotel_id,
            flight_id,
            pnr,
            destination,
            travel_date,
            travellers,
            seat_number,
            total_amount
        )
        send_booking_confirmation(
    session["user"],
    booking_id,
    destination,
    travel_date,
    travellers,
    seat_number,
    total_amount
)

        return redirect(url_for("dashboard"))

    return render_template("booking.html")

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect(url_for("login"))

    user = get_user(session["user"])

    return render_template("profile.html", user=user)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user" not in session:
        return redirect(url_for("login"))

    email = session["user"]

    if request.method == "POST":
        full_name = request.form["full_name"]
        phone = request.form["phone"]

        update_user(email, full_name, phone)

        return redirect(url_for("profile"))

    user = get_user(email)

    return render_template("edit_profile.html", user=user)

@app.route("/change_password", methods=["GET", "POST"])
def change_password_page():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            return "❌ New passwords do not match."

        user = login_user(session["user"], current_password)

        if user[0] == False:
            return "❌ Current password is incorrect."

        update_password(session["user"], new_password)

        return "✅ Password changed successfully!"

    return render_template("change_password.html")

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
