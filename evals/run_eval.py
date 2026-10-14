
import json
import time
import httpx
from pathlib import Path

# File locations
ROOT = Path(__file__).resolve().parent.parent
PROMPTS_FILE = ROOT / "evals" / "prompts.json"
RESULTS_FILE = ROOT / "evals" / "results.jsonl"
PRICES_FILE = ROOT / "prices.json"

# Our existing FastAPI endpoint
URL = "http://localhost:8000/v1/chat/completions"

STRATEGIES = ["small", "strong", "auto"]

# Start with 3 prompts for testing
LIMIT = 20

prompts = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
prices = json.loads(PRICES_FILE.read_text(encoding="utf-8"))

# Load previously completed requests
completed = set()

if RESULTS_FILE.exists():
    with RESULTS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                result = json.loads(line)
                completed.add((result["id"], result["strategy"]))

# Run the evaluation
with httpx.Client(timeout=180) as client:

    for prompt in prompts[:LIMIT]:

        for strategy in STRATEGIES:

            key = (prompt["id"], strategy)

            if key in completed:
                print("Skipping:", key)
                continue

            print("Running:", key)

            body = {
                "model": strategy,
                "messages": [
                    {"role": "user", "content": prompt["prompt"]}
                ],
                "max_tokens": 1500,
                "temperature": 0.2,
                "stream": False
            }

            try:
                start = time.perf_counter()
                response = client.post(URL, json=body)
                latency_ms = (time.perf_counter() - start) * 1000

                response.raise_for_status()
                data = response.json()

                model = data["model"]
                usage = data["usage"]
                answer = data["choices"][0]["message"]["content"]

                # Calculate estimated API cost
                price = prices[model]
                cost = (
                    usage["prompt_tokens"] * price["input"]
                    + usage["completion_tokens"] * price["output"]
                ) / 1_000_000

                result = {
                    "id": prompt["id"],
                    "strategy": strategy,
                    "model": model,
                    "category": prompt["category"],
                    "difficulty": prompt["difficulty"],
                    "split": prompt["split"],
                    "answer": answer,
                    "tokens_in": usage["prompt_tokens"],
                    "tokens_out": usage["completion_tokens"],
                    "cost": cost,
                    "latency_ms": latency_ms
                }

                # Append one completed result
                with RESULTS_FILE.open("a", encoding="utf-8") as file:
                    file.write(json.dumps(result) + "\n")

                completed.add(key)
                print("Saved:", key)

            except httpx.HTTPError as error:
                print("Request failed:", error)
                print("Stopping. Run again to resume.")
                raise SystemExit(1)

            except (KeyError, ValueError) as error:
                print("Invalid response or pricing:", error)
                raise SystemExit(1)

            # Avoid sending requests too quickly
            time.sleep(2)

print("Evaluation batch completed!")
