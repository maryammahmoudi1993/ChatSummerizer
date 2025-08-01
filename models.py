from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class Role(str, Enum):
    """Enum for message roles"""
    USER = "user"
    ASSISTANT = "assistant"


class Sentiment(str, Enum):
    """Enum for sentiment analysis results"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class TopicCategory(str, Enum):
    """Enum for topic classification categories"""
    COMPLAINT = "complaint"
    QUESTION = "question"
    SUPPORT_REQUEST = "support_request"
    PURCHASE_INTENT = "purchase_intent"
    FEEDBACK = "feedback"
    OTHER = "other"


class ChatMessage(BaseModel):
    """Model for individual chat messages"""
    session_id: str = Field(..., description="Unique session identifier")
    role: Role = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    message_id: Optional[str] = Field(None, description="Unique message identifier")
    sentiment: Optional[Sentiment] = Field(None, description="Sentiment analysis result")
    topic: Optional[TopicCategory] = Field(None, description="Topic classification result")


class ChatSession(BaseModel):
    """Model for chat sessions"""
    session_id: str = Field(..., description="Unique session identifier")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages in the session")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Session last update timestamp")


class SummaryRequest(BaseModel):
    """Model for summary generation requests"""
    session_id: str = Field(..., description="Session ID to summarize")
    max_length: Optional[int] = Field(500, description="Maximum summary length")


class SummaryResponse(BaseModel):
    """Model for summary responses"""
    session_id: str = Field(..., description="Session ID")
    summary: str = Field(..., description="Generated summary")
    message_count: int = Field(..., description="Number of messages summarized")
    generated_at: datetime = Field(default_factory=datetime.now, description="Summary generation timestamp")


class SentimentAnalysisRequest(BaseModel):
    """Model for sentiment analysis requests"""
    text: str = Field(..., description="Text to analyze")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class SentimentAnalysisResponse(BaseModel):
    """Model for sentiment analysis responses"""
    text: str = Field(..., description="Analyzed text")
    sentiment: Sentiment = Field(..., description="Detected sentiment")
    confidence: float = Field(..., description="Confidence score")
    session_id: Optional[str] = Field(None, description="Session ID")


class TopicClassificationRequest(BaseModel):
    """Model for topic classification requests"""
    text: str = Field(..., description="Text to classify")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class TopicClassificationResponse(BaseModel):
    """Model for topic classification responses"""
    text: str = Field(..., description="Classified text")
    topic: TopicCategory = Field(..., description="Detected topic")
    confidence: float = Field(..., description="Confidence score")
    session_id: Optional[str] = Field(None, description="Session ID")


class ChatStats(BaseModel):
    """Model for chat session statistics"""
    session_id: str = Field(..., description="Session ID")
    total_messages: int = Field(..., description="Total number of messages")
    user_messages: int = Field(..., description="Number of user messages")
    assistant_messages: int = Field(..., description="Number of assistant messages")
    avg_sentiment: Optional[float] = Field(None, description="Average sentiment score")
    topic_distribution: dict = Field(default_factory=dict, description="Distribution of topics")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp") 