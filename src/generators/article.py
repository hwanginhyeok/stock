"""Article generator using Claude API with type-based parameterization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.config import ArticleTypeConfig
from src.core.exceptions import ContentError
from src.core.models import (
    Article,
    ArticleType,
    ClaudeTask,
    MarketSnapshot,
    NewsItem,
    StockAnalysis,
)
from src.generators.base import BaseGenerator
from src.storage.article_repository import ArticleRepository


@dataclass
class ArticleContext:
    """Input context for article generation.

    Attributes:
        market_snapshots: Market state data.
        news_items: Relevant news items.
        stock_analyses: Stock analysis results.
        extra: Additional data (e.g., weekly sector performance).
    """

    market_snapshots: list[MarketSnapshot] = field(default_factory=list)
    news_items: list[NewsItem] = field(default_factory=list)
    stock_analyses: list[StockAnalysis] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


_TASK_MAP: dict[str, ClaudeTask] = {
    "general": ClaudeTask.GENERAL,
    "deep_analysis": ClaudeTask.DEEP_ANALYSIS,
    "summary": ClaudeTask.SUMMARY,
}


class ArticleGenerator(BaseGenerator):
    """Generate articles for all 4 article types using Claude API.

    Article types (morning_briefing, closing_review, stock_analysis,
    weekly_review) are parameterized via ``ArticleTypeConfig``, so a
    single class handles all variants through different prompt templates
    and Claude models.
    """

    def __init__(self) -> None:
        super().__init__()
        self._repo = ArticleRepository()

    def generate(self, **kwargs: Any) -> Article:
        """Generate an article.

        Args:
            **kwargs: Must include ``article_type`` (ArticleType) and
                ``context`` (ArticleContext).

        Returns:
            Generated Article model.
        """
        article_type: ArticleType = kwargs["article_type"]
        context: ArticleContext = kwargs["context"]
        return self.generate_article(article_type, context)

    def generate_article(
        self,
        article_type: ArticleType,
        context: ArticleContext,
    ) -> Article:
        """Generate a single article through the full pipeline.

        Pipeline: config load → prompt build → Claude call → post-process
        → quality score → Article model.

        Args:
            article_type: The article type enum.
            context: Input data context.

        Returns:
            Generated Article model.

        Raises:
            ContentError: If article type is not configured or generation fails.
        """
        # 1. Load article type config
        type_config = self._get_type_config(article_type)

        # 2. Build prompt context
        prompt_context = self._build_prompt_context(article_type, context)

        # 3. Render prompt template
        prompt_template = type_config.prompt_template
        if not prompt_template:
            raise ContentError(
                f"No prompt template configured for {article_type.value}",
                {"article_type": article_type.value},
            )
        user_message = self._render_prompt(prompt_template, **prompt_context)

        # 4. Build system prompt
        system_prompt = self._build_system_prompt(article_type)

        # 5. Call Claude API
        task = self._resolve_claude_task(type_config.model)
        self._logger.info(
            "generating_article",
            article_type=article_type.value,
            task=task.value,
        )
        raw_content = self._generate_content(task, user_message, system_prompt)

        # 6. Extract title and body
        title, body = self._extract_title(raw_content)

        # 7. Post-process
        body = self._post_process(body, type_config)

        # 8. Quality score
        quality_score = self._compute_quality_score(body, type_config)

        # 9. Build Article model
        related_tickers = self._collect_tickers(context)
        article = Article(
            article_type=article_type,
            title=title,
            content=body,
            summary=body[:200] + "..." if len(body) > 200 else body,
            related_tickers=related_tickers,
            model_used=self._config.claude.models.get(
                type_config.model,
                self._config.claude.default_model,
            ),
            char_count=len(body),
            disclaimer_included=self._has_disclaimer(body),
            quality_score=quality_score,
        )

        self._logger.info(
            "article_generated",
            article_type=article_type.value,
            title=title[:60],
            char_count=article.char_count,
            quality_score=quality_score,
        )

        return article

    def generate_and_store(
        self,
        article_type: ArticleType,
        context: ArticleContext,
    ) -> Article:
        """Generate an article and persist it to the database.

        Args:
            article_type: The article type enum.
            context: Input data context.

        Returns:
            Generated and stored Article model.
        """
        article = self.generate_article(article_type, context)
        self._repo.save(article)
        self._logger.info(
            "article_stored",
            article_id=article.id,
            article_type=article_type.value,
        )
        return article

    def _get_type_config(self, article_type: ArticleType) -> ArticleTypeConfig:
        """Get configuration for an article type.

        Args:
            article_type: The article type.

        Returns:
            ArticleTypeConfig for the given type.

        Raises:
            ContentError: If the article type is not configured.
        """
        config = self._content_config.article_types.get(article_type.value)
        if not config:
            raise ContentError(
                f"Article type not configured: {article_type.value}",
                {"article_type": article_type.value},
            )
        return config

    @staticmethod
    def _resolve_claude_task(model_key: str) -> ClaudeTask:
        """Map a model config key to a ClaudeTask enum.

        Args:
            model_key: Config model key (e.g., "general", "deep_analysis").

        Returns:
            Corresponding ClaudeTask.
        """
        return _TASK_MAP.get(model_key, ClaudeTask.GENERAL)

    def _build_prompt_context(
        self,
        article_type: ArticleType,
        context: ArticleContext,
    ) -> dict[str, Any]:
        """Convert domain models to template variables.

        Args:
            article_type: The article type.
            context: Input data context.

        Returns:
            Dict of template variables.
        """
        return {
            "article_type": article_type.value,
            "market_snapshots": [
                s.model_dump() for s in context.market_snapshots
            ],
            "news_headlines": [
                n.model_dump() for n in context.news_items
            ],
            "analyses": [
                a.model_dump() for a in context.stock_analyses
            ],
            "extra": context.extra,
        }

    def _build_system_prompt(self, article_type: ArticleType) -> str:
        """Build a system prompt for the given article type.

        Args:
            article_type: The article type.

        Returns:
            System prompt string.
        """
        style = self._content_config.style
        prohibited = self._content_config.prohibited_expressions

        type_config = self._content_config.article_types.get(article_type.value)
        display_name = type_config.display_name if type_config else article_type.value

        return (
            f"당신은 주식 시장 전문 분석가이자 금융 콘텐츠 작성자입니다.\n"
            f"'{display_name}' 기사를 작성합니다.\n\n"
            f"## 스타일 가이드\n"
            f"- 톤: {style.tone}\n"
            f"- 대상 독자: {style.target_audience}\n"
            f"- 어투: {style.formality}\n\n"
            f"## 절대 금지 표현\n"
            f"다음 표현은 절대 사용하지 마세요:\n"
            + "\n".join(f"- {expr}" for expr in prohibited)
            + "\n\n"
            f"## 핵심 원칙\n"
            f"- 투자 권유나 종목 추천 금지\n"
            f"- 객관적 데이터 기반 분석\n"
            f"- 마크다운 포맷으로 작성\n"
            f"- 첫 줄은 반드시 `# 제목` 형식\n"
        )

    @staticmethod
    def _extract_title(content: str) -> tuple[str, str]:
        """Extract title from the first heading line.

        Expects ``# Title`` on the first non-empty line. Falls back to
        using the first sentence as the title.

        Args:
            content: Raw generated content.

        Returns:
            Tuple of (title, body without the title line).
        """
        lines = content.strip().split("\n")
        if not lines:
            return "Untitled", content

        first_line = lines[0].strip()

        # Match "# Title" pattern
        if first_line.startswith("# "):
            title = first_line[2:].strip()
            body = "\n".join(lines[1:]).strip()
            return title, body

        # Fallback: use first sentence
        for char in (".", "!", "?"):
            idx = first_line.find(char)
            if idx > 0:
                return first_line[: idx + 1], content

        return first_line[:80], content

    def _post_process(self, content: str, config: ArticleTypeConfig) -> str:
        """Post-process generated content.

        Removes prohibited expressions and appends disclaimer.

        Args:
            content: Raw article body.
            config: Article type config.

        Returns:
            Processed content.
        """
        # Remove prohibited expressions
        found = self._check_prohibited(content)
        for expr in found:
            content = content.replace(expr, "")
            self._logger.warning(
                "prohibited_expression_removed",
                expression=expr,
            )

        # Append disclaimer if required
        if config.requires_disclaimer:
            content = self._append_disclaimer(content, lang="ko")

        return content

    def _has_disclaimer(self, content: str) -> bool:
        """Check if content includes the disclaimer.

        Args:
            content: Article content.

        Returns:
            True if disclaimer is present.
        """
        disclaimer_ko = self._content_config.disclaimer.ko.strip()
        if not disclaimer_ko:
            return True
        first_line = disclaimer_ko.split("\n")[0].strip()
        return first_line in content

    @staticmethod
    def _collect_tickers(context: ArticleContext) -> list[str]:
        """Collect unique tickers from context.

        Args:
            context: Article context.

        Returns:
            Deduplicated list of ticker strings.
        """
        tickers: set[str] = set()
        for analysis in context.stock_analyses:
            tickers.add(analysis.ticker)
        for news in context.news_items:
            tickers.update(news.related_tickers)
        return sorted(tickers)
