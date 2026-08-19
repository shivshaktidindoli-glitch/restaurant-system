import os
import sys
import unittest
from datetime import datetime

# Set test environment
os.environ['DATABASE_URL'] = 'sqlite:///test_poss.db'
os.environ['SECRET_KEY'] = 'test-poss-secret-key'

from app import app, db, limiter, User, Branch, Table, Category, MenuItem, Order, OrderItem, Invoice, Expense, CashFlow, OutletSetting

class POSSIntegrationTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['RATELIMIT_ENABLED'] = False
        limiter.enabled = False
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # Create Branch
            branch = Branch(name="Shiv Shakti Restaurant", address="Ahmedabad", phone="9876543210")
            db.session.add(branch)
            
            # Create Users with all 6 roles
            roles = ['admin', 'manager', 'waiter', 'chef', 'cashier', 'delivery']
            for r in roles:
                u = User(mobile=f"900000000{roles.index(r)}", name=f"{r.capitalize()} User", role=r, branch_id=1)
                u.set_password("password123")
                db.session.add(u)
                
            # Create Category & MenuItems
            cat1 = Category(name="Starters", sort_order=1)
            cat2 = Category(name="Main Course", sort_order=2)
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            item1 = MenuItem(name="Paneer Tikka", price=250.0, category_id=cat1.id, is_available=True)
            item2 = MenuItem(name="Butter Naan", price=50.0, category_id=cat2.id, is_available=True)
            db.session.add_all([item1, item2])
            
            # Create Tables
            t1 = Table(name="T1", section="AC Hall", seats=4, status="vacant", branch_id=branch.id)
            t2 = Table(name="T2", section="Garden", seats=6, status="occupied", branch_id=branch.id)
            db.session.add_all([t1, t2])
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_as(self, role):
        roles = ['admin', 'manager', 'waiter', 'chef', 'cashier', 'delivery']
        mobile = f"900000000{roles.index(role)}"
        return self.client.post('/admin/login', data={'mobile': mobile, 'password': 'password123'}, follow_redirects=True)

    def test_01_dashboard_and_operations_hub(self):
        self.login_as('admin')
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Operations Hub', res.data)
        self.assertIn(b'Dine In, Take Away', res.data)
        self.assertIn(b'Customer CRM, Loyalty', res.data)
        self.assertIn(b'Kitchen, Menu', res.data)
        self.assertIn(b'Shift, Cash Drawer', res.data)
        print("[PASS] Test 1: Operations Hub rendered with all 4 modules")

    def test_02_outlet_settings(self):
        self.login_as('admin')
        res = self.client.get('/admin/settings/outlet')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Display &amp; Calculation Settings', res.data)
        self.assertIn(b'Print Rules', res.data)
        
        # Test Save Outlet Settings API
        save_res = self.client.post('/api/settings/outlet/save', json={
            'round_off': 'true',
            'service_charge': 'false',
            'gst_rate': '5.0',
            'print_fssai': 'true',
            'print_gstin': 'true',
            'print_qr_upi': 'true',
            'loyalty_ratio': '100'
        })
        self.assertEqual(save_res.status_code, 200)
        self.assertTrue(save_res.json['success'])
        
        with app.app_context():
            s = OutletSetting.query.filter_by(key='gst_rate').first()
            self.assertEqual(s.value, '5.0')
        print("[PASS] Test 2: Outlet settings save and fetch working correctly")

    def test_03_petty_cash_and_expenses(self):
        self.login_as('admin')
        # Add expense
        res = self.client.post('/admin/expenses/add', data={
            'category': 'Raw Materials / Grocery',
            'amount': '450.00',
            'payment_mode': 'cash',
            'description': 'Dairy milk & curd purchase'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dairy milk &amp; curd purchase', res.data)
        self.assertIn(b'450.00', res.data)
        print("[PASS] Test 3: Daily Petty Cash & Expense tracking working")

    def test_04_cashflow_and_drawer(self):
        self.login_as('admin')
        # Opening cash
        res = self.client.post('/admin/cashflow/add', data={
            'flow_type': 'opening',
            'amount': '2000.00',
            'reason': 'Register 1 Morning Float'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Register 1 Morning Float', res.data)
        
        # Cash Out
        self.client.post('/admin/cashflow/add', data={
            'flow_type': 'out',
            'amount': '500.00',
            'reason': 'Owner withdrawal'
        })
        
        cf_res = self.client.get('/admin/cashflow')
        self.assertIn(b'2000.00', cf_res.data)
        self.assertIn(b'500.00', cf_res.data)
        print("[PASS] Test 4: Cash Drawer and Cash Flow reconciliation working")

    def test_05_reports_15_summaries(self):
        self.login_as('admin')
        reports = [
            'sales', 'employee_sales', 'category', 'best_selling', 'least_selling',
            'table_util', 'aov', 'covers', 'tips', 'orders', 'customers',
            'cancellations', 'day_end_summary', 'expense_summary', 'cashflow_summary'
        ]
        for r in reports:
            res = self.client.get(f'/api/report_data?type={r}')
            self.assertEqual(res.status_code, 200)
            self.assertIn('data', res.json)
        print(f"[PASS] Test 5: All 15 Report APIs verified ({len(reports)} summaries)")

    def test_06_topbar_quick_apis(self):
        self.login_as('admin')
        # Item status
        res = self.client.get('/api/all_items_status')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json['items']) >= 2)
        
        # Toggle item
        toggle_res = self.client.post('/api/toggle_item', json={'item_id': 1, 'is_available': False})
        self.assertTrue(toggle_res.json['success'])
        
        with app.app_context():
            itm = MenuItem.query.get(1)
            self.assertFalse(itm.is_available)
            
        # Hold orders API
        hold_res = self.client.get('/api/hold_orders')
        self.assertEqual(hold_res.status_code, 200)
        print("[PASS] Test 6: Soul Sip POS Topbar quick actions (Item toggle, Hold orders) verified")

    def tearDown(self):
        limiter.enabled = True
        app.config['RATELIMIT_ENABLED'] = True

if __name__ == '__main__':
    unittest.main()
