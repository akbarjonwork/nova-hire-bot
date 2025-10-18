# db.py
import sqlite3
from datetime import datetime
import os
from typing import Optional

DB_PATH = os.getenv("DATABASE_PATH", "./data/candidates.db")

def init_db(path: Optional[str] = None):
    path = path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    cur = conn.cursor()
    with open("schema.sql", "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    conn.commit()
    conn.close()

def save_candidate(data: dict, path: Optional[str] = None) -> int:
    path = path or DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''
      INSERT INTO candidates (
        full_name, occupation, phone_number,
        telegram_username, reason_apply, reason_leave,
        self_intro_text, self_intro_voice_file_id, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("full_name"),
        data.get("occupation"),
        data.get("phone_number"),
        data.get("telegram_username"),
        data.get("reason_apply"),
        data.get("reason_leave"),
        data.get("self_intro_text"),
        data.get("self_intro_voice_file_id"),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def get_last_id(path: Optional[str] = None) -> int:
    path = path or DB_PATH
    if not os.path.exists(path):
        return 0
    conn = sqlite3.connect(path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("SELECT id FROM candidates ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0
