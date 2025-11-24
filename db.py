import sqlite3

# Database file
DB_FILE = "scoop_tracker.db"

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")  # enforce foreign keys
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
    create_tables()
