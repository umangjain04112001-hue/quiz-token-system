"""
token_manager.py
----------------
Core logic for the one-time quiz make-up token system.

Handles three things:
  - issue()  : create a new token for a student who missed a quiz
  - verify() : check a token's status WITHOUT spending it
  - redeem() : spend a token (marks it used forever)

Storage is a local SQLite file so the "used" state survives between runs.
Without persistent storage, "use only once" would be impossible.
"""

import sqlite3
import secrets
from datetime import datetime, timezone

DB_FILE = "tokens.db"


def _connect():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the tokens table if it does not exist yet. Safe to run repeatedly."""
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            token           TEXT PRIMARY KEY,
            student_name    TEXT NOT NULL,
            student_email   TEXT NOT NULL,
            professor_email TEXT NOT NULL,
            quiz_id         TEXT NOT NULL,
            used            INTEGER NOT NULL DEFAULT 0,
            created_at      TEXT NOT NULL,
            used_at         TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def issue(student_name, student_email, professor_email, quiz_id):
    """
    Create a new one-time token and store it.
    Returns the token string.
    """
    init_db()
    token = secrets.token_urlsafe(24)  # cryptographically random, not guessable
    created_at = datetime.now(timezone.utc).isoformat()

    conn = _connect()
    conn.execute(
        """
        INSERT INTO tokens
            (token, student_name, student_email, professor_email, quiz_id, used, created_at, used_at)
        VALUES (?, ?, ?, ?, ?, 0, ?, NULL)
        """,
        (token, student_name, student_email, professor_email, quiz_id, created_at),
    )
    conn.commit()
    conn.close()
    return token


def get(token):
    """Fetch a token row as a dict, or None if it does not exist."""
    init_db()
    conn = _connect()
    row = conn.execute("SELECT * FROM tokens WHERE token = ?", (token,)).fetchone()
    conn.close()
    return dict(row) if row else None


def verify(token):
    """
    Check a token without spending it.
    Returns a tuple: (is_valid: bool, message: str, row: dict or None)
    """
    row = get(token)
    if row is None:
        return False, "Token not found.", None
    if row["used"] == 1:
        return False, f"Token already used at {row['used_at']}.", row
    return True, "Token is valid and unused.", row


def redeem(token):
    """
    Spend a token. Marks it used forever.

    IMPORTANT: this only flips the flag if the token is currently unused.
    The WHERE used = 0 condition makes this safe even if called twice quickly:
    the second call updates 0 rows and we detect that.

    Returns a tuple: (success: bool, message: str, row: dict or None)
    """
    is_valid, message, row = verify(token)
    if not is_valid:
        return False, message, row

    used_at = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    cursor = conn.execute(
        "UPDATE tokens SET used = 1, used_at = ? WHERE token = ? AND used = 0",
        (used_at, token),
    )
    conn.commit()
    rows_changed = cursor.rowcount
    conn.close()

    if rows_changed == 0:
        # Someone beat us to it between verify and update.
        return False, "Token was already used.", row

    row["used"] = 1
    row["used_at"] = used_at
    return True, "Token redeemed successfully.", row
