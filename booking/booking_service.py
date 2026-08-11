import sqlite3

DATABASE_NAME = "achron.db"


def get_user_bookings(user_id):
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

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
            booking_time
        FROM bookings
        WHERE user_id = ?
        ORDER BY booking_time DESC
    """, (user_id,))

    bookings = cursor.fetchall()

    connection.close()

    return bookings

def save_booking(
    booking_id,
    user_id,
    hotel_id,
    flight_id,
    pnr,
    destination,
    travel_date,
    travellers,
    seat_number,
    total_amount,
    payment_status="Pending"
):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bookings (
            booking_id,
            user_id,
            hotel_id,
            flight_id,
            pnr,
            destination,
            travel_date,
            travellers,
            seat_number,
            total_amount,
            payment_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking_id,
        user_id,
        hotel_id,
        flight_id,
        pnr,
        destination,
        travel_date,
        travellers,
        seat_number,
        total_amount,
        payment_status
    ))

    connection.commit()
    connection.close()

    return True