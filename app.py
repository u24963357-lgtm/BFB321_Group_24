from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="Template",
    static_folder="css",
    static_url_path="/css",
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/production')
def production():
    return render_template('Admin Facing/baseline_data.html')

@app.route('/logistics')
def logistics():
    return render_template('Admin Facing/inventory_management.html')

@app.route('/orders')
def orders():
    return render_template('Admin Facing/order_management.html', revenue=2450, open_order=7, fulfillment_rate=95, backorders=8)


@app.route('/storage')
def storage():
    return render_template('Admin Facing/replenishment.html')



if __name__ == '__main__':
    app.run(debug=True)