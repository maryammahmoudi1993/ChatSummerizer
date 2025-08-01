from transformers import pipeline
import torch
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from models import TopicCategory, TopicClassificationResponse

# Load environment variables
load_dotenv()


class TopicClassifier:
    """Topic classification using zero-shot classification"""
    
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """Initialize topic classifier with specified model"""
        self.model_name = model_name
        self.classifier = None
        self.candidate_labels = [
            "complaint",
            "question", 
            "support request",
            "purchase intent",
            "feedback",
            "other"
        ]
        self._load_model()
    
    def _load_model(self):
        """Load the zero-shot classification model"""
        try:
            print(f"Loading topic classification model: {self.model_name}")
            
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print("Topic classification model loaded successfully")
        except Exception as e:
            print(f"Error loading topic classification model: {e}")
            # Fallback to a simpler model
            try:
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="microsoft/DialoGPT-medium",
                    device=0 if torch.cuda.is_available() else -1
                )
                print("Fallback topic classification model loaded")
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                self.classifier = None
    
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
        """Classify topic of given text"""
        if not self.classifier:
            return TopicClassificationResponse(
                text=text,
                topic=TopicCategory.OTHER,
                confidence=0.0
            )
        
        try:
            # Perform zero-shot classification
            result = self.classifier(
                text,
                candidate_labels=self.candidate_labels,
                hypothesis_template="This text is about {}."
            )
            
            # Get the best label and confidence
            best_label = result['labels'][0]
            confidence = result['scores'][0]
            
            # Map to our topic category
            topic = self._map_label_to_topic(best_label)
            
            return TopicClassificationResponse(
                text=text,
                topic=topic,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Error in topic classification: {e}")
            return TopicClassificationResponse(
                text=text,
                topic=TopicCategory.OTHER,
                confidence=0.0
            )
    
    def classify_batch(self, texts: List[str]) -> List[TopicClassificationResponse]:
        """Classify topics for multiple texts"""
        if not self.classifier:
            return [
                TopicClassificationResponse(
                    text=text,
                    topic=TopicCategory.OTHER,
                    confidence=0.0
                ) for text in texts
            ]
        
        try:
            responses = []
            for text in texts:
                response = self.classify_topic(text)
                responses.append(response)
            
            return responses
            
        except Exception as e:
            print(f"Error in batch topic classification: {e}")
            return [
                TopicClassificationResponse(
                    text=text,
                    topic=TopicCategory.OTHER,
                    confidence=0.0
                ) for text in texts
            ]
    
    def get_topic_distribution(self, texts: List[str]) -> Dict[str, int]:
        """Get distribution of topics across multiple texts"""
        responses = self.classify_batch(texts)
        
        distribution = {}
        for response in responses:
            topic = response.topic.value
            distribution[topic] = distribution.get(topic, 0) + 1
        
        return distribution
    
    def classify_with_custom_labels(self, text: str, custom_labels: List[str]) -> Dict[str, float]:
        """Classify text with custom labels"""
        if not self.classifier:
            return {label: 0.0 for label in custom_labels}
        
        try:
            result = self.classifier(
                text,
                candidate_labels=custom_labels,
                hypothesis_template="This text is about {}."
            )
            
            return dict(zip(result['labels'], result['scores']))
            
        except Exception as e:
            print(f"Error in custom classification: {e}")
            return {label: 0.0 for label in custom_labels}
    
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
topic_classifier = TopicClassifier() 