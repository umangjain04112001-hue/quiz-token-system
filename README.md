# Quiz Make-Up Token System

A small command-line tool that issues a **one-time token** linking a student, a
professor, and a missed quiz. When the student redeems the token, the system
emails the professor a make-up request and permanently marks the token as used
so it can never be reused.

## How it works

1. **Issue** – The professor (or system) creates a token for a student who
   missed a quiz. The token is a cryptographically random string.
2. **Redeem** – The student runs the redeem command with their token. If the
   token is valid and unused, the system emails the professor and then flips the
   token to "used" forever.
3. **Verify** – Anyone can check a token's status without spending it.

The "used only once" guarantee is enforced by a SQLite database that persists
the `used` state between runs. Redeeming uses a conditional `UPDATE ... WHERE
used = 0`, so a token can never be spent twice — even on rapid double-runs.

## Project structure

```
quiz-token-system/
├── README.md          # this file
├── .gitignore         # keeps secrets + database out of git
├── .env.example       # template for your SMTP credentials
├── requirements.txt   # dependencies
├── token_manager.py   # issue / verify / redeem logic + SQLite storage
├── emailer.py         # sends the email via SMTP
└── main.py            # command-line entry point
```

## Setup

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/quiz-token-system.git
cd quiz-token-system
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure email credentials

Copy the example env file and fill in your real values:

```bash
cp .env.example .env
```

Then edit `.env`. For Gmail you must use an **App Password**, not your normal
password:

1. Enable 2-Step Verification on your Google account.
2. Go to Google Account → Security → App passwords.
3. Generate a password for "Mail" and paste the 16-character value into
   `SMTP_PASSWORD` in your `.env`.

## Usage

### Issue a token (professor)

```bash
python main.py issue \
    --student-name "Umang Jain" \
    --student-email "umang@example.com" \
    --professor-email "prof@example.com" \
    --quiz-id "QUIZ-03"
```

This prints a token. Give it to the student.

### Verify a token (no spend)

```bash
python main.py verify --token "PASTE_TOKEN_HERE"
```

### Redeem a token (student) — sends the email

```bash
python main.py redeem --token "PASTE_TOKEN_HERE"
```

Running redeem a second time on the same token will fail.

## Security note

This is a **convenience and tracking tool**, not a security system. A student
could always email a professor directly without a token. The token gives the
professor a clean, structured, one-time make-up request and a record of when it
was submitted. Do not treat it as authentication.

## License

MIT
