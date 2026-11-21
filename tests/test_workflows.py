import unittest
from unittest.mock import patch

import models


class FakeCursor:
    def __init__(self):
        self.statements = []
        self.row = None
        self.rows = []
        self.lastrowid = 23

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def execute(self, sql, params=()):
        self.statements.append((" ".join(sql.split()), params))
        if sql.startswith("SELECT status, stock_reserved"):
            self.row = {"status": "Open", "stock_reserved": True}
        elif sql.startswith("SELECT product_id, SUM(quantity)"):
            self.rows = [{"product_id": 8, "quantity": 2}]

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class FakeDatabase:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class WorkflowTests(unittest.TestCase):
    def test_factory_painting_goal_uses_non_cancelled_sales_orders(self):
        today = models.date.today()
        production_records = [{
            "id": 1, "product_id": 8, "name": "Painting",
            "product_type": "Painting", "month": today.replace(day=1),
            "units_produced": 4, "monthly_goal": 99,
            "money_spent": 10, "value_produced": 20,
        }]
        monthly_order_goals = [{
            "month": today.month, "quantity": 7,
        }]
        with (
            patch.object(models, "get_production_data", return_value=production_records),
            patch.object(
                models,
                "query_all",
                side_effect=[
                    monthly_order_goals,
                    [{"id": 8, "name": "Painting"}],
                    [{"id": 1, "name": "Studio"}],
                ],
            ) as query_all,
        ):
            data = models.get_production_page_data()

        self.assertEqual(data["monthly_goal"][today.month - 1], 7)
        self.assertEqual(data["num_in_stock"][today.month - 1], 4)
        order_query = query_all.call_args_list[0].args[0]
        self.assertIn("o.status <> 'Cancelled'", order_query)
        self.assertIn("p.product_type = 'Painting'", order_query)

    def test_new_factory_piece_and_production_record_are_created_together(self):
        db = FakeDatabase()
        with patch.object(models, "get_db", return_value=db):
            result = models.create_production_piece(
                "New painting", 2, 125.0, models.date(2026, 11, 12),
                3, 5, 40.0, 90.0,
            )

        self.assertEqual(result, (True, "New painting and production record added."))
        self.assertEqual(db.commits, 1)
        statements = db.cursor_instance.statements
        self.assertEqual(len(statements), 2)
        self.assertIn("stock_quantity, price", statements[0][0])
        self.assertEqual(statements[0][1], ("New painting", 2, 3, 125.0))
        self.assertIn("INSERT INTO production_records", statements[1][0])
        self.assertEqual(statements[1][1][0], 23)
        self.assertEqual(statements[1][1][1], models.date(2026, 11, 1))

    def test_new_factory_piece_rolls_back_if_production_record_cannot_be_saved(self):
        db = FakeDatabase()
        cursor = db.cursor_instance
        execute = cursor.execute

        def fail_on_production_record(sql, params=()):
            if sql.startswith("INSERT INTO production_records"):
                raise models.pymysql.err.IntegrityError("invalid production record")
            execute(sql, params)

        with (
            patch.object(cursor, "execute", side_effect=fail_on_production_record),
            patch.object(models, "get_db", return_value=db),
        ):
            success, _ = models.create_production_piece(
                "New painting", 2, 125.0, models.date(2026, 11, 12),
                3, 5, 40.0, 90.0,
            )

        self.assertFalse(success)
        self.assertEqual(db.commits, 0)
        self.assertEqual(db.rollbacks, 1)

    def test_inventory_insert_uses_generated_sku_not_missing_database_column(self):
        with patch.object(models, "execute") as execute:
            result = models.add_inventory("New canvas", "Canvas", 1, 4, 20.0, 2)

        self.assertTrue(result[0])
        sql = execute.call_args.args[0]
        self.assertIn("product_type", sql)
        self.assertNotIn("sku", sql.lower())

    def test_referenced_inventory_cannot_be_deleted(self):
        with (
            patch.object(
                models,
                "query_one",
                return_value={"ordered": 1, "purchased": 0, "produced": 0},
            ),
            patch.object(models, "execute") as execute,
        ):
            result = models.delete_inventory(8)

        self.assertFalse(result[0])
        execute.assert_not_called()

    def test_logistics_quantities_use_recorded_demand_and_production(self):
        products = [
            {
                "id": 1, "name": "Canvas", "product_type": "Canvas",
                "setup_cost": 50, "holding_cost": 10, "annual_demand": 120,
                "production_units": 0, "production_months": 0,
            },
            {
                "id": 2, "name": "Painting", "product_type": "Painting",
                "setup_cost": 20, "holding_cost": 5, "annual_demand": 50,
                "production_units": 60, "production_months": 6,
            },
        ]
        summary = {
            "total": 2, "active": 1, "delayed_count": 1, "delivered": 1,
        }
        with (
            patch.object(models, "query_one", return_value=summary),
            patch.object(models, "query_all", side_effect=[products, []]),
        ):
            data = models.get_logistics_page_data()

        self.assertEqual(data["eoq_items"][0]["eoq"], 10)
        self.assertEqual(data["epq_items"][1]["epq"], 8)
        self.assertEqual(data["delayed_shipments"], 1)

    def test_cancelling_reserved_order_restores_stock_transactionally(self):
        db = FakeDatabase()
        with patch.object(models, "get_db", return_value=db):
            success, _ = models.update_order_status(17, "Cancelled")

        self.assertTrue(success)
        self.assertEqual(db.commits, 1)
        self.assertEqual(db.rollbacks, 0)
        updates = db.cursor_instance.statements
        self.assertIn(
            ("UPDATE products SET stock_quantity = stock_quantity + %s WHERE id = %s", (2, 8)),
            updates,
        )
        self.assertIn(
            (
                "UPDATE orders SET status = %s, fulfilled_date = CASE WHEN %s = 'Fulfilled' "
                "THEN CURDATE() ELSE NULL END, stock_reserved = %s WHERE id = %s",
                ("Cancelled", "Cancelled", False, 17),
            ),
            updates,
        )


if __name__ == "__main__":
    unittest.main()
