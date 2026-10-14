
from dataclasses import dataclass
from app.schemas import ChatRequest, ChatResult


@dataclass
class CascadeResult:
    result: ChatResult
    escalated: bool
    reason: str
    small_result: ChatResult


def check_answer(answer: str) -> tuple[bool, str]:

    text = answer.strip().lower()

    if not text:
        return False, "Empty answer"

    uncertainty = [
        "i don't know",
        "i cannot answer",
        "not sure",
        "unable to determine"
    ]

    if any(term in text for term in uncertainty):
        return False, "Uncertain answer"

    if len(text.split()) < 5:
        return False, "Very short answer"

    return True, "Passed heuristic checks"


async def cascade_request(
    req: ChatRequest,
    provider,
    models: dict
) -> CascadeResult:

    # Step 1: Call small model
    small = await provider.complete(
        req, models["small"]
    )

    # Step 2: Evaluate answer
    acceptable, reason = check_answer(small.text)

    # Step 3: Return small answer if acceptable
    if acceptable:
        return CascadeResult(
            result=small,
            escalated=False,
            reason=reason,
            small_result=small
        )

    # Step 4: Escalate to stronger model
    strong = await provider.complete(
        req, models["strong"]
    )

    return CascadeResult(
        result=strong,
        escalated=True,
        reason=reason,
        small_result=small
    )
