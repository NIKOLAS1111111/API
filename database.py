import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

DB_HOST = os.getenv("db_host")
DB_PORT = os.getenv("db_port")
DB_NAME = os.getenv("db_name")
DB_USER = os.getenv("db_user")
DB_PASSWORD = os.getenv("db_password")

@contextmanager
def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    try:
        conn.set_session(readonly=True)
        yield conn
    finally:
        conn.close()

def search_products(query: str, limit: int = 5):
    sql = """
        SELECT
            pt.id,
            pt.name ->> 'en_US' AS name,
            pt.list_price,
            pt.description_sale ->> 'en_US' AS description,
            pc.complete_name As category,
            COALESCE(SUM(sq.quantity), 0) AS stock_qty
        FROM product_template pt
        LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
        LEFT JOIN stock_quant sq ON sq.product_id = pp.id
        LEFT JOIN product_category pc ON pt.categ_id = pc.id
        WHERE pt.active = true
          AND pc.complete_name !='All'
          AND (
              (pt.name ->> 'en_US') ILIKE %s
              OR pc.complete_name ILIKE %s
            )
        GROUP BY pt.id, pc.complete_name
        LIMIT %s;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            keyword = f"%{query}%"
            cur.execute(sql, (keyword, keyword, limit))
            return cur.fetchall()

def get_general_catalog_sample(limit: int = 8):
    sql = """
        SELECT
            pt.id,
            pt.name ->> 'en_US' AS name,
            pt.list_price,
            pc.complete_name AS category,
            COALESCE(SUM(sq.quantity), 0) AS stock_qty
        FROM product_template pt
        LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
        LEFT JOIN stock_quant sq ON sq.product_id = pp.id
        LEFT JOIN product_category pc ON pt.categ_id = pc.id
        WHERE pt.active = true
            AND pc.complete_name != 'All'
        GROUP BY pt.id, pc.complete_name
        ORDER BY pt.id DESC
        LIMIT %s;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            return cur.fetchall()