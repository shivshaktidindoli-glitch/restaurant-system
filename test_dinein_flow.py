import os
from app import app, db
from models import Table, Order

def test_dinein_flow():
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
                    
            print("\n--- Test 1: Empty Order Simulation ---")
            table = Table.query.filter_by(status='vacant').first()
            if not table:
                print("No vacant tables found. Aborting test.")
                return
                
            table_name = table.name
            table_id = table.id
            
            # Simulate navigating to /admin/new_dinein/
            resp = client.get(f'/admin/new_dinein/{table_id}')
            print(f"GET /admin/new_dinein/{table_id} status code: {resp.status_code}")
            
            # Since we cancel, we do not hit /api/place_order
            # Check table status in DB
            t = Table.query.get(table_id)
            print(f"Table status after just viewing screen: {t.status}")
            if t.status != 'vacant':
                print("FAIL: Table became occupied just by viewing screen.")
                
            print("\n--- Test 2: Actual Order Placement ---")
            resp = client.post('/api/place_order', json={
                'order_type': 'dine-in',
                'table_name': table_name,
                'covers': 2,
                'items': [{'id': 1, 'quantity': 1, 'price': 100}]
            })
            
            data = resp.get_json()
            print(f"POST /api/place_order response: {data}")
            
            t = Table.query.get(table_id)
            print(f"Table status after placing order: {t.status}")
            
            if t.status == 'occupied':
                print("PASS: Table is correctly occupied.")
                active_order = Order.query.filter_by(table_id=table_id, status='new').first()
                if active_order and len(active_order.items) > 0:
                    print(f"PASS: Order created successfully. Items: {len(active_order.items)}")
                else:
                    print("FAIL: Order not found or empty.")
            else:
                print("FAIL: Table status did not change to occupied.")
                
            # Clean up the test order
            if 'active_order' in locals() and active_order:
                db.session.delete(active_order)
                t.status = 'vacant'
                db.session.commit()

if __name__ == '__main__':
    test_dinein_flow()
