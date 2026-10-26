from flask import Flask, render_template
import numpy as np  
from eoq import calculate_eoq_canvas, calculate_eoq_frame


#Global data
SALES_MONTHLY = np.array([10, 12, 11, 13, 12, 14, 15, 16, 17, 18, 19, 20])
NUM_IN_STOCK = np.array([5, 4, 6, 5, 5,5,5,3, 4, 5, 6, 5]) 
MONTHLY_REVENUE = np.array([1000, 1220, 1240, 1260, 1280, 1300, 1320, 1340, 1360, 1380, 1400, 1420])
    

app = Flask(
    __name__,
    template_folder="Template",
    static_folder="css",
    static_url_path="/css",
)

@app.route('/')
def home():
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
    monthly_demand = SALES_MONTHLY[10] * 100
    eoq_canvas = round(calculate_eoq_canvas(monthly_demand))
    eoq_frame = round(calculate_eoq_frame(monthly_demand))
    return render_template('Admin Facing/inventory_management.html', eoq_canvas=eoq_canvas, eoq_frame=eoq_frame)

@app.route('/orders')
def orders(): # values coming from the database, for now, we are using static values
    monthly_revenue = MONTHLY_REVENUE
    revenue = monthly_revenue[9]  # October revenue
    open_order = 7
    fulfillment_rate = 95
    backorders = 8
    sales_monthly = SALES_MONTHLY
    revenue_precentage = round((monthly_revenue[9] - monthly_revenue[8]) / monthly_revenue[8], 2) * 100 # calculating revenue percentage change from September to October
    return render_template('Admin Facing/order_management.html', revenue=revenue, open_order=open_order, fulfillment_rate=fulfillment_rate, backorders=backorders, sales_monthly=sales_monthly, monthly_revenue=monthly_revenue, revenue_precentage=revenue_precentage)


@app.route('/storage')
def storage():

    quantity = np.array([1840,624,86,4250,312,42,168])
    sum_quantity = np.sum(quantity)
    low_stock_items = 3
    capacity = 10000
    capacity_utilization = round((sum_quantity / capacity) * 100, 2)

    return render_template('Admin Facing/replenishment.html',quantity=quantity, sum_quantity=sum_quantity, low_stock_items=low_stock_items, capacity_utilization=capacity_utilization)



if __name__ == '__main__':
    app.run(debug=True)