"""SQLite data layer for Spendly.

Three entry points:
    get_db()   — open a connection with row_factory + foreign_keys enabled
    init_db()  — create tables (idempotent)
    seed_db()  — insert demo user + sample expenses (idempotent)

All queries are parameterized. Passwords are hashed via werkzeug.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash


# Database file lives in the project root, next to app.py.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")


def get_db():
    """Return a SQLite connection with dict-like rows and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create users + expenses tables if they don't already exist."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert one demo user + 8 sample expenses. Safe to call repeatedly."""
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return  # already seeded

        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (
                "Demo User",
                "demo@spendly.com",
                generate_password_hash("demo123"),
            ),
        )
        demo_user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()["id"]

        # 8 expenses covering all 7 fixed categories (Food has two).
        expenses = [
            (demo_user_id, 12.50, "Food",          "2026-06-02", "Lunch at cafe"),
            (demo_user_id, 45.00, "Food",          "2026-06-05", "Weekly groceries"),
            (demo_user_id,  8.00, "Transport",     "2026-06-07", "Bus pass"),
            (demo_user_id, 89.99, "Bills",         "2026-06-10", "Internet bill"),
            (demo_user_id, 25.00, "Health",        "2026-06-12", "Pharmacy"),
            (demo_user_id, 15.00, "Entertainment", "2026-06-15", "Movie ticket"),
            (demo_user_id, 60.00, "Shopping",      "2026-06-18", "New shoes"),
            (demo_user_id, 10.00, "Other",         "2026-06-20", "Misc"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    finally:
        conn.close()
