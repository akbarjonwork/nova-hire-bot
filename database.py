# database.py
import sqlite3
from datetime import datetime

DB_PATH = "candidates.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT,
        full_name TEXT,
        birth_date TEXT,
        age INTEGER,
        address TEXT,
        job_type TEXT,
        extra_skills TEXT,
        phone_number TEXT,
        telegram_username TEXT,
        last_workplace_voice_id TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def save_candidate(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO candidates (
        candidate_id, full_name, birth_date, age, address, job_type,
        extra_skills, phone_number, telegram_username, last_workplace_voice_id, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("candidate_id"),
        data.get("full_name"),
        data.get("birth_date"),
        data.get("age"),
        data.get("address"),
        data.get("job_type"),
        data.get("extra_skills"),
        data.get("phone_number"),
        data.get("username"),
        data.get("last_workplace_voice_id", None),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
