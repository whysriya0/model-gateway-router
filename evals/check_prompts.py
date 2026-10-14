
import json
from collections import Counter
from pathlib import Path

path = Path(__file__).with_name("prompts.json")

prompts = json.loads(path.read_text(encoding="utf-8"))

# Check the number of prompts
assert len(prompts) == 100, "Expected 100 prompts"

# Check for duplicate IDs
assert len({p["id"] for p in prompts}) == len(prompts), "Duplicate IDs"

# Check for duplicate questions
assert len({p["prompt"] for p in prompts}) == len(prompts), "Duplicate questions"

# Validate each prompt
for p in prompts:

    assert p["split"] in {"train", "dev", "test"}, p["id"]

    assert p["difficulty"] in {"easy", "medium", "hard"}, p["id"]

    assert p["evaluation_type"] in {"exact", "numeric", "rubric"}, p["id"]

    assert p["prompt"].strip(), p["id"]

    if p["evaluation_type"] in {"exact", "numeric"}:
        assert p["reference_answer"] is not None, p["id"]

    else:
        assert p["rubric"], p["id"]

print("Dataset valid")

print("Splits:", dict(Counter(p["split"] for p in prompts)))

print("Categories:", dict(Counter(p["category"] for p in prompts)))

print("Scoring methods:", dict(Counter(p["evaluation_type"] for p in prompts)))
