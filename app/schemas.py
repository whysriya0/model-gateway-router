from pydantic import BaseModel

class Message(BaseModel):
    role: str        # "system" | "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    model: str = "auto"      # "auto", "small", "strong", or an exact model name
    messages: list[Message]
    max_tokens: int = 512
    temperature: float = 0.2
    stream: bool = False

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int

class ChatResult(BaseModel):
    text: str
    model: str
    usage: Usage
    latency_ms: float