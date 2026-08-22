import random
import sqlite3
import secrets
import time
import qrcode 
import os
from flask import Flask, render_template, request, session, redirect, url_for
from database.database import initialize_database
from auth.signup import create_user
from auth.login import login_user
from auth.profile import get_user, update_user
from auth.password import hash_password, verify_password, update_password
from email_system.email_service import send_welcome_email, send_booking_confirmation, send_password_reset_email
from booking.booking_service import save_booking
from booking.booking_service import get_user_bookings, save_booking

app = Flask(__name__)
app.secret_key = "ACHRON_SECRET_KEY_2026"
reset_tokens = {}

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

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        email = request.form["email"].strip()

        connection = sqlite3.connect("achron.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT email FROM users WHERE email = ?",
            (email,)
        )

        user = cursor.fetchone()
        connection.close()

        if user is None:
            return "❌ No account found with this email."

        token = secrets.token_urlsafe(32)

        reset_tokens[token] = {
            "email": email,
            "expires": time.time() + 900
        }

        reset_link = (
            "https://achron-travel-agent.onrender.com/reset-password/"
            + token
        )

        send_password_reset_email(email, reset_link)

        return "✅ Password reset link sent. Check your email."

    return """
    <h2>Forgot Password</h2>

    <form method="POST">
        <input type="email"
               name="email"
               placeholder="Your Email"
               required>

        <button type="submit">
            Send Reset Link
        </button>
    </form>
    """
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    data = reset_tokens.get(token)

    if data is None:
        return "❌ Invalid or expired reset link."

    if time.time() > data["expires"]:
        reset_tokens.pop(token, None)
        return "❌ This reset link has expired."

    if request.method == "POST":
        new_password = request.form["password"]

        if len(new_password) < 8:
            return "❌ Password must be at least 8 characters."

        update_password(data["email"], new_password)

        reset_tokens.pop(token, None)

        return "✅ Password changed successfully. You can now login."

    return """
    <h2>Set New Password</h2>

    <form method="POST">
        <input type="password"
               name="password"
               placeholder="New Password"
               minlength="8"
               required>

        <button type="submit">
            Change Password
        </button>
    </form>
    """

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
@app.route("/my-bookings")
def my_bookings():

    if "user" not in session:
        return redirect(url_for("login"))

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

    bookings = get_user_bookings(user_id)

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )
@app.route("/cancel-booking/<booking_id>", methods=["POST"])
def cancel_booking(booking_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    # Current logged-in user's ID
    cursor.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (session["user"],)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return "User not found"

    user_id = user[0]

    # Cancel only this user's booking
    cursor.execute("""
        UPDATE bookings
        SET booking_status = 'Cancelled'
        WHERE booking_id = ?
        AND user_id = ?
    """, (booking_id, user_id))

    connection.commit()
    connection.close()

    return redirect(url_for("my_bookings"))

@app.route("/booking-details/<booking_id>")
def booking_details(booking_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("achron.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (session["user"],)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return "User not found"

    user_id = user["user_id"]

    cursor.execute("""
        SELECT
            booking_id,
            destination,
            travel_date,
            travellers,
            seat_number,
            booking_status,
            total_amount,
            payment_status,
            booking_time,
            pnr
        FROM bookings
        WHERE booking_id = ?
        AND user_id = ?
    """, (booking_id, user_id))

    booking = cursor.fetchone()

    connection.close()

    if booking is None:
        return "Booking not found"

    print("BOOKING TIME:", booking["booking_time"])

    return render_template(
        "booking_details.html",
        booking=booking
    )

@app.route("/booking-qr/<booking_id>")
def booking_qr(booking_id):

    if "user" not in session:
        return redirect(url_for("login"))

    connection = sqlite3.connect("achron.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_id FROM users WHERE email = ?",
        (session["user"],)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return "User not found"

    user_id = user["user_id"]

    cursor.execute("""
        SELECT
            booking_id,
            destination,
            travel_date,
            travellers,
            seat_number,
            booking_status,
            total_amount,
            payment_status,
            pnr,
            booking_time
        FROM bookings
        WHERE booking_id = ?
        AND user_id = ?
    """, (booking_id, user_id))

    booking = cursor.fetchone()

    connection.close()

    if booking is None:
        return "Booking not found"

    qr_data = f"""
ACHRON TRAVEL AGENT
Booking ID: {booking["booking_id"]}
PNR: {booking["pnr"]}
Destination: {booking["destination"]}
Travel Date: {booking["travel_date"]}
Booking Time: {booking["booking_time"]}
Travellers: {booking["travellers"]}
Seat: {booking["seat_number"] or "Not selected"}
Status: {booking["booking_status"]}
"""

    qr = qrcode.make(qr_data)

    os.makedirs("static/qr", exist_ok=True)

    filename = f"{booking_id}.png"

    filepath = os.path.join(
        "static",
        "qr",
        filename
    )

    qr.save(filepath)

    return render_template(
        "qr_ticket.html",
        booking=booking,
        qr_file=f"qr/{filename}"
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
