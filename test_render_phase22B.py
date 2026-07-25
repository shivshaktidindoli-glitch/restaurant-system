import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from flask import url_for
from flask_login import login_user
from models import User, Order, Table, MenuItem, OrderItem

def test_phase22B_ui():
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
            
            print("--- Testing /admin/dashboard HTML ---")
            res = client.get('/admin/dashboard')
            html = res.data.decode('utf-8')
            
            if 'fa-cloud-arrow-down' in html:
                print("FOUND: FontAwesome cloud-arrow-down icon for Backup DB!")
            if 'fa-indian-rupee-sign' in html:
                print("FOUND: Background icon fa-indian-rupee-sign in Sales Card!")
                
            print("\n--- Testing Sidebar in Dashboard ---")
            if 'fa-chart-pie' in html and 'fa-bell-concierge' in html:
                print("FOUND: Sidebar FontAwesome icons present!")
                
            print("\n--- Testing /admin/new_parcel HTML ---")
            res2 = client.get('/admin/new_parcel')
            html2 = res2.data.decode('utf-8')
            
            if 'active-in-cart' in html2:
                print("FOUND: active-in-cart CSS class definition in <style> block!")
            if 'card-item-' in html2:
                print("FOUND: card-item-ID classes added to menu item cards!")
            if 'transform: translateY(-2px)' in html2:
                print("FOUND: Hover transform added for menu items!")

if __name__ == '__main__':
    test_phase22B_ui()
