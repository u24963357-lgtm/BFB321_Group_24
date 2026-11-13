import pymysql
from db import query_all, query_one, execute, get_db
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# AUTHENTICATION 
# ==========================================
def authenticate_user(username, password):
    user = query_one("SELECT * FROM users WHERE username = %s", (username,))
    if user and check_password_hash(user['password_hash'], password):
        return True
    return False

# ==========================================
# DASHBOARD 
# ==========================================
def get_dashboard_stats():
    # Real dynamic metrics instead of hardcoded numpy arrays
    revenue = query_one("""
        SELECT SUM(oi.quantity * oi.unit_price) AS total 
        FROM order_items oi JOIN orders o ON oi.order_id = o.id 
        WHERE o.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    """)['total'] or 0
    
    open_orders = query_one("SELECT COUNT(*) as count FROM orders WHERE status = 'Open'")['count']
    
    low_stock = query_one("SELECT COUNT(*) as count FROM products WHERE stock_quantity <= reorder_level")['count']
    
    # Calculate production efficiency for current month
    prod = query_one("""
        SELECT SUM(value_produced) as val, SUM(money_spent) as spent 
        FROM production_records 
        WHERE month = DATE_FORMAT(NOW(), '%Y-%m-01')
    """)
    efficiency = (prod['val'] / prod['spent'] * 100) if prod['spent'] else 0

    return {
        "revenue": float(revenue),
        "open_orders": open_orders,
        "low_stock": low_stock,
        "efficiency": round(efficiency, 1)
    }

# ==========================================
# PRODUCTION 
# ==========================================
def get_production_data():
    records = query_all("""
        SELECT p.name, pr.month, pr.units_produced, pr.monthly_goal, 
               pr.money_spent, pr.value_produced,
        CASE WHEN pr.money_spent > 0
             THEN pr.value_produced / pr.money_spent * 100
             ELSE 0
        END as efficiency
        FROM production_records pr
        JOIN products p ON pr.product_id = p.id
        ORDER BY pr.month DESC
    """)
    return records

# ==========================================
# LOGISTICS & SHIPMENTS 
# ==========================================
def get_shipments():
    return query_all("SELECT * FROM shipments ORDER BY is_past ASC, id DESC")

def add_shipment(shipment_id, origin, destination, status, arrival_date):
    if not shipment_id or not origin or not destination:
        return False, "All fields are required."
    try:
        execute("INSERT INTO shipments (id, origin, destination, status, arrival_date) VALUES (%s, %s, %s, %s, %s)",
                (shipment_id, origin, destination, status, arrival_date))
        return True, "Shipment added successfully."
    except pymysql.err.IntegrityError:
        get_db().rollback()
        return False, "Shipment ID already exists."

def delete_shipment(shipment_id):
    execute("DELETE FROM shipments WHERE id = %s", (shipment_id,))

# ==========================================
# SALES & ORDERS 
# ==========================================
def get_recent_orders():
    return query_all("""
        SELECT o.id, c.name as customer, o.order_date, o.status, 
               SUM(oi.quantity * oi.unit_price) as total_value
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id, c.name, o.order_date, o.status
        ORDER BY o.order_date DESC
    """)

def place_order(customer_id, product_id, quantity):
    """Step 4: True Transaction"""
    if int(quantity) <= 0:
        return False, "Quantity must be greater than zero."

    db = get_db()
    try:
        with db.cursor() as cur:
            # Lock the product row
            cur.execute("SELECT name, stock_quantity, price FROM products WHERE id = %s FOR UPDATE", (product_id,))
            product = cur.fetchone()
            
            if not product:
                db.rollback()
                return False, "Product not found."
            
            if product['stock_quantity'] < int(quantity):
                db.rollback()
                return False, f"Not enough stock. Only {product['stock_quantity']} available."

            # Create Order
            cur.execute("INSERT INTO orders (customer_id, status) VALUES (%s, 'Open')", (customer_id,))
            order_id = cur.lastrowid

            # Create Order Item
            cur.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                        (order_id, product_id, quantity, product['price']))

            # Deduct Stock
            cur.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s", (quantity, product_id))

        db.commit()
        return True, f"Order placed for {quantity} x {product['name']}."
    except pymysql.MySQLError:
        db.rollback()
        raise

# ==========================================
# STORAGE & INVENTORY 
# ==========================================
def get_inventory():
    return query_all("""
        SELECT p.id, CONCAT('SKU-', LPAD(p.id, 5, '0')) as sku,
               p.name, p.product_type as category, 
               sl.name as location, p.stock_quantity as quantity,
               CASE 
                   WHEN p.stock_quantity = 0 THEN 'Reorder'
                   WHEN p.stock_quantity <= p.reorder_level THEN 'Low stock'
                   ELSE 'In stock'
               END as status
        FROM products p
        JOIN storage_locations sl ON p.location_id = sl.id
    """)

def add_inventory(sku, name, category, location_id, quantity):
    if not sku or not name:
        return False, "SKU and Name are required."
    try:
        # Default price and costs for new items added via storage page
        execute("""INSERT INTO products (sku, name, product_type, location_id, stock_quantity, price) 
                   VALUES (%s, %s, %s, %s, %s, 100.00)""", 
                (sku, name, category, location_id, quantity))
        return True, "Inventory item added."
    except pymysql.err.IntegrityError:
        get_db().rollback()
        return False, "SKU already exists."

def delete_inventory(product_id):
    execute("DELETE FROM products WHERE id = %s", (product_id,))