"""
emailer.py
----------
Sends the quiz make-up request email to the professor via SMTP.

Credentials are read from environment variables (loaded from a .env file
locally, or set in the hosting dashboard when deployed), so nothing sensitive
is ever written into the code.

Required environment variables:
  SMTP_HOST     e.g. smtp.gmail.com
  SMTP_PORT     e.g. 587
  SMTP_USER     the sending email address
  SMTP_PASSWORD a Gmail App Password (NOT a normal password)
"""

import os
import smtplib
from email.message import EmailMessage


def send_makeup_request(row):
    """
    Send the make-up request email to the professor.
    `row` is the token record dict. Returns (success: bool, message: str).
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    missing = [
        name
        for name, value in [
            ("SMTP_HOST", smtp_host),
            ("SMTP_PORT", smtp_port),
            ("SMTP_USER", smtp_user),
            ("SMTP_PASSWORD", smtp_password),
        ]
        if not value
    ]
    if missing:
        return False, f"Email not configured (missing: {', '.join(missing)})."

    msg = EmailMessage()
    msg["Subject"] = f"Quiz Make-Up Request - Quiz {row['quiz_id']}"
    msg["From"] = smtp_user
    msg["To"] = row["professor_email"]
    msg["Reply-To"] = row["student_email"]

    body = (
        f"Dear Professor,\n\n"
        f"A student who missed a quiz has submitted a make-up request.\n\n"
        f"  Student name : {row['student_name']}\n"
        f"  Student email: {row['student_email']}\n"
        f"  Quiz ID      : {row['quiz_id']}\n"
        f"  Request time : {row['used_at']}\n\n"
        f"This request used a valid one-time token, which is now marked used "
        f"and cannot be reused.\n\n"
        f"Please reply directly to the student at {row['student_email']} to "
        f"arrange the make-up.\n\n"
        f"- Quiz Token System"
    )
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True, f"Email sent to {row['professor_email']}."
    except Exception as e:
        return False, f"Failed to send email: {e}"
