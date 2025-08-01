import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

from models import ChatMessage, ChatSession, Role

# Load environment variables
load_dotenv()


class MemoryClient:
    """In-memory storage client as alternative to Redis"""
    
    def __init__(self):
        """Initialize in-memory storage"""
        self.messages = {}  # message_id -> message_data
        self.sessions = {}  # session_id -> list of message_ids
        self.session_metadata = {}  # session_id -> metadata
        
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
        """Store a chat message in memory"""
        try:
            # Generate message ID if not provided
            if not message.message_id:
                message.message_id = str(uuid.uuid4())
            
            # Store individual message
            self.messages[message.message_id] = self._serialize_message(message)
            
            # Add message to session list
            if message.session_id not in self.sessions:
                self.sessions[message.session_id] = []
            self.sessions[message.session_id].insert(0, message.message_id)
            
            # Update session metadata
            self._update_session_metadata(message.session_id)
            
            return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Retrieve all messages for a session"""
        try:
            if session_id not in self.sessions:
                return []
            
            message_ids = self.sessions[session_id]
            messages = []
            
            for message_id in reversed(message_ids):  # Reverse to get chronological order
                if message_id in self.messages:
                    message_data = self.messages[message_id]
                    messages.append(self._deserialize_message(message_data))
            
            return messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a complete chat session"""
        try:
            messages = self.get_session_messages(session_id)
            if not messages:
                return None
            
            # Get session metadata
            metadata = self.session_metadata.get(session_id, {})
            created_at = metadata.get('created_at', messages[0].timestamp)
            updated_at = metadata.get('updated_at', messages[-1].timestamp)
            
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
            if session_id not in self.session_metadata:
                self.session_metadata[session_id] = {
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            else:
                self.session_metadata[session_id]['updated_at'] = datetime.now()
        except Exception as e:
            print(f"Error updating session metadata: {e}")
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        try:
            return list(self.sessions.keys())
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        try:
            if session_id in self.sessions:
                # Remove all messages for this session
                message_ids = self.sessions[session_id]
                for message_id in message_ids:
                    if message_id in self.messages:
                        del self.messages[message_id]
                
                # Remove session
                del self.sessions[session_id]
                
                # Remove metadata
                if session_id in self.session_metadata:
                    del self.session_metadata[session_id]
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        try:
            messages = self.get_session_messages(session_id)
            if not messages:
                return {}
            
            # Count messages by role
            user_messages = len([m for m in messages if m.role == Role.USER])
            assistant_messages = len([m for m in messages if m.role == Role.ASSISTANT])
            
            # Count sentiments
            sentiment_counts = {}
            for message in messages:
                if message.sentiment:
                    sentiment = message.sentiment.value
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Count topics
            topic_counts = {}
            for message in messages:
                if message.topic:
                    topic = message.topic.value
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            return {
                'total_messages': len(messages),
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'sentiment_distribution': sentiment_counts,
                'topic_distribution': topic_counts,
                'session_duration': (messages[-1].timestamp - messages[0].timestamp).total_seconds() if len(messages) > 1 else 0
            }
        except Exception as e:
            print(f"Error getting session stats: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Check if the storage is healthy"""
        try:
            # Simple health check - try to access the storage
            _ = len(self.messages)
            _ = len(self.sessions)
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False 