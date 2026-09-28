"""FastAPI application factory."""
import logging
from pathlib import Path
from typing import Annotated

from fastapi import Body, FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from . import __version__
from .classifier import TopicClassifier
from .config import Settings
from .models import (
    MAX_TEXT_LENGTH,
    ChatMessage,
    Role,
    SentimentAnalysisRequest,
    SummaryRequest,
    TopicClassificationRequest,
)
from .sentiment import SentimentAnalyzer
from .storage import BaseStore, create_store
from .summarizer import ChatSummarizer

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MAX_BATCH = 100
BatchTexts = Annotated[list[Annotated[str, Body(max_length=MAX_TEXT_LENGTH)]], Body(max_length=MAX_BATCH)]


def create_app(
    settings: Settings | None = None,
    store: BaseStore | None = None,
    summarizer: ChatSummarizer | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    store = store or create_store(settings)
    summarizer = summarizer or ChatSummarizer.from_settings(store, settings)
    sentiment = SentimentAnalyzer()
    classifier = TopicClassifier()

    app = FastAPI(
        title="Chat Summarizer API",
        description="Chat summarization with sentiment analysis and topic classification",
        version=__version__,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials="*" not in settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(
            request, "index.html", {"sessions": store.list_sessions()}
        )

    @app.post("/chat/send")
    async def send_message(
        session_id: Annotated[str, Form()],
        role: Annotated[str, Form()],
        content: Annotated[str, Form()],
    ):
        if role not in {r.value for r in Role}:
            raise HTTPException(status_code=400, detail="Invalid role")
        try:
            message = ChatMessage(session_id=session_id, role=Role(role), content=content)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors(include_url=False, include_context=False)) from exc
        sentiment_result = sentiment.analyze_sentiment(content)
        topic_result = classifier.classify_topic(content)
        message.sentiment = sentiment_result.sentiment
        message.topic = topic_result.topic
        if not store.store_message(message):
            raise HTTPException(status_code=500, detail="Failed to store message")
        return {
            "message_id": message.message_id,
            "sentiment": sentiment_result.sentiment.value,
            "topic": topic_result.topic.value,
            "confidence": {"sentiment": sentiment_result.confidence, "topic": topic_result.confidence},
        }

    @app.get("/chat/session/{session_id}")
    async def get_session(session_id: str):
        return {"session_id": session_id, "messages": store.get_session_messages(session_id)}

    @app.get("/chat/sessions")
    async def list_sessions():
        return {"sessions": store.list_sessions()}

    @app.delete("/chat/session/{session_id}")
    async def delete_session(session_id: str):
        if not store.delete_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}

    @app.post("/summary/generate")
    async def generate_summary(request: SummaryRequest):
        return summarizer.generate_summary(request.session_id, request.max_length)

    @app.get("/summary/brief/{session_id}")
    async def brief_summary(session_id: str):
        return {"session_id": session_id, "summary": summarizer.generate_brief_summary(session_id)}

    @app.get("/summary/structured/{session_id}")
    async def structured_summary(session_id: str):
        return {"session_id": session_id, "summary": summarizer.generate_structured_summary(session_id)}

    @app.post("/sentiment/analyze")
    async def analyze_sentiment(request: SentimentAnalysisRequest):
        result = sentiment.analyze_sentiment(request.text)
        result.session_id = request.session_id
        return result

    @app.post("/sentiment/batch")
    async def analyze_sentiment_batch(texts: BatchTexts):
        return {"results": sentiment.analyze_batch(texts)}

    @app.post("/topic/classify")
    async def classify_topic(request: TopicClassificationRequest):
        result = classifier.classify_topic(request.text)
        result.session_id = request.session_id
        return result

    @app.post("/topic/batch")
    async def classify_topic_batch(texts: BatchTexts):
        return {"results": classifier.classify_batch(texts)}

    @app.get("/stats/session/{session_id}")
    async def session_stats(session_id: str):
        stats = store.get_session_stats(session_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Session not found")
        return stats

    @app.get("/stats/overview")
    async def overview_stats():
        sessions = store.list_sessions()
        total = sum(store.get_session_stats(s).get("total_messages", 0) for s in sessions)
        return {
            "total_sessions": len(sessions),
            "total_messages": total,
            "avg_messages_per_session": total / len(sessions) if sessions else 0,
        }

    @app.get("/health")
    async def health_check():
        components = {
            "storage": store.health_check(),
            "summarizer": summarizer.health_check(),
            "sentiment_analyzer": sentiment.health_check(),
            "topic_classifier": classifier.health_check(),
        }
        return {"status": "healthy" if all(components.values()) else "unhealthy", "components": components}

    @app.get("/api/docs")
    async def api_docs():
        return RedirectResponse(url="/docs")

    return app
