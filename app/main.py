import time
import uuid
import json
from dotenv import load_dotenv

from app.router import route_request

load_dotenv()

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest
from app.providers.groq import GroqProvider
from app import ledger

app = FastAPI()
provider = GroqProvider()
ledger.init_db()

MODELS = {
    "small": "openai/gpt-oss-20b",
    "strong": "openai/gpt-oss-120b",
}

def pick_model(req: ChatRequest) -> str:
    if req.model in MODELS:
        return MODELS[req.model]

    if req.model == "auto":
        decision = route_request(req)

        print("Routing decision:", decision.model)
        print("Difficulty score:", decision.score)
        print("Reasons:", decision.reasons)

        return MODELS[decision.model]

    return req.model

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    model = pick_model(req)
    cid = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    if req.stream:
        async def gen():
            async for piece in provider.stream(req, model):
                chunk = {
                    "id": cid,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {"index": 0, "delta": {"content": piece}, "finish_reason": None}
                    ],
                }
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    t0 = time.perf_counter()
    try:
        res = await provider.complete(req, model)
    except httpx.HTTPStatusError as e:
        ms = (time.perf_counter() - t0) * 1000
        ledger.log_request(cid, model, 0, 0, ms, "error")
        code = e.response.status_code
        print("PROVIDER ERROR:", code, e.response.text)
        raise HTTPException(429 if code == 429 else 502, f"provider returned {code}")
    except httpx.ConnectError:
        ms = (time.perf_counter() - t0) * 1000
        ledger.log_request(cid, model, 0, 0, ms, "error")
        raise HTTPException(503, "provider unavailable")

    ledger.log_request(
        cid, res.model, res.usage.prompt_tokens,
        res.usage.completion_tokens, res.latency_ms, "ok",
    )

    return {
        "id": cid,
        "object": "chat.completion",
        "created": created,
        "model": res.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": res.text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": res.usage.prompt_tokens,
            "completion_tokens": res.usage.completion_tokens,
            "total_tokens": res.usage.prompt_tokens + res.usage.completion_tokens,
        },
    }