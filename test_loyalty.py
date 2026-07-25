import os
from app import app, db
from models import Order, OrderItem, CustomerProfile, Invoice
from datetime import datetime

def test_loyalty():
    print("Testing Loyalty Earn & Redeem Cycle...")
    
    app.config['LOGIN_DISABLED'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            from models import User
            admin = User.query.filter_by(role='admin').first()
            if admin:
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(admin.id)
                    sess['_fresh'] = True
                    
            test_mobile = "5555555555"
            
            # Reset customer
            existing = CustomerProfile.query.get(test_mobile)
            if existing:
                db.session.delete(existing)
                db.session.commit()
                
            customer = CustomerProfile(mobile=test_mobile, name="Loyalty Tester", loyalty_points=0)
            db.session.add(customer)
            db.session.commit()
            
            # ---- EARN CYCLE ----
            print("\n--- Phase 1: EARN ---")
            order1 = Order(branch_id=1, customer_mobile=test_mobile, type='takeaway', status='pending')
            db.session.add(order1)
            db.session.commit()
            
            # Add an item worth Rs. 500
            item1 = OrderItem(order_id=order1.id, menu_item_id=1, quantity=1, price_at_order=500.0)
            db.session.add(item1)
            db.session.commit()
            
            # Settle Order 1
            resp1 = client.post('/api/settle_bill', json={
                'order_ids': [order1.id],
                'payment_method': 'cash',
                'customer_paid': 525.0
            })
            
            data1 = resp1.get_json()
            print(f"Settle 1 Resp: {data1}")
            
            customer = CustomerProfile.query.get(test_mobile)
            print(f"Customer Points after Earn: {customer.loyalty_points}")
            if customer.loyalty_points != 5:  # 525 / 100 = 5 points
                print("FAIL: Earn calculation incorrect.")
                return
                
            # ---- REDEEM CYCLE ----
            print("\n--- Phase 2: REDEEM ---")
            order2 = Order(branch_id=1, customer_mobile=test_mobile, type='takeaway', status='pending')
            db.session.add(order2)
            db.session.commit()
            
            # Add an item worth Rs. 200
            item2 = OrderItem(order_id=order2.id, menu_item_id=1, quantity=1, price_at_order=200.0)
            db.session.add(item2)
            db.session.commit()
            
            # Settle Order 2 and redeem 3 points
            resp2 = client.post('/api/settle_bill', json={
                'order_ids': [order2.id],
                'payment_method': 'cash',
                'customer_paid': 200.0,
                'redeemed_points': 3
            })
            
            data2 = resp2.get_json()
            print(f"Settle 2 Resp: {data2}")
            
            customer = CustomerProfile.query.get(test_mobile)
            print(f"Customer Points after Redeem: {customer.loyalty_points}")
            if customer.loyalty_points != 3: # (5 - 3) = 2 points left + (200 - 3 discount) = 197 / 100 = 1 new point => 2 + 1 = 3 points total
                print(f"FAIL: Redeem calculation incorrect. Expected 3, got {customer.loyalty_points}")
                return
                
            invoice = Invoice.query.get(data2['invoice_id'])
            print(f"Invoice 2 Discount: {invoice.discount}")
            if invoice.discount != 3.0:
                print("FAIL: Invoice discount did not reflect redeemed points.")
                return
                
            print("\nTEST PASSED: Earn & Redeem cycle is perfect!")

if __name__ == '__main__':
    test_loyalty()
