import os
from app import app, db
from models import Order, CustomerProfile

def test_qr_order_crm_creation():
    print("Testing QR Order Edit CRM Integration...")
    
    app.config['LOGIN_DISABLED'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            from models import User
            from flask_login import login_user
            admin = User.query.filter_by(role='admin').first()
            if admin:
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(admin.id)
                    sess['_fresh'] = True
            
            # 1. Create a dummy QR order (no mobile)
            order = Order(branch_id=1, type='dine-in', status='pending')
            db.session.add(order)
            db.session.commit()
            
            order_id = order.id
            print(f"Created QR Order without mobile: #{order_id}")
            
            # Ensure mobile does not exist in CRM
            test_mobile = "8888888888"
            existing = CustomerProfile.query.get(test_mobile)
            if existing:
                db.session.delete(existing)
                db.session.commit()
                
            # 2. Staff edits order to add mobile via API
            resp = client.post('/api/update_order', json={
                'order_id': order_id,
                'items': [{'id': 1, 'quantity': 1, 'price': 100}],
                'customer_mobile': test_mobile,
                'customer_name': 'QR Walk-in Customer'
            })
            print(f"Update Order Response: {resp.status_code}, {resp.get_json()}")
            
            # 3. Verify CustomerProfile was created
            profile = CustomerProfile.query.get(test_mobile)
            if profile:
                print(f"SUCCESS: CustomerProfile created for {test_mobile} with name '{profile.name}'.")
            else:
                print(f"FAIL: CustomerProfile was NOT created for {test_mobile}.")
            
if __name__ == '__main__':
    test_qr_order_crm_creation()
