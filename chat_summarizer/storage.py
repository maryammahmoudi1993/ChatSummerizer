"""Message storage backends: in-memory (default) and Redis."""
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from .config import Settings
from .models import ChatMessage, Role

logger = logging.getLogger(__name__)


def serialize_message(message: ChatMessage) -> str:
    return json.dumps({
        "session_id": message.session_id,
        "role": message.role.value,
        "content": message.content,
        "timestamp": message.timestamp.isoformat(),
        "message_id": message.message_id,
        "sentiment": message.sentiment.value if message.sentiment else None,
        "topic": message.topic.value if message.topic else None,
    })


def deserialize_message(data: str) -> ChatMessage:
    raw = json.loads(data)
    raw["timestamp"] = datetime.fromisoformat(raw["timestamp"])
    return ChatMessage(**raw)


class BaseStore(ABC):
    """Common interface plus the shared statistics logic."""

    @abstractmethod
    def store_message(self, message: ChatMessage) -> bool: ...

    @abstractmethod
    def get_session_messages(self, session_id: str) -> list[ChatMessage]: ...

    @abstractmethod
    def list_sessions(self) -> list[str]: ...

    @abstractmethod
    def delete_session(self, session_id: str) -> bool: ...

    @abstractmethod
    def health_check(self) -> bool: ...

    def get_session_stats(self, session_id: str) -> dict[str, Any]:
        messages = self.get_session_messages(session_id)
        if not messages:
            return {}
        sentiments: dict[str, int] = {}
        topics: dict[str, int] = {}
        for m in messages:
            if m.sentiment:
                sentiments[m.sentiment.value] = sentiments.get(m.sentiment.value, 0) + 1
            if m.topic:
                topics[m.topic.value] = topics.get(m.topic.value, 0) + 1
        duration = (messages[-1].timestamp - messages[0].timestamp).total_seconds()
        return {
            "total_messages": len(messages),
            "user_messages": sum(m.role == Role.USER for m in messages),
            "assistant_messages": sum(m.role == Role.ASSISTANT for m in messages),
            "sentiment_distribution": sentiments,
            "topic_distribution": topics,
            "session_duration": duration,
        }


class MemoryStore(BaseStore):
    """Process-local storage; data is lost on restart."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[ChatMessage]] = {}

    def store_message(self, message: ChatMessage) -> bool:
        if not message.message_id:
            message.message_id = str(uuid.uuid4())
        self._sessions.setdefault(message.session_id, []).append(message)
        return True

    def get_session_messages(self, session_id: str) -> list[ChatMessage]:
        return list(self._sessions.get(session_id, []))

    def list_sessions(self) -> list[str]:
        return list(self._sessions)

    def delete_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def health_check(self) -> bool:
        return True


class RedisStore(BaseStore):
    """Redis-backed storage. `client` may be injected for testing."""

    def __init__(self, settings: Settings | None = None, client: Any = None) -> None:
        if client is None:  # pragma: no cover - requires a live server
            import redis

            settings = settings or Settings.from_env()
            client = redis.Redis(
                host=settings.redis_host, port=settings.redis_port,
                db=settings.redis_db, decode_responses=True,
            )
        self._r = client

    def store_message(self, message: ChatMessage) -> bool:
        try:
            if not message.message_id:
                message.message_id = str(uuid.uuid4())
            self._r.set(f"message:{message.message_id}", serialize_message(message))
            self._r.rpush(f"session:{message.session_id}", message.message_id)
            return True
        except Exception:
            logger.exception("Failed to store message")
            return False

    def get_session_messages(self, session_id: str) -> list[ChatMessage]:
        messages = []
        for message_id in self._r.lrange(f"session:{session_id}", 0, -1):
            data = self._r.get(f"message:{message_id}")
            if data:
                messages.append(deserialize_message(data))
        return messages

    def list_sessions(self) -> list[str]:
        return [key.split(":", 1)[1] for key in self._r.keys("session:*")]

    def delete_session(self, session_id: str) -> bool:
        key = f"session:{session_id}"
        ids = self._r.lrange(key, 0, -1)
        if not ids:
            return False
        for message_id in ids:
            self._r.delete(f"message:{message_id}")
        self._r.delete(key)
        return True

    def health_check(self) -> bool:
        try:
            return bool(self._r.ping())
        except Exception:
            logger.warning("Redis health check failed", exc_info=True)
            return False


def create_store(settings: Settings) -> BaseStore:
    if settings.storage_backend == "redis":
        return RedisStore(settings)
    return MemoryStore()
