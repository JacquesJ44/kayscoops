import sqlite3
import os
from kivy.utils import platform

DB_PATH = None

# -----------------------------
# Determine database path
# -----------------------------
def get_db_path():
    if platform == "android":
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "kayscoops.db")

    return os.path.join(os.getcwd(), "kayscoops.db")


def init_db():
    global DB_PATH
    DB_PATH = get_db_path()

    # Very important for Android (ensures DB opens cleanly)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Clients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        contact_info TEXT,
        email TEXT,
        total_spent REAL DEFAULT 0
    )
    """)

    # Items table (real rewards)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        cost_price REAL,
        selling_price REAL
    )
    """)

    # Scoops table (customer purchases)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scoops (
        id INTEGER PRIMARY KEY,
        client_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        total_price REAL,
        video_url TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    """)

    # ScoopItems table (items assigned per scoop)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scoop_items (
        id INTEGER PRIMARY KEY,
        scoop_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(scoop_id) REFERENCES scoops(id),
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

if __name__ == "__main__":
    print("DB Path:", DB_PATH)
    init_db()
