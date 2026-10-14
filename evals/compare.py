
import json
from pathlib import Path
from collections import defaultdict
from statistics import mean

ROOT = Path(__file__).resolve().parent

RESULTS_FILE = ROOT / "results.jsonl"
SCORES_FILE = ROOT / "scores.jsonl"

# Load model responses and evaluation scores
results = [
    json.loads(line)
    for line in RESULTS_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

scores = [
    json.loads(line)
    for line in SCORES_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

# Map (prompt ID, strategy) to quality score
score_map = {
    (s["id"], s["strategy"]): s["score"]
    for s in scores
}

# Group results by strategy
groups = defaultdict(list)

for result in results:
    key = (result["id"], result["strategy"])

    # Only compare responses that have been scored
    if key not in score_map:
        continue

    result["quality"] = score_map[key]
    groups[result["strategy"]].append(result)

# Print comparison
print(
    f"{'Strategy':<12}"
    f"{'Count':>7}"
    f"{'Quality':>10}"
    f"{'Avg Cost ($)':>15}"
    f"{'Avg Latency (ms)':>20}"
)

for strategy, rows in sorted(groups.items()):

    avg_quality = mean(r["quality"] for r in rows)
    avg_cost = mean(r["cost"] for r in rows)
    avg_latency = mean(r["latency_ms"] for r in rows)

    print(
        f"{strategy:<12}"
        f"{len(rows):>7}"
        f"{avg_quality:>10.3f}"
        f"{avg_cost:>15.8f}"
        f"{avg_latency:>20.2f}"
    )

print(f"\nScored results: {sum(len(rows) for rows in groups.values())}")
print(f"Total generated results: {len(results)}")
