"""Summary generator using Claude Haiku for low-cost text summarization."""

from __future__ import annotations

from typing import Any

from src.core.models import ClaudeTask, NewsItem
from src.generators.base import BaseGenerator

_SYSTEM_PROMPT_KO = (
    "당신은 금융 뉴스 요약 전문가입니다. "
    "핵심만 간결하게 요약하되, 숫자와 팩트를 정확히 보존하세요. "
    "투자 권유 표현은 사용하지 마세요."
)

_SYSTEM_PROMPT_EN = (
    "You are a financial news summarization expert. "
    "Summarize concisely while preserving key numbers and facts. "
    "Do not use any investment solicitation language."
)


class SummaryGenerator(BaseGenerator):
    """Generate text summaries using Claude Haiku (SUMMARY task).

    Designed for low-cost, low-latency summarization of news articles,
    market data, and generated articles.
    """

    def generate(self, **kwargs: Any) -> str:
        """Generate a summary.

        Args:
            **kwargs: Must include ``text`` (str). Optional: ``max_sentences``
                (int, default 3), ``lang`` (str, default "ko").

        Returns:
            Summarized text string.
        """
        text: str = kwargs["text"]
        max_sentences: int = kwargs.get("max_sentences", 3)
        lang: str = kwargs.get("lang", "ko")
        return self.summarize_text(text, max_sentences=max_sentences, lang=lang)

    def summarize_text(
        self,
        text: str,
        max_sentences: int = 3,
        lang: str = "ko",
    ) -> str:
        """Summarize a text into N sentences.

        Args:
            text: Source text to summarize.
            max_sentences: Maximum number of sentences in the summary.
            lang: Language ("ko" or "en").

        Returns:
            Summarized text. Empty string on failure.
        """
        if not text.strip():
            return ""

        system_prompt = _SYSTEM_PROMPT_KO if lang == "ko" else _SYSTEM_PROMPT_EN
        user_message = (
            f"다음 텍스트를 {max_sentences}문장 이내로 요약하세요.\n\n{text}"
            if lang == "ko"
            else f"Summarize the following text in {max_sentences} sentences or fewer.\n\n{text}"
        )

        try:
            return self._generate_content(
                ClaudeTask.SUMMARY,
                user_message,
                system_prompt,
            )
        except Exception as e:
            self._logger.warning(
                "summarize_text_failed",
                text_length=len(text),
                error=str(e),
            )
            return ""

    def summarize_news_batch(
        self,
        news_items: list[NewsItem],
        max_sentences: int = 2,
    ) -> list[tuple[str, str]]:
        """Summarize a batch of news items.

        Args:
            news_items: List of NewsItem to summarize.
            max_sentences: Max sentences per summary.

        Returns:
            List of (title, summary) tuples.
        """
        results: list[tuple[str, str]] = []
        for item in news_items:
            source_text = item.content if item.content else item.title
            summary = self.summarize_text(
                source_text,
                max_sentences=max_sentences,
                lang="ko" if item.market.value == "korea" else "en",
            )
            results.append((item.title, summary))

        self._logger.info(
            "batch_summary_complete",
            count=len(results),
            successful=sum(1 for _, s in results if s),
        )
        return results

    def generate_article_summary(
        self,
        content: str,
        max_length: int = 200,
    ) -> str:
        """Generate a short summary of an article.

        Args:
            content: Full article content.
            max_length: Approximate max character length for summary.

        Returns:
            Short summary string. Empty string on failure.
        """
        if not content.strip():
            return ""

        user_message = (
            f"다음 기사를 {max_length}자 이내로 한 문단으로 요약하세요. "
            f"핵심 수치와 결론 위주로 작성하세요.\n\n{content}"
        )

        try:
            summary = self._generate_content(
                ClaudeTask.SUMMARY,
                user_message,
                _SYSTEM_PROMPT_KO,
            )
            # Trim if exceeds max_length
            if len(summary) > max_length:
                summary = summary[: max_length - 3] + "..."
            return summary
        except Exception as e:
            self._logger.warning(
                "article_summary_failed",
                content_length=len(content),
                error=str(e),
            )
            return ""
