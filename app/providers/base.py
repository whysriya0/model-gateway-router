from abc import ABC, abstractmethod
from typing import AsyncIterator
from app.schemas import ChatRequest, ChatResult

class Provider(ABC):
    name: str

    @abstractmethod
    async def complete(self, req: ChatRequest, model: str) -> ChatResult:
        ...

    @abstractmethod
    def stream(self, req: ChatRequest, model: str) -> AsyncIterator[str]:
        ...