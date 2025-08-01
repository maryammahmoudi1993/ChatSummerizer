from typing import List, Dict, Any, Optional
import re
import os
from dotenv import load_dotenv

from models import TopicCategory, TopicClassificationResponse

# Load environment variables
load_dotenv()


class SimpleTopicClassifier:
    """Simple topic classification using keyword-based approach"""
    
    def __init__(self):
        """Initialize the simple topic classifier"""
        self.topic_keywords = {
            TopicCategory.COMPLAINT: [
                'complaint', 'problem', 'issue', 'error', 'bug', 'broken',
                'not working', 'doesn\'t work', 'failed', 'failure',
                'disappointed', 'unhappy', 'angry', 'frustrated',
                'terrible', 'awful', 'horrible', 'worst', 'bad'
            ],
            TopicCategory.QUESTION: [
                'question', 'what', 'how', 'why', 'when', 'where',
                'can you', 'could you', 'would you', 'do you',
                'is it', 'are you', 'does it', 'will it',
                'help me understand', 'explain', 'clarify'
            ],
            TopicCategory.SUPPORT_REQUEST: [
                'help', 'support', 'assist', 'assistance', 'need help',
                'troubleshoot', 'fix', 'resolve', 'solve', 'issue',
                'problem', 'broken', 'not working', 'error',
                'technical support', 'customer service'
            ],
            TopicCategory.PURCHASE_INTENT: [
                'buy', 'purchase', 'order', 'price', 'cost', 'payment',
                'subscription', 'plan', 'package', 'deal', 'offer',
                'discount', 'sale', 'buying', 'interested in',
                'want to buy', 'looking to purchase', 'cost'
            ],
            TopicCategory.FEEDBACK: [
                'feedback', 'review', 'rating', 'opinion', 'thoughts',
                'experience', 'suggestion', 'recommendation', 'advice',
                'improvement', 'feature request', 'comment'
            ]
        }
        
        # Compile regex patterns for better matching
        self.topic_patterns = {}
        for topic, keywords in self.topic_keywords.items():
            patterns = []
            for keyword in keywords:
                # Create case-insensitive pattern
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                patterns.append(pattern)
            self.topic_patterns[topic] = patterns
    
    def _map_label_to_topic(self, label: str) -> TopicCategory:
        """Map classifier label to TopicCategory enum"""
        label_lower = label.lower()
        
        if "complaint" in label_lower:
            return TopicCategory.COMPLAINT
        elif "question" in label_lower:
            return TopicCategory.QUESTION
        elif "support" in label_lower or "help" in label_lower:
            return TopicCategory.SUPPORT_REQUEST
        elif "purchase" in label_lower or "buy" in label_lower or "order" in label_lower:
            return TopicCategory.PURCHASE_INTENT
        elif "feedback" in label_lower or "review" in label_lower:
            return TopicCategory.FEEDBACK
        else:
            return TopicCategory.OTHER
    
    def classify_topic(self, text: str) -> TopicClassificationResponse:
        """Classify topic of given text using keyword matching"""
        try:
            text_lower = text.lower()
            topic_scores = {}
            
            # Calculate scores for each topic
            for topic, patterns in self.topic_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = pattern.findall(text_lower)
                    score += len(matches)
                
                if score > 0:
                    topic_scores[topic] = score
            
            # Find the topic with highest score
            if topic_scores:
                best_topic = max(topic_scores, key=topic_scores.get)
                confidence = min(topic_scores[best_topic] / 3.0, 0.95)  # Normalize confidence
            else:
                best_topic = TopicCategory.OTHER
                confidence = 0.3
            
            return TopicClassificationResponse(
                text=text,
                topic=best_topic,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Error in topic classification: {e}")
            return TopicClassificationResponse(
                text=text,
                topic=TopicCategory.OTHER,
                confidence=0.3
            )
    
    def classify_batch(self, texts: List[str]) -> List[TopicClassificationResponse]:
        """Classify topics for multiple texts"""
        responses = []
        for text in texts:
            response = self.classify_topic(text)
            responses.append(response)
        return responses
    
    def get_topic_distribution(self, texts: List[str]) -> Dict[str, int]:
        """Get distribution of topics across multiple texts"""
        responses = self.classify_batch(texts)
        
        distribution = {}
        for response in responses:
            topic = response.topic.value
            distribution[topic] = distribution.get(topic, 0) + 1
        
        return distribution
    
    def classify_with_custom_labels(self, text: str, custom_labels: List[str]) -> Dict[str, float]:
        """Classify text with custom labels (simplified version)"""
        # For custom labels, we'll use a simple approach
        result = {}
        for label in custom_labels:
            # Simple keyword matching for custom labels
            if label.lower() in text.lower():
                result[label] = 0.7
            else:
                result[label] = 0.1
        return result
    
    def health_check(self) -> bool:
        """Check if topic classifier is working"""
        try:
            test_text = "I have a question about your product"
            result = self.classify_topic(test_text)
            return result.topic in [TopicCategory.QUESTION, TopicCategory.OTHER]
        except Exception as e:
            print(f"Topic classifier health check failed: {e}")
            return False


# Global topic classifier instance
topic_classifier = SimpleTopicClassifier() 