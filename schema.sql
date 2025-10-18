CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT,
  occupation TEXT,
  phone_number TEXT,
  telegram_username TEXT,
  reason_apply TEXT,
  reason_leave TEXT,
  self_intro_text TEXT,
  self_intro_voice_file_id TEXT,
  created_at TEXT
);
