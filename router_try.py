
from app.schemas import ChatRequest, Message
from app.router import route_request

prompts = [
    "What is the capital of France?",
    "Summarize this short paragraph.",
    "Debug this Python algorithm.",
    "Prove that sqrt(2) is irrational.",
    "Calculate the solution step by step."
]

for prompt in prompts:
    req = ChatRequest(
        model="auto",
        messages=[
            Message(role="user", content=prompt)
        ]
    )

    decision = route_request(req)

    print("\nPrompt:", prompt)
    print("Model:", decision.model)
    print("Score:", decision.score)
    print("Reasons:", decision.reasons)
