import sqlite3
from auth.password import hash_password

def create_user(full_name, email, phone, password):
    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(password)
        print("DEBUG PHONE:", repr(phone))

        cursor.execute("""
            INSERT INTO users(full_name, email, phone, password)
            VALUES (?, ?, ?, ?)
        """, (full_name, email, phone, hashed_password))

        connection.commit()
        print("✅ Account Created Successfully!")
        return True, "Account created successfully!"

    except sqlite3.IntegrityError as e:
        connection.rollback()

        if "users.phone" in str(e):
            return False, "Phone number already registered."

        if "users.email" in str(e):
            return False, "Email already registered."

        return False, "This account information is already registered."

    finally:
        connection.close()