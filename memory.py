import os
import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PG_HOST"),
        port=os.environ.get("PG_PORT"),
        user=os.environ.get("PG_USER"),
        password=os.environ.get("PG_PASSWORD"),
        dbname=os.environ.get("PG_DATABASE"),
        sslmode="require"
    )

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active',
            timestamp TEXT NOT NULL
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
        CREATE TABLE IF NOT EXISTS preferences (
            key VARCHAR(100) PRIMARY KEY,
            value TEXT NOT NULL
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
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, content, timestamp) VALUES (%s, %s, %s)",
               (role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def load_messages():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

def save_note(title, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content, timestamp) VALUES (%s, %s, %s)",
               (title, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def load_notes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, content, timestamp FROM notes ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "content": r[2], "timestamp": r[3]} for r in rows]

def delete_note(note_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    conn.close()
    
def save_preference(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO preferences (key, value) VALUES (%s, %s)
        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """, (key, value))
    conn.commit()
    conn.close()

def load_preferences():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM preferences")
    rows = c.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}

def delete_preference(key):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM preferences WHERE key = %s", (key,))
    conn.commit()
    conn.close()
def save_goal(title):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO goals (title, status, timestamp) VALUES (%s, 'active', %s)",
               (title, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def load_goals():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, status, timestamp FROM goals ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "status": r[2], "timestamp": r[3]} for r in rows]

def update_goal_status(goal_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE goals SET status = %s WHERE id = %s", (status, goal_id))
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE id = %s", (goal_id,))
    conn.commit()
    conn.close()