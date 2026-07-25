import os
from app import app, db
from models import Order, Table

def test():
    app.config['LOGIN_DISABLED'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Create a vacant table
        t = Table.query.filter_by(status='vacant').first()
        t.status = 'occupied'
        db.session.commit()
        
        # Create a phantom order
        new_order = Order(
            branch_id=1,
            table_id=t.id,
            type='dine-in',
            status='new',
            covers=1
        )
        db.session.add(new_order)
        db.session.commit()
        
        print(f"Created phantom order {new_order.id} for table {t.id} ({t.name}), status={t.status}")
        
        # Run cleanup logic
        orders = Order.query.all()
        empty_orders = [o for o in orders if len(o.items) == 0]
        
        count = 0
        freed_tables = 0
        freed_table_ids = []
        for o in empty_orders:
            table_id = o.table_id
            db.session.delete(o)
            count += 1
            
            if table_id:
                other_active = Order.query.filter_by(table_id=table_id).filter(Order.status.in_(['new', 'preparing', 'served'])).filter(Order.id != o.id).first()
                if not other_active:
                    table = Table.query.get(table_id)
                    if table and table.status != 'vacant':
                        table.status = 'vacant'
                        table.session_start_time = None
                        freed_tables += 1
                        freed_table_ids.append(table.name)
                        
        db.session.commit()
        print(f"Cleanup complete! Deleted {count} empty phantom orders.")
        print(f"Freed up {freed_tables} tables: {freed_table_ids}")

if __name__ == '__main__':
    test()
