import sqlite3

def get_user(email):
    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT full_name, email, phone
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return user

def update_user(email, full_name, phone):
    connection = sqlite3.connect("achron.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET full_name = ?, phone = ?
        WHERE email = ?
    """, (full_name, phone, email))

    connection.commit()
    connection.close()