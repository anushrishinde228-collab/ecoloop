import sqlite3
from datetime import datetime

DB_NAME = "ecoloop.db"

def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users table (with password column)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            total_earned INTEGER DEFAULT 0,
            total_items INTEGER DEFAULT 0,
            env_score INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # Recycling history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            item_type TEXT NOT NULL,
            price INTEGER NOT NULL,
            address TEXT,
            phone TEXT,
            pickup_date TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def get_or_create_user(username):
    """Get user from DB or create if new. Returns user data."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT username, total_earned, total_items, env_score FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    if user is None:
        c.execute(
            "INSERT INTO users (username, total_earned, total_items, env_score, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, 0, 0, 0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
        user = (username, 0, 0, 0)
    
    conn.close()
    return {
        "username": user[0],
        "total_earned": user[1],
        "total_items": user[2],
        "env_score": user[3]
    }


def get_user_password(username):
    """Get the saved password for a user. Returns None if user doesn't exist or has no password."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_user_password(username, password):
    """Save password for a user (first-time registration)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (password, username))
    conn.commit()
    conn.close()


def save_pickup(username, items, address, phone, pickup_date, total):
    """Save a completed pickup to history and update user totals."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for item, price in items:
        c.execute(
            "INSERT INTO history (username, item_type, price, address, phone, pickup_date, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, item, price, address, phone, str(pickup_date), timestamp)
        )
    
    c.execute("SELECT total_earned, total_items, env_score FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    new_earned = user[0] + total
    new_items = user[1] + len(items)
    new_score = 100 + (new_earned * 10)
    
    c.execute(
        "UPDATE users SET total_earned = ?, total_items = ?, env_score = ? WHERE username = ?",
        (new_earned, new_items, new_score, username)
    )
    
    conn.commit()
    conn.close()
    return new_earned, new_items, new_score


def get_history(username):
    """Get all pickups for a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT item_type, price, address, pickup_date, timestamp FROM history WHERE username = ? ORDER BY id DESC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_leaderboard():
    """Get top 10 recyclers."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT username, env_score, total_items, total_earned FROM users ORDER BY env_score DESC LIMIT 10"
    )
    rows = c.fetchall()
    conn.close()
    return rows