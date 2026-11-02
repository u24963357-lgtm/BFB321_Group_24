-- ==========================================================
-- seed.sql : sample data for Kelvic the Artist Websolution
-- Parents are inserted before children so foreign keys pass.
-- Dates use DATE_SUB / DATE_ADD so the dashboard always shows
-- recent activity, however long after setup you run it.
-- ==========================================================

-- ==========================================
-- 1. Customers (7)
-- ==========================================
INSERT INTO customers (full_name, email, phone, address, created_at) VALUES
    ('Thando Mokoena',      'thando.mokoena@example.co.za', '082 555 0101', '12 Jacaranda Street, Hatfield, Pretoria',  DATE_SUB(NOW(), INTERVAL 170 DAY)),
    ('Lerato Khumalo',      'lerato.khumalo@example.co.za', '083 555 0102', '45 Church Street, Arcadia, Pretoria',      DATE_SUB(NOW(), INTERVAL 150 DAY)),
    ('Pieter van der Merwe','pieter.vdm@example.co.za',     '084 555 0103', '8 Protea Road, Centurion',                 DATE_SUB(NOW(), INTERVAL 120 DAY)),
    ('Aisha Patel',         'aisha.patel@example.co.za',    '071 555 0104', '23 Rivonia Road, Sandton, Johannesburg',   DATE_SUB(NOW(), INTERVAL 100 DAY)),
    ('Sipho Nkosi',         'sipho.nkosi@example.co.za',    '072 555 0105', '77 Vilakazi Street, Soweto, Johannesburg', DATE_SUB(NOW(), INTERVAL 80 DAY)),
    ('Naledi Dlamini',      'naledi.dlamini@example.co.za', '073 555 0106', '5 Lynnwood Road, Menlo Park, Pretoria',    DATE_SUB(NOW(), INTERVAL 60 DAY)),
    ('Johan Botha',         'johan.botha@example.co.za',    '074 555 0107', '19 Main Street, Stellenbosch',             DATE_SUB(NOW(), INTERVAL 40 DAY));

-- ==========================================
-- 2. Suppliers (3)
-- ==========================================
INSERT INTO suppliers (name, email, phone, lead_time_days) VALUES
    ('Artisan Canvas and Frames', 'sales@artisancanvas.example.co.za', '012 555 0201', 5),
    ('Studio Paint Wholesalers',  'orders@studiopaint.example.co.za',  '011 555 0202', 7),
    ('PackRight Supplies',        'info@packright.example.co.za',      '012 555 0203', 3);

-- ==========================================
-- 3. Storage locations (2)
-- ==========================================
INSERT INTO storage_locations (name, capacity, monthly_rent) VALUES
    ('Main Studio Storeroom',   10000, 2500.00),
    ('Garage Overflow Storage',  2000,  600.00);

-- ==========================================
-- 4. Materials (8)
-- supplier_id: 1 = Canvas and Frames, 2 = Paint, 3 = Packaging
-- ==========================================
INSERT INTO materials (supplier_id, name, category, unit, unit_cost, reorder_level) VALUES
    (1, 'Stretched Canvas 60x90cm', 'Raw Material', 'each',   85.00, 20),
    (1, 'Wooden Frame 60x90cm',     'Raw Material', 'each',  120.00, 15),
    (2, 'Acrylic Paint Set (12)',   'Consumable',   'set',   210.00,  6),
    (2, 'Oil Paint Tube 200ml',     'Consumable',   'tube',   95.00, 10),
    (2, 'Brush Set (10 pieces)',    'Consumable',   'set',   150.00,  5),
    (2, 'Gloss Varnish 500ml',      'Consumable',   'bottle',130.00,  4),
    (3, 'Bubble Wrap Roll',         'Packaging',    'roll',  180.00,  3),
    (3, 'Shipping Box Large',       'Packaging',    'each',   25.00, 25);

-- ==========================================
-- 5. EOQ parameters (one row per material)
-- setup_cost = ordering cost S, holding_cost = H per unit per year
-- ==========================================
INSERT INTO eoq_parameters (material_id, setup_cost, holding_cost) VALUES
    (1, 50.00, 10.00),
    (2, 50.00,  5.00),
    (3, 50.00,  6.00),
    (4, 50.00,  4.00),
    (5, 50.00,  5.00),
    (6, 50.00,  3.00),
    (7, 50.00,  9.00),
    (8, 50.00,  1.50);

-- ==========================================
-- 6. Inventory (stock per location and material)
-- Frames (12 <= 15) and Brush Sets (3 <= 5) are below their reorder level
-- ==========================================
INSERT INTO inventory (location_id, material_id, quantity_on_hand) VALUES
    (1, 1, 45),
    (2, 1, 15),
    (1, 2, 12),
    (1, 3, 10),
    (1, 4, 22),
    (1, 5,  3),
    (1, 6,  8),
    (2, 7,  6),
    (2, 8, 60);

-- ==========================================
-- 7. Artworks (10)
-- ==========================================
INSERT INTO artworks (title, status, hours_worked, hourly_rate, allocated_rent, selling_price, completed_date) VALUES
    ('Sunset over the Magaliesberg', 'Sold',        12.50, 100.00, 150.00, 2800.00, DATE_SUB(CURDATE(), INTERVAL 150 DAY)),
    ('Jacaranda Avenue',             'Sold',         9.00, 100.00, 150.00, 2100.00, DATE_SUB(CURDATE(), INTERVAL 110 DAY)),
    ('Township Rhythm',              'Sold',        15.00, 100.00, 150.00, 3400.00, DATE_SUB(CURDATE(), INTERVAL 90 DAY)),
    ('Savanna Dusk',                 'Sold',        11.00, 100.00, 150.00, 2500.00, DATE_SUB(CURDATE(), INTERVAL 70 DAY)),
    ('Blue Wildebeest',              'Sold',         8.00, 100.00, 150.00, 1900.00, DATE_SUB(CURDATE(), INTERVAL 50 DAY)),
    ('Ubuntu Portrait',              'Completed',   18.00, 100.00, 150.00, 3800.00, DATE_SUB(CURDATE(), INTERVAL 12 DAY)),
    ('Highveld Storm',               'Completed',   10.00, 100.00, 150.00, 2300.00, DATE_SUB(CURDATE(), INTERVAL 6 DAY)),
    ('Pretoria Rooftops',            'In Progress',  6.00, 100.00, 150.00, 2600.00, NULL),
    ('Protea Bloom',                 'In Progress',  4.50, 100.00, 150.00, 1700.00, NULL),
    ('Morning Market',               'Sold',         7.00, 100.00, 150.00, 1800.00, DATE_SUB(CURDATE(), INTERVAL 170 DAY));

-- ==========================================
-- 8. Artwork materials (bill of materials per artwork)
-- unit_cost is a snapshot of the material cost at the time
-- Acrylic works: 1,3,5,7,9   Oil works: 2,4,6,8,10
-- ==========================================
INSERT INTO artwork_materials (artwork_id, material_id, quantity_used, unit_cost) VALUES
    (1, 1, 1.00,  85.00),
    (1, 2, 1.00, 120.00),
    (1, 3, 0.25, 210.00),
    (1, 5, 0.10, 150.00),
    (2, 1, 1.00,  85.00),
    (2, 2, 1.00, 120.00),
    (2, 4, 3.00,  95.00),
    (3, 1, 1.00,  85.00),
    (3, 2, 1.00, 120.00),
    (3, 3, 0.25, 210.00),
    (3, 5, 0.10, 150.00),
    (4, 1, 1.00,  85.00),
    (4, 2, 1.00, 120.00),
    (4, 4, 3.00,  95.00),
    (5, 1, 1.00,  85.00),
    (5, 2, 1.00, 120.00),
    (5, 3, 0.25, 210.00),
    (6, 1, 1.00,  85.00),
    (6, 2, 1.00, 120.00),
    (6, 4, 4.00,  95.00),
    (6, 5, 0.10, 150.00),
    (7, 1, 1.00,  85.00),
    (7, 2, 1.00, 120.00),
    (7, 3, 0.25, 210.00),
    (7, 5, 0.10, 150.00),
    (8, 1, 1.00,  85.00),
    (8, 2, 1.00, 120.00),
    (8, 4, 3.00,  95.00),
    (9, 1, 1.00,  85.00),
    (9, 2, 1.00, 120.00),
    (9, 3, 0.25, 210.00),
    (10, 1, 1.00,  85.00),
    (10, 2, 1.00, 120.00),
    (10, 4, 2.00,  95.00),
    (10, 5, 0.10, 150.00);

-- ==========================================
-- 9. Customer orders (10)
-- total_amount equals the sum of that order's items
-- 6 Completed, 2 Pending, 1 Processing, 1 Cancelled
-- ==========================================
INSERT INTO customer_orders (customer_id, order_date, due_date, fulfilled_date, status, total_amount) VALUES
    (1, DATE_SUB(CURDATE(), INTERVAL 140 DAY), DATE_SUB(CURDATE(), INTERVAL 125 DAY), DATE_SUB(CURDATE(), INTERVAL 126 DAY), 'Completed',  1800.00),
    (2, DATE_SUB(CURDATE(), INTERVAL 75 DAY),  DATE_SUB(CURDATE(), INTERVAL 60 DAY),  DATE_SUB(CURDATE(), INTERVAL 62 DAY),  'Completed',  2800.00),
    (3, DATE_SUB(CURDATE(), INTERVAL 60 DAY),  DATE_SUB(CURDATE(), INTERVAL 45 DAY),  DATE_SUB(CURDATE(), INTERVAL 47 DAY),  'Completed',  2100.00),
    (4, DATE_SUB(CURDATE(), INTERVAL 50 DAY),  DATE_SUB(CURDATE(), INTERVAL 35 DAY),  DATE_SUB(CURDATE(), INTERVAL 36 DAY),  'Completed',  3400.00),
    (5, DATE_SUB(CURDATE(), INTERVAL 35 DAY),  DATE_SUB(CURDATE(), INTERVAL 20 DAY),  DATE_SUB(CURDATE(), INTERVAL 22 DAY),  'Completed',  2500.00),
    (6, DATE_SUB(CURDATE(), INTERVAL 25 DAY),  DATE_SUB(CURDATE(), INTERVAL 10 DAY),  DATE_SUB(CURDATE(), INTERVAL 11 DAY),  'Completed',  1900.00),
    (7, DATE_SUB(CURDATE(), INTERVAL 10 DAY),  DATE_ADD(CURDATE(), INTERVAL 5 DAY),   NULL,                                  'Processing', 3800.00),
    (1, DATE_SUB(CURDATE(), INTERVAL 4 DAY),   DATE_ADD(CURDATE(), INTERVAL 10 DAY),  NULL,                                  'Pending',    2300.00),
    (3, DATE_SUB(CURDATE(), INTERVAL 2 DAY),   DATE_ADD(CURDATE(), INTERVAL 30 DAY),  NULL,                                  'Pending',    2600.00),
    (4, DATE_SUB(CURDATE(), INTERVAL 15 DAY),  DATE_ADD(CURDATE(), INTERVAL 15 DAY),  NULL,                                  'Cancelled',  1700.00);

-- ==========================================
-- 10. Order items (one artwork per order)
-- Order 9 is for Pretoria Rooftops, still in progress, so it is backordered
-- ==========================================
INSERT INTO order_items (order_id, artwork_id, quantity, backordered_qty, unit_price) VALUES
    (1,  10, 1, 0, 1800.00),
    (2,   1, 1, 0, 2800.00),
    (3,   2, 1, 0, 2100.00),
    (4,   3, 1, 0, 3400.00),
    (5,   4, 1, 0, 2500.00),
    (6,   5, 1, 0, 1900.00),
    (7,   6, 1, 0, 3800.00),
    (8,   7, 1, 0, 2300.00),
    (9,   8, 1, 1, 2600.00),
    (10,  9, 1, 0, 1700.00);

-- ==========================================
-- 11. Purchase orders (4)
-- ==========================================
INSERT INTO purchase_orders (supplier_id, order_date, expected_date, received_date, status) VALUES
    (1, DATE_SUB(CURDATE(), INTERVAL 60 DAY), DATE_SUB(CURDATE(), INTERVAL 55 DAY), DATE_SUB(CURDATE(), INTERVAL 56 DAY), 'Received'),
    (2, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 23 DAY), DATE_SUB(CURDATE(), INTERVAL 24 DAY), 'Received'),
    (3, DATE_SUB(CURDATE(), INTERVAL 12 DAY), DATE_SUB(CURDATE(), INTERVAL 9 DAY),  DATE_SUB(CURDATE(), INTERVAL 10 DAY), 'Received'),
    (1, DATE_SUB(CURDATE(), INTERVAL 3 DAY),  DATE_ADD(CURDATE(), INTERVAL 2 DAY),  NULL,                                'Ordered');

-- ==========================================
-- 12. Purchase order items
-- ==========================================
INSERT INTO purchase_order_items (po_id, material_id, quantity, unit_cost) VALUES
    (1, 1, 30,  85.00),
    (1, 2, 20, 120.00),
    (2, 3,  6, 210.00),
    (2, 4, 12,  95.00),
    (2, 5,  4, 150.00),
    (3, 7,  4, 180.00),
    (3, 8, 50,  25.00),
    (4, 2, 15, 120.00),
    (4, 1, 10,  85.00);