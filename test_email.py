import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

response = resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": "subhamacharya419@gmail.com",
    "subject": "ACHRON Travel Agent Test",
    "html": "<h1>Welcome to ACHRON Travel Agent</h1>"
})

print(response)