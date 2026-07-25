import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Table

def seed_sections():
    with app.app_context():
        tables = Table.query.order_by(Table.name).all()
        for t in tables:
            try:
                # Assuming table names are like 'T-1', 'T-2', etc.
                num_part = t.name.replace('T-', '').strip()
                if num_part.isdigit():
                    num = int(num_part)
                    if num <= 8:
                        t.section = 'Ground Floor'
                    else:
                        t.section = 'Basement'
                else:
                    t.section = 'Ground Floor' # fallback
            except Exception as e:
                t.section = 'Main'
                
        db.session.commit()
        print("Updated existing tables with new sections.")

if __name__ == '__main__':
    seed_sections()
