import json
import sqlite3
import time
from pathlib import Path

DB_PATH = "ledger.db"
PRICES = json.loads((Path(__file__).parent.parent / "prices.json").read_text())

def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL,
                request_id TEXT,
                model TEXT,
                tokens_in INTEGER,
                tokens_out INTEGER,
                cost REAL,
                latency_ms REAL,
                status TEXT
            )
        """)

def compute_cost(model, tokens_in, tokens_out):
    p = PRICES[model]   # KeyError on unknown model is intentional
    return (tokens_in * p["input"] + tokens_out * p["output"]) / 1_000_000

def log_request(request_id, model, tokens_in, tokens_out, latency_ms, status):
    cost = compute_cost(model, tokens_in, tokens_out) if status == "ok" else 0.0
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "INSERT INTO requests (ts, request_id, model, tokens_in, tokens_out,"
            " cost, latency_ms, status) VALUES (?,?,?,?,?,?,?,?)",
            (time.time(), request_id, model, tokens_in, tokens_out,
             cost, latency_ms, status),
        )
    return cost