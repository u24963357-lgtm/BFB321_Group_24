# import os

# import pymysql
# import pymysql.cursors
# from dotenv import load_dotenv
# from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))  # DB_HOST, DB_PASSWORD, ... from .env


# def connect():
#     """Open a new connection using the settings in .env."""
#     options = dict(
#         host=os.getenv("DB_HOST", "DB_HOST=your-service-name-your-project.a.aivencloud.com"),
#         port=int(os.getenv("DB_PORT", "26525")),
#         user=os.getenv("DB_USER", "avnadmin"),
#         password=os.getenv("DB_PASSWORD", ""),
#         database=os.getenv("DB_NAME", "defaultdb"),
#         charset="utf8mb4",
#         cursorclass=pymysql.cursors.DictCursor,  # rows come back as dictionaries
#         autocommit=False,                        # nothing is saved until commit()
#         connect_timeout=15,
#     )

#     # Optional: verify the server with a CA certificate (only when DB_SSL_CA is set).
#     ca = os.getenv("DB_SSL_CA", "").strip()
#     if ca:
#         ca_path = ca if os.path.isabs(ca) else os.path.join(BASE_DIR, ca)
#         if not os.path.exists(ca_path):
#             raise FileNotFoundError(
#                 f"DB_SSL_CA points to '{ca}' but that file was not found. "
#                 "Download the CA certificate from Aiven and save it as ca.pem next to app.py."
#             )
#         options["ssl_ca"] = ca_path
#         options["ssl_verify_cert"] = True
#         options["ssl_verify_identity"] = (
#             os.getenv("DB_SSL_VERIFY_HOST", "false").lower() == "true")

#     return pymysql.connect(**options)



# def get_db():
#     """Open the connection the first time it is needed in this request."""
#     if "db" not in g:
#         g.db = connect()
#     return g.db


# def close_db(exception=None):
#     db = g.pop("db", None)
#     if db is not None:
#         db.close()


# def init_app(app):
#     app.teardown_appcontext(close_db)



# def query_all(sql, params=None):
#     """SELECT many rows -> list of dictionaries."""
#     with get_db().cursor() as cur:
#         cur.execute(sql, params or ())
#         return cur.fetchall()


# def query_one(sql, params=None):
#     """SELECT the first row -> one dictionary (or None)."""
#     with get_db().cursor() as cur:
#         cur.execute(sql, params or ())
#         return cur.fetchone()


# def execute(sql, params=None):
#     """INSERT / UPDATE / DELETE: run it, commit, return the new row id."""
#     db = get_db()
#     with db.cursor() as cur:
#         cur.execute(sql, params or ())
#         new_id = cur.lastrowid
#     db.commit()
#     return new_id
