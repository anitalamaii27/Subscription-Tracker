import sqlite3

# Connect to the existing database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Add session_token column if it doesn't exist
try:
    cursor.execute("""
    ALTER TABLE users ADD COLUMN session_token TEXT
    """)
    print("Added session_token column successfully.")
except sqlite3.OperationalError:
    print("Column already exists or error occurred.")

conn.commit()
conn.close()
