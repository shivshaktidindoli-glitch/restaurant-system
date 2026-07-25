import sqlite3
import os

db_path = 'database/restaurant.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns exist and add them
    try:
        cursor.execute("ALTER TABLE tables ADD COLUMN section VARCHAR(50) DEFAULT 'Main'")
        print("Added 'section' to tables.")
    except sqlite3.OperationalError as e:
        print("Column 'section' might already exist or another error:", e)

    try:
        cursor.execute("ALTER TABLE menu_items ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
        print("Added 'is_favorite' to menu_items.")
    except sqlite3.OperationalError as e:
        print("Column 'is_favorite' might already exist or another error:", e)

    try:
        cursor.execute("ALTER TABLE menu_items ADD COLUMN food_type VARCHAR(20) DEFAULT 'veg'")
        print("Added 'food_type' to menu_items.")
    except sqlite3.OperationalError as e:
        print("Column 'food_type' might already exist or another error:", e)
        
    try:
        cursor.execute("ALTER TABLE menu_items ADD COLUMN short_code VARCHAR(10)")
        print("Added 'short_code' to menu_items.")
    except sqlite3.OperationalError as e:
        print("Column 'short_code' might already exist or another error:", e)
        
    conn.commit()
    conn.close()
    print("Database patching complete.")
else:
    print("No database found to patch.")
