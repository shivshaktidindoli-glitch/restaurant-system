import csv
import os
from models import db, Branch, Category, MenuItem, Table, User

def seed_data():
    """
    Seeds initial database data (Branch, Admin, Staff, Tables, Menu)
    without circular imports or aggressive drops.
    """
    try:
        # Check or create default branch
        branch = Branch.query.first()
        if not branch:
            branch = Branch(
                name="Soul Sip Cafe",
                address="Shop no. 8 & 9, Green Residency, Commercial Shopping Center, Opp. Madhav Crest, Surat",
                phone="9876543210"
            )
            db.session.add(branch)
            db.session.commit()
            print("Default Branch created.")

        # Add admin and staff users if none exist
        if User.query.count() == 0:
            admin = User(name='Admin User', mobile='7999620244', role='admin', branch_id=branch.id)
            admin.set_password('soulsip@2000')
            db.session.add(admin)
            
            manager = User(name='Manager User', mobile='8888888888', role='manager', branch_id=branch.id)
            manager.set_password('manager123')
            db.session.add(manager)
            
            waiter = User(name='Waiter User', mobile='7777777777', role='waiter', branch_id=branch.id)
            waiter.set_password('waiter123')
            db.session.add(waiter)
            
            chef = User(name='Chef User', mobile='6666666666', role='chef', branch_id=branch.id)
            chef.set_password('chef123')
            db.session.add(chef)
            
            cashier = User(name='Cashier User', mobile='5555555555', role='cashier', branch_id=branch.id)
            cashier.set_password('cashier123')
            db.session.add(cashier)
            db.session.commit()
            print("Staff users created.")

        # Create Tables if none exist
        if Table.query.count() == 0:
            tables = []
            for i in range(1, 13):
                section = "Ground Floor" if i <= 8 else "Basement"
                tables.append(Table(branch_id=branch.id, name=f"T-{i}", section=section, seats=4, status="vacant"))
            db.session.add_all(tables)
            db.session.commit()
            print("Tables created.")

        # Load Menu from CSV
        load_menu_from_csv()

        print("Data seeded successfully!")
        print("-" * 30)
        print("Admin Credentials: 7999620244 / soulsip@2000")
        print("-" * 30)
        return True
    except Exception as e:
        print(f"Error in seed_data: {e}")
        db.session.rollback()
        return False

def load_menu_from_csv(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), 'menu_data.csv')
        
    if not os.path.exists(csv_path):
        print(f"WARNING: {csv_path} not found, skipping menu items.")
        return False
        
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            categories_map = {c.name: c for c in Category.query.all()}
            sort_counter = len(categories_map) + 1
            
            for row in reader:
                cat_name = row['csvcategory'].strip()
                
                if cat_name not in categories_map:
                    new_cat = Category(name=cat_name, sort_order=sort_counter)
                    db.session.add(new_cat)
                    db.session.commit()
                    categories_map[cat_name] = new_cat
                    sort_counter += 1
                    
                cat_obj = categories_map[cat_name]
                
                item_name = row['item_name'].strip()
                item_name_gu = row.get('item_name_gu', '').strip()
                description = row.get('description', '').strip()
                price = float(row['price'].strip()) if row['price'].strip() else 0.0
                is_fav = str(row.get('is_favorite', 'False')).strip().lower() == 'true'
                food_type = row.get('food_type', 'veg').strip()
                
                # Create or update item
                existing_item = MenuItem.query.filter_by(category_id=cat_obj.id, name=item_name).first()
                if not existing_item:
                    item = MenuItem(
                        category_id=cat_obj.id,
                        name=item_name,
                        name_gu=item_name_gu,
                        description=description,
                        price=price,
                        is_favorite=is_fav,
                        food_type=food_type,
                        is_available=True
                    )
                    db.session.add(item)
                else:
                    existing_item.price = price
                    existing_item.description = description
                    existing_item.is_favorite = is_fav
                    existing_item.food_type = food_type
                    
        db.session.commit()
        print("Menu data loaded successfully from CSV!")
        return True
    except Exception as e:
        print(f"Error loading menu from CSV: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed_data()
