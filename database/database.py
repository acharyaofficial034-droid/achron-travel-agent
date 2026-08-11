import sqlite3
DATABASE_NAME = "achron.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection
def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    print("✅ Database Connected Successfully!")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    language TEXT DEFAULT 'English',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    address TEXT,
    rating REAL,
    price_per_night REAL,
    total_rooms INTEGER,
    available_rooms INTEGER,
    amenities TEXT,
    verified INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airline_name TEXT NOT NULL,
    flight_number TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    duration TEXT,
    price REAL NOT NULL,
    available_seats INTEGER,
    status TEXT DEFAULT 'On Time',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    booking_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    hotel_id INTEGER,
    flight_id INTEGER,
    pnr TEXT UNIQUE,
    destination TEXT NOT NULL,
    travel_date TEXT NOT NULL,
    travellers INTEGER NOT NULL,
    seat_number TEXT,
    booking_status TEXT DEFAULT 'Confirmed',
    total_amount REAL NOT NULL,
    payment_status TEXT DEFAULT 'Pending',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(hotel_id) REFERENCES hotels(hotel_id),
    FOREIGN KEY(flight_id) REFERENCES flights(flight_id)
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    booking_id TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    transaction_id TEXT UNIQUE,
    payment_status TEXT DEFAULT 'Success',
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS wishlist (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination TEXT,
    hotel_id INTEGER,
    flight_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(hotel_id) REFERENCES hotels(hotel_id),
    FOREIGN KEY(flight_id) REFERENCES flights(flight_id)
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hotel_id INTEGER,
    rating REAL NOT NULL,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(hotel_id) REFERENCES hotels(hotel_id)
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS coupons (
    coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_code TEXT UNIQUE NOT NULL,
    discount REAL NOT NULL,
    expiry_date TEXT NOT NULL,
    status TEXT DEFAULT 'Active'
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS referrals (
    referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_user_id INTEGER NOT NULL,
    referred_user_id INTEGER NOT NULL,
    reward REAL DEFAULT 0,

    FOREIGN KEY(referrer_user_id) REFERENCES users(user_id),
    FOREIGN KEY(referred_user_id) REFERENCES users(user_id)
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_query TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS emergency_contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    city TEXT,
    police TEXT,
    ambulance TEXT,
    hospital TEXT,
    embassy TEXT
)
""")
    
    connection.commit()
    connection.close()

