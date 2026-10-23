from flask import Flask, render_template
import numpy as np  


#Global data


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

    num_in_stock = np.array([5, 4, 6, 5, 5,5,5,3, 4, 5, 6, 5]) 
    moneyspent = np.array([1000, 1200, 1100, 1300, 1250, 1400, 1500, 1600, 1700, 1800, 1900, 2000])
    value = np.array([5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 10500])
    monthly_goal = np.array([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
    
    cur_frm_goal = abs(monthly_goal[10] - num_in_stock[10]) 
    efficiency = (value[10] / moneyspent[10]) * 100
    efficiency_monthly = (value / moneyspent) * 100
    return render_template('Admin Facing/baseline_data.html', 
                           monthly_goal=monthly_goal, 
                           cur_frm_goal=cur_frm_goal, 
                           efficiency=efficiency,
                           num_in_stock=num_in_stock,
                           efficiency_monthly=np.round(efficiency_monthly, 2),
                           moneyspent=moneyspent, value=value)



@app.route('/logistics')
def logistics():
    return render_template('Admin Facing/inventory_management.html')

@app.route('/orders')
def orders():
    return render_template('Admin Facing/order_management.html', revenue=2450, open_order=7, fulfillment_rate=95, backorders=8)


@app.route('/storage')
def storage():

    quantity = np.array([1840,624,86,4250,312,42,168])
    sum_quantity = np.sum(quantity)
    low_stock_items = 18
    capacity = 10000
    capacity_utilization = round(sum_quantity / capacity) * 100

    return render_template('Admin Facing/replenishment.html',quantity=quantity, sum_quantity=sum_quantity, low_stock_items=low_stock_items, capacity_utilization=capacity_utilization)



if __name__ == '__main__':
    app.run(debug=True)