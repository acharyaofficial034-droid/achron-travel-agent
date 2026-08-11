import sqlite3
from auth.password import hash_password

def create_user(full_name, email, phone, password):
    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        INSERT INTO users(full_name, email, phone, password)
        VALUES (?, ?, ?, ?)
    """, (full_name, email, phone, hashed_password))

    connection.commit()
    connection.close()

    print("✅ Account Created Successfully!")