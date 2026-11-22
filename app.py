import os
import secrets
import logging
from datetime import date

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from db import init_app as init_db_app
from models import (
    add_inventory,
    add_shipment,
    create_production_piece,
    delete_inventory as delete_inventory_record,
    delete_shipment as delete_shipment_record,
    get_dashboard_stats,
    get_logistics_page_data,
    get_order_detail,
    get_orders_page_data,
    get_production_page_data,
    get_storage_page_data,
    place_order,
    save_production_record,
    update_inventory as update_inventory_record,
    update_order_item,
    update_order_status,
    authenticate_user,
    get_products_paginated, # NEW
    update_product_price     # NEW
)

app = Flask(
    __name__,
    template_folder="Template",
    static_folder="css",
    static_url_path="/css",
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
init_db_app(app)


logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": "The request was invalid."}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "The requested resource does not exist."}), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Server Error: {error}")
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500


@app.route('/')
def login():
    return render_template('login.html')

@app.before_request
def require_login():
    # Allow API routes without login for testing (or add login check if required)
    if request.path.startswith('/api/'):
        return
        
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
            
        if not authenticate_user(username, password):
            logging.warning(f"Failed login attempt for user: {username}")
            return render_template('login.html', error='Invalid username or password.'), 401
            
        session['username'] = username
        logging.info(f"User {username} logged in.")
        return redirect(url_for('home'))

    return render_template('index.html', **get_dashboard_stats())

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/production', methods=['GET', 'POST'])
def production():
    if request.method == 'POST':
        product_choice = request.form.get('product_id', '')
        record_id = request.form.get('record_id', type=int)
        try:
            month = date.fromisoformat(request.form.get('month', ''))
            units = int(request.form.get('units_produced', ''))
            goal = int(request.form.get('monthly_goal', ''))
            money_spent = float(request.form.get('money_spent', ''))
            value_produced = float(request.form.get('value_produced', ''))
        except ValueError:
            flash('Enter a valid month and numeric production values.', 'error')
        else:
            if product_choice == 'new':
                location_id = request.form.get('location_id', type=int)
                price = request.form.get('piece_price', type=float)
                if record_id:
                    flash('A new piece cannot be created while editing a production record.', 'error')
                elif not location_id or price is None:
                    flash('Enter the new piece name, price, and storage location.', 'error')
                else:
                    success, message = create_production_piece(
                        request.form.get('piece_name', ''), location_id, price,
                        month, units, goal, money_spent, value_produced,
                    )
                    flash(message, 'success' if success else 'error')
            else:
                product_id = request.form.get('product_id', type=int)
                if not product_id:
                    flash('Choose a product or add a new piece.', 'error')
                else:
                    success, message = save_production_record(
                        record_id, product_id, month, units, goal, money_spent, value_produced
                    )
                    flash(message, 'success' if success else 'error')
        return redirect(url_for('production'))
    return render_template('Admin Facing/baseline_data.html', **get_production_page_data())

@app.route('/logistics', methods=['GET', 'POST'])
def logistics():
    if request.method == 'POST':
        success, message = add_shipment(
            request.form.get('shipment_id', '').strip(), request.form.get('origin', '').strip(),
            request.form.get('destination', '').strip(), request.form.get('status', '').strip(),
            request.form.get('arrival_date', '').strip(),
        )
        flash(message, 'success' if success else 'error')
        return redirect(url_for('logistics'))
    return render_template('Admin Facing/inventory_management.html', **get_logistics_page_data())

@app.route('/shipments/<string:shipment_id>/delete', methods=['POST'])
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
    return render_template('Admin Facing/order_management.html', **get_orders_page_data())

@app.route('/orders/<int:order_id>')
def order_detail(order_id):
    order = get_order_detail(order_id)
    if order is None:
        return 'Order not found.', 404
    return render_template('Admin Facing/order_detail.html', order=order)

@app.route('/orders/<int:order_id>/items/<int:item_id>', methods=['POST'])
def edit_order_item(order_id, item_id):
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)
    if not product_id or not quantity:
        flash('Choose a product and quantity.', 'error')
    else:
        success, message = update_order_item(order_id, item_id, product_id, quantity)
        flash(message, 'success' if success else 'error')
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def change_order_status(order_id):
    status = request.form.get('status', '')
    success, message = update_order_status(order_id, status)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/inventory', methods=['POST'])
def create_inventory():
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '')
    location_id = request.form.get('location_id', type=int)
    quantity = request.form.get('quantity', type=int)
    reorder_level = request.form.get('reorder_level', type=int)
    price = request.form.get('price', type=float)
    if None in (location_id, quantity, reorder_level, price):
        flash('Enter a valid location, quantity, reorder level, and price.', 'error')
    else:
        success, message = add_inventory(name, category, location_id, quantity, price, reorder_level)
        flash(message, 'success' if success else 'error')
    return redirect(url_for('storage'))

@app.route('/storage')
def storage():
    return render_template('Admin Facing/replenishment.html', **get_storage_page_data())

@app.route('/inventory/<int:product_id>/delete', methods=['POST'])
def delete_inventory(product_id):
    success, message = delete_inventory_record(product_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('storage'))


@app.route('/inventory/<int:product_id>/update', methods=['POST'])
def update_inventory(product_id):
    location_id = request.form.get('location_id', type=int)
    quantity = request.form.get('quantity', type=int)
    status = request.form.get('status', '')
    if location_id is None or quantity is None:
        flash('Enter a valid storage location and quantity.', 'error')
    else:
        success, message = update_inventory_record(
            product_id, location_id, quantity, status
        )
        flash(message, 'success' if success else 'error')
    return redirect(url_for('storage'))





@app.route('/api/products', methods=['GET'])
def api_get_products():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    category = request.args.get('category', type=str)
    
    if limit < 1 or offset < 0:
        return jsonify({"error": "Invalid pagination values. Limit must be > 0 and offset >= 0."}), 400
        
    products = get_products_paginated(limit, offset, category)
    return jsonify({
        "meta": {"limit": limit, "offset": offset, "count": len(products)},
        "data": products
    }), 200


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def api_get_order(order_id):
    order = get_order_detail(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200


@app.route('/api/orders', methods=['POST'])
def api_create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
        
    customer_id = data.get('customer_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if not all([customer_id, product_id, quantity]):
        return jsonify({"error": "customer_id, product_id, and quantity are required"}), 400
        
    success, message = place_order(customer_id, product_id, quantity)
    
    if success:
        logging.info(f"API: Order placed for product {product_id}")
        return jsonify({"message": message}), 201
    else:
        return jsonify({"error": message}), 400


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def api_update_product(product_id):
    data = request.get_json()
    if not data or 'price' not in data:
        return jsonify({"error": "Missing 'price' in JSON payload"}), 400
        
    try:
        new_price = float(data['price'])
    except ValueError:
        return jsonify({"error": "Price must be a number"}), 400
        
    success, message = update_product_price(product_id, new_price)
    
    if success:
        logging.info(f"API: Updated price for product {product_id} to {new_price}")
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400


if __name__ == '__main__':
    print("Open your website at http://127.0.0.1:5000/", flush=True)
    app.run(debug=True)