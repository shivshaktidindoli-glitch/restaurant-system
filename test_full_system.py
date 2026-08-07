import os
import sys
import unittest
import json

# Set test environment
os.environ['DATABASE_URL'] = 'sqlite:///test_full_system.db'

from app import app, db, User, Category, MenuItem, Table, Branch, RawMaterial, Order, OrderItem

class SystemIntegrationTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            
            # Setup admin user
            admin = User.query.filter_by(mobile='7999620244').first()
            if not admin:
                admin = User(name='Admin', mobile='7999620244', role='admin')
                admin.set_password('soulsip@2000')
                db.session.add(admin)
                db.session.commit()
                
            # Setup branch
            branch = Branch.query.first()
            if not branch:
                branch = Branch(name='Main Branch')
                db.session.add(branch)
                db.session.commit()
                
            # Setup category & item
            cat = Category.query.filter_by(name='Burgers').first()
            if not cat:
                cat = Category(name='Burgers', sort_order=1)
                db.session.add(cat)
                db.session.commit()
                
            item = MenuItem.query.filter_by(name='Veg Supreme Burger').first()
            if not item:
                item = MenuItem(name='Veg Supreme Burger', price=120.0, category_id=cat.id, is_available=True)
                db.session.add(item)
                db.session.commit()
                
            # Setup raw material
            mat = RawMaterial.query.filter_by(name='Veg Supreme Burger').first()
            if not mat:
                mat = RawMaterial(name='Veg Supreme Burger', unit='pcs', current_stock=20.0, low_stock_threshold=5.0)
                db.session.add(mat)
                db.session.commit()
                
            # Setup table
            tbl = Table.query.filter_by(name='T-1').first()
            if not tbl:
                tbl = Table(name='T-1', section='Ground Floor', seats=4, status='vacant', branch_id=branch.id)
                db.session.add(tbl)
                db.session.commit()

    def login_admin(self):
        return self.client.post('/admin/login', data={'mobile': '7999620244', 'password': 'soulsip@2000'}, follow_redirects=True)

    def test_1_qr_generation(self):
        with app.app_context():
            tbl = Table.query.first()
            table_id = tbl.id
            table_name = tbl.name

        resp = self.client.get(f'/table/qr/{table_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'image/png')
        self.assertTrue(len(resp.data) > 100)
        print("PASS: /table/qr/<id> generates valid PNG QR code")

        resp2 = self.client.get(f'/table/qr_by_name/{table_name}')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.mimetype, 'image/png')
        print("PASS: /table/qr_by_name/<name> generates valid PNG QR code")

    def test_2_item_edit(self):
        self.login_admin()
        with app.app_context():
            item = MenuItem.query.filter_by(name='Veg Supreme Burger').first()
            cat = Category.query.first()
            item_id = item.id
            cat_id = cat.id

        edit_data = {
            'name': 'Super Veg Supreme Burger',
            'name_hi': 'सुपर वेज बर्गर',
            'name_gu': 'સુપર વેજ બર્ગર',
            'category_id': cat_id,
            'price': 140.0,
            'description': 'Crispy patty with fresh lettuce and sauces',
            'food_type': 'veg',
            'short_code': 'B101'
        }
        resp = self.client.post(f'/admin/items/edit/{item_id}', data=edit_data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        with app.app_context():
            updated = MenuItem.query.get(item_id)
            self.assertEqual(updated.name, 'Super Veg Supreme Burger')
            self.assertEqual(updated.price, 140.0)
            self.assertEqual(updated.short_code, 'B101')
            # Check raw material name auto-updated
            mat = RawMaterial.query.filter_by(name='Super Veg Supreme Burger').first()
            self.assertIsNotNone(mat)
            print("PASS: Item edit and RawMaterial auto-sync verified!")

    def test_3_category_edit(self):
        self.login_admin()
        with app.app_context():
            cat = Category.query.filter_by(name='Burgers').first()
            cat_id = cat.id

        resp = self.client.post(f'/admin/categories/edit/{cat_id}', data={
            'name': 'Gourmet Burgers',
            'name_hi': 'स्वादिष्ट बर्गर',
            'name_gu': 'ગોર્મેટ બર્ગર'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        with app.app_context():
            updated_cat = Category.query.get(cat_id)
            self.assertEqual(updated_cat.name, 'Gourmet Burgers')
            print("PASS: Category edit verified!")

    def test_4_place_order_and_inventory(self):
        with app.app_context():
            item = MenuItem.query.first()
            tbl = Table.query.first()
            # Set initial stock to 6.0
            mat = RawMaterial.query.filter_by(name=item.name).first()
            if not mat:
                mat = RawMaterial(name=item.name, unit='pcs', current_stock=6.0, low_stock_threshold=5.0)
                db.session.add(mat)
                db.session.commit()
            else:
                mat.current_stock = 6.0
                db.session.commit()

            item_id = item.id
            item_name = item.name
            item_price = item.price
            table_name = tbl.name

        # Place order for 2 items -> stock should become 4.0 (<= threshold 5, triggers low stock)
        payload = {
            'table_name': table_name,
            'order_type': 'dine-in',
            'customer_name': 'Test Customer',
            'customer_mobile': '9876543210',
            'items': [
                {
                    'id': item_id,
                    'name': item_name,
                    'price': item_price,
                    'quantity': 2
                }
            ]
        }
        resp = self.client.post('/api/place_order', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        res_json = resp.get_json()
        self.assertTrue(res_json.get('success'))
        order_id = res_json.get('order_id')
        self.assertIsNotNone(order_id)

        with app.app_context():
            mat = RawMaterial.query.filter_by(name=item_name).first()
            self.assertEqual(mat.current_stock, 4.0)
            print(f"PASS: Order placed (ID: {order_id}) & inventory reduced correctly from 6.0 to 4.0 pcs (Low stock threshold: 5.0)!")

    def test_5_table_status_and_pos(self):
        self.login_admin()
        with app.app_context():
            # Create a fresh vacant table
            tbl2 = Table.query.filter_by(name='T-99').first()
            if not tbl2:
                branch = Branch.query.first()
                tbl2 = Table(name='T-99', section='First Floor', seats=2, status='vacant', branch_id=branch.id)
                db.session.add(tbl2)
                db.session.commit()
            tbl_id = tbl2.id

        # Update table status
        resp = self.client.post('/api/update_table_status', data=json.dumps({
            'table_id': tbl_id,
            'status': 'occupied'
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        with app.app_context():
            tbl = Table.query.get(tbl_id)
            self.assertEqual(tbl.status, 'occupied')
            print("PASS: Table status update verified (marked as occupied)!")

        # Access POS Dine-in page for table without active order
        pos_resp = self.client.get(f'/admin/new_dinein/{tbl_id}')
        self.assertEqual(pos_resp.status_code, 200)
        print("PASS: POS Dine-in screen loaded successfully!")

    def test_6_settle_bill(self):
        self.login_admin()
        with app.app_context():
            order = Order.query.filter_by(status='new').first()
            order_id = order.id

        # Settle bill
        settle_data = {
            'order_ids': [order_id],
            'payment_method': 'cash',
            'customer_paid': 280.0,
            'change_returned': 0.0
        }
        resp = self.client.post('/api/settle_bill', data=json.dumps(settle_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        res_json = resp.get_json()
        self.assertTrue(res_json.get('success'))
        print(f"PASS: Order #{order_id} settled successfully into Invoice #{res_json.get('invoice_number')}!")

if __name__ == '__main__':
    unittest.main()
