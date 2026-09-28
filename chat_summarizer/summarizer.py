"""Chat summarization: OpenAI when configured, extractive fallback otherwise."""
import json
import logging
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

from .config import Settings
from .models import ChatMessage, Role, SummaryResponse
from .storage import BaseStore

logger = logging.getLogger(__name__)

LLM = Callable[[str], str]
MODEL = "gpt-4o-mini"

SUMMARY_PROMPT = """You are an expert at summarizing chat conversations.
Summarize the conversation below: main topics, decisions, key questions and
answers, overall sentiment and action items. Use at most {max_length} words.

{text}

Summary:"""
BRIEF_PROMPT = "Summarize this chat conversation in 1-2 sentences:\n\n{text}\n\nSummary:"
STRUCTURED_PROMPT = """Analyze this chat and reply with JSON only, using the keys
main_topics, key_decisions, questions_asked, overall_sentiment, action_items.

{text}

JSON:"""


def openai_llm(api_key: str) -> LLM:  # pragma: no cover - network call
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    def call(prompt: str) -> str:
        response = client.chat.completions.create(
            model=MODEL, temperature=0.3, messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content or ""

    return call


def format_chat(messages: list[ChatMessage]) -> str:
    lines = []
    for m in messages:
        role = "User" if m.role == Role.USER else "Assistant"
        meta = "".join(
            f" [{label}: {value.value}]"
            for label, value in (("Sentiment", m.sentiment), ("Topic", m.topic))
            if value
        )
        lines.append(f"[{m.timestamp:%Y-%m-%d %H:%M:%S}] {role}{meta}: {m.content}")
    return "\n".join(lines)


def extractive_summary(messages: list[ChatMessage], max_words: int) -> str:
    """Offline fallback: pick the sentences with the most frequent content words."""
    sentences = [s.strip() for m in messages for s in re.split(r"(?<=[.!?])\s+", m.content) if s.strip()]
    words = Counter(w for s in sentences for w in re.findall(r"[a-z']{4,}", s.lower()))
    ranked = sorted(
        range(len(sentences)),
        key=lambda i: -sum(words[w] for w in re.findall(r"[a-z']{4,}", sentences[i].lower())),
    )
    chosen, count = [], 0
    for i in ranked:
        n = len(sentences[i].split())
        if chosen and count + n > max_words:
            continue
        chosen.append(i)
        count += n
    return " ".join(sentences[i] for i in sorted(chosen))


class ChatSummarizer:
    def __init__(self, store: BaseStore, llm: LLM | None = None) -> None:
        self.store = store
        self.llm = llm

    @classmethod
    def from_settings(cls, store: BaseStore, settings: Settings) -> "ChatSummarizer":
        llm = openai_llm(settings.openai_api_key) if settings.openai_api_key else None  # pragma: no cover
        return cls(store, llm)

    def generate_summary(self, session_id: str, max_length: int = 500) -> SummaryResponse:
        messages = self.store.get_session_messages(session_id)
        if not messages:
            return SummaryResponse(
                session_id=session_id, summary="No messages found for this session.", message_count=0
            )
        summary = None
        if self.llm:
            try:
                prompt = SUMMARY_PROMPT.format(text=format_chat(messages), max_length=max_length)
                summary = self.llm(prompt).strip()
            except Exception:
                logger.exception("LLM summary failed; using extractive fallback")
        if not summary:
            summary = extractive_summary(messages, max_length)
        return SummaryResponse(session_id=session_id, summary=summary, message_count=len(messages))

    def generate_brief_summary(self, session_id: str) -> str:
        messages = self.store.get_session_messages(session_id)
        if not messages:
            return "No messages in this session."
        if self.llm:
            try:
                return self.llm(BRIEF_PROMPT.format(text=format_chat(messages))).strip()
            except Exception:
                logger.exception("LLM brief summary failed; using extractive fallback")
        return extractive_summary(messages, 40)

    def generate_structured_summary(self, session_id: str) -> dict[str, Any]:
        messages = self.store.get_session_messages(session_id)
        if not messages:
            return {"error": "No messages found"}
        if self.llm:
            try:
                raw = self.llm(STRUCTURED_PROMPT.format(text=format_chat(messages)))
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                return json.loads(match.group()) if match else {"raw_summary": raw}
            except json.JSONDecodeError:
                return {"raw_summary": raw}
            except Exception:
                logger.exception("LLM structured summary failed")
        stats = self.store.get_session_stats(session_id)
        counts = stats["sentiment_distribution"]
        return {
            "main_topics": list(stats["topic_distribution"]),
            "overall_sentiment": max(counts, key=lambda k: counts[k], default="neutral"),
            "questions_asked": [m.content for m in messages if m.content.rstrip().endswith("?")],
            "participant_count": len({m.role for m in messages}),
            "summary": extractive_summary(messages, 60),
        }

    def health_check(self) -> bool:
        """Always usable: falls back to extractive summaries without an LLM."""
        return True
