import os
import time
import json
import httpx
from app.providers.base import Provider
from app.schemas import ChatRequest, ChatResult, Usage

URL = "https://api.groq.com/openai/v1/chat/completions"

class GroqProvider(Provider):
    name = "groq"

    def __init__(self):
        self.key = os.environ["GROQ_API_KEY"]
        self.client = httpx.AsyncClient(timeout=30.0)

    def _headers(self):
        return {"Authorization": f"Bearer {self.key}"}

    def _payload(self, req: ChatRequest, model: str, stream: bool):
        return {
            "model": model,
            "messages": [m.model_dump() for m in req.messages],
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "stream": stream,
        }

    async def complete(self, req: ChatRequest, model: str) -> ChatResult:
        t0 = time.perf_counter()
        r = await self.client.post(
            URL, json=self._payload(req, model, False), headers=self._headers()
        )
        r.raise_for_status()
        data = r.json()
        return ChatResult(
            text=data["choices"][0]["message"]["content"],
            model=model,
            usage=Usage(
                prompt_tokens=data["usage"]["prompt_tokens"],
                completion_tokens=data["usage"]["completion_tokens"],
            ),
            latency_ms=(time.perf_counter() - t0) * 1000,
        )

    async def stream(self, req: ChatRequest, model: str):
        async with self.client.stream(
            "POST", URL, json=self._payload(req, model, True), headers=self._headers()
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.startswith("data: "):
                    continue
                chunk = line[6:]
                if chunk == "[DONE]":
                    break
                choices = json.loads(chunk).get("choices")
                if not choices:
                    continue
                delta = choices[0]["delta"].get("content")
                if delta:
                    yield delta