
from dataclasses import dataclass
from app.schemas import ChatRequest


@dataclass
class RouteDecision:
    model:str
    score:int
    reasons:list[str]

def route_request(req: ChatRequest) ->RouteDecision:
    prompt = " ".join(
        msg.content for msg in req.messages if msg.role == "user"
    ).lower()
    score=0
    reasons=[]
    if len(prompt)>400:
        score+=1
        reasons.append("prompt too long")
    coding_terms=[
        "debug", "fix this code",
        "implement", "algorithm", "traceback"
    ]
    if any(term in prompt for term in coding_terms):
        score+=1
        reasons.append("coding prompt")

    reasoning_terms = [
            "step by step", "derive",
            "reasoning", "calculate"
        ]
    if any(term in prompt for term in reasoning_terms):
            score += 2
            reasons.append("Reasoning task")
    proof_terms = ["prove", "proof"]

    if any(term in prompt for term in proof_terms):
        score += 3
        reasons.append("Proof task")
    selected="strong" if score>2 else "small"
    return RouteDecision(
            model=selected,
            score=score,
            reasons=reasons
        )


