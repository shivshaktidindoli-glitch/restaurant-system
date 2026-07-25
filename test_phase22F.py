import os
from datetime import datetime, timedelta
from app import app, db
from models import Order, OrderItem, MenuItem, Table, Branch, User, Invoice, DayEndRecord

def test_reports():
    print("Testing Phase 22F: Reports & Day-End Close...")
    
    app.config['LOGIN_DISABLED'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Setup users
            admin = User.query.filter_by(mobile='9999999999').first()
            if not admin:
                admin = User(name='Admin', mobile='9999999999', role='admin')
                admin.set_password('1234')
                db.session.add(admin)
                
            waiter = User.query.filter_by(mobile='8888888888').first()
            if not waiter:
                waiter = User(name='Test Waiter', mobile='8888888888', role='waiter', pin='1234')
                waiter.set_password('1234')
                db.session.add(waiter)
                
            db.session.commit()
            
            # Delete old records today for clean test
            today = datetime.utcnow().date()
            DayEndRecord.query.filter_by(date=today).delete()
            db.session.commit()
            
            # Setup dummy order 1 (by admin)
            order1 = Order(branch_id=1, type='dine-in', status='completed', created_by=admin.id, covers=4, customer_name='Alice')
            db.session.add(order1)
            db.session.commit()
            
            oi1 = OrderItem(order_id=order1.id, menu_item_id=1, quantity=2, price_at_order=100.0)
            db.session.add(oi1)
            
            inv1 = Invoice(order_id=order1.id, invoice_number=f"INV-TEST-1-{order1.id}", subtotal=200, total=210, payment_method='cash', customer_paid=210, tip_amount=50.0)
            db.session.add(inv1)
            
            # Setup dummy order 2 (by waiter)
            order2 = Order(branch_id=1, type='parcel', status='completed', created_by=waiter.id, covers=1, customer_name='Bob')
            db.session.add(order2)
            db.session.commit()
            
            inv2 = Invoice(order_id=order2.id, invoice_number=f"INV-TEST-2-{order2.id}", subtotal=300, total=315, payment_method='upi', tip_amount=0)
            db.session.add(inv2)
            
            # Setup dummy QR order (no created_by)
            order3 = Order(branch_id=1, type='dine-in', status='completed', covers=1, customer_name='Charlie') # covers default 1
            db.session.add(order3)
            db.session.commit()
            
            inv3 = Invoice(order_id=order3.id, invoice_number=f"INV-TEST-3-{order3.id}", subtotal=100, total=105, payment_method='cash', customer_paid=105, tip_amount=10)
            db.session.add(inv3)
            db.session.commit()
            
        print("\n--- Testing API Reports ---")
        
        # Test Employee Sales
        resp = client.get('/api/report_data?type=employee_sales')
        print("\nEmployee Sales Report:")
        print(resp.get_json())
        
        # Test Covers
        resp = client.get('/api/report_data?type=covers')
        print("\nCovers Report:")
        print(resp.get_json())
        
        # Test Tips
        resp = client.get('/api/report_data?type=tips')
        print("\nTips Report:")
        print(resp.get_json())
        
        print("\n--- Testing Day End API ---")
        
        with app.app_context():
            admin = User.query.filter_by(mobile='9999999999').first()
            admin_id = admin.id

        # Login admin for day end API
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_id)
            
        resp = client.post('/api/day_end_close')
        print(f"Day End Close Status: {resp.status_code}")
        print(f"Day End Close Response: {resp.get_json()}")
        
        with app.app_context():
            der = DayEndRecord.query.order_by(DayEndRecord.id.desc()).first()
            if der:
                print("\nCreated DayEndRecord:")
                print(f"Sales: {der.total_sales}, Orders: {der.total_orders}, Expected Cash: {der.expected_cash}, Total Tips: {der.total_tips}")
            
if __name__ == '__main__':
    test_reports()
