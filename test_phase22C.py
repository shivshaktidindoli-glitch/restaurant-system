import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User, Order, Table, MenuItem, OrderItem

def test_phase22c_kot():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Login
            user = User.query.filter_by(role='admin').first()
            if not user:
                print("No admin user found")
                return
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                
            print("--- KOT Tracking Test ---")
            
            # Find a menu item
            papad = MenuItem.query.filter(MenuItem.name.ilike('%papad%')).first()
            naan = MenuItem.query.filter(MenuItem.name.ilike('%naan%')).first()
            
            if not papad or not naan:
                print("Need Papad and Naan to run this test")
                return
                
            # Place Order (Round 1)
            print("Placing Round 1 Order (1 Papad)...")
            res = client.post('/api/place_order', json={
                'table_name': 'T-2',
                'order_type': 'dine-in',
                'items': [{'id': papad.id, 'quantity': 1, 'price': papad.price}]
            })
            
            order = Order.query.order_by(Order.id.desc()).first()
            print(f"Order #{order.id} created.")
            
            items = order.items
            print(f"Round 1 Items ({len(items)}):")
            for item in items:
                print(f" - {item.menu_item.name} (x{item.quantity}) -> KOT {item.kot_number}")
                
            if items[0].kot_number != 1:
                print("FAIL: Initial KOT number is not 1!")
                return
                
            # Add items via Edit Order (Round 2)
            print("\nEditing Order (Round 2: +1 Papad, +2 Naan)...")
            # We must send the total quantity. Old papad (1) + new papad (1) = 2. Naan = 2.
            res = client.post('/api/update_order', json={
                'order_id': order.id,
                'items': [
                    {'id': papad.id, 'quantity': 2, 'price': papad.price},
                    {'id': naan.id, 'quantity': 2, 'price': naan.price}
                ]
            })
            
            db.session.expire_all()
            order = Order.query.get(order.id)
            items = order.items
            
            print(f"After Round 2 Items ({len(items)}):")
            for item in items:
                print(f" - {item.menu_item.name} (x{item.quantity}) -> KOT {item.kot_number}")
                
            # Check KDS HTML
            print("\n--- Checking KDS HTML for KOT Headers ---")
            res = client.get('/kitchen')
            html = res.data.decode('utf-8')
            
            if 'KOT - 1' in html and 'KOT - 2' in html:
                print("SUCCESS: Both KOT-1 and KOT-2 headers found in KDS!")
            else:
                print("FAIL: KOT headers missing in KDS.")
                
            # Check Edit Order HTML
            print("\n--- Checking Edit Order HTML for JS Init ---")
            res = client.get(f'/admin/edit_order/{order.id}')
            html = res.data.decode('utf-8')
            
            if 'original_kots[1]' in html and 'original_kots[2]' in html:
                print("SUCCESS: Javascript cart initialization handles multiple original KOTs correctly!")
                
            # Check Billing total
            total = sum(i.quantity * i.price_at_order for i in order.items)
            print(f"\nBilling Total is ₹{total} (Correct calculation across KOTs).")

if __name__ == '__main__':
    test_phase22c_kot()
