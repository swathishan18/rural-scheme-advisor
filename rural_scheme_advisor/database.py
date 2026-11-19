import os
import sqlite3
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get(
    "RURAL_SCHEME_DB", os.path.join(BASE_DIR, "rural_scheme_advisor.db")
)


def get_connection(db_path=None):
    path = db_path or DATABASE_PATH
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                phone_number TEXT,
                state TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message_content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                age INTEGER,
                gender TEXT,
                occupation TEXT,
                annual_income INTEGER,
                owns_land INTEGER,
                has_pucca_house INTEGER,
                state TEXT,
                has_girl_child_under_10 INTEGER,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
            """
        )


def _now():
    return datetime.now().isoformat(timespec="seconds")


def create_user(full_name, email, password_hash, phone_number="", state="", db_path=None):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO users
               (full_name, email, password_hash, phone_number, state, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (full_name.strip(), email.lower().strip(), password_hash,
             phone_number.strip(), state.strip(), _now()),
        )
        return cur.lastrowid


def get_user_by_email(email, db_path=None):
    with get_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE lower(email) = lower(?)", (email.strip(),)
        ).fetchone()


def get_user_by_id(user_id, db_path=None):
    with get_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (int(user_id),)
        ).fetchone()


def update_user(user_id, full_name, phone_number, state, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE users SET full_name=?, phone_number=?, state=? WHERE user_id=?""",
            (full_name.strip(), phone_number.strip(), state.strip(), int(user_id)),
        )


def update_password(user_id, password_hash, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE users SET password_hash=? WHERE user_id=?",
            (password_hash, int(user_id)),
        )


def create_conversation(user_id, title="Scheme assistance", db_path=None):
    now = _now()
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO conversations
               (user_id, conversation_title, created_at, updated_at)
               VALUES (?, ?, ?, ?)""",
            (int(user_id), title[:120], now, now),
        )
        return cur.lastrowid


def get_conversations(user_id, db_path=None):
    with get_connection(db_path) as conn:
        return conn.execute(
            """SELECT * FROM conversations
               WHERE user_id=? ORDER BY updated_at DESC""",
            (int(user_id),),
        ).fetchall()


def get_conversation(conversation_id, user_id, db_path=None):
    with get_connection(db_path) as conn:
        return conn.execute(
            """SELECT * FROM conversations
               WHERE conversation_id=? AND user_id=?""",
            (int(conversation_id), int(user_id)),
        ).fetchone()


def add_message(conversation_id, user_id, role, content, db_path=None):
    now = _now()
    with get_connection(db_path) as conn:
        owned = conn.execute(
            "SELECT 1 FROM conversations WHERE conversation_id=? AND user_id=?",
            (int(conversation_id), int(user_id)),
        ).fetchone()
        if not owned:
            raise PermissionError("Conversation does not belong to this user")
        conn.execute(
            """INSERT INTO messages
               (conversation_id, role, message_content, created_at)
               VALUES (?, ?, ?, ?)""",
            (int(conversation_id), role, content, now),
        )
        conn.execute(
            "UPDATE conversations SET updated_at=? WHERE conversation_id=?",
            (now, int(conversation_id)),
        )


def get_messages(conversation_id, user_id, db_path=None):
    with get_connection(db_path) as conn:
        owned = conn.execute(
            "SELECT 1 FROM conversations WHERE conversation_id=? AND user_id=?",
            (int(conversation_id), int(user_id)),
        ).fetchone()
        if not owned:
            return []
        return conn.execute(
            """SELECT role, message_content, created_at FROM messages
               WHERE conversation_id=? ORDER BY created_at, message_id""",
            (int(conversation_id),),
        ).fetchall()


def delete_conversation(conversation_id, user_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            "DELETE FROM conversations WHERE conversation_id=? AND user_id=?",
            (int(conversation_id), int(user_id)),
        )


def clear_conversations(user_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM conversations WHERE user_id=?", (int(user_id),))


def get_profile(user_id, db_path=None):
    with get_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM user_profiles WHERE user_id=?", (int(user_id),)
        ).fetchone()


def save_profile(user_id, profile, db_path=None):
    now = _now()
    values = (
        int(user_id),
        profile.get("age"),
        profile.get("gender"),
        profile.get("occupation"),
        profile.get("annual_income"),
        1 if profile.get("owns_land") is True else (0 if profile.get("owns_land") is False else None),
        1 if profile.get("has_pucca_house") is True else (0 if profile.get("has_pucca_house") is False else None),
        profile.get("state"),
        1 if profile.get("has_girl_child_under_10") is True else (0 if profile.get("has_girl_child_under_10") is False else None),
        now,
    )
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO user_profiles
               (user_id, age, gender, occupation, annual_income, owns_land,
                has_pucca_house, state, has_girl_child_under_10, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
               age=excluded.age, gender=excluded.gender,
               occupation=excluded.occupation, annual_income=excluded.annual_income,
               owns_land=excluded.owns_land, has_pucca_house=excluded.has_pucca_house,
               state=excluded.state,
               has_girl_child_under_10=excluded.has_girl_child_under_10,
               updated_at=excluded.updated_at""",
            values,
        )


def dashboard_stats(user_id, db_path=None):
    with get_connection(db_path) as conn:
        conversations = conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE user_id=?", (int(user_id),)
        ).fetchone()[0]
        questions = conn.execute(
            """SELECT COUNT(*) FROM messages m
               JOIN conversations c ON c.conversation_id=m.conversation_id
               WHERE c.user_id=? AND m.role='user'""",
            (int(user_id),),
        ).fetchone()[0]
        recent = conn.execute(
            """SELECT conversation_title, updated_at FROM conversations
               WHERE user_id=? ORDER BY updated_at DESC LIMIT 5""",
            (int(user_id),),
        ).fetchall()
    return conversations, questions, recent


init_db()
