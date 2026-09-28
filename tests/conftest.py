import pytest
from fastapi.testclient import TestClient

from chat_summarizer.api import create_app
from chat_summarizer.config import Settings
from chat_summarizer.storage import MemoryStore
from chat_summarizer.summarizer import ChatSummarizer


@pytest.fixture
def store():
    return MemoryStore()


@pytest.fixture
def client(store):
    app = create_app(Settings(), store, ChatSummarizer(store))
    return TestClient(app)
