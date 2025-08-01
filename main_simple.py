from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from typing import List, Optional
from dotenv import load_dotenv

from models import (
    ChatMessage, Role, SummaryRequest, SummaryResponse,
    SentimentAnalysisRequest, SentimentAnalysisResponse,
    TopicClassificationRequest, TopicClassificationResponse,
    ChatStats
)
from redis_client import RedisClient
from summarizer import chat_summarizer

# Import simple versions instead of full ML versions
try:
    from sentiment import sentiment_analyzer
    from classifier import topic_classifier
    print("✅ Using full ML models")
except ImportError:
    try:
        from sentiment_simple import sentiment_analyzer
        from classifier_simple import topic_classifier
        print("✅ Using simple rule-based models")
    except ImportError:
        print("❌ No sentiment/classifier modules found")
        sentiment_analyzer = None
        topic_classifier = None

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Chat Summarizer API (Simple Version)",
    description="A comprehensive chat summarization system with sentiment analysis and topic classification",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
redis_client = RedisClient()
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main chat interface"""
    sessions = redis_client.list_sessions()
    return templates.TemplateResponse("index.html", {"request": request, "sessions": sessions})


@app.post("/chat/send")
async def send_message(
    session_id: str = Form(...),
    role: str = Form(...),
    content: str = Form(...)
):
    """Send a chat message"""
    try:
        # Validate role
        if role not in [Role.USER.value, Role.ASSISTANT.value]:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        # Create message
        message = ChatMessage(
            session_id=session_id,
            role=Role(role),
            content=content
        )
        
        # Analyze sentiment and topic (if analyzers are available)
        sentiment_result = None
        topic_result = None
        
        if sentiment_analyzer:
            sentiment_result = sentiment_analyzer.analyze_sentiment(content)
            message.sentiment = sentiment_result.sentiment
        
        if topic_classifier:
            topic_result = topic_classifier.classify_topic(content)
            message.topic = topic_result.topic
        
        # Store in Redis
        success = redis_client.store_message(message)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store message")
        
        response_data = {
            "message_id": message.message_id,
        }
        
        if sentiment_result:
            response_data["sentiment"] = sentiment_result.sentiment.value
            response_data["confidence"] = {"sentiment": sentiment_result.confidence}
        
        if topic_result:
            response_data["topic"] = topic_result.topic.value
            if "confidence" not in response_data:
                response_data["confidence"] = {}
            response_data["confidence"]["topic"] = topic_result.confidence
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/session/{session_id}")
async def get_session(session_id: str):
    """Get all messages for a session"""
    try:
        messages = redis_client.get_session_messages(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/sessions")
async def list_sessions():
    """List all chat sessions"""
    try:
        sessions = redis_client.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chat/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        success = redis_client.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summary/generate")
async def generate_summary(request: SummaryRequest):
    """Generate a summary for a chat session"""
    try:
        summary = chat_summarizer.generate_summary(
            request.session_id,
            request.max_length
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summary/brief/{session_id}")
async def get_brief_summary(session_id: str):
    """Get a brief summary for a session"""
    try:
        summary = chat_summarizer.generate_brief_summary(session_id)
        return {"session_id": session_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summary/structured/{session_id}")
async def get_structured_summary(session_id: str):
    """Get a structured summary for a session"""
    try:
        summary = chat_summarizer.generate_structured_summary(session_id)
        return {"session_id": session_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment/analyze")
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyze sentiment of text"""
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analyzer not available")
    
    try:
        result = sentiment_analyzer.analyze_sentiment(request.text)
        result.session_id = request.session_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment/batch")
async def analyze_sentiment_batch(texts: List[str]):
    """Analyze sentiment for multiple texts"""
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analyzer not available")
    
    try:
        results = sentiment_analyzer.analyze_batch(texts)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/topic/classify")
async def classify_topic(request: TopicClassificationRequest):
    """Classify topic of text"""
    if not topic_classifier:
        raise HTTPException(status_code=503, detail="Topic classifier not available")
    
    try:
        result = topic_classifier.classify_topic(request.text)
        result.session_id = request.session_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/topic/batch")
async def classify_topic_batch(texts: List[str]):
    """Classify topics for multiple texts"""
    if not topic_classifier:
        raise HTTPException(status_code=503, detail="Topic classifier not available")
    
    try:
        results = topic_classifier.classify_batch(texts)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/session/{session_id}")
async def get_session_stats(session_id: str):
    """Get statistics for a session"""
    try:
        stats = redis_client.get_session_stats(session_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Session not found")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/overview")
async def get_overview_stats():
    """Get overview statistics for all sessions"""
    try:
        sessions = redis_client.list_sessions()
        total_sessions = len(sessions)
        total_messages = 0
        
        for session_id in sessions:
            stats = redis_client.get_session_stats(session_id)
            if stats:
                total_messages += stats.get('total_messages', 0)
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_health = redis_client.health_check()
        summarizer_health = chat_summarizer.health_check()
        
        sentiment_health = False
        if sentiment_analyzer:
            sentiment_health = sentiment_analyzer.health_check()
        
        classifier_health = False
        if topic_classifier:
            classifier_health = topic_classifier.health_check()
        
        return {
            "status": "healthy" if all([redis_health, summarizer_health]) else "unhealthy",
            "components": {
                "redis": redis_health,
                "summarizer": summarizer_health,
                "sentiment_analyzer": sentiment_health,
                "topic_classifier": classifier_health
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/docs")
async def api_docs():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Chat Summarizer API (Simple Version) on {host}:{port}")
    print("Health check available at /health")
    print("API documentation available at /docs")
    
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        reload=debug
    ) 