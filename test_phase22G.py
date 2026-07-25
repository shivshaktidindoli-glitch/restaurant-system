import os
from datetime import datetime, timedelta
from app import app, db
from models import Order, OrderItem, MenuItem, CustomerProfile, Invoice

def test_customer_features():
    print("Testing Phase 22G: Customer History & Autocomplete...")
    
    app.config['LOGIN_DISABLED'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Create a customer profile
            cust = CustomerProfile.query.get('9876543210')
            if not cust:
                cust = CustomerProfile(mobile='9876543210', name='Test Customer')
                db.session.add(cust)
                db.session.commit()
                
            # Create test orders for this customer
            order1 = Order(branch_id=1, type='dine-in', status='completed', customer_mobile='9876543210', customer_name='Test Customer', created_at=datetime.utcnow() - timedelta(days=10))
            db.session.add(order1)
            db.session.commit()
            
            oi1_1 = OrderItem(order_id=order1.id, menu_item_id=1, quantity=2, price_at_order=100.0) # 2x item 1 (Pizza)
            oi1_2 = OrderItem(order_id=order1.id, menu_item_id=2, quantity=1, price_at_order=50.0)  # 1x item 2 (Coke)
            db.session.add_all([oi1_1, oi1_2])
            db.session.commit()
            
            inv1 = Invoice(order_id=order1.id, invoice_number=f"INV-TEST-G1-{order1.id}", subtotal=250, total=262.5, payment_method='cash', created_at=order1.created_at)
            db.session.add(inv1)
            db.session.commit()
            
            order2 = Order(branch_id=1, type='parcel', status='completed', customer_mobile='9876543210', customer_name='Test Customer', created_at=datetime.utcnow() - timedelta(days=2))
            db.session.add(order2)
            db.session.commit()
            
            oi2_1 = OrderItem(order_id=order2.id, menu_item_id=1, quantity=3, price_at_order=100.0) # 3x item 1 (Pizza)
            db.session.add(oi2_1)
            db.session.commit()
            
            inv2 = Invoice(order_id=order2.id, invoice_number=f"INV-TEST-G2-{order2.id}", subtotal=300, total=315, payment_method='upi', created_at=order2.created_at)
            db.session.add(inv2)
            db.session.commit()
            
        print("\n--- Testing Autocomplete ---")
        resp = client.get('/api/customer/autocomplete?q=9876')
        print(f"Status: {resp.status_code}")
        print(f"Suggestions: {resp.get_json()}")
        
        print("\n--- Testing Customer History ---")
        resp = client.get('/api/customer/history?mobile=9876543210')
        print(f"Status: {resp.status_code}")
        data = resp.get_json()
        print(f"Name: {data.get('name')}")
        print(f"Mobile: {data.get('mobile')}")
        print(f"Max Ordered: {data.get('max_ordered')}")
        print(f"Avg Bill: {data.get('avg_bill')}")
        print(f"Coming Since: {data.get('coming_since')}")
        print(f"Visits: {data.get('visits')}")
        print(f"Recent Orders (count): {len(data.get('recent_orders', []))}")
        if data.get('recent_orders'):
            print(f"Last Order: {data['recent_orders'][0]}")

if __name__ == '__main__':
    test_customer_features()
