import os

filepath = 'app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find("@app.route('/api/get_bill_details/<string:type>/<int:id>')")
if start_idx == -1:
    print("Start not found")
else:
    end_idx = content.find("def settle_bill():", start_idx)
    old_func = content[start_idx:end_idx]
    
    new_func = '''@app.route('/api/get_bill_details/<string:type>/<int:id>')
@login_required
def get_bill_details(type, id):
    try:
        items = []
        subtotal = 0.0
        orders = []
        
        if type == 'table':
            orders = Order.query.outerjoin(Invoice).filter(Order.table_id == id, Order.status == 'completed', Invoice.id == None).all()
        else:
            order = Order.query.get(id)
            if order and order.status == 'completed':
                orders = [order]
                
        for order in orders:
            for item in order.items:
                items.append({
                    'name': item.menu_item.name if item.menu_item else 'Deleted Item',
                    'quantity': item.quantity,
                    'price': item.price_at_order,
                    'total': item.quantity * item.price_at_order
                })
                subtotal += item.quantity * item.price_at_order
                
        merged_items = {}
        for item in items:
            key = item['name']
            if key not in merged_items:
                merged_items[key] = item
            else:
                merged_items[key]['quantity'] += item['quantity']
                merged_items[key]['total'] += item['total']
                
        return jsonify({'items': list(merged_items.values()), 'subtotal': subtotal, 'order_ids': [o.id for o in orders]})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'items': [], 'subtotal': 0.0, 'order_ids': [], 'error': str(e)})

@app.route('/api/settle_bill', methods=['POST'])
@login_required
'''
    content = content.replace(old_func, new_func)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced!")
