from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from models import Sentiment, SentimentAnalysisResponse

# Load environment variables
load_dotenv()


class SentimentAnalyzer:
    """Sentiment analysis using HuggingFace transformers"""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        """Initialize sentiment analyzer with specified model"""
        self.model_name = model_name
        self.analyzer = None
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentiment analysis model"""
        try:
            print(f"Loading sentiment model: {self.model_name}")
            
            # Use pipeline for easier inference
            self.analyzer = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print("Sentiment model loaded successfully")
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
            # Fallback to a simpler model
            try:
                self.analyzer = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment",
                    device=0 if torch.cuda.is_available() else -1
                )
                print("Fallback sentiment model loaded")
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                self.analyzer = None
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysisResponse:
        """Analyze sentiment of given text"""
        if not self.analyzer:
            return SentimentAnalysisResponse(
                text=text,
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0
            )
        
        try:
            # Perform sentiment analysis
            result = self.analyzer(text)[0]
            
            # Map model output to our sentiment enum
            label = result['label'].lower()
            confidence = result['score']
            
            # Handle different model output formats
            if 'pos' in label or 'positive' in label:
                sentiment = Sentiment.POSITIVE
            elif 'neg' in label or 'negative' in label:
                sentiment = Sentiment.NEGATIVE
            else:
                sentiment = Sentiment.NEUTRAL
            
            return SentimentAnalysisResponse(
                text=text,
                sentiment=sentiment,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return SentimentAnalysisResponse(
                text=text,
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0
            )
    
    def analyze_batch(self, texts: list) -> list[SentimentAnalysisResponse]:
        """Analyze sentiment for multiple texts"""
        if not self.analyzer:
            return [
                SentimentAnalysisResponse(
                    text=text,
                    sentiment=Sentiment.NEUTRAL,
                    confidence=0.0
                ) for text in texts
            ]
        
        try:
            # Batch processing
            results = self.analyzer(texts)
            
            responses = []
            for text, result in zip(texts, results):
                label = result['label'].lower()
                confidence = result['score']
                
                if 'pos' in label or 'positive' in label:
                    sentiment = Sentiment.POSITIVE
                elif 'neg' in label or 'negative' in label:
                    sentiment = Sentiment.NEGATIVE
                else:
                    sentiment = Sentiment.NEUTRAL
                
                responses.append(SentimentAnalysisResponse(
                    text=text,
                    sentiment=sentiment,
                    confidence=confidence
                ))
            
            return responses
            
        except Exception as e:
            print(f"Error in batch sentiment analysis: {e}")
            return [
                SentimentAnalysisResponse(
                    text=text,
                    sentiment=Sentiment.NEUTRAL,
                    confidence=0.0
                ) for text in texts
            ]
    
    def get_sentiment_score(self, text: str) -> float:
        """Get numerical sentiment score (-1 to 1)"""
        response = self.analyze_sentiment(text)
        
        if response.sentiment == Sentiment.POSITIVE:
            return response.confidence
        elif response.sentiment == Sentiment.NEGATIVE:
            return -response.confidence
        else:
            return 0.0
    
    def health_check(self) -> bool:
        """Check if sentiment analyzer is working"""
        try:
            test_text = "I love this product!"
            result = self.analyze_sentiment(test_text)
            return result.sentiment in [Sentiment.POSITIVE, Sentiment.NEUTRAL]
        except Exception as e:
            print(f"Sentiment analyzer health check failed: {e}")
            return False


# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer() 