import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi import HTTPException

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
FRONTEND_URL = os.getenv("FRONTEND_URL")


"""
This module provides functionality to send email verification messages using SendGrid.
"""


def send_verification_email(to_email: str, token: str):
    """
    Sends a verification email to the specified email address using the provided token.

    Args:
        to_email (str): The recipient's email address.
        token (str): The token used to generate the verification link.

    Raises:
        HTTPException: If the email fails to send or an exception occurs during the process.
    """
    subject = "Verify Your Email"
    verification_link = f"{FRONTEND_URL}/auth/verify-email?token={token}"

    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=to_email,
        subject=subject,
        html_content=f"""
        <h1>Verify Your Email Address</h1>
        <p>Click the link below to verify your email address:</p>
        <a href="{verification_link}">Verify Email</a>
        """,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code != 202:
            raise HTTPException(status_code=500, detail="Email failed to send")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")
