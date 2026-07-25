import sqlite3
import os
import json
import requests
import time
from app import app, db, auto_migrate
from models import Order, OrderItem, MenuItem, Table, Invoice

def run_tests():
    auto_migrate()
    with app.app_context():
        # Setup
        app.config['WTF_CSRF_ENABLED'] = False
        item1 = MenuItem.query.filter_by(name="Test Item 1").first()
        if not item1:
            item1 = MenuItem(name="Test Item 1", price=100.0, category_id=1)
            db.session.add(item1)
            
        item2 = MenuItem.query.filter_by(name="Test Item 2").first()
        if not item2:
            item2 = MenuItem(name="Test Item 2", price=200.0, category_id=1)
            db.session.add(item2)
            
        try:
            db.session.commit()
        except:
            db.session.rollback()
            
        item1_id = item1.id
        item2_id = item2.id
        
        print("\n=== Phase 22D Tests (Advanced Billing & Split Bill) ===")
        
        # Test 1: Settle Math (Exact)
        o1 = Order(branch_id=1, type='dine-in', status='served')
        db.session.add(o1)
        db.session.flush()
        oi1 = OrderItem(order_id=o1.id, menu_item_id=item1_id, quantity=2, price_at_order=100.0)
        db.session.add(oi1)
        db.session.commit()
        o1_id = o1.id
        
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
        
        # Test 1 Settle Math
        resp = client.post('/api/settle_bill', json={
            'order_ids': [o1_id],
            'payment_method': 'cash',
            'customer_paid': 250.0, # Total is 210, customer gave 250
            'change_returned': 40.0,
            'tip_amount': 0.0
        })
        print(f"Test 1 (Settle Bill Excess Pay) Data: {resp.data}")
        
        with app.app_context():
            inv1 = Invoice.query.filter_by(order_id=o1_id).first()
            if inv1:
                print(f" -> Invoice Total: {inv1.total}")
                print(f" -> Customer Paid: {inv1.customer_paid}, Change Returned: {inv1.change_returned}")

        # Test 2: Item-wise Split
        with app.app_context():
            o2 = Order(branch_id=1, type='dine-in', status='served')
            db.session.add(o2)
            db.session.flush()
            oi2 = OrderItem(order_id=o2.id, menu_item_id=item1_id, quantity=1, price_at_order=100.0)
            oi3 = OrderItem(order_id=o2.id, menu_item_id=item2_id, quantity=1, price_at_order=200.0)
            db.session.add(oi2)
            db.session.add(oi3)
            db.session.commit()
            
            o2_id = o2.id
            o2_total_expected = (100.0 + 200.0) * 1.05 # 315.0
            
        # Call split API
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
            
        resp2 = client.post('/api/split_bill', json={
            'order_id': o2_id,
            'split_type': 'item',
            'item_parts': [
                {'part': 1, 'items': [{'menu_item_id': item1_id, 'price': 100.0}]},
                {'part': 2, 'items': [{'menu_item_id': item2_id, 'price': 200.0}]}
            ]
        })
        print(f"\nTest 2 (Item-wise Split) Data: {resp2.data}")
        
        with app.app_context():
            invs = Invoice.query.filter_by(order_id=o2_id).all()
            print(f" -> Original Order Expected Total: {o2_total_expected}")
            print(f" -> Invoices created: {len(invs)}")
            split_sum = 0
            for inv in invs:
                split_sum += inv.total
                meta = json.loads(inv.split_metadata)
                print(f" -> Inv {inv.invoice_number}: Subtotal={inv.subtotal}, Total={inv.total}, Part={meta['part']}, Items={len(meta['items'])}")
            print(f" -> Sum of Split Invoices: {split_sum} (Matches Expected: {split_sum == o2_total_expected})")

        # Test 3: Settle Math (Less Amount)
        with app.app_context():
            o3 = Order(branch_id=1, type='dine-in', status='served')
            db.session.add(o3)
            db.session.flush()
            oi4 = OrderItem(order_id=o3.id, menu_item_id=item1_id, quantity=2, price_at_order=100.0)
            db.session.add(oi4)
            db.session.commit()
            o3_id = o3.id

        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
            
        resp3 = client.post('/api/settle_bill', json={
            'order_ids': [o3_id],
            'payment_method': 'cash',
            'customer_paid': 150.0, # Total is 210, customer gave 150 (less amount)
            'change_returned': 0.0, # JS sends 0 if customerPaid < total
            'tip_amount': 0.0
        })
        print(f"\nTest 3 (Settle Bill Less Pay) Data: {resp3.data}")
        
        with app.app_context():
            inv3 = Invoice.query.filter_by(order_id=o3_id).first()
            if inv3:
                print(f" -> Invoice Total: {inv3.total}")
                print(f" -> Customer Paid: {inv3.customer_paid}, Change Returned: {inv3.change_returned}")

if __name__ == '__main__':
    run_tests()
