# database.py
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")  # must be set in Railway env variables
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set. Please configure your Postgres DATABASE_URL env var.")
    # We still allow import but operations will fail later with clear error.

def init_db():
    """Create candidates table in Postgres (id SERIAL PRIMARY KEY)."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not configured. init_db cannot proceed.")

    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError as e:
        raise RuntimeError("psycopg2 not installed. Add psycopg2-binary to requirements.") from e

    conn = None
    try:
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
        logger.info("✅ Postgres: candidates table is ready.")
    except Exception as e:
        logger.exception("Failed to initialize Postgres DB: %s", e)
        raise
    finally:
        if conn:
            conn.close()

def save_candidate(data: dict):
    """Insert a candidate row into Postgres."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not configured. save_candidate cannot proceed.")

    try:
        import psycopg2
    except ImportError as e:
        raise RuntimeError("psycopg2 not installed. Add psycopg2-binary to requirements.") from e

    insert_sql = """
        INSERT INTO candidates (
            candidate_id, full_name, birth_date, age, address, job_type,
            extra_skills, phone_number, telegram_username, last_workplace_voice_id, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode=os.getenv("PGSSLMODE", "require"))
        cur = conn.cursor()
        cur.execute(insert_sql, values)
        conn.commit()
        cur.close()
        logger.info("✅ Saved candidate %s", data.get("candidate_id"))
    except Exception as e:
        logger.exception("Failed to save candidate: %s", e)
        raise
    finally:
        if conn:
            conn.close()
