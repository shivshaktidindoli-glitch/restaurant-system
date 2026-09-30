from app import app, db
from models import MenuItem

with app.app_context():
    items = MenuItem.query.filter(MenuItem.name.like('%''%')).all()
    for item in items:
        print(item.name)
