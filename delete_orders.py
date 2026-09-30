from app import app, db
from models import Order, OrderItem, Invoice, CreditLedger, Refund, Table

with app.app_context():
    # 1. Delete dependents of Invoice
    Refund.query.delete()
    CreditLedger.query.delete()
    # 2. Delete Invoices
    Invoice.query.delete()
    # 3. Delete dependents of Order
    OrderItem.query.delete()
    # 4. Delete Orders
    Order.query.delete()
    
    # 5. Reset all tables to vacant
    tables = Table.query.all()
    for t in tables:
        t.status = 'vacant'
        t.session_start_time = None
        
    db.session.commit()
    print("All orders, invoices, refunds, and ledgers deleted successfully. Tables reset.")
