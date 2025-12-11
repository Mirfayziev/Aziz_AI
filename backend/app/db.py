import sqlite3
from contextlib import closing
from sqlalchemy.orm import Session 

DB_PATH = "azizai.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn:
        cur = conn.cursor()

        # User context (memory / state)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_context (
            user_id TEXT PRIMARY KEY,
            context TEXT
        )
        """)

        # Chat history
        cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()


# ================================
#  MEMORY FUNCTIONS
# ================================

def get_user_context(user_id: str) -> str:
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        row = cur.execute("SELECT context FROM user_context WHERE user_id=?", (user_id,)).fetchone()
        return row["context"] if row else ""


def save_user_context(user_id: str, context: str):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_context (user_id, context)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET context=excluded.context
        """, (user_id, context))
        conn.commit()


# ================================
#  CHAT HISTORY
# ================================

def save_ai_message(user_id: str, role: str, message: str):
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chat_history (user_id, role, message)
            VALUES (?, ?, ?)
        """, (user_id, role, message))
        conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
