import pymysql
from db import query_all, query_one, execute, get_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
from math import isfinite, sqrt

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
    _, month_start, next_month = _month_bounds()
    production = query_one("""
        SELECT COALESCE(SUM(pr.units_produced), 0) AS units,
               COALESCE(SUM(pr.monthly_goal), 0) AS goal,
               COALESCE(SUM(pr.value_produced), 0) AS value_produced,
               COALESCE(SUM(pr.money_spent), 0) AS money_spent
        FROM production_records pr
        JOIN products p ON p.id = pr.product_id
        WHERE p.product_type = 'Painting'
          AND pr.month >= %s AND pr.month < %s
    """, (month_start, next_month))
    shipments = query_one("""
        SELECT COALESCE(SUM(is_past = FALSE AND status <> 'Delivered'), 0) AS active,
               COALESCE(SUM(status = 'Delayed'), 0) AS delayed_count
        FROM shipments
    """)
    efficiency = (
        float(production["value_produced"]) / float(production["money_spent"]) * 100
        if production["money_spent"] else 0.0
    )
    return {
        "monthly_revenue": _revenue_between(month_start, next_month),
        "new_paintings": int(production["units"]),
        "monthly_goal": int(production["goal"]),
        "production_efficiency": round(efficiency, 1),
        "active_shipments": int(shipments["active"]),
        "delayed_shipments": int(shipments["delayed_count"]),
        "low_stock_items": int(query_one(
            "SELECT COUNT(*) AS count FROM products WHERE stock_quantity <= reorder_level"
        )["count"]),
    }

# ==========================================
# PRODUCTION 
# ==========================================
def get_production_data():
    records = query_all("""
        SELECT pr.id, pr.product_id, p.name, p.product_type, pr.month,
               pr.units_produced, pr.monthly_goal,
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


def get_production_page_data():
    """Everything the production page needs, including current-year order goals."""
    year = date.today().year
    units = [0] * 12
    goals = [0] * 12
    values = [0.0] * 12
    costs = [0.0] * 12
    records = get_production_data()
    order_goals = query_all("""
        SELECT MONTH(o.order_date) AS month, COALESCE(SUM(oi.quantity), 0) AS quantity
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id
        WHERE p.product_type = 'Painting'
          AND o.order_date >= %s AND o.order_date < %s
          AND o.status <> 'Cancelled'
        GROUP BY MONTH(o.order_date)
    """, (date(year, 1, 1), date(year + 1, 1, 1)))

    for order_goal in order_goals:
        goals[int(order_goal["month"]) - 1] = int(order_goal["quantity"])

    for record in records:
        if record["product_type"] != "Painting" or record["month"].year != year:
            continue
        index = record["month"].month - 1
        units[index] += int(record["units_produced"])
        values[index] += float(record["value_produced"])
        costs[index] += float(record["money_spent"])

    efficiency = [
        round(value / cost * 100, 2) if cost else 0.0
        for value, cost in zip(values, costs)
    ]
    current_index = date.today().month - 1
    current_units = units[current_index]
    current_goal = goals[current_index]
    return {
        "production": records,
        "products": query_all("SELECT id, name FROM products ORDER BY name"),
        "locations": query_all("SELECT id, name FROM storage_locations ORDER BY name"),
        "num_in_stock": units,
        "monthly_goal": goals,
        "efficiency_monthly": efficiency,
        "current_month_index": current_index,
        "current_month_name": date.today().strftime("%B"),
        "current_month_date": date(year, current_index + 1, 1).isoformat(),
        "cur_frm_goal": max(current_goal - current_units, 0),
        "goal_met": current_goal > 0 and current_units >= current_goal,
        "efficiency": efficiency[current_index],
        "value": values,
        "moneyspent": costs,
    }


def save_production_record(record_id, product_id, month, units, goal, money_spent, value_produced):
    if (
        product_id <= 0
        or units < 0
        or goal < 0
        or not isfinite(money_spent)
        or not isfinite(value_produced)
        or money_spent < 0
        or value_produced < 0
    ):
        return False, "Production values must be non-negative and a product is required."

    month = month.replace(day=1)
    db = get_db()
    try:
        with db.cursor() as cur:
            if record_id:
                cur.execute(
                    "SELECT id FROM production_records WHERE id = %s FOR UPDATE",
                    (record_id,),
                )
                if not cur.fetchone():
                    db.rollback()
                    return False, "Production record not found."
                cur.execute(
                    "UPDATE production_records SET product_id = %s, month = %s, "
                    "units_produced = %s, monthly_goal = %s, money_spent = %s, "
                    "value_produced = %s WHERE id = %s",
                    (product_id, month, units, goal, money_spent, value_produced, record_id),
                )
            else:
                cur.execute(
                    "INSERT INTO production_records "
                    "(product_id, month, units_produced, monthly_goal, money_spent, value_produced) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (product_id, month, units, goal, money_spent, value_produced),
                )
        db.commit()
        return True, "Production record saved."
    except pymysql.err.IntegrityError:
        db.rollback()
        return False, "The product is invalid or a record already exists for that product and month."
    except pymysql.MySQLError:
        db.rollback()
        raise


def create_production_piece(name, location_id, price, month, units, goal, money_spent, value_produced):
    name = name.strip()
    if not name or len(name) > 120 or location_id <= 0:
        return False, "Enter a piece name and choose a valid storage location."
    if (
        not isfinite(price)
        or price < 0
        or units < 0
        or goal < 0
        or not isfinite(money_spent)
        or not isfinite(value_produced)
        or money_spent < 0
        or value_produced < 0
    ):
        return False, "Piece price and production values must be non-negative."

    month = month.replace(day=1)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO products "
                "(name, product_type, location_id, stock_quantity, price) "
                "VALUES (%s, 'Painting', %s, %s, %s)",
                (name, location_id, units, price),
            )
            product_id = cur.lastrowid
            cur.execute(
                "INSERT INTO production_records "
                "(product_id, month, units_produced, monthly_goal, money_spent, value_produced) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (product_id, month, units, goal, money_spent, value_produced),
            )
        db.commit()
        return True, "New painting and production record added."
    except pymysql.err.IntegrityError:
        db.rollback()
        return False, "Could not add the piece. Check the storage location and production values."
    except pymysql.MySQLError:
        db.rollback()
        raise

# ==========================================
# LOGISTICS & SHIPMENTS 
# ==========================================
def get_shipments():
    return query_all("SELECT * FROM shipments ORDER BY is_past ASC, id DESC")


def get_logistics_page_data():
    summary = query_one("""
        SELECT COUNT(*) AS total,
               COALESCE(SUM(is_past = FALSE AND status <> 'Delivered'), 0) AS active,
               COALESCE(SUM(status = 'Delayed'), 0) AS delayed_count,
               COALESCE(SUM(is_past = TRUE OR status = 'Delivered'), 0) AS delivered
        FROM shipments
    """)
    products = query_all("""
        SELECT p.id, p.name, p.product_type, p.setup_cost, p.holding_cost,
               COALESCE((
                   SELECT SUM(oi.quantity)
                   FROM order_items oi
                   JOIN orders o ON o.id = oi.order_id
                   WHERE oi.product_id = p.id
                     AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                     AND o.status <> 'Cancelled'
               ), 0) AS annual_demand,
               COALESCE((
                   SELECT SUM(pr.units_produced)
                   FROM production_records pr
                   WHERE pr.product_id = p.id
                     AND pr.month >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
               ), 0) AS production_units,
               COALESCE((
                   SELECT COUNT(DISTINCT pr.month)
                   FROM production_records pr
                   WHERE pr.product_id = p.id
                     AND pr.month >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
               ), 0) AS production_months
        FROM products p
        ORDER BY p.product_type, p.name
    """)

    eoq_items = []
    epq_items = []
    for product in products:
        demand = float(product["annual_demand"])
        setup_cost = float(product["setup_cost"])
        annual_holding_cost = float(product["holding_cost"]) * 12
        eoq = (
            round(sqrt(2 * demand * setup_cost / annual_holding_cost))
            if demand > 0 and annual_holding_cost > 0 else None
        )
        if product["product_type"] in ("Canvas", "Frame"):
            eoq_items.append({**product, "eoq": eoq})

        months = int(product["production_months"])
        production_rate = (
            float(product["production_units"]) * 12 / months if months else 0
        )
        epq = None
        if demand > 0 and production_rate > demand and annual_holding_cost > 0:
            epq = round(sqrt(
                (2 * demand * setup_cost / annual_holding_cost)
                * production_rate / (production_rate - demand)
            ))
        epq_items.append({
            "name": product["name"],
            "demand": demand,
            "production_rate": round(production_rate, 1),
            "epq": epq,
        })

    return {
        "shipments": get_shipments(),
        "total_shipments": int(summary["total"]),
        "active_shipments": int(summary["active"]),
        "delayed_shipments": int(summary["delayed_count"]),
        "delivered_shipments": int(summary["delivered"]),
        "eoq_items": eoq_items,
        "epq_items": epq_items,
    }


def add_shipment(shipment_id, origin, destination, status, arrival_date):
    allowed_statuses = {"In transit", "On schedule", "Delayed", "At terminal", "Delivered"}
    if not shipment_id or not origin or not destination or not arrival_date:
        return False, "All fields are required."
    if status not in allowed_statuses:
        return False, "Choose a valid shipment status."
    try:
        execute(
            "INSERT INTO shipments "
            "(id, origin, destination, status, arrival_date, is_past) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (shipment_id, origin, destination, status, arrival_date, status == "Delivered"),
        )
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


def get_order_detail(order_id):
    order = query_one("""
        SELECT o.id, o.customer_id, c.name AS customer, o.order_date, o.status,
               o.stock_reserved
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        WHERE o.id = %s
    """, (order_id,))
    if not order:
        return None
    order["items"] = query_all("""
        SELECT oi.id, oi.product_id, p.name AS product, oi.quantity, oi.unit_price,
               p.stock_quantity
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id = %s
        ORDER BY oi.id
    """, (order_id,))
    order["products"] = list_order_products()
    return order

def place_order(customer_id, product_id, quantity):
    """Step 4: True Transaction"""
    if int(quantity) <= 0:
        return False, "Quantity must be greater than zero."
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT name, stock_quantity, price FROM products WHERE id = %s FOR UPDATE",
                (product_id,),
            )
            product = cur.fetchone()

            if not product:
                db.rollback()
                return False, "Product not found."

            if product["stock_quantity"] < int(quantity):
                db.rollback()
                return False, f"Not enough stock. Only {product['stock_quantity']} available."

            cur.execute(
                "INSERT INTO orders (customer_id, status, stock_reserved) "
                "VALUES (%s, 'Open', TRUE)",
                (customer_id,),
            )
            order_id = cur.lastrowid

            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                "VALUES (%s, %s, %s, %s)",
                (order_id, product_id, quantity, product["price"]),
            )
            cur.execute(
                "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s",
                (quantity, product_id),
            )

        db.commit()
        return True, f"Order placed for {quantity} x {product['name']}."
    except pymysql.err.IntegrityError:
        db.rollback()
        return False, "The selected customer or product is no longer available."
    except pymysql.MySQLError:
        db.rollback()
        raise


def update_order_item(order_id, item_id, product_id, quantity):
    if product_id <= 0 or quantity <= 0:
        return False, "Choose a product and a quantity greater than zero."

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT status, stock_reserved FROM orders WHERE id = %s FOR UPDATE",
                (order_id,),
            )
            order = cur.fetchone()
            if not order:
                db.rollback()
                return False, "Order not found."
            if order["status"] != "Open":
                db.rollback()
                return False, "Only open orders can be edited."
            if not order["stock_reserved"]:
                db.rollback()
                return False, "This older order has no stock reservation; cancel it and place a new order to edit its items."

            cur.execute(
                "SELECT product_id, quantity, unit_price FROM order_items "
                "WHERE id = %s AND order_id = %s FOR UPDATE",
                (item_id, order_id),
            )
            item = cur.fetchone()
            if not item:
                db.rollback()
                return False, "Order item not found."

            previous_product_id = int(item["product_id"])
            locked_products = {}
            for locked_id in sorted({previous_product_id, product_id}):
                cur.execute(
                    "SELECT id, name, stock_quantity, price FROM products WHERE id = %s FOR UPDATE",
                    (locked_id,),
                )
                product = cur.fetchone()
                if product:
                    locked_products[locked_id] = product
            if product_id not in locked_products:
                db.rollback()
                return False, "Product not found."

            target = locked_products[product_id]
            available = int(target["stock_quantity"])
            if product_id == previous_product_id:
                available += int(item["quantity"])
            if available < quantity:
                db.rollback()
                return False, f"Not enough stock. Only {available} available."

            if product_id == previous_product_id:
                cur.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + %s - %s "
                    "WHERE id = %s",
                    (item["quantity"], quantity, product_id),
                )
                unit_price = item["unit_price"]
            else:
                cur.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + %s WHERE id = %s",
                    (item["quantity"], previous_product_id),
                )
                cur.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s",
                    (quantity, product_id),
                )
                unit_price = target["price"]
            cur.execute(
                "UPDATE order_items SET product_id = %s, quantity = %s, unit_price = %s "
                "WHERE id = %s AND order_id = %s",
                (product_id, quantity, unit_price, item_id, order_id),
            )
        db.commit()
        return True, "Order item updated."
    except pymysql.MySQLError:
        db.rollback()
        raise


def update_order_status(order_id, new_status):
    if new_status not in {"Open", "Fulfilled", "Backordered", "Cancelled"}:
        return False, "Choose a valid order status."

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT status, stock_reserved FROM orders WHERE id = %s FOR UPDATE",
                (order_id,),
            )
            order = cur.fetchone()
            if not order:
                db.rollback()
                return False, "Order not found."

            current_status = order["status"]
            transitions = {
                "Open": {"Fulfilled", "Backordered", "Cancelled"},
                "Backordered": {"Open", "Cancelled"},
                "Fulfilled": set(),
                "Cancelled": set(),
            }
            if new_status not in transitions[current_status]:
                db.rollback()
                return False, f"Cannot change an order from {current_status} to {new_status}."

            cur.execute(
                "SELECT product_id, SUM(quantity) AS quantity FROM order_items "
                "WHERE order_id = %s GROUP BY product_id ORDER BY product_id",
                (order_id,),
            )
            items = cur.fetchall()
            needs_reservation = (
                current_status == "Backordered" and new_status == "Open"
            ) or (
                current_status == "Open"
                and new_status == "Fulfilled"
                and not order["stock_reserved"]
            )
            if needs_reservation:
                for item in items:
                    cur.execute(
                        "SELECT stock_quantity FROM products WHERE id = %s FOR UPDATE",
                        (item["product_id"],),
                    )
                    product = cur.fetchone()
                    if not product or int(product["stock_quantity"]) < int(item["quantity"]):
                        db.rollback()
                        return False, f"There is not enough stock to {new_status.lower()} this order."
                for item in items:
                    cur.execute(
                        "UPDATE products SET stock_quantity = stock_quantity - %s "
                        "WHERE id = %s",
                        (item["quantity"], item["product_id"]),
                    )
            elif (
                current_status == "Open"
                and order["stock_reserved"]
                and new_status in {"Backordered", "Cancelled"}
            ):
                for item in items:
                    cur.execute(
                        "UPDATE products SET stock_quantity = stock_quantity + %s "
                        "WHERE id = %s",
                        (item["quantity"], item["product_id"]),
                    )

            cur.execute(
                "UPDATE orders SET status = %s, "
                "fulfilled_date = CASE WHEN %s = 'Fulfilled' THEN CURDATE() ELSE NULL END, "
                "stock_reserved = %s "
                "WHERE id = %s",
                (new_status, new_status, new_status == "Open", order_id),
            )
        db.commit()
        return True, f"Order marked {new_status.lower()}."
    except pymysql.MySQLError:
        db.rollback()
        raise


# ==========================================
# ORDERS PAGE: values for order_management.html
# ==========================================
def _month_bounds(today=None):
    """First day of last month, this month and next month (handles January)."""
    today = today or date.today()
    this_month = today.replace(day=1)
    prev_month = (this_month - timedelta(days=1)).replace(day=1)
    next_month = (this_month + timedelta(days=32)).replace(day=1)
    return prev_month, this_month, next_month


def _revenue_between(start, end):
    """Revenue of all orders placed in [start, end)."""
    row = query_one("""
        SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        WHERE o.order_date >= %s AND o.order_date < %s
          AND o.status <> 'Cancelled'
    """, (start, end))
    return float(row["total"])


def get_order_status_counts():
    """Open / backordered / fulfilled counts and the fulfilment rate (%)."""
    row = query_one("""
        SELECT COALESCE(SUM(status <> 'Cancelled'), 0) AS total,
               COALESCE(SUM(status = 'Open'), 0)        AS open_count,
               COALESCE(SUM(status = 'Backordered'), 0) AS backordered,
               COALESCE(SUM(status = 'Fulfilled'), 0)   AS fulfilled
        FROM orders
    """)
    total = int(row["total"])
    fulfilled = int(row["fulfilled"])
    backordered = int(row["backordered"])
    return {
        "open_order": int(row["open_count"]),
        "backorders": backordered,
        "fulfillment_rate": round(fulfilled / total * 100, 1) if total else 0.0,
        "backorder_pct": round(backordered / total * 100, 1) if total else 0.0,
    }


def get_monthly_revenue_summary():
    """Revenue this month and % change compared with last month."""
    prev_start, this_start, next_start = _month_bounds()
    revenue = _revenue_between(this_start, next_start)
    previous = _revenue_between(prev_start, this_start)
    change = round((revenue - previous) / previous * 100, 1) if previous else 0.0
    return revenue, change


def get_open_orders_this_month():
    """Open orders placed this month (for the '+N this month' badge)."""
    _, this_start, next_start = _month_bounds()
    return query_one("""
        SELECT COUNT(*) AS n FROM orders
        WHERE status = 'Open' AND order_date >= %s AND order_date < %s
    """, (this_start, next_start))["n"]


def get_monthly_sales(year=None):
    """
    Orders and revenue for each month of the year.
    Returns two lists of 12 values: index 0 = January ... index 11 = December.
    Months with no orders are filled with 0.
    """
    year = year or date.today().year
    rows = query_all("""
        SELECT MONTH(o.order_date)                          AS m,
               COUNT(DISTINCT o.id)                         AS order_count,
               COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        WHERE o.order_date >= %s AND o.order_date < %s
          AND o.status <> 'Cancelled'
        GROUP BY MONTH(o.order_date)
    """, (date(year, 1, 1), date(year + 1, 1, 1)))

    sales_monthly = [0] * 12
    monthly_revenue = [0.0] * 12
    for r in rows:
        sales_monthly[r["m"] - 1] = int(r["order_count"])
        monthly_revenue[r["m"] - 1] = float(r["revenue"])
    return sales_monthly, monthly_revenue


def list_customers():
    """Customers for the 'Place Order' dropdown."""
    return query_all("SELECT id, name FROM customers ORDER BY name")


def list_order_products():
    """Products for the 'Place Order' dropdown."""
    return query_all(
        "SELECT id, name, stock_quantity, price FROM products ORDER BY name")


def get_orders_page_data():
    """Everything order_management.html needs, in one dictionary."""
    revenue, revenue_precentage = get_monthly_revenue_summary()  # spelling matches the template
    sales_monthly, monthly_revenue = get_monthly_sales()
    data = get_order_status_counts()
    data.update(
        revenue=revenue,
        revenue_precentage=revenue_precentage,
        open_this_month=get_open_orders_this_month(),
        sales_monthly=sales_monthly,
        monthly_revenue=monthly_revenue,
        orders=get_recent_orders(),
        customers=list_customers(),
        products=list_order_products(),
    )
    return data

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


def get_inventory_summary():
    """Values for the summary cards on replenishment.html."""
    row = query_one("""
        SELECT COALESCE(SUM(stock_quantity), 0) AS units_on_hand,
               COALESCE(SUM(stock_quantity <= reorder_level), 0) AS low_stock
        FROM products
    """)
    capacity = int(query_one(
        "SELECT COALESCE(SUM(capacity), 0) AS total FROM storage_locations"
    )["total"])

    units = int(row["units_on_hand"])
    return {
        "sum_quantity": units,
        "low_stock_items": int(row["low_stock"]),
        "capacity_utilization": round(units / capacity * 100, 2) if capacity else 0.0,
    }


def get_storage_page_data():
    """Everything replenishment.html needs, in one dictionary."""
    data = get_inventory_summary()
    data["inventory"] = get_inventory()
    data["locations"] = query_all(
        "SELECT id, name FROM storage_locations ORDER BY name"
    )
    return data


def add_inventory(name, category, location_id, quantity, price, reorder_level):
    if not name or category not in {"Painting", "Canvas", "Frame"}:
        return False, "Enter a product name and choose a valid category."
    if (
        location_id <= 0
        or quantity < 0
        or reorder_level < 0
        or not isfinite(price)
        or price < 0
    ):
        return False, "Location, quantity, reorder level, and price must be valid."
    try:
        execute(
            "INSERT INTO products "
            "(name, product_type, location_id, stock_quantity, price, reorder_level) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, category, location_id, quantity, price, reorder_level),
        )
        return True, "Inventory item added."
    except pymysql.err.IntegrityError:
        get_db().rollback()
        return False, "The selected storage location or product details are invalid."


def delete_inventory(product_id):
    references = query_one("""
        SELECT EXISTS(SELECT 1 FROM order_items WHERE product_id = %s) AS ordered,
               EXISTS(SELECT 1 FROM purchase_orders WHERE product_id = %s) AS purchased,
               EXISTS(SELECT 1 FROM production_records WHERE product_id = %s) AS produced
    """, (product_id, product_id, product_id))
    if references["ordered"] or references["purchased"] or references["produced"]:
        return False, "This product has order, purchase, or production history and cannot be deleted."
    execute("DELETE FROM products WHERE id = %s", (product_id,))
    return True, "Inventory item deleted."


def get_products_paginated(limit, offset, category=None):
    """Fetch products for the API with pagination and optional filtering."""
    sql = """
        SELECT id, name, product_type, price, stock_quantity, reorder_level 
        FROM products
    """
    params = []
    
    if category:
        sql += " WHERE product_type = %s"
        params.append(category)
        
    sql += " ORDER BY id LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    return query_all(sql, params)

def update_product_price(product_id, new_price):
    """RESTful update for a product's price."""
    if new_price < 0:
        return False, "Price cannot be negative."
    
    product = query_one("SELECT id FROM products WHERE id = %s", (product_id,))
    if not product:
        return False, "Product not found."
        
    execute("UPDATE products SET price = %s WHERE id = %s", (new_price, product_id))
    return True, "Product price updated successfully."