import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Table, Order, OrderItem, MenuItem, User
from bs4 import BeautifulSoup
from flask_login import login_user

def run_render_tests():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            print("--- Setting up UI Data ---")
            # Create a user to login
            admin = User.query.filter_by(mobile='9999999999').first()
            if not admin:
                admin = User(name='admin', mobile='9999999999', role='admin', branch_id=1)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            
            # Make sure we have a veg item with shortcode and favorite
            m_veg = MenuItem.query.filter_by(name='Test Veg').first()
            if not m_veg:
                m_veg = MenuItem(name='Test Veg', price=100.0, category_id=1, food_type='veg', is_favorite=True, short_code='V101')
                db.session.add(m_veg)
                
            m_nonveg = MenuItem.query.filter_by(name='Test Chicken').first()
            if not m_nonveg:
                m_nonveg = MenuItem(name='Test Chicken', price=200.0, category_id=1, food_type='non-veg', is_favorite=False, short_code='NV201')
                db.session.add(m_nonveg)
                
            db.session.commit()
            
            # Reset session start time to RIGHT NOW to prove 0 minutes logic
            t1 = Table.query.filter_by(name='T-1').first()
            from datetime import datetime
            t1.session_start_time = datetime.utcnow()
            t1.status = 'occupied'
            
            # Make sure there is an active order
            existing_order = Order.query.filter_by(table_id=t1.id).filter(Order.status.notin_(['completed', 'cancelled'])).first()
            if not existing_order:
                o1 = Order(branch_id=1, table_id=t1.id, type='dine-in', status='new')
                db.session.add(o1)
                db.session.commit()
                m = MenuItem.query.first()
                if m:
                    oi = OrderItem(order_id=o1.id, menu_item_id=m.id, quantity=1, price_at_order=100.0)
                    db.session.add(oi)
            db.session.commit()
            
            # Login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
                sess['_fresh'] = True
                
            print("\n--- 1. Testing /admin/live_tables HTML ---")
            res = client.get('/admin/live_tables')
            html = res.data.decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find Section headers
            sections = soup.select('#sections-container h3')
            for s in sections:
                print(f"FOUND SECTION HEADER: {s}")
                
            # Find Active Amounts and Timers
            tables = soup.select('.table-card.occupied')
            for t in tables:
                name = t.select_one('.table-name').text
                amount = t.select_one('div[style*="background: var(--brand-orange)"]')
                timer = t.select_one('.timer-display')
                print(f"TABLE TILE HTML: Name={name.encode('ascii','ignore').decode()}, Amount Badge={str(amount).encode('ascii','ignore').decode()}, Timer Badge={str(timer).encode('ascii','ignore').decode()}")
            
            print("\n--- 2. Testing /admin/new_parcel HTML ---")
            res2 = client.get('/admin/new_parcel')
            html2 = res2.data.decode('utf-8')
            soup2 = BeautifulSoup(html2, 'html.parser')
            
            # Check Favorites section
            fav_section = soup2.select_one('#cat-favorites')
            if fav_section:
                print(f"FAVORITES SECTION HEADER: {fav_section.select_one('.category-title').text.encode('ascii','ignore').decode()}")
                fav_items = fav_section.select('.menu-item-card')
                for f in fav_items:
                    print(f"FAV ITEM HTML CLASS: {f['class']}")
                    name = f.select_one('.item-name').text
                    print(f"FAV ITEM NAME: {name.strip()}")
            
            # Check non-veg border class
            non_veg = soup2.select('.food-non-veg')
            for nv in non_veg:
                print(f"NON-VEG ITEM FOUND WITH CLASS: {nv['class']} (Name: {nv.select_one('.item-name').text.strip()})")

            # Check if favorites appear in other sections (duplicates)
            all_fav_class_items = soup2.select('.menu-item-card')
            fav_count = sum(1 for f in all_fav_class_items if 'Test Veg' in f.select_one('.item-name').text)
            print(f"Total occurrences of 'Test Veg' in DOM: {fav_count} (Should be exactly 1)")

if __name__ == '__main__':
    run_render_tests()
