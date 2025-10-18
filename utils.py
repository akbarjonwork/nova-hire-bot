# utils.py
import os
from dotenv import load_dotenv
from db import get_last_id

load_dotenv()

def get_env(key: str, default=None):
    return os.getenv(key, default)

def next_candidate_code() -> str:
    last = get_last_id()
    return f"{last + 1:06d}"
