import json

from chat_summarizer.config import Settings
from chat_summarizer.models import ChatMessage, Role, Sentiment, TopicCategory
from chat_summarizer.storage import MemoryStore
from chat_summarizer.summarizer import ChatSummarizer, extractive_summary, format_chat


def seeded(llm=None):
    store = MemoryStore()
    for role, text in [
        (Role.USER, "My invoice is wrong. Can you check the invoice total?"),
        (Role.ASSISTANT, "Sure, the invoice total was corrected."),
    ]:
        store.store_message(ChatMessage(
            session_id="s", role=role, content=text,
            sentiment=Sentiment.NEUTRAL, topic=TopicCategory.QUESTION,
        ))
    return ChatSummarizer(store, llm)


def test_format_chat_includes_metadata():
    text = format_chat(seeded().store.get_session_messages("s"))
    assert "User [Sentiment: neutral] [Topic: question]" in text and "Assistant" in text


def test_extractive_respects_budget():
    msgs = seeded().store.get_session_messages("s")
    out = extractive_summary(msgs, 8)
    assert out and len(out.split()) <= 12
    assert extractive_summary([], 10) == ""


def test_empty_session():
    s = ChatSummarizer(MemoryStore())
    assert s.generate_summary("x").message_count == 0
    assert s.generate_brief_summary("x") == "No messages in this session."
    assert s.generate_structured_summary("x") == {"error": "No messages found"}
    assert s.health_check()


def test_llm_used_when_available():
    s = seeded(lambda prompt: "  LLM says hi  ")
    r = s.generate_summary("s", 100)
    assert r.summary == "LLM says hi" and r.message_count == 2
    assert s.generate_brief_summary("s") == "LLM says hi"


def test_llm_failure_falls_back():
    def boom(prompt):
        raise RuntimeError("api down")

    s = seeded(boom)
    assert "invoice" in s.generate_summary("s").summary
    assert "invoice" in s.generate_brief_summary("s")
    assert "main_topics" in s.generate_structured_summary("s")


def test_structured_llm_json_and_raw():
    payload = {"main_topics": ["billing"]}
    assert seeded(lambda p: "sure " + json.dumps(payload)).generate_structured_summary("s") == payload
    assert seeded(lambda p: "no json").generate_structured_summary("s") == {"raw_summary": "no json"}
    assert seeded(lambda p: "{bad json}").generate_structured_summary("s") == {"raw_summary": "{bad json}"}


def test_structured_fallback_content():
    out = seeded().generate_structured_summary("s")
    assert out["participant_count"] == 2
    assert out["questions_asked"] == ["My invoice is wrong. Can you check the invoice total?"]
    assert out["overall_sentiment"] == "neutral"


def test_from_settings_without_key_has_no_llm():
    assert ChatSummarizer.from_settings(MemoryStore(), Settings()).llm is None
