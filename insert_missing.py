from app import app, db
from models import Category, MenuItem

missing_data = [
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Sp. Methi Makai Mattre", "name_hi": "????. ???? ???? ???", "price": 180},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Veg. Handi", "name_hi": "???. ?????", "price": 190},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Veg. kadai", "name_hi": "???. ????", "price": 190},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Vag. Jaipuri", "name_hi": "???. ??????", "price": 180},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Veg. Hedraldadi", "name_hi": "???. ?????????", "price": 180},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Veg. Hariyali Mix", "name_hi": "???. ??????? ?????", "price": 180},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Veg. kolapuri", "name_hi": "???. ??????????", "price": 180},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Mix Vegetable", "name_hi": "????? ????????", "price": 150},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "MushRoom Butter Masala", "name_hi": "????? ??? ?????", "price": 200},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Chana Masala", "name_hi": "??? ?????", "price": 150},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Chana Paneer Masala", "name_hi": "??? ???? ?????", "price": 220},
    {"cat": "Veg. Panjabi (Khajana)", "name_en": "Plain Palak", "name_hi": "????? ????", "price": 140},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Tava Chapati", "name_hi": "??? ?????", "price": 15},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Butter Tava Chapadi", "name_hi": "??? ??? ?????", "price": 20},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Plain Parratha", "name_hi": "???? ?????", "price": 40},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Butter Parratha", "name_hi": "??? ?????", "price": 50},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Marwadi Tikkad Roti (Ghee)", "name_hi": "??????? ?????? ???? (??)", "price": 80},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Khoba Roti (Ghee)", "name_hi": "???? ???? (??)", "price": 100},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Aloo parrtha Tava (Lunch)", "name_hi": "??? ????? ??? (???)", "price": 130},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Paneer Parratha Tava", "name_hi": "???? ????? ???", "price": 160},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Bajri na Rotala", "name_hi": "????? ?? ?????", "price": 60},
    {"cat": "Tava Roti Tikad & Khoba", "name_en": "Extra Ghee (20 gm)", "name_hi": "????????? ?? (20 gm)", "price": 20},
    {"cat": "Started Chineese", "name_en": "Veg. Manchurian Dry.", "name_hi": "???. ???????? ?????", "price": 120},
    {"cat": "Started Chineese", "name_en": "Veg. Manchurian Greavy", "name_hi": "???. ???????? ??????", "price": 140},
    {"cat": "Started Chineese", "name_en": "Paneer Chilly Dry.", "name_hi": "???? ???? ?????", "price": 200},
    {"cat": "Started Chineese", "name_en": "Veg. Schezwan Manchurian", "name_hi": "???. ?????? ????????", "price": 140},
    {"cat": "Started Chineese", "name_en": "Paneer Chilly Greavy", "name_hi": "???? ???? ??????", "price": 220},
    {"cat": "Chinese Rice & Noodles", "name_en": "Veg. Hakka Noodles", "name_hi": "???. ????? ??????", "price": 120},
    {"cat": "Chinese Rice & Noodles", "name_en": "Singapori Noodles", "name_hi": "????????? ??????", "price": 130},
    {"cat": "Chinese Rice & Noodles", "name_en": "Chainiz Bhel", "name_hi": "?????? ???", "price": 150},
    {"cat": "Chinese Rice & Noodles", "name_en": "Fried Rice", "name_hi": "?????? ????", "price": 120},
    {"cat": "Chinese Rice & Noodles", "name_en": "Singapori Fried Rice", "name_hi": "????????? ?????? ????", "price": 130},
    {"cat": "Chinese Rice & Noodles", "name_en": "Schezwan Noodles", "name_hi": "?????? ??????", "price": 140},
    {"cat": "Chinese Rice & Noodles", "name_en": "Bombay Bhal", "name_hi": "?????? ???", "price": 140},
    {"cat": "Started Tandoor", "name_en": "Paneer Tikka Dry.", "name_hi": "???? ?????? ?????", "price": 210},
    {"cat": "Started Tandoor", "name_en": "Hara Bhara Kabab", "name_hi": "??? ??? ????", "price": 150},
    {"cat": "Started Tandoor", "name_en": "Pudina Tikka Dry.", "name_hi": "?????? ?????? ?????", "price": 220},
    {"cat": "Soups", "name_en": "Hot N Sour Soup", "name_hi": "??? ??? ??? ???", "price": 100},
    {"cat": "Soups", "name_en": "Manshau Soup", "name_hi": "????? ???", "price": 100},
    {"cat": "Soups", "name_en": "Cream Of Tomato Soup", "name_hi": "????? ?? ?????? ???", "price": 90},
    {"cat": "Soups", "name_en": "Lemon Coriander", "name_hi": "???? ????????", "price": 70}
]

with app.app_context():
    output = []
    for item in missing_data:
        cat = Category.query.filter_by(name=item['cat']).first()
        if not cat:
            cat = Category(name=item['cat'], branch_id=1)
            db.session.add(cat)
            db.session.flush()
        
        existing = MenuItem.query.filter_by(name=item['name_en'], category_id=cat.id).first()
        if not existing:
            new_item = MenuItem(
                name=item['name_en'],
                name_hi=item['name_hi'],
                price=item['price'],
                category_id=cat.id,
                branch_id=1,
                type='veg',
                is_available=True
            )
            db.session.add(new_item)
            output.append(f"Added {item['name_en']}")
        else:
            existing.name_hi = item['name_hi']
            existing.price = item['price']
            output.append(f"Updated {item['name_en']}")
            
    db.session.commit()
    print("Success:")
    for o in output: print(o)
