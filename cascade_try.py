
from app.cascade import check_answer

answers = [
    "",
    "I don't know",
    "42",
    "The capital of France is Paris.",
    "A deadlock occurs when processes wait indefinitely for resources."
]

for answer in answers:
    acceptable, reason = check_answer(answer)

    print("Answer:", repr(answer))
    print("Acceptable:", acceptable)
    print("Reason:", reason)
    print()
