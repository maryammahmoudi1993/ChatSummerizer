import pytest
from fastapi.testclient import TestClient

from chat_summarizer.api import create_app
from chat_summarizer.config import Settings
from chat_summarizer.models import MAX_TEXT_LENGTH


def send(client, content="I love this product", sid="s1", role="user"):
    return client.post("/chat/send", data={"session_id": sid, "role": role, "content": content})


def test_index_and_static(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/api/docs", follow_redirects=False).status_code in (302, 307)


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "healthy"
    assert set(body["components"]) == {"storage", "summarizer", "sentiment_analyzer", "topic_classifier"}


def test_health_reports_unhealthy(store):
    store.health_check = lambda: False
    body = TestClient(create_app(Settings(), store)).get("/health").json()
    assert body["status"] == "unhealthy"


def test_send_and_fetch(client):
    r = send(client)
    assert r.status_code == 200
    body = r.json()
    assert body["sentiment"] == "positive" and body["message_id"]
    assert client.get("/chat/sessions").json() == {"sessions": ["s1"]}
    messages = client.get("/chat/session/s1").json()["messages"]
    assert messages[0]["content"] == "I love this product"


def test_send_rejects_bad_role_and_content(client):
    assert send(client, role="admin").status_code == 400
    assert send(client, content="").status_code == 422
    assert send(client, content="x" * (MAX_TEXT_LENGTH + 1)).status_code == 422


def test_send_reports_storage_failure(store):
    store.store_message = lambda m: False
    c = TestClient(create_app(Settings(), store))
    assert send(c).status_code == 500


def test_delete_session_and_404(client):
    send(client)
    assert client.delete("/chat/session/s1").status_code == 200
    assert client.delete("/chat/session/s1").status_code == 404


def test_stats(client):
    assert client.get("/stats/session/none").status_code == 404
    send(client)
    send(client, content="How does this work?", role="assistant")
    assert client.get("/stats/session/s1").json()["total_messages"] == 2
    overview = client.get("/stats/overview").json()
    assert overview == {"total_sessions": 1, "total_messages": 2, "avg_messages_per_session": 2.0}


def test_overview_empty(client):
    assert client.get("/stats/overview").json()["avg_messages_per_session"] == 0


def test_summaries(client):
    send(client, content="My invoice is wrong. Please check the invoice.")
    r = client.post("/summary/generate", json={"session_id": "s1", "max_length": 50})
    assert r.status_code == 200 and r.json()["message_count"] == 1
    assert client.get("/summary/brief/s1").json()["summary"]
    assert "main_topics" in client.get("/summary/structured/s1").json()["summary"]


def test_summary_validation(client):
    assert client.post("/summary/generate", json={"session_id": "s1", "max_length": 5}).status_code == 422
    assert client.post("/summary/generate", json={"session_id": "s1", "max_length": 99999}).status_code == 422


def test_sentiment_and_topic_endpoints(client):
    r = client.post("/sentiment/analyze", json={"text": "terrible, I hate it", "session_id": "z"})
    assert r.json()["sentiment"] == "negative" and r.json()["session_id"] == "z"
    r = client.post("/topic/classify", json={"text": "How do I pay?"})
    assert r.json()["topic"] == "question"
    assert client.post("/sentiment/analyze", json={"text": ""}).status_code == 422


def test_batch_endpoints(client):
    r = client.post("/sentiment/batch", json=["great", "awful"])
    assert [x["sentiment"] for x in r.json()["results"]] == ["positive", "negative"]
    r = client.post("/topic/batch", json=["how?", "buy now"])
    assert len(r.json()["results"]) == 2


@pytest.mark.parametrize("path", ["/sentiment/batch", "/topic/batch"])
def test_batch_limits(client, path):
    assert client.post(path, json=["a"] * 101).status_code == 422
    assert client.post(path, json=["x" * (MAX_TEXT_LENGTH + 1)]).status_code == 422


def test_cors_allows_only_configured_origin(store):
    c = TestClient(create_app(Settings(cors_origins=["http://ok.test"]), store))
    ok = c.get("/health", headers={"Origin": "http://ok.test"})
    bad = c.get("/health", headers={"Origin": "http://evil.test"})
    assert ok.headers.get("access-control-allow-origin") == "http://ok.test"
    assert "access-control-allow-origin" not in bad.headers


def test_default_app_builds_from_env():
    import main

    assert main.app.title == "Chat Summarizer API"
