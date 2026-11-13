import os
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for
import numpy as np  
from eoq import calculate_eoq_canvas, calculate_eoq_frame
from db import init_app as init_db_app, query_all, query_one
from models import (
    add_shipment,
    delete_inventory as delete_inventory_record,
    delete_shipment as delete_shipment_record,
    get_inventory,
    get_production_data,
    get_recent_orders,
    get_shipments,
    place_order,
)
from werkzeug.security import check_password_hash


#Global data
VALID_USERS = {
    "adminA": "pbkdf2:sha256:600000$cb76IivmMSLD8fFK$01760879a4953b8cf91adb090ef6c7f74f8ea9825737cbb218d223a08a3a8894",
    "adminB": "pbkdf2:sha256:600000$GSUXAPSubV5qockQ$57bf56d20358068e9394e626de73075cd34f2e5b3a84a9214f967f3e87e790a7",
}
SALES_MONTHLY = np.array([10, 12, 11, 13, 12, 14, 15, 16, 17, 18, 19, 20])
NUM_IN_STOCK = np.array([5, 4, 6, 5, 5,5,5,3, 4, 5, 6, 5]) 
MONTHLY_REVENUE = np.array([1000, 1220, 1240, 1260, 1280, 1300, 1320, 1340, 1360, 1380, 1400, 1420])
    

app = Flask(
    __name__,
    template_folder="Template",
    static_folder="css",
    static_url_path="/css",
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
init_db_app(app)

@app.route('/')
def login():
    return render_template('login.html')

@app.before_request
def require_login():
    if request.endpoint in ('login', 'static'):
        return
    if request.endpoint == 'home' and request.method == 'POST':
        return
    if 'username' not in session:
        return redirect(url_for('login'))

@app.route('/index', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session.clear()
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if not username or not password:
            return render_template('login.html', error='Enter both a username and password.'), 400
        password_hash = VALID_USERS.get(username)
        if password_hash is None or not check_password_hash(password_hash, password):
            return render_template('login.html', error='Invalid username or password.'), 401
        session['username'] = username
        return redirect(url_for('home'))

    new_paintings=NUM_IN_STOCK[10] # October stock
    on_time_rate= 95
    monthly_revenue=MONTHLY_REVENUE[10] # October revenue
    low_stock_items=18
    return render_template('index.html', new_paintings=new_paintings, on_time_rate=on_time_rate, monthly_revenue=monthly_revenue, low_stock_items=low_stock_items)

@app.route('/production')
def production():

    num_in_stock = NUM_IN_STOCK[9] # October stock
    moneyspent = np.array([1000, 1200, 1100, 1300, 1250, 1400, 1500, 1600, 1700, 1800, 1900, 2000])
    value = np.array([5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 10500])
    monthly_goal = np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
    cur_frm_goal = abs(monthly_goal[10] - NUM_IN_STOCK[10]) 
    efficiency = (value[10] / moneyspent[10]) * 100
    efficiency_monthly = (value / moneyspent) * 100
    return render_template('Admin Facing/baseline_data.html', 
                           monthly_goal=monthly_goal, 
                           cur_frm_goal=cur_frm_goal, 
                           efficiency=efficiency,
                           num_in_stock=num_in_stock,
                           efficiency_monthly=np.round(efficiency_monthly, 2),
                           moneyspent=moneyspent, value=value,
                           production=get_production_data())



@app.route('/logistics', methods=['GET', 'POST'])
def logistics():
    if request.method == 'POST':
        success, message = add_shipment(
            request.form.get('shipment_id', '').strip(),
            request.form.get('origin', '').strip(),
            request.form.get('destination', '').strip(),
            request.form.get('status', '').strip(),
            request.form.get('arrival_date', '').strip(),
        )
        flash(message, 'success' if success else 'error')
        return redirect(url_for('logistics'))

    monthly_demand = SALES_MONTHLY[10] * 100
    eoq_canvas = round(calculate_eoq_canvas(monthly_demand))
    eoq_frame = round(calculate_eoq_frame(monthly_demand))
    return render_template(
        'Admin Facing/inventory_management.html',
        eoq_canvas=eoq_canvas,
        eoq_frame=eoq_frame,
        shipments=get_shipments(),
    )


@app.route(
    '/shipments/<string:shipment_id>/delete',
    methods=['POST'],
)
def delete_shipment(shipment_id):
    delete_shipment_record(shipment_id)
    return redirect(url_for('logistics'))


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', type=int)
        if not customer_id or not product_id or not quantity:
            flash('Choose a customer, product, and quantity.', 'error')
        else:
            success, message = place_order(customer_id, product_id, quantity)
            flash(message, 'success' if success else 'error')
        return redirect(url_for('orders'))

    monthly_revenue = MONTHLY_REVENUE
    revenue = monthly_revenue[9]  # October revenue
    open_order = query_one(
        "SELECT COUNT(*) AS count FROM orders WHERE status = 'Open'"
    )['count']
    fulfillment_rate = 95
    backorders = 8
    sales_monthly = SALES_MONTHLY
    revenue_precentage = round((monthly_revenue[9] - monthly_revenue[8]) / monthly_revenue[8], 2) * 100 # calculating revenue percentage change from September to October
    return render_template(
        'Admin Facing/order_management.html',
        revenue=revenue,
        open_order=open_order,
        fulfillment_rate=fulfillment_rate,
        backorders=backorders,
        sales_monthly=sales_monthly,
        monthly_revenue=monthly_revenue,
        revenue_precentage=revenue_precentage,
        orders=get_recent_orders(),
        products=query_all(
            "SELECT id, name, stock_quantity, price FROM products ORDER BY name"
        ),
        customers=query_all("SELECT id, name FROM customers ORDER BY name"),
    )


@app.route('/storage')
def storage():
    inventory = get_inventory()
    sum_quantity = sum(item['quantity'] for item in inventory)
    low_stock_items = sum(item['status'] != 'In stock' for item in inventory)
    capacity = query_one(
        "SELECT COALESCE(SUM(capacity), 0) AS total FROM storage_locations"
    )['total']
    capacity_utilization = round((sum_quantity / capacity) * 100, 2) if capacity else 0

    return render_template(
        'Admin Facing/replenishment.html',
        inventory=inventory,
        sum_quantity=sum_quantity,
        low_stock_items=low_stock_items,
        capacity_utilization=capacity_utilization,
    )


@app.route(
    '/inventory/<int:product_id>/delete',
    methods=['POST'],
)
def delete_inventory(product_id):
    delete_inventory_record(product_id)
    return redirect(url_for('storage'))



if __name__ == '__main__':
    app.run(debug=True)