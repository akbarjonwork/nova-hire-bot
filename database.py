# database.py
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    """Create candidates table in Postgres."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not configured.")

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
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Database initialized successfully.")


def get_next_candidate_id():
    """Generate next candidate ID based on current max(id) in DB."""
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL, sslmode=os.getenv("PGSSLMODE", "require"))
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM candidates;")
    next_num = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"C-{next_num:03d}"


def save_candidate(data: dict):
    """Insert candidate data into Postgres."""
    import psycopg2
    insert_sql = """
        INSERT INTO candidates (
            candidate_id, full_name, birth_date, age, address, job_type,
            extra_skills, phone_number, telegram_username, last_workplace_voice_id, created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    values = (
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
    )

    conn = psycopg2.connect(DATABASE_URL, sslmode=os.getenv("PGSSLMODE", "require"))
    cur = conn.cursor()
    cur.execute(insert_sql, values)
    conn.commit()
    cur.close()
    conn.close()
    logger.info("✅ Candidate %s saved.", data.get("candidate_id"))
