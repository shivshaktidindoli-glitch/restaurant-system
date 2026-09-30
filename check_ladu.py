from app import app, db
from models import MenuItem

with app.app_context():
    items = MenuItem.query.filter(MenuItem.name.ilike('%churma%') | MenuItem.name.ilike('%ladu%') | MenuItem.name.ilike('%ladoo%')).all()
    for item in items:
        print(f"ID: {item.id}, Name: {item.name}, Cat: {item.category.name if item.category else 'None'}, Available: {item.is_available}")
