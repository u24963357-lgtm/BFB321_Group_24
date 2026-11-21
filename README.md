# Kelvic-the-Artist-Webpage
Web page for BFB 321
Project Title and  Description:
Kelvic The Artist Websolution
An enterprise system for small independant artists without business background and no money for large ERP systems like SAP. We are using the small artist Kelvic the artist as a base to make this web solution.


| Group names |  student numbers|
|-------------|----------------|
|Siviwe Vilane | u24693180 |
|Kelley Thlamo | u24963357 |
|Snethemba Ndlovu | u24990150 |
|Kelebone Kgalaeng | u16068221 |


## Features
| Page |  What it does |
|-------------|----------------|
| overview/ | The Web solution woks as an ERP system as in connects the business operations to one database. It has modules such as production, logistics, orders, orders and storage. |
| /login | The login page aunthenticates if the user is the admin meant to access the web solution, it uses mySQL tables. |
| /index | The welcome page. Summarises data shown in each and every page and provides current status. |
| /production | Tracks the artists studio operations. It uses the database to show data such as monthly goals and cost efficiency |
| /logistics | The shipping manager. Uses EOQ and EPQ to provide insights to the user. |
| /orders | Handles demand and fulfilment. Shows historic demand and fulfilment and also takes new orders. |
| /orders/<id> | It allows the user to see a more detailed view of the individual order. |
| /storage | The storage of the business. Uses the EPQ/EOQ formulas to show the status of an SKU. |
| / |  |

All pages use the same data base and all the tables and KPI's are updated by calculated values from the database.

## Tech stack

| Stack name |  | |
|-------------|-------------|------------|
| Python & flask| Werkzeug Security | Jinja 2  |
| MySQL | PyMySQL | Aiven | 
| HTML 5 | CSS | Javascript | 
| Git/GitHub |  |  | 

## Project structure
```text
├── app.py              # Flask routes, API endpoints, and error handling
├── models.py           # SQL queries, business logic, and supply chain math
├── db.py               # MySQL connection pool and query helpers
├── init_db.py          # Script to create tables and load seed data
├── schema.sql          # CREATE TABLE statements
├── seed.sql            # Sample data for demo
├── requirements.txt    # Python package dependencies
├── .env.example        # Template for environment variables
├── templates/          # Jinja2 HTML templates
├── static/css/         # Stylesheets
```
## Data Structure

### ERD

```mermaid
erDiagram
    STORAGE_LOCATIONS ||--o{ PRODUCTS : "stores"
    CUSTOMERS         ||--o{ ORDERS   : "places"
    ORDERS            ||--o{ ORDER_ITEMS : "contains"
    PRODUCTS          ||--o{ ORDER_ITEMS : "appears in"
    SUPPLIERS         ||--o{ PURCHASE_ORDERS : "supplies"
    PRODUCTS          ||--o{ PURCHASE_ORDERS : "restocked by"
    PRODUCTS          ||--o{ PRODUCTION_RECORDS : "manufactured in"

    STORAGE_LOCATIONS {
        int id PK
        varchar name
        int capacity
    }
    PRODUCTS {
        int id PK
        int location_id FK
        varchar name
        varchar product_type
        decimal price
        int stock_quantity
        int reorder_level
        decimal setup_cost
        decimal holding_cost
        timestamp created_at
    }
    CUSTOMERS {
        int id PK
        varchar name
        varchar email
        varchar phone
        timestamp created_at
    }
    ORDERS {
        int id PK
        int customer_id FK
        datetime order_date
        date due_date
        date fulfilled_date
        enum status
        boolean stock_reserved
    }
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
    }
    SUPPLIERS {
        int id PK
        varchar name
        varchar email
        varchar phone
    }
    PURCHASE_ORDERS {
        int id PK
        int supplier_id FK
        int product_id FK
        int quantity
        decimal cost
        date order_date
        date received_date
    }
    PRODUCTION_RECORDS {
        int id PK
        int product_id FK
        date month
        int units_produced
        int monthly_goal
        decimal money_spent
        decimal value_produced
    }
    SHIPMENTS {
        varchar id PK
        varchar origin
        varchar destination
        varchar status
        varchar arrival_date
        boolean is_past
    }
    USERS {
        int id PK
        varchar username
        varchar password_hash
    }
```

### Schema Details

**`storage_locations`**: Physical locations where stock is kept (Home, Commercial storage, Painting Studio).
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| name | VARCHAR(80) | required, unique |
| capacity | INT | required, `CHECK (capacity > 0)` |

**`products`**: What the business sells (paintings, canvases, frames).
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| location_id | INT | required, foreign key → `storage_locations.id` |
| name | VARCHAR(120) | required |
| product_type | VARCHAR(20) | required, `CHECK` (Painting, Canvas, Frame) |
| price | DECIMAL(10,2) | required, `CHECK (price >= 0)` |
| stock_quantity | INT | default 0, `CHECK (stock_quantity >= 0)` |
| reorder_level | INT | default 10, `CHECK (reorder_level >= 0)` |
| setup_cost | DECIMAL(10,2) | default 50.00 (used for EOQ calculations) |
| holding_cost | DECIMAL(10,2) | default 5.00 (used for EOQ calculations) |
| created_at | TIMESTAMP | defaults to current time |

**`customers`**: Who buys from the business.
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| name | VARCHAR(120) | required |
| email | VARCHAR(160) | required, unique |
| phone | VARCHAR(30) | optional |
| created_at | TIMESTAMP | defaults to current time |

**`orders`**: Customer orders (the header record). 
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| customer_id | INT | required, foreign key → `customers.id` |
| order_date | DATETIME | defaults to current time |
| due_date | DATE | optional |
| fulfilled_date | DATE | optional |
| status | ENUM | 'Open', 'Fulfilled', 'Backordered', 'Cancelled' |
| stock_reserved | BOOLEAN | flags if inventory has been deducted for this order |

**`order_items`**: The line items inside an order.
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| order_id | INT | required, foreign key → `orders.id` |
| product_id | INT | required, foreign key → `products.id` |
| quantity | INT | required, `CHECK (quantity > 0)` |
| unit_price | DECIMAL(10,2) | copies price at time of order |

**`suppliers`**: Who the business buys raw materials from.
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| name | VARCHAR(120) | required |
| email | VARCHAR(160) | optional |
| phone | VARCHAR(30) | optional |

**`purchase_orders`**: Restocking history from suppliers.
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| supplier_id | INT | required, foreign key → `suppliers.id` |
| product_id | INT | required, foreign key → `products.id` |
| quantity | INT | required, `CHECK (quantity > 0)` |
| cost | DECIMAL(10,2) | required, `CHECK (cost >= 0)` |
| order_date | DATE | required |
| received_date | DATE | optional (NULL until delivered) |

**`production_records`**: Monthly manufacturing data (used for efficiency/EPQ).
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| product_id | INT | required, foreign key → `products.id` |
| month | DATE | stored as 1st of month (e.g., 2026-10-01) |
| units_produced | INT | default 0 |
| monthly_goal | INT | default 0 |
| money_spent | DECIMAL(10,2)| default 0 |
| value_produced | DECIMAL(10,2)| default 0 |

**`shipments`**: Outbound freight tracking for the Logistics page.
| Column | Type | Rules |
|---|---|---|
| id | VARCHAR(50) | primary key (e.g., "SHP-24908") |
| origin | VARCHAR(120) | required |
| destination | VARCHAR(120) | required |
| status | VARCHAR(50) | required |
| arrival_date | VARCHAR(50) | required (formatted string) |
| is_past | BOOLEAN | flags if the shipment is in history |

**`users`**: System access accounts for management.
| Column | Type | Rules |
|---|---|---|
| id | INT | primary key, auto increment |
| username | VARCHAR(50) | required, unique |
| password_hash | VARCHAR(255)| required (Werkzeug PBKDF2 hash) |


## How to Run

### Prerequisites
* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)
* Access to a MySQL Database (This project uses [Aiven Cloud MySQL](https://aiven.io/), but a local MySQL server will also work).

### Step 1: Clone the Repository
Open your terminal and clone the project:
```bash
git clone    git clone [https://github.com/u24963357-lgtm/BFB321_Group_24
cd BFB321_Group_24
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
*(You will know the environment is active when your terminal prompt starts with `(venv)`).*

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
1. Copy the template file to create your actual environment file:
   ```bash
   cp .env.example .env
   ```
2. Open the newly created `.env` file and fill in your database credentials:
   ```ini
   DB_HOST=your-database-host.aivencloud.com
   DB_PORT=26525
   DB_USER=avnadmin
   DB_PASSWORD=your-secure-password
   DB_NAME=defaultdb
   FLASK_SECRET_KEY=any-random-string-here
   ```

### Step 5: Initialize the Database
Run the initialization script to create tables, constraints, and load the sample data:
```bash
python init_db.py --reset
```

### Step 6: Run the Application
```bash
python app.py
```

### Step 7: Access the System
Open your web browser and navigate to:
**http://127.0.0.1:5000/**

### Step 8: Log In
Use the following test credentials:

| Username | Password |
| :--- | :--- |
| `adminA` | `Kelvic_2026A` |
| `adminB` | `Kelvic_2026B` |

---

## REST API Documentation

The application includes a RESTful JSON API layer for integration with external systems. You can test these endpoints using Postman or `curl`.

| Method | Endpoint | Description | Request Body (JSON) or Query Params |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/products` | Returns a paginated list of products. | `?limit=10&offset=0&category=Canvas` |
| **GET** | `/api/orders/<id>` | Returns details for a specific order. | None |
| **POST** | `/api/orders` | Creates a new order and deducts stock. | `{"customer_id": 1, "product_id": 2, "quantity": 5}` |
| **PUT** | `/api/products/<id>` | Updates the price of a specific product. | `{"price": 1500.00}` |

*Note: API routes return appropriate HTTP status codes (200 OK, 201 Created, 400 Bad Request, 404 Not Found) and errors are logged to `app.log`.*

---


