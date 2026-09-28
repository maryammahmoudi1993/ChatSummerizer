"""Rule-based sentiment analysis (no ML dependencies)."""
import re

from .models import Sentiment, SentimentAnalysisResponse

POSITIVE = {
    "love", "like", "great", "good", "excellent", "amazing", "wonderful",
    "fantastic", "awesome", "perfect", "best", "happy", "pleased", "satisfied",
    "enjoy", "enjoyed", "brilliant", "outstanding", "superb", "terrific",
    "fabulous", "delighted", "thrilled", "excited", "impressed", "recommend",
    "thanks", "thank",
}
NEGATIVE = {
    "hate", "dislike", "terrible", "bad", "awful", "horrible", "worst",
    "disappointed", "unhappy", "angry", "frustrated", "annoyed", "upset", "sad",
    "miserable", "dreadful", "pathetic", "useless", "worthless", "waste",
    "regret", "sorry", "complaint", "problem", "issue", "broken",
}
INTENSIFIERS = {
    "very", "really", "extremely", "absolutely", "completely", "totally",
    "utterly", "incredibly", "exceptionally",
}
THRESHOLD = 0.05


class SentimentAnalyzer:
    def analyze_sentiment(self, text: str) -> SentimentAnalysisResponse:
        words = re.findall(r"[a-z']+", text.lower())
        if not words:
            return SentimentAnalysisResponse(text=text, sentiment=Sentiment.NEUTRAL, confidence=0.5)

        boost = 1 + 0.2 * sum(w in INTENSIFIERS for w in words)
        pos = sum(w in POSITIVE for w in words) / len(words) * boost
        neg = sum(w in NEGATIVE for w in words) / len(words) * boost

        if pos > neg and pos > THRESHOLD:
            sentiment, confidence = Sentiment.POSITIVE, min(pos * 2, 0.95)
        elif neg > pos and neg > THRESHOLD:
            sentiment, confidence = Sentiment.NEGATIVE, min(neg * 2, 0.95)
        else:
            sentiment, confidence = Sentiment.NEUTRAL, 0.6
        return SentimentAnalysisResponse(text=text, sentiment=sentiment, confidence=confidence)

    def analyze_batch(self, texts: list[str]) -> list[SentimentAnalysisResponse]:
        return [self.analyze_sentiment(t) for t in texts]

    def get_sentiment_score(self, text: str) -> float:
        """Signed score in [-1, 1]."""
        result = self.analyze_sentiment(text)
        if result.sentiment == Sentiment.POSITIVE:
            return result.confidence
        if result.sentiment == Sentiment.NEGATIVE:
            return -result.confidence
        return 0.0

    def health_check(self) -> bool:
        return self.analyze_sentiment("I love this product!").sentiment == Sentiment.POSITIVE
