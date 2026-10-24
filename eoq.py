# function to calculat the recommended order quantity based on EOQ formula for cnavas and frames   
setup_cost_canvas = 50  # Cost to place an order
setup_cost_frame = 50  # Cost to place an order
holding_cost_canvas = 10  # Cost to hold one unit in inventory for a month
holding_cost_frame = 5  # Cost to hold one unit in inventory for a month

def calculate_eoq_canvas(demand_canvas):
    eoq = ((2 * demand_canvas * setup_cost_canvas) / holding_cost_canvas) ** 0.5
    return eoq

def calculate_eoq_frame(demand_frame):
    eoq = ((2 * demand_frame * setup_cost_frame) / holding_cost_frame) ** 0.5
    return eoq