import os
import bcrypt
import psycopg2
import psycopg2.errors
from datetime import datetime


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PG_HOST", "localhost"),
        port=os.environ.get("PG_PORT", "5432"),
        user=os.environ.get("PG_USER"),
        password=os.environ.get("PG_PASSWORD"),
        dbname=os.environ.get("PG_DATABASE"),
        sslmode=os.environ.get("PG_SSLMODE", "prefer")
    )


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            timestamp VARCHAR(50) NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            timestamp VARCHAR(50) NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key VARCHAR(100) NOT NULL,
            value TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            timestamp TEXT NOT NULL
        )
    """)

    # Migration: add user_id to tables that already exist without it
    for table in ["messages", "notes", "preferences", "goals"]:
        c.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS user_id INT")

    # preferences used key as the primary key; it must be unique per user instead
    c.execute("ALTER TABLE preferences DROP CONSTRAINT IF EXISTS preferences_pkey")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS prefs_user_key ON preferences (user_id, key)")

    conn.commit()
    conn.close()


# ---------- users ----------

def create_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, created) VALUES (%s, %s, %s)",
                  (username, hashed, datetime.now().isoformat()))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row[1].encode()):
        return row[0]
    return None


# ---------- messages ----------

def save_message(user_id, role, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, role, content, timestamp) VALUES (%s, %s, %s, %s)",
              (user_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def load_messages(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE user_id = %s ORDER BY id", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r, "content": content} for r, content in rows]


# ---------- notes ----------

def save_note(user_id, title, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, title, content, timestamp) VALUES (%s, %s, %s, %s)",
              (user_id, title, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def load_notes(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, content, timestamp FROM notes WHERE user_id = %s ORDER BY id DESC",
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "content": r[2], "timestamp": r[3]} for r in rows]


def delete_note(user_id, note_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
    conn.commit()
    conn.close()


# ---------- preferences ----------

def save_preference(user_id, key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO preferences (user_id, key, value) VALUES (%s, %s, %s)
        ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value
    """, (user_id, key, value))
    conn.commit()
    conn.close()


def load_preferences(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM preferences WHERE user_id = %s", (user_id,))
    rows = c.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def delete_preference(user_id, key):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM preferences WHERE key = %s AND user_id = %s", (key, user_id))
    conn.commit()
    conn.close()


# ---------- goals ----------

def save_goal(user_id, title):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO goals (user_id, title, status, timestamp) VALUES (%s, %s, 'active', %s)",
              (user_id, title, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def load_goals(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, status, timestamp FROM goals WHERE user_id = %s ORDER BY id DESC",
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "status": r[2], "timestamp": r[3]} for r in rows]


def update_goal_status(user_id, goal_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE goals SET status = %s WHERE id = %s AND user_id = %s",
              (status, goal_id, user_id))
    conn.commit()
    conn.close()


def delete_goal(user_id, goal_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
    conn.commit()
    conn.close()