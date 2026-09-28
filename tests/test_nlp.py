import pytest

from chat_summarizer.classifier import TopicClassifier
from chat_summarizer.models import Sentiment, TopicCategory
from chat_summarizer.sentiment import SentimentAnalyzer

sa, tc = SentimentAnalyzer(), TopicClassifier()


@pytest.mark.parametrize("text,expected", [
    ("I love this, it is great!", Sentiment.POSITIVE),
    ("This is terrible and I hate it", Sentiment.NEGATIVE),
    ("The meeting is at noon", Sentiment.NEUTRAL),
    ("", Sentiment.NEUTRAL),
    ("!!!", Sentiment.NEUTRAL),
])
def test_sentiment(text, expected):
    assert sa.analyze_sentiment(text).sentiment == expected


def test_intensifier_raises_confidence():
    plain = sa.analyze_sentiment("great service and a fine day today folks").confidence
    boosted = sa.analyze_sentiment("really great service and a fine day today").confidence
    assert boosted > plain


def test_confidence_capped():
    assert sa.analyze_sentiment("love love love").confidence <= 0.95


def test_score_sign_and_batch():
    assert sa.get_sentiment_score("I love it") > 0
    assert sa.get_sentiment_score("I hate it") < 0
    assert sa.get_sentiment_score("noon") == 0
    assert len(sa.analyze_batch(["a", "b", "c"])) == 3
    assert sa.health_check()


@pytest.mark.parametrize("text,expected", [
    ("How do I reset my password?", TopicCategory.QUESTION),
    ("This is broken and I am frustrated", TopicCategory.COMPLAINT),
    ("I want to buy the premium plan, what is the price", TopicCategory.PURCHASE_INTENT),
    ("Here is my feedback and suggestion", TopicCategory.FEEDBACK),
    ("I need help, please assist", TopicCategory.SUPPORT_REQUEST),
    ("zzz qqq", TopicCategory.OTHER),
])
def test_topics(text, expected):
    assert tc.classify_topic(text).topic == expected


def test_topic_batch_and_health():
    assert len(tc.classify_batch(["a", "b"])) == 2
    assert tc.health_check()
    assert tc.classify_topic("zzz").confidence == 0.3
