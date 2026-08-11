from dataclasses import dataclass

# =========================
# USER MODEL
# =========================
@dataclass
class User:
    user_id: int
    full_name: str
    email: str
    phone: str
    password: str
    language: str
    created_at: str


# =========================
# HOTEL MODEL
# =========================
@dataclass
class Hotel:
    hotel_id: int
    hotel_name: str
    city: str
    country: str
    rating: float
    price: float
    verified: bool


# =========================
# FLIGHT MODEL
# =========================
@dataclass
class Flight:
    flight_id: int
    airline: str
    flight_number: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float


# =========================
# BOOKING MODEL
# =========================
@dataclass
class Booking:
    booking_id: str
    user_id: int
    hotel_id: int
    flight_id: int
    pnr: str
    travel_date: str
    travellers: int
    total_amount: float
    booking_status: str


# =========================
# PAYMENT MODEL
# =========================
@dataclass
class Payment:
    payment_id: str
    booking_id: str
    amount: float
    payment_method: str
    payment_status: str
    transaction_id: str