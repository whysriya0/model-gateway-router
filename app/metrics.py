
import math
import sqlite3
from statistics import mean
from app.ledger import DB_PATH


def percentile(values, p):
    if not values:
        return 0.0

    values = sorted(values)

    index = math.ceil(p / 100 * len(values)) - 1

    return values[index]


def get_metrics():

    with sqlite3.connect(DB_PATH) as db:

        rows = db.execute("""
            SELECT model, cost, latency_ms, status
            FROM requests
        """).fetchall()

    total_requests = len(rows)

    successful = [
        row for row in rows if row[3] == "ok"
    ]

    failed = [
        row for row in rows if row[3] == "error"
    ]

    costs = [row[1] for row in successful]
    latencies = [row[2] for row in successful]

    total_cost = sum(costs)

    return {
        "total_requests": total_requests,
        "successful_requests": len(successful),
        "failed_requests": len(failed),
        "error_rate": (
            len(failed) / total_requests
            if total_requests else 0
        ),
        "estimated_total_cost_usd": total_cost,
        "average_cost_usd": (
            mean(costs) if costs else 0
        ),
        "average_latency_ms": (
            mean(latencies) if latencies else 0
        ),
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95)
    }
