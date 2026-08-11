import sqlite3
from auth.password import verify_password


def login_user(email, password):
    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT full_name, password FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return False, "User not found"

    full_name, hashed_password = user

    if verify_password(password, hashed_password):
        return True, full_name

    return False, "Incorrect password"