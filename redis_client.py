import redis
import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

from models import ChatMessage, ChatSession, Role

# Load environment variables
load_dotenv()


class RedisClient:
    """Redis client for storing and retrieving chat data"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
    def _serialize_message(self, message: ChatMessage) -> str:
        """Serialize ChatMessage to JSON string"""
        return json.dumps({
            'session_id': message.session_id,
            'role': message.role.value,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'message_id': message.message_id,
            'sentiment': message.sentiment.value if message.sentiment else None,
            'topic': message.topic.value if message.topic else None
        })
    
    def _deserialize_message(self, message_data: str) -> ChatMessage:
        """Deserialize JSON string to ChatMessage"""
        data = json.loads(message_data)
        return ChatMessage(
            session_id=data['session_id'],
            role=Role(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_id=data['message_id'],
            sentiment=data['sentiment'],
            topic=data['topic']
        )
    
    def _serialize_session(self, session: ChatSession) -> str:
        """Serialize ChatSession to JSON string"""
        return json.dumps({
            'session_id': session.session_id,
            'messages': [self._serialize_message(msg) for msg in session.messages],
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        })
    
    def _deserialize_session(self, session_data: str) -> ChatSession:
        """Deserialize JSON string to ChatSession"""
        data = json.loads(session_data)
        return ChatSession(
            session_id=data['session_id'],
            messages=[self._deserialize_message(msg) for msg in data['messages']],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )
    
    def store_message(self, message: ChatMessage) -> bool:
        """Store a chat message in Redis"""
        try:
            # Generate message ID if not provided
            if not message.message_id:
                message.message_id = str(uuid.uuid4())
            
            # Store individual message
            message_key = f"message:{message.session_id}:{message.message_id}"
            self.redis_client.set(message_key, self._serialize_message(message))
            
            # Add message to session list
            session_key = f"session:{message.session_id}"
            self.redis_client.lpush(session_key, message.message_id)
            
            # Update session metadata
            self._update_session_metadata(message.session_id)
            
            return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Retrieve all messages for a session"""
        try:
            session_key = f"session:{session_id}"
            message_ids = self.redis_client.lrange(session_key, 0, -1)
            
            messages = []
            for msg_id in message_ids:
                message_key = f"message:{session_id}:{msg_id}"
                message_data = self.redis_client.get(message_key)
                if message_data:
                    messages.append(self._deserialize_message(message_data))
            
            # Sort by timestamp
            messages.sort(key=lambda x: x.timestamp)
            return messages
        except Exception as e:
            print(f"Error retrieving session messages: {e}")
            return []
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a complete chat session"""
        try:
            messages = self.get_session_messages(session_id)
            if not messages:
                return None
            
            # Get session metadata
            metadata_key = f"session_metadata:{session_id}"
            metadata = self.redis_client.hgetall(metadata_key)
            
            created_at = datetime.fromisoformat(metadata.get('created_at', datetime.now().isoformat()))
            updated_at = datetime.fromisoformat(metadata.get('updated_at', datetime.now().isoformat()))
            
            return ChatSession(
                session_id=session_id,
                messages=messages,
                created_at=created_at,
                updated_at=updated_at
            )
        except Exception as e:
            print(f"Error retrieving session: {e}")
            return None
    
    def _update_session_metadata(self, session_id: str):
        """Update session metadata"""
        try:
            metadata_key = f"session_metadata:{session_id}"
            now = datetime.now().isoformat()
            
            # Check if session exists
            if not self.redis_client.exists(metadata_key):
                self.redis_client.hset(metadata_key, 'created_at', now)
            
            self.redis_client.hset(metadata_key, 'updated_at', now)
        except Exception as e:
            print(f"Error updating session metadata: {e}")
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        try:
            pattern = "session_metadata:*"
            keys = self.redis_client.keys(pattern)
            return [key.split(':')[1] for key in keys]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        try:
            # Get all message IDs for the session
            session_key = f"session:{session_id}"
            message_ids = self.redis_client.lrange(session_key, 0, -1)
            
            # Delete individual messages
            for msg_id in message_ids:
                message_key = f"message:{session_id}:{msg_id}"
                self.redis_client.delete(message_key)
            
            # Delete session list and metadata
            self.redis_client.delete(session_key)
            self.redis_client.delete(f"session_metadata:{session_id}")
            
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        try:
            messages = self.get_session_messages(session_id)
            if not messages:
                return {}
            
            user_messages = len([m for m in messages if m.role == Role.USER])
            assistant_messages = len([m for m in messages if m.role == Role.ASSISTANT])
            
            # Calculate sentiment distribution
            sentiments = [m.sentiment for m in messages if m.sentiment]
            sentiment_dist = {}
            if sentiments:
                for sentiment in sentiments:
                    sentiment_dist[sentiment.value] = sentiment_dist.get(sentiment.value, 0) + 1
            
            # Calculate topic distribution
            topics = [m.topic for m in messages if m.topic]
            topic_dist = {}
            if topics:
                for topic in topics:
                    topic_dist[topic.value] = topic_dist.get(topic.value, 0) + 1
            
            return {
                'session_id': session_id,
                'total_messages': len(messages),
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'sentiment_distribution': sentiment_dist,
                'topic_distribution': topic_dist,
                'created_at': messages[0].timestamp if messages else None,
                'last_activity': messages[-1].timestamp if messages else None
            }
        except Exception as e:
            print(f"Error getting session stats: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False 