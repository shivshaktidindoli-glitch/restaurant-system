from app import app, db
from models import Category, MenuItem, Table
import traceback

with app.app_context():
    try:
        categories = Category.query.order_by(Category.sort_order.asc()).all()
        print("Successfully queried categories. Count:", len(categories))
    except Exception as e:
        print("Error querying database:")
        traceback.print_exc()
