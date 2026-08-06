import unittest
import json
import warnings
from app import app, db, limiter
from models import User, Order, Branch, Table, MenuItem, OrderItem

class SecurityTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['RATELIMIT_ENABLED'] = True
        limiter.enabled = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF by default for tests that don't need it
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            
            # Create a test branch
            branch = Branch.query.first()
            if not branch:
                branch = Branch(name="Test Branch")
                db.session.add(branch)
                db.session.commit()
                
            # Ensure the test admin exists with correct password
            admin = User.query.filter_by(mobile='7999620244').first()
            if not admin:
                admin = User(name='Admin', mobile='7999620244', role='admin', branch_id=branch.id)
                db.session.add(admin)
            admin.set_password('shivshakti@2000')
            
            # Ensure menu items exist for order tests
            if MenuItem.query.count() < 2:
                from models import Category
                cat = Category.query.first()
                if not cat:
                    cat = Category(name="General")
                    db.session.add(cat)
                    db.session.commit()
                item1 = MenuItem(name="Test Item 1", price=100.0, category_id=cat.id)
                item2 = MenuItem(name="Test Item 2", price=200.0, category_id=cat.id)
                db.session.add_all([item1, item2])
            db.session.commit()

    def test_1_rate_limiting_login(self):
        limiter.enabled = True
        app.config['RATELIMIT_ENABLED'] = True
        # We test that hitting /admin/login 7 times triggers a 429
        responses = []
        for _ in range(7):
            res = self.client.post('/admin/login', data={'mobile': '7999620244', 'password': 'wrong'}, environ_base={'REMOTE_ADDR': '127.0.0.99'})
            responses.append(res.status_code)
            
        self.assertIn(429, responses, "Rate limit (429) was not triggered after 5 attempts.")

    def test_2_static_folder_isolation(self):
        # By default, Flask only serves static files from /static/
        # Root files like .env or database/restaurant.db should return 404.
        res_env = self.client.get('/.env')
        res_db = self.client.get('/database/restaurant.db')
        
        self.assertEqual(res_env.status_code, 404, ".env should not be accessible")
        self.assertEqual(res_db.status_code, 404, "Database file should not be accessible")

    def test_3_security_headers(self):
        res = self.client.get('/admin/login')
        headers = res.headers
        self.assertIn('X-Content-Type-Options', headers)
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn('X-Frame-Options', headers)
        self.assertEqual(headers['X-Frame-Options'], 'DENY')

    def test_4_live_orders_state_persistence(self):
        with app.app_context():
            # 1. Place a test order with at least 1 item
            branch = Branch.query.first()
            menu_item = MenuItem.query.first()
            order = Order(branch_id=branch.id, type='parcel', status='new', customer_name='TestPersistence')
            db.session.add(order)
            db.session.flush()
            oi = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=1, price_at_order=menu_item.price)
            db.session.add(oi)
            db.session.commit()
            order_id = order.id
            
        # 2. Login to simulate real flow (using different IP to avoid rate limit from Test 1)
        login_res = self.client.post('/admin/login', data={
            'mobile': '7999620244',
            'password': 'shivshakti@2000'
        }, follow_redirects=True, environ_base={'REMOTE_ADDR': '127.0.0.4'})
        self.assertEqual(login_res.status_code, 200)
        
        # 3. Fetch Live Orders page
        live_res = self.client.get('/admin/live_orders', environ_base={'REMOTE_ADDR': '127.0.0.4'})
        self.assertEqual(live_res.status_code, 200)
        
        # 4. Check if the newly placed order is rendered in the HTML
        html_content = live_res.data.decode('utf-8')
        self.assertIn('TestPersistence', html_content, "Pre-existing order did not render on page load!")
        self.assertIn(f"#{order_id}", html_content, "Order ID did not render on page load!")
        
        # Cleanup
        with app.app_context():
            OrderItem.query.filter_by(order_id=order_id).delete()
            Order.query.filter_by(id=order_id).delete()
            db.session.commit()

    def test_5_billing_settle_csrf(self):
        # 1. Enable CSRF explicitly for this test
        app.config['WTF_CSRF_ENABLED'] = True
        
        with app.app_context():
            # Setup a test order that is completed
            branch = Branch.query.first()
            order = Order(branch_id=branch.id, type='dine-in', status='completed', customer_name='SettleTest')
            db.session.add(order)
            db.session.commit()
            order_id = order.id
            
        # 2. Login to get session and CSRF token
        login_page = self.client.get('/admin/login', environ_base={'REMOTE_ADDR': '127.0.0.5'}).data.decode('utf-8')
        import re
        match = re.search(r'<input type="hidden" name="csrf_token" value="([^"]+)"/>', login_page)
        if not match:
            match = re.search(r'<meta name="csrf-token" content="([^"]+)">', login_page)
        login_csrf = match.group(1) if match else ''

        login_res = self.client.post('/admin/login', data={
            'mobile': '7999620244',
            'password': 'shivshakti@2000',
            'csrf_token': login_csrf
        }, follow_redirects=True, environ_base={'REMOTE_ADDR': '127.0.0.5'})
        self.assertEqual(login_res.status_code, 200)
        
        # 3. Extract CSRF token from the admin page
        admin_page = self.client.get('/admin/billing', environ_base={'REMOTE_ADDR': '127.0.0.5'}).data.decode('utf-8')
        import re
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', admin_page)
        self.assertIsNotNone(match, "CSRF token meta tag missing in billing page")
        csrf_token = match.group(1)
        
        # 4. Settle the bill via the API
        settle_res = self.client.post('/api/settle_bill', json={
            'order_ids': [order_id],
            'discount': 0,
            'payment_method': 'Cash'
        }, headers={'X-CSRFToken': csrf_token}, environ_base={'REMOTE_ADDR': '127.0.0.5'})
        
        self.assertEqual(settle_res.status_code, 200)
        data = settle_res.get_json()
        self.assertTrue(data.get('success'))
        
        # 5. Verify the invoice was created in DB
        with app.app_context():
            from models import Invoice
            invoice = Invoice.query.filter_by(order_id=order_id).first()
            self.assertIsNotNone(invoice, "Invoice was not created in the database")
            
            # Cleanup
            Invoice.query.filter_by(id=invoice.id).delete()
            Order.query.filter_by(id=order_id).delete()
            db.session.commit()
            
        app.config['WTF_CSRF_ENABLED'] = False # Re-disable for any subsequent tests if needed

    def test_6_order_editing(self):
        # 1. Enable CSRF explicitly for this test
        app.config['WTF_CSRF_ENABLED'] = True
        
        with app.app_context():
            # Setup a test order that is 'preparing'
            branch = Branch.query.first()
            menu_item_1 = MenuItem.query.first()
            order = Order(branch_id=branch.id, type='dine-in', status='preparing', customer_name='EditTest')
            db.session.add(order)
            db.session.flush()
            
            oi = OrderItem(order_id=order.id, menu_item_id=menu_item_1.id, quantity=1, price_at_order=100)
            db.session.add(oi)
            db.session.commit()
            
            order_id = order.id
            item_1_id = menu_item_1.id
            
        # 2. Login to get session and CSRF token
        login_page = self.client.get('/admin/login', environ_base={'REMOTE_ADDR': '127.0.0.6'}).data.decode('utf-8')
        import re
        match = re.search(r'<input type="hidden" name="csrf_token" value="([^"]+)"/>', login_page)
        if not match:
            match = re.search(r'<meta name="csrf-token" content="([^"]+)">', login_page)
        login_csrf = match.group(1) if match else ''

        login_res = self.client.post('/admin/login', data={
            'mobile': '7999620244',
            'password': 'shivshakti@2000',
            'csrf_token': login_csrf
        }, follow_redirects=True, environ_base={'REMOTE_ADDR': '127.0.0.6'})
        self.assertEqual(login_res.status_code, 200)
        
        # 3. Extract CSRF token from the admin page
        admin_page = self.client.get('/admin/live_orders', environ_base={'REMOTE_ADDR': '127.0.0.6'}).data.decode('utf-8')
        match = re.search(r'<meta name="csrf-token" content="([^"]+)">', admin_page)
        csrf_token = match.group(1)
        
        # 4. Edit the order (change qty, add new item)
        with app.app_context():
            menu_item_2 = MenuItem.query.filter(MenuItem.id != item_1_id).first()
            item_2_id = menu_item_2.id
            
        edit_res = self.client.post('/api/update_order', json={
            'order_id': order_id,
            'items': [
                {'id': item_1_id, 'quantity': 2, 'price': 100}, # Modified qty
                {'id': item_2_id, 'quantity': 1, 'price': 200}  # New item
            ]
        }, headers={'X-CSRFToken': csrf_token})
        
        self.assertEqual(edit_res.status_code, 200)
        
        # 5. Verify the order changes in DB
        with app.app_context():
            order = Order.query.get(order_id)
            self.assertTrue(order.has_new_items, "has_new_items flag was not set")
            self.assertEqual(sum(i.quantity for i in order.items), 3, "Total item quantity should be 3")
            
            # Check ActivityLog
            from models import ActivityLog
            log = ActivityLog.query.order_by(ActivityLog.created_at.desc()).first()
            self.assertIn('Added', log.details)
            
            # Cleanup
            OrderItem.query.filter_by(order_id=order_id).delete()
            Order.query.filter_by(id=order_id).delete()
            db.session.commit()
            
        app.config['WTF_CSRF_ENABLED'] = False

if __name__ == '__main__':
    unittest.main(verbosity=2)
