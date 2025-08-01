from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from models import Sentiment, SentimentAnalysisResponse

# Load environment variables
load_dotenv()


class SimpleSentimentAnalyzer:
    """Simple sentiment analysis using rule-based approach"""
    
    def __init__(self):
        """Initialize the simple sentiment analyzer"""
        self.positive_words = {
            'love', 'like', 'great', 'good', 'excellent', 'amazing', 'wonderful',
            'fantastic', 'awesome', 'perfect', 'best', 'happy', 'pleased',
            'satisfied', 'enjoy', 'enjoyed', 'enjoying', 'wonderful', 'brilliant',
            'outstanding', 'superb', 'terrific', 'fabulous', 'marvelous',
            'delighted', 'thrilled', 'excited', 'impressed', 'recommend'
        }
        
        self.negative_words = {
            'hate', 'dislike', 'terrible', 'bad', 'awful', 'horrible', 'worst',
            'disappointed', 'unhappy', 'angry', 'frustrated', 'annoyed',
            'upset', 'sad', 'depressed', 'miserable', 'awful', 'dreadful',
            'atrocious', 'abysmal', 'pathetic', 'useless', 'worthless',
            'waste', 'regret', 'sorry', 'complaint', 'problem', 'issue'
        }
        
        self.intensifiers = {
            'very', 'really', 'extremely', 'absolutely', 'completely',
            'totally', 'utterly', 'incredibly', 'exceptionally'
        }
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysisResponse:
        """Analyze sentiment of given text using rule-based approach"""
        try:
            # Convert to lowercase for analysis
            text_lower = text.lower()
            words = text_lower.split()
            
            # Count positive and negative words
            positive_count = 0
            negative_count = 0
            intensifier_count = 0
            
            for word in words:
                # Remove punctuation
                clean_word = word.strip('.,!?;:')
                
                if clean_word in self.positive_words:
                    positive_count += 1
                elif clean_word in self.negative_words:
                    negative_count += 1
                elif clean_word in self.intensifiers:
                    intensifier_count += 1
            
            # Calculate sentiment score
            total_words = len(words)
            if total_words == 0:
                return SentimentAnalysisResponse(
                    text=text,
                    sentiment=Sentiment.NEUTRAL,
                    confidence=0.5
                )
            
            # Simple scoring algorithm
            positive_score = positive_count / total_words
            negative_score = negative_count / total_words
            
            # Apply intensifier boost
            if intensifier_count > 0:
                positive_score *= (1 + intensifier_count * 0.2)
                negative_score *= (1 + intensifier_count * 0.2)
            
            # Determine sentiment
            if positive_score > negative_score and positive_score > 0.05:
                sentiment = Sentiment.POSITIVE
                confidence = min(positive_score * 2, 0.95)
            elif negative_score > positive_score and negative_score > 0.05:
                sentiment = Sentiment.NEGATIVE
                confidence = min(negative_score * 2, 0.95)
            else:
                sentiment = Sentiment.NEUTRAL
                confidence = 0.6
            
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
                confidence=0.5
            )
    
    def analyze_batch(self, texts: list) -> list[SentimentAnalysisResponse]:
        """Analyze sentiment for multiple texts"""
        responses = []
        for text in texts:
            response = self.analyze_sentiment(text)
            responses.append(response)
        return responses
    
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
            return result.sentiment == Sentiment.POSITIVE
        except Exception as e:
            print(f"Sentiment analyzer health check failed: {e}")
            return False


# Global sentiment analyzer instance
sentiment_analyzer = SimpleSentimentAnalyzer() 