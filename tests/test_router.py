
from app.schemas import ChatRequest, Message
from app.router import route_request


def make_request(prompt):
    return ChatRequest(
        model="auto",
        messages=[
            Message(role="user", content=prompt)
        ]
    )


def test_simple_question():
    req = make_request("What is the capital of France?")

    decision = route_request(req)

    assert decision.model == "small"


def test_coding_question():
    req = make_request("Debug this Python algorithm")

    decision = route_request(req)

    assert decision.model == "strong"


def test_reasoning_question():
    req = make_request("Calculate this step by step")

    decision = route_request(req)

    assert decision.model == "strong"


def test_proof_question():
    req = make_request("Prove that sqrt(2) is irrational")

    decision = route_request(req)

    assert decision.model == "strong"


def test_long_prompt():
    req = make_request("hello " * 100)

    decision = route_request(req)

    assert decision.score >= 1
