import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table with session_token column
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    session_token TEXT
)
""")

# Create subscriptions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    amount REAL,
    billing_date TEXT,
    recurring TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database initialized successfully.")
