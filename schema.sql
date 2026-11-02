-- Disable foreign key checks during setup
SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 1. Sales and Customers
-- ==========================================

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    phone VARCHAR(50) NULL,
    address VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customer_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    due_date DATE NULL,
    fulfilled_date DATE NULL,
    status ENUM('Pending', 'Processing', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_customer_orders_customer 
        FOREIGN KEY (customer_id) REFERENCES customers (id),
    CONSTRAINT chk_customer_orders_total_amount 
        CHECK (total_amount >= 0)
);

-- ==========================================
-- 2. Production and Costing
-- ==========================================

CREATE TABLE IF NOT EXISTS artworks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status ENUM('In Progress', 'Completed', 'Sold') NOT NULL DEFAULT 'In Progress',
    hours_worked DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    allocated_rent DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    selling_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    completed_date DATE NULL,
    CONSTRAINT chk_artworks_hours 
        CHECK (hours_worked >= 0),
    CONSTRAINT chk_artworks_hourly_rate 
        CHECK (hourly_rate >= 0),
    CONSTRAINT chk_artworks_allocated_rent 
        CHECK (allocated_rent >= 0),
    CONSTRAINT chk_artworks_selling_price 
        CHECK (selling_price >= 0)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    artwork_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    backordered_qty INT NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_items_order 
        FOREIGN KEY (order_id) REFERENCES customer_orders (id),
    CONSTRAINT fk_order_items_artwork 
        FOREIGN KEY (artwork_id) REFERENCES artworks (id),
    CONSTRAINT chk_order_items_quantity 
        CHECK (quantity > 0),
    CONSTRAINT chk_order_items_backordered 
        CHECK (backordered_qty >= 0),
    CONSTRAINT chk_order_items_price 
        CHECK (unit_price >= 0)
);

-- ==========================================
-- 3. Inventory and Purchasing
-- ==========================================

CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(160) NULL,
    phone VARCHAR(50) NULL,
    lead_time_days INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_suppliers_lead_time 
        CHECK (lead_time_days >= 0)
);

CREATE TABLE IF NOT EXISTS materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    category ENUM('Raw Material', 'Packaging', 'Consumable', 'Other') NOT NULL,
    unit VARCHAR(50) NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    reorder_level INT NOT NULL DEFAULT 10,
    CONSTRAINT fk_materials_supplier 
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
    CONSTRAINT chk_materials_unit_cost 
        CHECK (unit_cost >= 0),
    CONSTRAINT chk_materials_reorder_level 
        CHECK (reorder_level >= 0)
);

CREATE TABLE IF NOT EXISTS artwork_materials (
    artwork_id INT NOT NULL,
    material_id INT NOT NULL,
    quantity_used DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    unit_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (artwork_id, material_id),
    CONSTRAINT fk_artwork_materials_artwork 
        FOREIGN KEY (artwork_id) REFERENCES artworks (id),
    CONSTRAINT fk_artwork_materials_material 
        FOREIGN KEY (material_id) REFERENCES materials (id),
    CONSTRAINT chk_artwork_materials_qty 
        CHECK (quantity_used >= 0),
    CONSTRAINT chk_artwork_materials_cost 
        CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS eoq_parameters (
    material_id INT PRIMARY KEY,
    setup_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    holding_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT fk_eoq_parameters_material 
        FOREIGN KEY (material_id) REFERENCES materials (id),
    CONSTRAINT chk_eoq_setup_cost 
        CHECK (setup_cost >= 0),
    CONSTRAINT chk_eoq_holding_cost 
        CHECK (holding_cost >= 0)
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    order_date DATE NOT NULL,
    expected_date DATE NULL,
    received_date DATE NULL,
    status ENUM('Pending', 'Ordered', 'Received', 'Cancelled') NOT NULL DEFAULT 'Pending',
    CONSTRAINT fk_purchase_orders_supplier 
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    po_id INT NOT NULL,
    material_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_cost DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_po_items_po 
        FOREIGN KEY (po_id) REFERENCES purchase_orders (id),
    CONSTRAINT fk_po_items_material 
        FOREIGN KEY (material_id) REFERENCES materials (id),
    CONSTRAINT chk_po_items_quantity 
        CHECK (quantity > 0),
    CONSTRAINT chk_po_items_price 
        CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS storage_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL DEFAULT 0,
    monthly_rent DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT chk_storage_capacity 
        CHECK (capacity >= 0),
    CONSTRAINT chk_storage_rent 
        CHECK (monthly_rent >= 0)
);

CREATE TABLE IF NOT EXISTS inventory (
    location_id INT NOT NULL,
    material_id INT NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (location_id, material_id),
    CONSTRAINT fk_inventory_location 
        FOREIGN KEY (location_id) REFERENCES storage_locations (id),
    CONSTRAINT fk_inventory_material 
        FOREIGN KEY (material_id) REFERENCES materials (id),
    CONSTRAINT chk_inventory_qty 
        CHECK (quantity_on_hand >= 0)
);

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;