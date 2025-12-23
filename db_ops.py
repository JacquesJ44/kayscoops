import sqlite3
from db import get_db_path

class DBOps:
    def __init__(self):
        self.db_path = None

    def _ensure_db_path(self):
        if self.db_path is None:
            self.db_path = get_db_path()

    def get_connection(self):
        self._ensure_db_path()
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    

    # ---------- Client Functions ----------
    def add_client(self, name, contact, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clients (name, contact_info, email) VALUES (?, ?, ?)",
                (name, contact, email),
            )
            conn.commit()

    def update_client(self,client_id, name, contact, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clients SET name=?, contact_info=?, email=? WHERE id=?",
                (name, contact, email, client_id),
            )
            conn.commit()

    def delete_client(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
            conn.commit()

    def fetch_clients(self, search_term=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if search_term:
                query = """
                    SELECT id, name, contact_info, email, total_spent
                    FROM clients
                    WHERE name LIKE ? OR contact_info LIKE ? OR email LIKE ?
                """
                like_term = f"%{search_term}%"
                cursor.execute(query, (like_term, like_term, like_term))
            else:
                cursor.execute("SELECT id, name, contact_info, email, total_spent FROM clients")
            rows = cursor.fetchall()
            return rows

    def email_exists(self, email):
        if not email:
            return False  # empty email is allowed, or you could make it mandatory
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients WHERE email = ?", (email,))
            count = cursor.fetchone()[0]
            return count > 0
        

    # ---------- Item Functions ----------
    def add_item(self, name, quantity, cost_price, selling_price):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO items (name, quantity, cost_price, selling_price) VALUES (?, ?, ?, ?)",
                (name, quantity, cost_price, selling_price)
            )
            conn.commit()

    def update_item(self, item_id, name, quantity, cost_price, selling_price):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE items SET name=?, quantity=?, cost_price=?, selling_price=? WHERE id=?",
                (name, quantity, cost_price, selling_price, item_id)
            )
            conn.commit()

    def delete_item(self, item_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
            conn.commit()

    def fetch_items(self, search_term=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if search_term:
                cursor.execute(
                    "SELECT id, name, quantity, cost_price, selling_price FROM items WHERE name LIKE ?",
                    (f"%{search_term}%",)
                )
            else:
                cursor.execute("SELECT id, name, quantity, cost_price, selling_price FROM items")
            
            rows = cursor.fetchall()
            return rows

    # ---------- Scoop Functions ----------     
    def save_scoop(self, client_id, scoop_price, items, video_url=None):
        from datetime import datetime, timedelta

        # UTC now
        utc_now = datetime.utcnow()
        # Johannesburg offset is +2 hours
        local_dt = utc_now + timedelta(hours=2)
        # Format as string
        local_dt_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Insert scoop
            cursor.execute(
                "INSERT INTO scoops (client_id, date, total_price, video_url) VALUES (?, ?, ?, ?)",
                (client_id, local_dt_str, scoop_price, video_url)
            )
            scoop_id = cursor.lastrowid

            # Insert scoop items and deduct stock
            for i in items:
                cursor.execute(
                    "INSERT INTO scoop_items (scoop_id, item_id, quantity) VALUES (?, ?, ?)",
                    (scoop_id, i["item_id"], i["quantity"])
                )
                cursor.execute("UPDATE items SET quantity = quantity - ? WHERE id = ?", (i["quantity"], i["item_id"]))

            # Update total_spent for client
            cursor.execute(
                "UPDATE clients SET total_spent = total_spent + ? WHERE id = ?",
                (scoop_price, client_id)
            )

            conn.commit()

    # ---------- Fetch Orders ----------
    def fetch_orders(self, search_term=""):
        with self.get_connection() as conn: 
            cursor = conn.cursor()
            if search_term:
                query = """
                    SELECT s.id, c.name, s.date, s.total_price
                    FROM scoops s
                    JOIN clients c ON s.client_id = c.id
                    WHERE LOWER(c.name) LIKE ?
                    ORDER BY s.date DESC
                """
                cursor.execute(query, (f"%{search_term.lower()}%",))
            else:
                query = """
                    SELECT s.id, c.name, s.date, s.total_price
                    FROM scoops s
                    JOIN clients c ON s.client_id = c.id
                    ORDER BY s.date DESC
                """
                cursor.execute(query)

        return cursor.fetchall()
