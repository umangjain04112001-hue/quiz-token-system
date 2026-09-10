"""
emailer.py
----------
Sends the quiz make-up request email to the professor via SMTP.

Credentials are read from environment variables (loaded from a .env file),
so NOTHING sensitive is ever written into the code or committed to GitHub.

Required environment variables:
  SMTP_HOST     e.g. smtp.gmail.com
  SMTP_PORT     e.g. 587
  SMTP_USER     the sending email address (e.g. your Gmail)
  SMTP_PASSWORD an app password (NOT your normal login password)
"""

import os
import smtplib
from email.message import EmailMessage


def send_makeup_request(row):
    """
    Send the make-up request email to the professor.

    `row` is the token record dict (from token_manager).
    Returns a tuple: (success: bool, message: str)
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    # Fail loudly if the environment is not configured.
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
        return False, f"Missing environment variables: {', '.join(missing)}"

    # Build the email.
    msg = EmailMessage()
    msg["Subject"] = f"Quiz Make-Up Request - Quiz {row['quiz_id']}"
    msg["From"] = smtp_user
    msg["To"] = row["professor_email"]
    msg["Reply-To"] = row["student_email"]

    body = (
        f"Dear Professor,\n\n"
        f"This is an automated make-up request submitted by a student "
        f"who missed a quiz.\n\n"
        f"  Student name : {row['student_name']}\n"
        f"  Student email: {row['student_email']}\n"
        f"  Quiz ID      : {row['quiz_id']}\n"
        f"  Request time : {row['used_at']}\n\n"
        f"This request was submitted using a valid one-time token, "
        f"which has now been marked as used and cannot be reused.\n\n"
        f"Please reply directly to the student at {row['student_email']} "
        f"to arrange the make-up.\n\n"
        f"— Quiz Token System"
    )
    msg.set_content(body)

    # Send it.
    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()  # upgrade the connection to encrypted
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True, f"Email sent to {row['professor_email']}."
    except Exception as e:
        return False, f"Failed to send email: {e}"
