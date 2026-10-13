import httpx, time

URL = "http://localhost:8000/v1/chat/completions"
prompts = [
    "What is the capital of France?",
    "Summarize in two sentences: Photosynthesis converts light, water and CO2 into glucose and oxygen inside chloroplasts.",
    "Write a Python function that checks if a string is a palindrome.",
    "Explain the difference between a process and a thread, with one example each.",
    "A train leaves at 3pm at 60 km/h. Another leaves the same station at 4pm at 80 km/h on the same track. At what time does the second catch the first? Show steps.",
]

for model in ["small", "strong"]:
    for p in prompts:
        r = httpx.post(URL, json={"model": model, "max_tokens": 1500,
                       "messages": [{"role": "user", "content": p}]}, timeout=60)
        usage = r.json().get("usage") if r.status_code == 200 else r.text
        print(model, r.status_code, usage)
        time.sleep(2)   # stay under the free-tier request limit