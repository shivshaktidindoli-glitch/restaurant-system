import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'restaurant.db')

def patch_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("kot_number", "INTEGER DEFAULT 1"),
        ("added_at", "DATETIME")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE order_items ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to order_items")
            
            if col_name == 'added_at':
                # Populate existing rows with current time so they aren't completely null
                now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(f"UPDATE order_items SET added_at = '{now_str}' WHERE added_at IS NULL")
                
            if col_name == 'kot_number':
                cursor.execute(f"UPDATE order_items SET kot_number = 1 WHERE kot_number IS NULL")
                
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Database patched successfully for Phase 22C.")

if __name__ == '__main__':
    patch_db()
