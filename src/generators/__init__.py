"""Content generators for the Stock Rich Project.

Provides generators for articles, summaries, insights, hashtags,
and chart images using Claude API and matplotlib.
"""

from src.generators.article import ArticleContext, ArticleGenerator
from src.generators.base import BaseGenerator
from src.generators.hashtag import HashtagGenerator
from src.generators.image import ImageGenerator
from src.generators.insight import InsightContext, InsightGenerator
from src.generators.summary import SummaryGenerator

__all__ = [
    "ArticleContext",
    "ArticleGenerator",
    "BaseGenerator",
    "HashtagGenerator",
    "ImageGenerator",
    "InsightContext",
    "InsightGenerator",
    "SummaryGenerator",
]
