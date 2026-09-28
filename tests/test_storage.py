import pytest

from chat_summarizer.config import Settings
from chat_summarizer.models import ChatMessage, Role, Sentiment, TopicCategory
from chat_summarizer.storage import (
    MemoryStore,
    RedisStore,
    create_store,
    deserialize_message,
    serialize_message,
)


def msg(sid="s1", role=Role.USER, content="hi", **kw):
    return ChatMessage(session_id=sid, role=role, content=content, **kw)


class FakeRedis:
    def __init__(self):
        self.kv, self.lists = {}, {}

    def set(self, k, v):
        self.kv[k] = v

    def get(self, k):
        return self.kv.get(k)

    def rpush(self, k, v):
        self.lists.setdefault(k, []).append(v)

    def lrange(self, k, a, b):
        return list(self.lists.get(k, []))

    def keys(self, pattern):
        prefix = pattern.rstrip("*")
        return [k for k in self.lists if k.startswith(prefix)]

    def delete(self, k):
        self.kv.pop(k, None)
        self.lists.pop(k, None)

    def ping(self):
        return True


class BrokenRedis(FakeRedis):
    def set(self, k, v):
        raise ConnectionError("down")

    def ping(self):
        raise ConnectionError("down")


@pytest.fixture(params=["memory", "redis"])
def store(request):
    return MemoryStore() if request.param == "memory" else RedisStore(client=FakeRedis())


def test_store_assigns_id_and_orders_messages(store):
    a, b = msg(content="one"), msg(content="two")
    assert store.store_message(a) and store.store_message(b)
    assert a.message_id and a.message_id != b.message_id
    assert [m.content for m in store.get_session_messages("s1")] == ["one", "two"]


def test_unknown_session_is_empty(store):
    assert store.get_session_messages("nope") == []
    assert store.get_session_stats("nope") == {}


def test_list_and_delete_sessions(store):
    store.store_message(msg("a"))
    store.store_message(msg("b"))
    assert sorted(store.list_sessions()) == ["a", "b"]
    assert store.delete_session("a") is True
    assert store.delete_session("a") is False
    assert store.list_sessions() == ["b"]


def test_stats(store):
    store.store_message(msg(sentiment=Sentiment.POSITIVE, topic=TopicCategory.QUESTION))
    store.store_message(msg(role=Role.ASSISTANT, sentiment=Sentiment.POSITIVE))
    stats = store.get_session_stats("s1")
    assert stats["total_messages"] == 2
    assert stats["user_messages"] == 1 and stats["assistant_messages"] == 1
    assert stats["sentiment_distribution"] == {"positive": 2}
    assert stats["topic_distribution"] == {"question": 1}
    assert stats["session_duration"] >= 0


def test_health(store):
    assert store.health_check() is True


def test_serialization_roundtrip():
    m = msg(message_id="x", sentiment=Sentiment.NEGATIVE, topic=TopicCategory.COMPLAINT)
    assert deserialize_message(serialize_message(m)) == m


def test_redis_failures_are_handled():
    r = RedisStore(client=BrokenRedis())
    assert r.store_message(msg()) is False
    assert r.health_check() is False


def test_redis_skips_dangling_ids():
    fake = FakeRedis()
    r = RedisStore(client=fake)
    r.store_message(msg())
    fake.kv.clear()
    assert r.get_session_messages("s1") == []


def test_create_store_selects_backend():
    assert isinstance(create_store(Settings(storage_backend="memory")), MemoryStore)


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com, http://b.com")
    monkeypatch.setenv("STORAGE_BACKEND", "REDIS")
    monkeypatch.setenv("REDIS_PORT", "6380")
    monkeypatch.setenv("USE_ML_MODELS", "true")
    s = Settings.from_env()
    assert s.cors_origins == ["http://a.com", "http://b.com"]
    assert s.storage_backend == "redis" and s.redis_port == 6380 and s.use_ml_models
