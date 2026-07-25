import os
from app import app, db
from models import Order, Table

def clean_empty_orders():
    print("Starting cleanup of phantom empty orders...")
    
    with app.app_context():
        # Find all orders that have no items
        # We can fetch all orders and check len(o.items) or do a left outer join
        orders = Order.query.all()
        empty_orders = [o for o in orders if len(o.items) == 0]
        
        count = 0
        freed_tables = 0
        for o in empty_orders:
            table_id = o.table_id
            db.session.delete(o)
            count += 1
            
            # Check if this table has any OTHER active orders. If not, make it vacant
            if table_id:
                other_active = Order.query.filter_by(table_id=table_id).filter(Order.status.in_(['new', 'preparing', 'served'])).filter(Order.id != o.id).first()
                if not other_active:
                    table = Table.query.get(table_id)
                    if table and table.status != 'vacant':
                        table.status = 'vacant'
                        table.session_start_time = None
                        freed_tables += 1
                        
        db.session.commit()
        print(f"Cleanup complete! Deleted {count} empty phantom orders.")
        print(f"Freed up {freed_tables} tables that were incorrectly marked as occupied.")

if __name__ == '__main__':
    clean_empty_orders()
