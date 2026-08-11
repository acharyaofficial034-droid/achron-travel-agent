import bcrypt
import sqlite3

def hash_password(password):
    password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode("utf-8")


def verify_password(password, hashed_password):
    password = password.encode("utf-8")
    hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password, hashed_password)


def update_password(email, new_password):
    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    hashed_password = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE email = ?
    """, (hashed_password, email))

    connection.commit()
    connection.close()

