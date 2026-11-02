
-- ============================================
-- KELVIC INVENTORY DATABASE
-- seed.sql - Sample data
-- ============================================

-- 1. STORAGE LOCATIONS (parent table)
INSERT INTO storage_locations (name, capacity) VALUES
('Main Warehouse', 500),
('Painting Studio', 150),
('Canvas Storage', 300),
('Frame Storage', 200);

-- 2. CUSTOMERS (parent table)
INSERT INTO customers (name, email, phone) VALUES
('Thandi Mokoena', 'thandi.mokoena@example.com', '0821234567'),
('Sipho Dlamini', 'sipho.dlamini@example.com', '0832345678'),
('Lerato Nkosi', 'lerato.nkosi@example.com', '0843456789'),
('Michael van der Merwe', 'michael.vdm@example.com', '0724567890'),
('Ayesha Patel', 'ayesha.patel@example.com', '0735678901'),
('Nomsa Khumalo', 'nomsa.khumalo@example.com', '0766789012'),
('Daniel Botha', 'daniel.botha@example.com', '0717890123');

-- 3. SUPPLIERS (parent table)
INSERT INTO suppliers (name, email, phone) VALUES
('Art Supplies SA', 'orders@artsuppliessa.example', '0115550101'),
('Canvas World', 'sales@canvasworld.example', '0115550102'),
('Premium Frames', 'sales@premiumframes.example', '0115550103'),
('Creative Materials', 'info@creativematerials.example', '0115550104');

-- 4. PRODUCTS (references storage_locations)
INSERT INTO products
    (location_id, name, product_type, price, stock_quantity,
     reorder_level, setup_cost, holding_cost)
VALUES
(2, 'African Sunset Painting', 'Painting', 2500.00, 12, 5, 150.00, 25.00),
(2, 'Mountain Landscape Painting', 'Painting', 3200.00, 8, 5, 180.00, 30.00),
(2, 'Abstract Blue Painting', 'Painting', 1800.00, 4, 6, 120.00, 20.00),
(2, 'Wildlife Canvas Painting', 'Painting', 2750.00, 10, 5, 160.00, 25.00),
(3, 'Small Blank Canvas', 'Canvas', 120.00, 80, 20, 50.00, 3.00),
(3, 'Medium Blank Canvas', 'Canvas', 220.00, 45, 15, 60.00, 5.00),
(3, 'Large Blank Canvas', 'Canvas', 350.00, 12, 15, 75.00, 8.00),
(4, 'Small Wooden Frame', 'Frame', 180.00, 50, 15, 45.00, 4.00),
(4, 'Medium Wooden Frame', 'Frame', 280.00, 25, 10, 55.00, 6.00),
(4, 'Large Wooden Frame', 'Frame', 420.00, 8, 10, 70.00, 9.00),
(1, 'Gold Decorative Frame', 'Frame', 650.00, 6, 8, 90.00, 12.00),
(1, 'Premium Stretched Canvas', 'Canvas', 480.00, 18, 10, 80.00, 10.00);

-- 5. ORDERS (references customers)
-- Dates are relative to the current date so the data remains useful.
INSERT INTO orders
    (customer_id, order_date, due_date, fulfilled_date, status)
VALUES
(1, DATE_SUB(NOW(), INTERVAL 5 DAY),
    DATE_ADD(CURDATE(), INTERVAL 2 DAY), NULL, 'Open'),

(2, DATE_SUB(NOW(), INTERVAL 20 DAY),
    DATE_SUB(CURDATE(), INTERVAL 10 DAY),
    DATE_SUB(CURDATE(), INTERVAL 12 DAY), 'Fulfilled'),

(3, DATE_SUB(NOW(), INTERVAL 3 DAY),
    DATE_ADD(CURDATE(), INTERVAL 7 DAY), NULL, 'Backordered'),

(4, DATE_SUB(NOW(), INTERVAL 35 DAY),
    DATE_SUB(CURDATE(), INTERVAL 25 DAY),
    DATE_SUB(CURDATE(), INTERVAL 27 DAY), 'Fulfilled'),

(5, DATE_SUB(NOW(), INTERVAL 10 DAY),
    DATE_ADD(CURDATE(), INTERVAL 5 DAY), NULL, 'Open'),

(1, DATE_SUB(NOW(), INTERVAL 60 DAY),
    DATE_SUB(CURDATE(), INTERVAL 50 DAY),
    DATE_SUB(CURDATE(), INTERVAL 52 DAY), 'Fulfilled'),

(6, DATE_SUB(NOW(), INTERVAL 15 DAY),
    DATE_SUB(CURDATE(), INTERVAL 5 DAY), NULL, 'Backordered'),

(7, DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_ADD(CURDATE(), INTERVAL 10 DAY), NULL, 'Open'),

(2, DATE_SUB(NOW(), INTERVAL 90 DAY),
    DATE_SUB(CURDATE(), INTERVAL 80 DAY),
    DATE_SUB(CURDATE(), INTERVAL 82 DAY), 'Fulfilled'),

(5, DATE_SUB(NOW(), INTERVAL 1 DAY),
    DATE_ADD(CURDATE(), INTERVAL 14 DAY), NULL, 'Open');

-- 6. ORDER ITEMS (references orders and products)
-- unit_price records the price at the time of the order.
INSERT INTO order_items
    (order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 1, 2500.00),
(1, 5, 2, 120.00),

(2, 2, 1, 3200.00),
(2, 9, 1, 280.00),

(3, 3, 2, 1800.00),
(3, 6, 3, 220.00),

(4, 4, 1, 2750.00),
(4, 11, 1, 650.00),

(5, 1, 1, 2500.00),
(5, 8, 2, 180.00),

(6, 2, 1, 3200.00),
(6, 10, 1, 420.00),

(7, 7, 4, 350.00),
(7, 9, 2, 280.00),

(8, 5, 5, 120.00),
(8, 8, 2, 180.00),

(9, 4, 2, 2750.00),
(9, 12, 1, 480.00),

(10, 3, 1, 1800.00),
(10, 11, 1, 650.00);

-- 7. PURCHASE ORDERS (references suppliers and products)
INSERT INTO purchase_orders
    (supplier_id, product_id, quantity, cost, order_date, received_date)
VALUES
(1, 5, 100, 8500.00,
    DATE_SUB(CURDATE(), INTERVAL 30 DAY),
    DATE_SUB(CURDATE(), INTERVAL 20 DAY)),

(2, 6, 60, 7800.00,
    DATE_SUB(CURDATE(), INTERVAL 20 DAY),
    DATE_SUB(CURDATE(), INTERVAL 10 DAY)),

(3, 8, 50, 6000.00,
    DATE_SUB(CURDATE(), INTERVAL 15 DAY),
    DATE_SUB(CURDATE(), INTERVAL 5 DAY)),

(3, 10, 30, 9000.00,
    DATE_SUB(CURDATE(), INTERVAL 8 DAY), NULL),

(4, 7, 40, 10000.00,
    DATE_SUB(CURDATE(), INTERVAL 5 DAY), NULL),

(1, 12, 25, 9000.00,
    DATE_SUB(CURDATE(), INTERVAL 45 DAY),
    DATE_SUB(CURDATE(), INTERVAL 35 DAY)),

(2, 9, 35, 7000.00,
    DATE_SUB(CURDATE(), INTERVAL 60 DAY),
    DATE_SUB(CURDATE(), INTERVAL 50 DAY)),

(4, 11, 20, 8000.00,
    DATE_SUB(CURDATE(), INTERVAL 2 DAY), NULL);

-- 8. PRODUCTION RECORDS (references products)
-- One row per product per month.
-- The month column stores the first day of each month.
INSERT INTO production_records
    (product_id, month, units_produced, monthly_goal,
     money_spent, value_produced)
VALUES
(1, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 2 MONTH), '%Y-%m-01'),
    8, 10, 8500.00, 20000.00),
(1, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
    10, 10, 10000.00, 25000.00),
(1, DATE_FORMAT(CURDATE(), '%Y-%m-01'),
    6, 12, 6500.00, 15000.00),

(2, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 2 MONTH), '%Y-%m-01'),
    6, 8, 9000.00, 19200.00),
(2, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
    8, 8, 11000.00, 25600.00),
(2, DATE_FORMAT(CURDATE(), '%Y-%m-01'),
    4, 8, 6000.00, 12800.00),

(3, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 2 MONTH), '%Y-%m-01'),
    10, 10, 7000.00, 18000.00),
(3, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
    9, 12, 6800.00, 16200.00),
(3, DATE_FORMAT(CURDATE(), '%Y-%m-01'),
    7, 12, 5500.00, 12600.00),

(4, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 2 MONTH), '%Y-%m-01'),
    7, 8, 8000.00, 19250.00),
(4, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
    8, 8, 9000.00, 22000.00),
(4, DATE_FORMAT(CURDATE(), '%Y-%m-01'),
    5, 10, 6000.00, 13750.00);

-- ============================================
-- END OF SEED DATA
-- ============================================
