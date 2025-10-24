# database.py
import os
import sqlite3
from datetime import datetime

# Try Postgres first (DATABASE_URL), else use SQLite file
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgres://user:pass@host:port/dbname
DB_PATH = os.getenv("DATABASE_PATH", "candidates.db")


def init_db():
    """Initialize DB. If DATABASE_URL present, create table in Postgres.
       Otherwise create SQLite database file and table."""
    if DATABASE_URL:
        # create table in Postgres
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL, sslmode=os.getenv("PGSSLMODE", "require"))
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id SERIAL PRIMARY KEY,
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
                    created_at TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            raise
    else:
        # sqlite fallback
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
    """Save candidate dict to the active DB (Postgres if configured, otherwise sqlite)."""
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL, sslmode=os.getenv("PGSSLMODE", "require"))
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO candidates (
                candidate_id, full_name, birth_date, age, address, job_type,
                extra_skills, phone_number, telegram_username, last_workplace_voice_id, created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
            data.get("last_workplace_voice_id"),
            datetime.now()
        ))
        conn.commit()
        cur.close()
        conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO candidates (
                candidate_id, full_name, birth_date, age, address, job_type,
                extra_skills, phone_number, telegram_username, last_workplace_voice_id, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
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
            data.get("last_workplace_voice_id"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
