"""Application configuration using pydantic-settings with YAML integration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.exceptions import ConfigError
from src.core.logger import get_logger

logger = get_logger(__name__)

# Project root directory (src/core/config.py -> src/core -> src -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_yaml(filename: str) -> dict[str, Any]:
    """Load a YAML file from the config directory.

    Args:
        filename: Name of the YAML file to load.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        ConfigError: If the file cannot be loaded or parsed.
    """
    filepath = CONFIG_DIR / filename
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data or {}
    except FileNotFoundError as e:
        raise ConfigError(
            f"Config file not found: {filepath}",
            {"file": filename},
        ) from e
    except yaml.YAMLError as e:
        raise ConfigError(
            f"Invalid YAML: {filepath}",
            {"file": filename, "error": str(e)},
        ) from e


# ============================================================
# Sub-config models (from settings.yaml)
# ============================================================


class AppInfo(BaseModel):
    """Application metadata."""

    name: str = "주식부자프로젝트"
    version: str = "0.1.0"
    env: str = "development"


class ClaudeModelConfig(BaseModel):
    """Claude AI model configuration."""

    default_model: str = "claude-sonnet-4-6"
    models: dict[str, str] = Field(default_factory=lambda: {
        "general": "claude-sonnet-4-6",
        "deep_analysis": "claude-opus-4-6",
        "summary": "claude-haiku-4-5-20251001",
    })
    max_tokens: dict[str, int] = Field(default_factory=lambda: {
        "general": 4096,
        "deep_analysis": 8192,
        "summary": 1024,
    })
    temperature: dict[str, float] = Field(default_factory=lambda: {
        "general": 0.7,
        "deep_analysis": 0.5,
        "summary": 0.3,
    })


class ScheduleConfig(BaseModel):
    """Schedule configuration."""

    timezone: str = "Asia/Seoul"
    morning_briefing: str = "08:00"
    closing_review: str = "16:30"
    stock_analysis: list[str] = Field(default_factory=lambda: ["12:00", "19:00"])
    weekly_review: str = "SAT 10:00"
    news_collection: dict[str, int] = Field(default_factory=lambda: {
        "market_hours_interval_min": 30,
        "off_hours_interval_min": 120,
    })


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = "sqlite:///data/db/stock_rich.db"
    echo: bool = False


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "json"
    file: str = "logs/app.log"
    rotation: str = "10 MB"
    retention: str = "30 days"


class RetryConfig(BaseModel):
    """Retry configuration."""

    max_attempts: int = 3
    wait_exponential_min: int = 1
    wait_exponential_max: int = 30


# ============================================================
# News sources config (from news_sources.yaml)
# ============================================================


class NewsSource(BaseModel):
    """Single news source definition."""

    name: str
    type: str = "rss"
    url: str
    category: str = "종합"
    language: str = "ko"
    enabled: bool = True


class CollectionSettings(BaseModel):
    """News collection settings."""

    max_articles_per_source: int = 20
    dedup_similarity_threshold: float = 0.85
    dedup_window_hours: int = 24
    request_timeout_sec: int = 15
    request_delay_sec: int = 2


class NewsSourcesConfig(BaseModel):
    """News sources configuration."""

    korea: list[NewsSource] = Field(default_factory=list)
    us: list[NewsSource] = Field(default_factory=list)
    collection: CollectionSettings = Field(default_factory=CollectionSettings)


# ============================================================
# Market config (from market_config.yaml)
# ============================================================


class IndexInfo(BaseModel):
    """Market index info."""

    name: str
    code: str = ""
    ticker: str = ""


class WatchlistItem(BaseModel):
    """Watchlist stock."""

    ticker: str
    name: str


class MACDConfig(BaseModel):
    """MACD parameters."""

    fast: int = 12
    slow: int = 26
    signal: int = 9


class BollingerConfig(BaseModel):
    """Bollinger Bands parameters."""

    period: int = 20
    std_dev: int = 2


class TechnicalConfig(BaseModel):
    """Technical analysis parameters."""

    sma_periods: list[int] = Field(default_factory=lambda: [5, 20, 60, 120])
    ema_periods: list[int] = Field(default_factory=lambda: [12, 26])
    rsi_period: int = 14
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    macd: MACDConfig = Field(default_factory=MACDConfig)
    bollinger: BollingerConfig = Field(default_factory=BollingerConfig)
    golden_cross_pairs: list[list[int]] = Field(
        default_factory=lambda: [[5, 20], [20, 60]],
    )


class ValuationThresholds(BaseModel):
    """Valuation thresholds."""

    per_max: int = 30
    pbr_max: int = 5
    psr_max: int = 10


class ProfitabilityThresholds(BaseModel):
    """Profitability thresholds."""

    roe_min: int = 10
    roa_min: int = 5
    operating_margin_min: int = 10


class GrowthThresholds(BaseModel):
    """Growth thresholds."""

    revenue_growth_min: int = 5
    earnings_growth_min: int = 10


class FundamentalConfig(BaseModel):
    """Fundamental analysis configuration."""

    valuation: ValuationThresholds = Field(default_factory=ValuationThresholds)
    profitability: ProfitabilityThresholds = Field(
        default_factory=ProfitabilityThresholds,
    )
    growth: GrowthThresholds = Field(default_factory=GrowthThresholds)


class ScreeningConfig(BaseModel):
    """Stock screening configuration."""

    weights: dict[str, float] = Field(
        default_factory=lambda: {"technical": 0.5, "fundamental": 0.5},
    )
    top_n: int = 10
    min_market_cap_krw: int = 1_000_000_000_000
    min_market_cap_usd: int = 10_000_000_000


class KoreaMarket(BaseModel):
    """Korea market config."""

    indices: list[IndexInfo] = Field(default_factory=list)
    watchlist: list[WatchlistItem] = Field(default_factory=list)


class USMarket(BaseModel):
    """US market config."""

    indices: list[IndexInfo] = Field(default_factory=list)
    watchlist: list[WatchlistItem] = Field(default_factory=list)


class CacheConfig(BaseModel):
    """Cache TTL configuration."""

    indices_ttl_hours: int = 4
    stocks_ttl_hours: int = 4
    sentiment_ttl_hours: int = 6


class MarketConfig(BaseModel):
    """Full market configuration."""

    korea: KoreaMarket = Field(default_factory=KoreaMarket)
    us: USMarket = Field(default_factory=USMarket)
    technical: TechnicalConfig = Field(default_factory=TechnicalConfig)
    fundamental: FundamentalConfig = Field(default_factory=FundamentalConfig)
    screening: ScreeningConfig = Field(default_factory=ScreeningConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)


# ============================================================
# Content config (from content_config.yaml)
# ============================================================


class ArticleTypeConfig(BaseModel):
    """Single article type configuration."""

    display_name: str
    model: str = "general"
    min_length: int = 800
    max_length: int = 1200
    template: str = ""
    prompt_template: str = ""
    schedule: str | list[str] = ""
    requires_disclaimer: bool = True


class DisclaimerConfig(BaseModel):
    """Disclaimer text configuration."""

    ko: str = ""
    en: str = ""


class StyleConfig(BaseModel):
    """Content style configuration."""

    tone: str = "professional_friendly"
    target_audience: str = "개인 투자자"
    formality: str = "반말/존댓말 혼용 (존댓말 기본)"
    emoji_usage: str = "minimal"


class ContentConfig(BaseModel):
    """Content generation configuration."""

    article_types: dict[str, ArticleTypeConfig] = Field(default_factory=dict)
    disclaimer: DisclaimerConfig = Field(default_factory=DisclaimerConfig)
    prohibited_expressions: list[str] = Field(default_factory=list)
    style: StyleConfig = Field(default_factory=StyleConfig)


# ============================================================
# SNS config (from sns_config.yaml)
# ============================================================


class ImageSize(BaseModel):
    """Image dimensions."""

    width: int
    height: int


class HashtagConfig(BaseModel):
    """Hashtag configuration."""

    max_count: int = 30
    default_tags: list[str] = Field(default_factory=list)


class InstagramConfig(BaseModel):
    """Instagram platform configuration."""

    enabled: bool = True
    post_types: dict[str, Any] = Field(default_factory=dict)
    hashtag: HashtagConfig = Field(default_factory=HashtagConfig)


class XConfig(BaseModel):
    """X (Twitter) platform configuration."""

    enabled: bool = True
    post_types: dict[str, Any] = Field(default_factory=dict)
    hashtag: HashtagConfig = Field(default_factory=HashtagConfig)


class SNSRetryConfig(BaseModel):
    """SNS-specific retry configuration."""

    max_attempts: int = 3
    delay_between_sec: int = 300


class RateLimitConfig(BaseModel):
    """Per-platform rate limit."""

    instagram: dict[str, int] = Field(default_factory=lambda: {
        "max_posts_per_hour": 5,
        "max_posts_per_day": 25,
    })
    x: dict[str, int] = Field(default_factory=lambda: {
        "max_tweets_per_15min": 15,
        "max_tweets_per_day": 100,
    })


class SNSConfig(BaseModel):
    """SNS publishing configuration."""

    instagram: InstagramConfig = Field(default_factory=InstagramConfig)
    x: XConfig = Field(default_factory=XConfig)
    posting_schedule: dict[str, Any] = Field(default_factory=dict)
    retry: SNSRetryConfig = Field(default_factory=SNSRetryConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)


# ============================================================
# Root configuration
# ============================================================


class AppConfig(BaseSettings):
    """Root application configuration.

    Loads secrets from .env file (environment variables) and
    structured settings from YAML config files.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Environment variables (from .env) ---
    anthropic_api_key: str = ""
    x_api_key: str = ""
    x_api_secret: str = ""
    x_access_token: str = ""
    x_access_token_secret: str = ""
    x_bearer_token: str = ""
    instagram_username: str = ""
    instagram_password: str = ""
    database_url: str = "sqlite:///data/db/stock_rich.db"
    app_env: str = "development"
    log_level: str = "INFO"

    # --- YAML-loaded sub-configs ---
    app: AppInfo = Field(default_factory=AppInfo)
    claude: ClaudeModelConfig = Field(default_factory=ClaudeModelConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    news_sources: NewsSourcesConfig = Field(default_factory=NewsSourcesConfig)
    market: MarketConfig = Field(default_factory=MarketConfig)
    content: ContentConfig = Field(default_factory=ContentConfig)
    sns: SNSConfig = Field(default_factory=SNSConfig)

    def model_post_init(self, __context: Any) -> None:
        """Load YAML configurations after env vars are initialized."""
        self._load_yaml_configs()

    def _load_yaml_configs(self) -> None:
        """Load all YAML configuration files into sub-config models."""
        # settings.yaml
        settings = _load_yaml("settings.yaml")
        if "app" in settings:
            self.app = AppInfo(**settings["app"])
        if "claude" in settings:
            self.claude = ClaudeModelConfig(**settings["claude"])
        if "schedule" in settings:
            self.schedule = ScheduleConfig(**settings["schedule"])
        if "database" in settings:
            self.database = DatabaseConfig(**settings["database"])
        if "logging" in settings:
            self.logging = LoggingConfig(**settings["logging"])
        if "retry" in settings:
            self.retry = RetryConfig(**settings["retry"])

        # news_sources.yaml
        news_data = _load_yaml("news_sources.yaml")
        self.news_sources = NewsSourcesConfig(**news_data)

        # market_config.yaml
        market_data = _load_yaml("market_config.yaml")
        self.market = MarketConfig(**market_data)

        # content_config.yaml
        content_data = _load_yaml("content_config.yaml")
        self.content = ContentConfig(**content_data)

        # sns_config.yaml
        sns_data = _load_yaml("sns_config.yaml")
        self.sns = SNSConfig(**sns_data)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Get the singleton application configuration.

    Returns:
        The AppConfig singleton instance.

    Note:
        Call ``get_config.cache_clear()`` to reload configuration in tests.
    """
    config = AppConfig()
    logger.info(
        "configuration_loaded",
        app=config.app.name,
        env=config.app.env,
    )
    return config
