import sqlite3

db = sqlite3.connect("ledger.db")
rows = db.execute("""
    SELECT model, COUNT(*), SUM(tokens_in), SUM(tokens_out),
           SUM(cost), AVG(latency_ms)
    FROM requests WHERE status = 'ok' GROUP BY model
""").fetchall()

print(f"{'model':28} {'n':>4} {'in':>8} {'out':>8} {'cost$':>10} {'avg ms':>8}")
for m, n, ti, to, c, lat in rows:
    print(f"{m:28} {n:>4} {ti:>8} {to:>8} {c:>10.6f} {lat:>8.0f}")