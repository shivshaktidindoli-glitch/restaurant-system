import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Table, Order, OrderItem, MenuItem
from datetime import datetime, timedelta

def run_tests():
    with app.app_context():
        print("Running tests for Phase 22A...")
        
        # 1. Update/Add Table with Section
        t1 = Table.query.filter_by(name='T-1').first()
        if not t1:
            print("No T-1 found.")
            return
            
        t1.section = 'Ground Floor'
        t1.status = 'occupied'
        t1.session_start_time = datetime.utcnow() - timedelta(minutes=15)
        
        t2 = Table.query.filter_by(name='T-2').first()
        if t2:
            t2.section = 'Party Hall'
        
        db.session.commit()
        
        # 2. Add multiple orders to T-1
        o1 = Order(branch_id=1, table_id=t1.id, type='dine-in', status='served')
        db.session.add(o1)
        db.session.commit()
        
        o2 = Order(branch_id=1, table_id=t1.id, type='dine-in', status='new')
        db.session.add(o2)
        db.session.commit()
        
        # 3. Add items to these orders
        m = MenuItem.query.first()
        if m:
            oi1 = OrderItem(order_id=o1.id, menu_item_id=m.id, quantity=2, price_at_order=100.0)
            oi2 = OrderItem(order_id=o2.id, menu_item_id=m.id, quantity=1, price_at_order=150.0)
            db.session.add_all([oi1, oi2])
            db.session.commit()
        
        print("Data setup complete. Testing live amount calculation...")
        
        # Now replicate live_tables logic
        t1_fresh = Table.query.get(t1.id)
        active_orders = Order.query.filter(Order.table_id == t1_fresh.id, Order.status.notin_(['completed', 'cancelled'])).all()
        
        active_total = 0
        for o in active_orders:
            for item in o.items:
                active_total += item.price_at_order * item.quantity
                
        print(f"Table {t1_fresh.name} in {t1_fresh.section}: Active Total = {active_total} (Expected: 350.0)")
        
        if active_total == 350.0:
            print("✅ TEST PASSED: Multiple orders summed correctly.")
        else:
            print("❌ TEST FAILED.")
            
if __name__ == '__main__':
    run_tests()
