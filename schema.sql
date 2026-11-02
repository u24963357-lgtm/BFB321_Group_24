-- Parents are created before children so the foreign keys always work
 
-- STORAGE: where stock is kept (capacity is used for utilisation)
CREATE TABLE IF NOT EXISTS storage_locations (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(80) NOT NULL UNIQUE,
    capacity  INT         NOT NULL,
    CONSTRAINT chk_locations_capacity CHECK (capacity > 0)
);
 
-- PRODUCTS: paintings, canvases and frames
CREATE TABLE IF NOT EXISTS products (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    location_id     INT            NOT NULL,
    name            VARCHAR(120)   NOT NULL,
    product_type    VARCHAR(20)    NOT NULL,
    price           DECIMAL(10,2)  NOT NULL,
    stock_quantity  INT            NOT NULL DEFAULT 0,
    reorder_level   INT            NOT NULL DEFAULT 10,
    setup_cost      DECIMAL(10,2)  NOT NULL DEFAULT 50.00,
    holding_cost    DECIMAL(10,2)  NOT NULL DEFAULT 5.00,
    created_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_location
        FOREIGN KEY (location_id) REFERENCES storage_locations (id),
    CONSTRAINT chk_products_type
        CHECK (product_type IN ('Painting', 'Canvas', 'Frame')),
    CONSTRAINT chk_products_price   CHECK (price >= 0),
    CONSTRAINT chk_products_stock   CHECK (stock_quantity >= 0),
    CONSTRAINT chk_products_reorder CHECK (reorder_level >= 0),
    CONSTRAINT chk_products_setup   CHECK (setup_cost >= 0),
    CONSTRAINT chk_products_holding CHECK (holding_cost >= 0)
);
 
-- CUSTOMERS: who buys from Kelvic
CREATE TABLE IF NOT EXISTS customers (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL,
    email       VARCHAR(160) NOT NULL UNIQUE,
    phone       VARCHAR(30)  NULL,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
 
-- ORDERS: one row per customer order (the items are in order_items)
-- fulfilled_date stays NULL until the order is delivered
CREATE TABLE IF NOT EXISTS orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT          NOT NULL,
    order_date      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date        DATE         NULL,
    fulfilled_date  DATE         NULL,
    status          enum('Open', 'Fulfilled', 'Backordered') NOT NULL DEFAULT 'Open',
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers (id),
    CONSTRAINT chk_orders_status
        CHECK (status IN ('Open', 'Fulfilled', 'Backordered'))
);
 
-- ORDER_ITEMS: link table between orders and products
-- unit_price copies the product price AT THE TIME of the order
CREATE TABLE IF NOT EXISTS order_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    order_id    INT            NOT NULL,
    product_id  INT            NOT NULL,
    quantity    INT            NOT NULL,
    unit_price  DECIMAL(10,2)  NOT NULL,
    CONSTRAINT fk_items_order
        FOREIGN KEY (order_id) REFERENCES orders (id),
    CONSTRAINT fk_items_product
        FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT chk_items_quantity CHECK (quantity > 0),
    CONSTRAINT chk_items_price    CHECK (unit_price >= 0)
);
 
-- SUPPLIERS: who Kelvic buys canvases and frames from
CREATE TABLE IF NOT EXISTS suppliers (
    id     INT AUTO_INCREMENT PRIMARY KEY,
    name   VARCHAR(120) NOT NULL,
    email  VARCHAR(160) NULL,
    phone  VARCHAR(30)  NULL
);
 
-- PURCHASE_ORDERS: restocking from a supplier
-- received_date stays NULL until the stock arrives
CREATE TABLE IF NOT EXISTS purchase_orders (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id    INT            NOT NULL,
    product_id     INT            NOT NULL,
    quantity       INT            NOT NULL,
    cost           DECIMAL(10,2)  NOT NULL,
    order_date     DATE           NOT NULL,
    received_date  DATE           NULL,
    CONSTRAINT fk_po_supplier
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
    CONSTRAINT fk_po_product
        FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT chk_po_quantity CHECK (quantity > 0),
    CONSTRAINT chk_po_cost     CHECK (cost >= 0)
);
 
-- PRODUCTION_RECORDS: one row per product per month
-- store the first day of the month in month (for example 2026-10-01)
-- efficiency = value_produced / money_spent is calculated, not stored
CREATE TABLE IF NOT EXISTS production_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    product_id      INT            NOT NULL,
    month           DATE           NOT NULL,
    units_produced  INT            NOT NULL DEFAULT 0,
    monthly_goal    INT            NOT NULL DEFAULT 0,
    money_spent     DECIMAL(10,2)  NOT NULL DEFAULT 0,
    value_produced  DECIMAL(10,2)  NOT NULL DEFAULT 0,
    CONSTRAINT fk_production_product
        FOREIGN KEY (product_id) REFERENCES products (id),
    CONSTRAINT uq_production_month UNIQUE (product_id, month),
    CONSTRAINT chk_production_units CHECK (units_produced >= 0),
    CONSTRAINT chk_production_goal  CHECK (monthly_goal >= 0),
    CONSTRAINT chk_production_spent CHECK (money_spent >= 0),
    CONSTRAINT chk_production_value CHECK (value_produced >= 0)
);