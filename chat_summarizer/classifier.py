"""Keyword-based topic classification (no ML dependencies)."""
import re

from .models import TopicCategory, TopicClassificationResponse

TOPIC_KEYWORDS: dict[TopicCategory, list[str]] = {
    TopicCategory.COMPLAINT: [
        "complaint", "problem", "issue", "error", "bug", "broken", "not working",
        "doesn't work", "failed", "failure", "disappointed", "unhappy", "angry",
        "frustrated", "terrible", "awful", "horrible", "worst", "bad",
    ],
    TopicCategory.QUESTION: [
        "question", "what", "how", "why", "when", "where", "can you", "could you",
        "would you", "do you", "is it", "are you", "does it", "will it", "explain",
        "clarify",
    ],
    TopicCategory.SUPPORT_REQUEST: [
        "help", "support", "assist", "assistance", "need help", "troubleshoot",
        "fix", "resolve", "solve", "technical support", "customer service",
    ],
    TopicCategory.PURCHASE_INTENT: [
        "buy", "purchase", "order", "price", "cost", "payment", "subscription",
        "plan", "package", "deal", "offer", "discount", "sale", "buying",
        "interested in",
    ],
    TopicCategory.FEEDBACK: [
        "feedback", "review", "rating", "opinion", "thoughts", "experience",
        "suggestion", "recommendation", "advice", "improvement", "feature request",
        "comment",
    ],
}

_PATTERNS = {
    topic: [re.compile(r"\b" + re.escape(k) + r"\b", re.IGNORECASE) for k in kws]
    for topic, kws in TOPIC_KEYWORDS.items()
}


class TopicClassifier:
    def classify_topic(self, text: str) -> TopicClassificationResponse:
        scores = {
            topic: sum(len(p.findall(text)) for p in patterns)
            for topic, patterns in _PATTERNS.items()
        }
        scores = {t: s for t, s in scores.items() if s > 0}
        if not scores:
            return TopicClassificationResponse(text=text, topic=TopicCategory.OTHER, confidence=0.3)
        best = max(scores, key=lambda t: scores[t])
        return TopicClassificationResponse(
            text=text, topic=best, confidence=min(scores[best] / 3.0, 0.95)
        )

    def classify_batch(self, texts: list[str]) -> list[TopicClassificationResponse]:
        return [self.classify_topic(t) for t in texts]

    def health_check(self) -> bool:
        return self.classify_topic("I have a question about your product").topic == TopicCategory.QUESTION
