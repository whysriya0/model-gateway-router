
from app.cache import SemanticCache

cache = SemanticCache(threshold=0.92)

# Initially, the cache is empty
answer, status = cache.get("What is recursion?")
print("First lookup:", status, answer)

# Store an answer
cache.put(
    "What is recursion?",
    "Recursion is when a function calls itself."
)

# Exact same question
answer, status = cache.get("What is recursion?")
print("Second lookup:", status, answer)

# Similar question
answer, status = cache.get(
    "Can you explain recursion?"
)
print("Third lookup:", status, answer)

# Different question
answer, status = cache.get(
    "What is the capital of France?"
)
print("Fourth lookup:", status, answer)

print("Cache size:", cache.size())
