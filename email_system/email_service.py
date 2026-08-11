import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_welcome_email(user_email, user_name):
    response = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": user_email,
        "subject": "Welcome to ACHRON Travel Agent",
        "html": f"""
        <h1>Welcome {user_name} 🎉</h1>
        <p>Thank you for joining ACHRON Travel Agent.</p>
        <p>Your journey starts here.</p>
        """
    })
    return response


def send_booking_confirmation(
    user_email,
    booking_id,
    destination,
    travel_date,
    travellers,
    seat_number,
    total_amount
):
    booking_url = "https://YOUR-DOMAIN.com/bookings"

    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": user_email,
            "subject": f"ACHRON Booking Confirmed - {booking_id}",
            "html": f"""
                <h2>🎉 ACHRON Booking Confirmed</h2>
                <p>Booking ID: {booking_id}</p>
                <p>Destination: {destination}</p>
                <p>Travel Date: {travel_date}</p>
                <p>Travellers: {travellers}</p>
                <p>Total: ₹{total_amount}</p>

                <a href="{booking_url}">
                    View My Booking
                </a>
            """
        })

        print("EMAIL SENT:", response)
        return response

    except Exception as e:
        print("EMAIL ERROR:", e)
        return None