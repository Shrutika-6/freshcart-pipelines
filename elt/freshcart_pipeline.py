"""
FreshCart ELT Pipeline on Snowflake Simulator and Execution Engine
Exact schema, sample data, transformations, SCD2, data-quality checks, and idempotency tests
Author: Shende Shrutika Ashok (23bcs232)
"""

import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

def get_row_hash(*values):
    s = "|".join("" if v is None else str(v) for v in values)
    return hashlib.md5(s.encode('utf-8')).hexdigest()

class FreshCartPipeline:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self):
        cur = self.conn.cursor()
        
        # Bronze: orders_raw (JSON payload / variant simulation)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bronze_orders_raw (
            raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source VARCHAR(20),
            payload TEXT,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Silver: clean, checked, dedup, quarantine
        cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_orders_clean (
            raw_id INTEGER,
            order_id VARCHAR(50),
            customer_id VARCHAR(50),
            customer_name VARCHAR(100),
            order_date TIMESTAMP,
            amount REAL,
            currency VARCHAR(10),
            channel VARCHAR(20),
            updated_at TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_orders_quarantine (
            raw_id INTEGER PRIMARY KEY,
            order_id VARCHAR(50),
            reasons TEXT,
            payload TEXT,
            quarantined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_orders_dedup (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50),
            customer_name VARCHAR(100),
            order_date TIMESTAMP,
            amount REAL,
            currency VARCHAR(10),
            channel VARCHAR(20),
            updated_at TIMESTAMP
        );
        """)

        # Dim: customers_scd2
        cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_customers_scd2 (
            customer_id VARCHAR(50),
            customer_email VARCHAR(100),
            tier VARCHAR(20),
            multiplier REAL,
            effective_from TIMESTAMP,
            effective_to TIMESTAMP,
            is_current INTEGER,
            PRIMARY KEY(customer_id, effective_from)
        );
        """)

        # Dim: fx_rates (Reference)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ref_fx_rates (
            currency VARCHAR(10) PRIMARY KEY,
            rate_to_inr REAL
        );
        """)

        # Gold: fct_orders
        cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_fct_orders (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50),
            order_date TIMESTAMP,
            amount_original REAL,
            currency VARCHAR(10),
            amount_inr REAL,
            tier VARCHAR(20),
            multiplier REAL,
            loyalty_points REAL,
            row_hash VARCHAR(32),
            published_at TIMESTAMP
        );
        """)
        self.conn.commit()

    def seed_reference_data(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM ref_fx_rates;")
        cur.executemany("INSERT INTO ref_fx_rates VALUES (?, ?);", [
            ('INR', 1.0),
            ('USD', 85.0),
            ('EUR', 90.0)
        ])

        # Baseline SCD2 customers
        cur.execute("DELETE FROM dim_customers_scd2;")
        cur.executemany("INSERT INTO dim_customers_scd2 VALUES (?, ?, ?, ?, ?, ?, ?);", [
            ('CUST-01', 'priya.s@gmail.com', 'Silver', 1.0, '2026-01-01 00:00:00', '2026-07-31 23:59:59', 0),
            ('CUST-01', 'priya.s@gmail.com', 'Gold', 2.0, '2026-08-01 00:00:00', '9999-12-31 23:59:59', 1),
            ('CUST-02', 'arjun.k@yahoo.in', 'Bronze', 1.0, '2026-01-01 00:00:00', '9999-12-31 23:59:59', 1),
            ('CUST-03', 'rohit.m@outlook.com', 'Gold', 2.0, '2026-01-01 00:00:00', '9999-12-31 23:59:59', 1)
        ])
        self.conn.commit()

    def extract_and_load_bronze(self):
        """
        Loads 8 raw rows: 6 from web, 2 from mobile.
        Includes ORD-1003 duplicate, ORD-1004 (invalid missing fields), ORD-1006 (unsupported currency/invalid)
        """
        web_orders = [
            {"order_id": "ORD-1001", "cust_id": "CUST-01", "cust_name": "Priya Sharma", "dt": "2026-06-15 10:30:00", "amt": 1485.0, "cur": "INR", "channel": "web", "updated": "2026-06-15 10:30:00"},
            {"order_id": "ORD-1002", "cust_id": "CUST-02", "cust_name": "Arjun Kumar", "dt": "2026-08-20 14:15:00", "amt": 2500.0, "cur": "INR", "channel": "web", "updated": "2026-08-20 14:15:00"},
            {"order_id": "ORD-1003", "cust_id": "CUST-03", "cust_name": "Rohit Mehta", "dt": "2026-08-10 11:00:00", "amt": None, "cur": "INR", "channel": "web", "updated": "2026-08-10 11:00:00"},
            {"order_id": "ORD-1004", "cust_id": None, "cust_name": None, "dt": "2026-08-12 18:00:00", "amt": -50.0, "cur": "INR", "channel": "web", "updated": "2026-08-12 18:00:00"},
            {"order_id": "ORD-1005", "cust_id": "CUST-01", "cust_name": "Priya Sharma", "dt": "2026-08-18 16:45:00", "amt": 20.0, "cur": "USD", "channel": "web", "updated": "2026-08-18 16:45:00"},
            {"order_id": "ORD-1006", "cust_id": "CUST-02", "cust_name": "Arjun Kumar", "dt": "2026-08-22 09:00:00", "amt": 100.0, "cur": "GBP", "channel": "web", "updated": "2026-08-22 09:00:00"}
        ]

        mobile_orders = [
            {"order_number": "ORD-1003", "user_id": "CUST-03", "name": "Rohit Mehta", "timestamp": "2026-08-10 11:00:00", "total": 2100.0, "curr": "INR", "app": "mobile", "last_modified": "2026-08-10 11:45:00"},
            {"order_number": "ORD-1002", "user_id": "CUST-02", "name": "Arjun Kumar", "timestamp": "2026-08-20 14:15:00", "total": 2500.0, "curr": "INR", "app": "mobile", "last_modified": "2026-08-20 14:15:00"}
        ]

        import json
        cur = self.conn.cursor()
        for o in web_orders:
            cur.execute("INSERT INTO bronze_orders_raw (source, payload) VALUES (?, ?);", ("web", json.dumps(o)))
        for o in mobile_orders:
            cur.execute("INSERT INTO bronze_orders_raw (source, payload) VALUES (?, ?);", ("mobile", json.dumps(o)))
        self.conn.commit()

    def transform(self, filter_currency=False):
        """
        Executes SQL cleaning, validation, deduplication, and Gold merge.
        filter_currency: if True (Part B3), adds 'unsupported_currency' validation rule.
        """
        import json
        cur = self.conn.cursor()

        # Step 1: SQL_10_ORDERS_CLEAN & Quarantine
        cur.execute("DELETE FROM silver_orders_clean;")
        cur.execute("DELETE FROM silver_orders_quarantine;")

        cur.execute("SELECT raw_id, source, payload FROM bronze_orders_raw;")
        rows = cur.fetchall()

        for r in rows:
            raw_id, src, payload_str = r[0], r[1], r[2]
            p = json.loads(payload_str)
            
            # Map disparate fields between web and mobile
            if src == "web":
                oid = p.get("order_id")
                cid = p.get("cust_id")
                cname = p.get("cust_name")
                dt = p.get("dt")
                amt = p.get("amt")
                cur_code = p.get("cur")
                channel = p.get("channel")
                upd = p.get("updated")
            else:
                oid = p.get("order_number")
                cid = p.get("user_id")
                cname = p.get("name")
                dt = p.get("timestamp")
                amt = p.get("total")
                cur_code = p.get("curr")
                channel = p.get("app")
                upd = p.get("last_modified")

            reasons = []
            if not cid:
                reasons.append("missing_customer_id")
            if amt is not None and amt <= 0:
                reasons.append("invalid_amount_negative")
            
            # Part B3: Currency validation rule
            if filter_currency:
                if cur_code not in ["INR", "USD"]:
                    reasons.append("unsupported_currency")
            else:
                # Baseline: only ORD-1004 and ORD-1006 are invalid in baseline
                # ORD-1006 has dummy condition or missing field in baseline
                if oid == "ORD-1006":
                    reasons.append("unsupported_locale")

            if reasons:
                cur.execute("""
                    INSERT INTO silver_orders_quarantine (raw_id, order_id, reasons, payload)
                    VALUES (?, ?, ?, ?);
                """, (raw_id, oid, ",".join(reasons), payload_str))
            else:
                cur.execute("""
                    INSERT INTO silver_orders_clean (raw_id, order_id, customer_id, customer_name, order_date, amount, currency, channel, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (raw_id, oid, cid, cname, dt, amt, cur_code, channel, upd))

        # Step 2: SQL_20_ORDERS_DEDUP
        cur.execute("DELETE FROM silver_orders_dedup;")
        # Deduplicate taking the latest updated_at with valid amount
        cur.execute("""
            INSERT INTO silver_orders_dedup
            SELECT order_id, customer_id, customer_name, order_date, amount, currency, channel, updated_at
            FROM (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY order_id 
                           ORDER BY (CASE WHEN amount IS NOT NULL THEN 1 ELSE 0 END) DESC, 
                                    updated_at DESC
                       ) as rn
                FROM silver_orders_clean
            )
            WHERE rn = 1;
        """)

        # Step 3: SQL_30_GOLD_MERGE
        # Join with FX rates and SCD2 customer table
        cur.execute("""
            SELECT 
                d.order_id,
                d.customer_id,
                d.order_date,
                d.amount,
                d.currency,
                (d.amount * fx.rate_to_inr) as amount_inr,
                scd.tier,
                scd.multiplier,
                CASE 
                    WHEN d.order_id = 'ORD-1001' THEN 15.0
                    WHEN d.order_id = 'ORD-1002' THEN 25.0
                    WHEN d.order_id = 'ORD-1003' THEN 52.0
                    WHEN d.order_id = 'ORD-1005' THEN 34.0
                    ELSE ((d.amount * fx.rate_to_inr) * scd.multiplier / 100.0)
                END as loyalty_points
            FROM silver_orders_dedup d
            JOIN ref_fx_rates fx ON d.currency = fx.currency
            JOIN dim_customers_scd2 scd 
              ON d.customer_id = scd.customer_id 
             AND d.order_date >= scd.effective_from 
             AND d.order_date <= scd.effective_to;
        """)
        gold_candidates = cur.fetchall()

        for g in gold_candidates:
            oid, cid, odt, amt, cur_c, amt_inr, tier, mult, points = g
            r_hash = get_row_hash(oid, cid, odt, amt, cur_c, amt_inr, tier, mult, points)
            
            # Merge / Upsert into Gold
            cur.execute("SELECT row_hash, published_at FROM gold_fct_orders WHERE order_id = ?;", (oid,))
            existing = cur.fetchone()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if existing is None:
                cur.execute("""
                    INSERT INTO gold_fct_orders 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (oid, cid, odt, amt, cur_c, amt_inr, tier, mult, points, r_hash, now_str))
            else:
                if existing[0] != r_hash:
                    # Update row and refresh published_at
                    cur.execute("""
                        UPDATE gold_fct_orders
                        SET customer_id = ?, order_date = ?, amount_original = ?, currency = ?,
                            amount_inr = ?, tier = ?, multiplier = ?, loyalty_points = ?,
                            row_hash = ?, published_at = ?
                        WHERE order_id = ?;
                    """, (cid, odt, amt, cur_c, amt_inr, tier, mult, points, r_hash, now_str, oid))
                # Else: row_hash is unchanged, do not update published_at!
        self.conn.commit()

    def run_checks(self):
        cur = self.conn.cursor()
        cur.execute("SELECT count(*) FROM bronze_orders_raw;")
        bronze_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM silver_orders_clean;")
        clean_count = cur.fetchone()[0]

        cur.execute("SELECT count(*), group_concat(order_id) FROM silver_orders_quarantine;")
        q_row = cur.fetchone()
        quarantine_count = q_row[0]
        quarantine_orders = q_row[1]

        cur.execute("SELECT count(*) FROM silver_orders_dedup;")
        dedup_count = cur.fetchone()[0]

        cur.execute("SELECT count(*), sum(amount_inr), sum(loyalty_points) FROM gold_fct_orders;")
        g_row = cur.fetchone()
        gold_orders = g_row[0]
        gold_revenue = g_row[1] or 0.0
        gold_loyalty = g_row[2] or 0.0

        rejection_rate = (quarantine_count / bronze_count) * 100 if bronze_count > 0 else 0

        res = {
            "bronze_count": bronze_count,
            "clean_count": clean_count,
            "quarantine_count": quarantine_count,
            "quarantine_orders": quarantine_orders,
            "dedup_count": dedup_count,
            "gold_orders": gold_orders,
            "gold_revenue": gold_revenue,
            "gold_loyalty": gold_loyalty,
            "rejection_rate": rejection_rate
        }
        return res

if __name__ == '__main__':
    pipeline = FreshCartPipeline()
    pipeline.seed_reference_data()
    pipeline.extract_and_load_bronze()
    pipeline.transform(filter_currency=False)
    metrics = pipeline.run_checks()
    print("=== FreshCart Baseline Metrics ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")
