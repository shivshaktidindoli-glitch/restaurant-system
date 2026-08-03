import sys
import os

# Add the current directory to the path so we can import app and models
sys.path.insert(0, os.path.abspath('.'))

from app import app
from models import db, RawMaterial, InventoryLog, User

def run_tests():
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Ensure tables exist
            db.create_all()
            
            # Setup a test admin user if not exists
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                admin = User(name='Test Admin', mobile='9999999999', role='admin')
                db.session.add(admin)
            admin.set_password('1234')
            db.session.commit()
            
            print("--- Starting Inventory Tests ---")
            
            # Log in as admin
            resp = client.post('/admin/login', data={'mobile': admin.mobile, 'password': '1234'}, follow_redirects=True)
            if b'Dashboard' not in resp.data:
                print("Failed to login as admin!")
                print(resp.data.decode()[:500])
                return
            
            print("\n1. Creating Raw Material: Burger Bun (initial: 50, threshold: 10)")
            resp = client.post('/admin/inventory/material', data={
                'name': 'Burger Bun',
                'unit': 'pieces',
                'initial_stock': 50,
                'low_stock_threshold': 10
            }, follow_redirects=True)
            
            mat = RawMaterial.query.filter_by(name='Burger Bun').order_by(RawMaterial.id.desc()).first()
            print(f"-> Created material ID: {mat.id}, Stock: {mat.current_stock}")
            
            print("\n2. Deducting 45 items (expected stock: 5)")
            client.post('/admin/inventory/entry', data={
                'material_id': mat.id,
                'type': 'deduct',
                'quantity': 45,
                'reason': 'Test deduction'
            }, follow_redirects=True)
            
            db.session.refresh(mat)
            print(f"-> Current Stock after deduction: {mat.current_stock}")
            
            print("\n3. Checking Dashboard for Low Stock Alert...")
            resp = client.get('/admin', follow_redirects=True)
            html = resp.data.decode('utf-8')
            if 'Low Stock Alerts' in html and 'Burger Bun' in html:
                print("-> SUCCESS: Burger Bun appears in Low Stock Alerts on Dashboard.")
            else:
                print("-> FAILED: Burger Bun not found in Low Stock Alerts.")
                
            print("\n4. Adding 50 items (expected stock: 55)")
            client.post('/admin/inventory/entry', data={
                'material_id': mat.id,
                'type': 'add',
                'quantity': 50,
                'reason': 'Test addition'
            }, follow_redirects=True)
            
            db.session.refresh(mat)
            print(f"-> Current Stock after addition: {mat.current_stock}")
            
            print("\n5. Checking Dashboard again (Alert should be gone)...")
            resp = client.get('/admin', follow_redirects=True)
            html = resp.data.decode('utf-8')
            # Check if Burger Bun is in the low stock alerts table (which should either be missing or empty)
            if 'Burger Bun' not in html.split('Low Stock Alerts')[-1]:
                print("-> SUCCESS: Burger Bun is no longer in Low Stock Alerts.")
            else:
                print("-> FAILED: Burger Bun still appears in Low Stock Alerts.")
                
            print("\n6. Deducting 100 items (exceeds stock 55, should cap at 0)")
            resp = client.post('/admin/inventory/entry', data={
                'material_id': mat.id,
                'type': 'deduct',
                'quantity': 100,
                'reason': 'Test over-deduction'
            }, follow_redirects=True)
            
            db.session.refresh(mat)
            print(f"-> Current Stock after over-deduction: {mat.current_stock}")
            if mat.current_stock == 0:
                print("-> SUCCESS: Stock was correctly capped at 0 and did not go negative.")
            else:
                print("-> FAILED: Stock is not 0.")

if __name__ == '__main__':
    run_tests()
