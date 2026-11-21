import os
import sys

from db import BASE_DIR, connect

# Children before parents (orders before clients - a table with a foreign key
# must be dropped BEFORE the table it points to)
TABLES_IN_DROP_ORDER = [
    "production_records",
    "purchase_orders",
    "order_items",
    "orders",
    "products",
    "suppliers",
    "customers",
    "storage_locations",
    "shipments",
    "users"
]


def read_statements(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines()
                 if not ln.strip().startswith("--")]
    return [s.strip()
            for s in "\n".join(lines).split(";")
            if s.strip()]




def main(reset=False):
    conn = connect()
    with conn:
        with conn.cursor() as cur:
            if reset:
                print("Dropping existing tables...")
                for table in TABLES_IN_DROP_ORDER:
                    cur.execute(f"DROP TABLE IF EXISTS {table}")

            print("Creating tables from schema.sql ...")
            for stmt in read_statements("schema.sql"):
                cur.execute(stmt)

            cur.execute(
                "ALTER TABLE orders MODIFY COLUMN status "
                "ENUM('Open', 'Fulfilled', 'Backordered', 'Cancelled') "
                "NOT NULL DEFAULT 'Open'"
            )
            cur.execute("""
                SELECT CONSTRAINT_NAME
                FROM information_schema.TABLE_CONSTRAINTS
                WHERE CONSTRAINT_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'orders'
                  AND CONSTRAINT_NAME = 'chk_orders_status'
            """)
            if cur.fetchone():
                cur.execute("ALTER TABLE orders DROP CHECK chk_orders_status")
            cur.execute("SHOW COLUMNS FROM orders LIKE 'stock_reserved'")
            if not cur.fetchone():
                cur.execute(
                    "ALTER TABLE orders ADD COLUMN stock_reserved "
                    "BOOLEAN NOT NULL DEFAULT FALSE"
                )

            cur.execute("SELECT COUNT(*) AS n FROM products")
            if cur.fetchone()["n"] == 0:
                print("Loading sample data from seed.sql ...")
                for stmt in read_statements("seed.sql"):
                    cur.execute(stmt)
            else:
                print("Products already exist - "
                      "sample data NOT loaded")

            user_seed = next(
                (
                    stmt for stmt in read_statements("seed.sql")
                    if stmt.startswith("INSERT INTO users ")
                ),
                None,
            )
            if user_seed is None:
                raise RuntimeError("seed.sql does not contain demo user accounts.")
            cur.execute(user_seed.replace("INSERT INTO users ", "INSERT IGNORE INTO users ", 1))

            for table in reversed(TABLES_IN_DROP_ORDER):
                cur.execute(f"SELECT COUNT(*) AS n FROM {table}")
                print(f"  {table:<20}{cur.fetchone()['n']} rows")
        conn.commit()
    print("Done. Now run:  python app.py")


if __name__ == "__main__":
    main(reset="--reset" in sys.argv)