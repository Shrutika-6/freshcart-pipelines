import os
import sys
import json
import time
from datetime import datetime
import pika

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from elt.freshcart_pipeline import FreshCartPipeline

class LakehouseStreamConsumer:
    def __init__(self, buffer_file="stream/landing_buffer.json"):
        self.buffer_file = buffer_file
        self.buffer = []
        self.pipeline = FreshCartPipeline()
        self.pipeline.seed_reference_data()

    def write_landing(self, orders):
        """Writes buffered stream records as a raw landing file"""
        with open(self.buffer_file, "w") as f:
            json.dump(orders, f, indent=2)
        print(f"[LakehouseConsumer] Landed {len(orders)} stream orders to {self.buffer_file}")

    def load_file(self):
        """Loads landed raw file into bronze table"""
        if not os.path.exists(self.buffer_file):
            print(f"Landing file {self.buffer_file} not found.")
            return

        with open(self.buffer_file, "r") as f:
            orders = json.load(f)

        cur = self.pipeline.conn.cursor()
        for order in orders:
            cur.execute(
                "INSERT INTO bronze_orders_raw (source, payload) VALUES (?, ?);",
                ("stream_landing", json.dumps(order))
            )
        self.pipeline.conn.commit()
        print(f"[LakehouseConsumer] Loaded {len(orders)} rows from file into bronze_orders_raw.")

    def run_batch_cycle(self, mock_stream_orders):
        print("\n--- Cycle 1: Land and Transform Streamed Orders ---")
        self.write_landing(mock_stream_orders)
        self.load_file()
        self.pipeline.transform(filter_currency=True)
        res1 = self.pipeline.run_checks()
        print(f"Cycle 1 Gold Orders: {res1['gold_orders']} | Revenue: {res1['gold_revenue']} | Loyalty: {res1['gold_loyalty']}")

        print("\n--- Cycle 2: Re-running Same Batch (Demonstrating Idempotency) ---")
        # Load same file again (simulating duplicate delivery or retry)
        self.load_file()
        self.pipeline.transform(filter_currency=True)
        res2 = self.pipeline.run_checks()
        print(f"Cycle 2 Gold Orders: {res2['gold_orders']} | Revenue: {res2['gold_revenue']} | Loyalty: {res2['gold_loyalty']}")
        
        # Verify idempotency
        assert res1['gold_orders'] == res2['gold_orders'], "Idempotency failed: Order count changed!"
        assert res1['gold_revenue'] == res2['gold_revenue'], "Idempotency failed: Revenue doubled!"
        assert res1['gold_loyalty'] == res2['gold_loyalty'], "Idempotency failed: Loyalty points doubled!"
        print("\n[SUCCESS] Lakehouse idempotency confirmed! Re-running batch does NOT double gold totals.")

if __name__ == '__main__':
    consumer = LakehouseStreamConsumer()
    # Baseline load first
    consumer.pipeline.extract_and_load_bronze()
    consumer.pipeline.transform(filter_currency=True)
    
    mock_stream = [
        {"order_id": "ORD-1007", "cust_id": "CUST-01", "cust_name": "Priya Sharma", "dt": "2026-08-25 12:00:00", "amt": 1000.0, "cur": "INR", "channel": "stream", "updated": "2026-08-25 12:00:00"},
        {"order_id": "ORD-1008", "cust_id": "CUST-03", "cust_name": "Rohit Mehta", "dt": "2026-08-25 12:05:00", "amt": 500.0, "cur": "INR", "channel": "stream", "updated": "2026-08-25 12:05:00"}
    ]
    consumer.run_batch_cycle(mock_stream)
