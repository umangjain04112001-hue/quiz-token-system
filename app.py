"""
app.py
------
Web version of the one-time quiz make-up token system.

Pages:
  /            - home, links to the two flows
  /issue       - professor issues a token (form)
  /redeem      - student redeems a token (form) -> emails the professor
  /verify      - optional, check a token's status without spending it

Run locally:
  python app.py
then open http://localhost:5000

When deployed, a host like Render runs it with gunicorn (see Procfile).
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

import token_manager
import emailer

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/issue", methods=["GET", "POST"])
def issue():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        student_email = request.form.get("student_email", "").strip()
        professor_email = request.form.get("professor_email", "").strip()
        quiz_id = request.form.get("quiz_id", "").strip()

        # Basic validation: all fields required.
        if not all([student_name, student_email, professor_email, quiz_id]):
            return render_template(
                "issue.html",
                error="Please fill in every field.",
                form=request.form,
            )

        token = token_manager.issue(
            student_name, student_email, professor_email, quiz_id
        )
        return render_template("issue.html", token=token)

    return render_template("issue.html")


@app.route("/redeem", methods=["GET", "POST"])
def redeem():
    if request.method == "POST":
        token = request.form.get("token", "").strip()

        if not token:
            return render_template("redeem.html", error="Please paste your token.")

        # Check the token WITHOUT spending it.
        is_valid, message, row = token_manager.verify(token)
        if not is_valid:
            return render_template("redeem.html", error=message)

        # Send the email FIRST. If it fails, the token stays valid.
        sent, email_message = emailer.send_makeup_request(row)
        if not sent:
            return render_template(
                "redeem.html",
                error=f"{email_message} Your token was NOT used - please try again.",
            )

        # Email worked, so now spend the token.
        success, spend_message, row = token_manager.redeem(token)
        if not success:
            return render_template("redeem.html", error=spend_message)

        return render_template(
            "redeem.html",
            success=True,
            professor_email=row["professor_email"],
            quiz_id=row["quiz_id"],
        )

    return render_template("redeem.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        token = request.form.get("token", "").strip()
        if not token:
            return render_template("verify.html", error="Please paste a token.")
        is_valid, message, row = token_manager.verify(token)
        return render_template(
            "verify.html", checked=True, is_valid=is_valid, message=message, row=row
        )
    return render_template("verify.html")


if __name__ == "__main__":
    # host=0.0.0.0 so it works both locally and when deployed.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
