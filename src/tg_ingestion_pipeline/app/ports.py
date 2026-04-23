from typing import Any, Dict, List, Optional, Protocol


class MessageRepository(Protocol):
    def upsert(self, message: Dict[str, Any]) -> bool:
        ...


class VectorStore(Protocol):
    def upsert(self, message: Dict[str, Any], vector: Optional[List[float]]) -> bool:
        ...


class DeadLetterPublisher(Protocol):
    def publish(self, key: str, payload: Dict[str, Any]) -> None:
        ...
