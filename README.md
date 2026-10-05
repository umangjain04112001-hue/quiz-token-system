# Quiz Make-Up Token System (Web App)

A small web application that issues **one-time tokens** for quiz make-up
requests. A professor issues a token to a student who missed a quiz; the student
redeems it on the website, which emails the professor a make-up request and
permanently marks the token as used so it can never be reused.

Live pages:
- **Issue** a token (professor)
- **Redeem** a token (student) — sends the email
- **Check** a token's status without using it

---

## Run it locally

1. Install Python 3.9+ (https://www.python.org/downloads/).
2. Open a terminal in this folder and run:

   ```
   python -m venv venv
   venv\Scripts\activate        (Mac/Linux: source venv/bin/activate)
   pip install -r requirements.txt
   ```

3. Set up email (see "Email setup" below), then start the server:

   ```
   python app.py
   ```

4. Open http://localhost:5000 in your browser.

---

## Email setup

The redeem page sends an email through Gmail. You configure this **once**.

1. Turn on 2-Step Verification: https://myaccount.google.com/security
2. Create an App Password: https://myaccount.google.com/apppasswords
   (Google shows it with spaces for readability — remove the spaces when you use it.)
3. Copy `.env.example` to `.env` and fill in:

   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_real_gmail@gmail.com
   SMTP_PASSWORD=your16charapppassword
   ```

If email is not configured, issuing and checking tokens still work; only the
redeem email will report that it isn't set up (and the token stays unused so it
can be retried).

---

## Deploy it to a public URL (Render, free)

This makes the app reachable at a link like `https://quiz-token-system.onrender.com`,
with no one's laptop needing to stay on.

1. Push this project to a GitHub repository.
2. Create a free account at https://render.com and connect your GitHub.
3. Click **New → Web Service** and pick this repository.
4. Render reads `render.yaml` automatically. Confirm:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
5. In the service's **Environment** settings, add your two secret values:
   - `SMTP_USER` = your Gmail address
   - `SMTP_PASSWORD` = your Gmail App Password (no spaces)
   (`SMTP_HOST` and `SMTP_PORT` come from `render.yaml`.)
6. Click **Deploy**. When it finishes, Render gives you the public URL.

> Note: on Render's free plan the app sleeps after inactivity and the local
> token database resets on a full redeploy. That's fine for a demo or class use.
> For permanent storage, attach a managed database.

---

## How the one-time guarantee works

Each token is a long random string. Its used/unused state lives in a small
database. Redeeming runs a conditional update that only succeeds if the token is
still unused, so a token can never be spent twice — even on a rapid double
submit. The email is sent *before* the token is marked used, so a failed email
never wastes a token.

---

## Files

```
quiz-token-system/
|-- app.py             # Flask web server (routes for issue/redeem/verify)
|-- token_manager.py   # issue / verify / redeem logic + storage
|-- emailer.py         # sends the email
|-- templates/         # the web pages (home, issue, redeem, verify)
|-- static/            # stylesheet
|-- requirements.txt   # dependencies
|-- Procfile           # tells the host how to start the app
|-- render.yaml        # Render deployment config
|-- .env.example       # template for email credentials
`-- .gitignore         # keeps secrets + database out of version control
```

---

## Scope

This is a **convenience and tracking tool, not a security system.** A student
could always email a professor directly. What the token adds is a clean,
one-time, timestamped make-up request.

## License

MIT
