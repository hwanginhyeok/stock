# PROJECT MAP (프로젝트 지도)

> **목적**: 모든 디렉토리와 파일의 역할을 한눈에 파악하여 빠른 업무 처리 지원
> **관리**: 파일/디렉토리 추가/변경 시 반드시 이 문서를 업데이트할 것
> **최종 업데이트**: 2026-02-21

---

## 전체 구조 요약

```
주식부자프로젝트/
├── config/          # YAML 설정 파일 (앱, 시장, 콘텐츠, 뉴스, SNS)
├── agents/          # 에이전트 역할 정의서 (5개 AI 에이전트)
├── src/             # 메인 소스 코드
│   ├── core/        #   공통 인프라 (설정, DB, 로깅, API 클라이언트)
│   ├── collectors/  #   데이터 수집 (뉴스 RSS, 한국/미국 시장)
│   ├── analyzers/   #   분석 엔진 (기술, 기본, 감성, 트렌드)
│   ├── generators/  #   콘텐츠 생성 (기사, 요약, 해시태그, 차트)
│   ├── storage/     #   DB 저장소 (제네릭 CRUD + 도메인별 리포지토리)
│   ├── exporters/   #   엑셀 출력 (대시보드, 상세차트, 종목, 감정분석)
│   ├── publishers/  #   [미구현] SNS 게시 (Instagram, X)
│   └── workflows/   #   [미구현] 오케스트레이션 (모닝, 장마감, 주간)
├── scripts/         # 실행 스크립트 (대시보드 생성 등)
├── templates/       # Jinja2 템플릿 (프롬프트, 기사, SNS)
├── data/            # 데이터 (캐시, DB, 생성물) — git ignored
├── tests/           # [미구현] 테스트
└── logs/            # 로그 파일 — git ignored
```

---

## config/ — 설정 파일

| 파일 | 설명 |
|------|------|
| `settings.yaml` | 앱 전역 설정 — Claude 모델 선택, 스케줄, DB 경로, 로깅, 재시도 정책 |
| `market_config.yaml` | 시장 데이터 설정 — 한국(KOSPI/KOSDAQ + 10종목), 미국(S&P500/NASDAQ/DOW/VIX + 10종목), 분석 파라미터 |
| `content_config.yaml` | 콘텐츠 생성 설정 — 기사 유형별 모델, 토큰 한도, 템플릿, 면책조항 |
| `news_sources.yaml` | 뉴스 RSS 피드 소스 목록 |
| `sns_config.yaml` | SNS 플랫폼 설정 (Instagram, X 게시 규칙) |

---

## agents/ — 에이전트 역할 정의서

| 파일 | 역할 | 담당 |
|------|------|------|
| `뉴스분석가.md` | 뉴스 수집/분류/감성분석 | collectors/news, analyzers/sentiment |
| `시장분석가.md` | 시장 데이터 수집/기술적·기본적 분석 | collectors/market, analyzers/* |
| `아티클작성가.md` | Claude API 기반 콘텐츠 생성/품질 관리 | generators/* |
| `SNS매니저.md` | Instagram/X 포맷 변환/게시/스케줄 | publishers/* |
| `리서치어시스턴트.md` | 온디맨드 심층 리서치/SWOT/비교분석 | workflows/research |

---

## src/core/ — 공통 인프라

| 파일 | 설명 | 주요 클래스/함수 |
|------|------|-----------------|
| `__init__.py` | 패키지 export — 모든 core 모듈의 공개 API 집합 | — |
| `config.py` | Pydantic-settings + YAML 통합 설정 시스템 | `AppConfig`, `get_config()` (LRU 캐시) |
| `models.py` | 도메인 모델 (Pydantic) + Enum 정의 | `NewsItem`, `MarketSnapshot`, `StockAnalysis`, `Article`, `SNSPost`, `ResearchReport` / Enum 9개 |
| `database.py` | SQLAlchemy ORM 모델 + 세션 관리 | `Base`, `init_db()`, `get_session()`, ORM 6개 테이블 |
| `logger.py` | structlog JSON 구조화 로깅 | `setup_logging()`, `get_logger()` |
| `claude_client.py` | Claude API 클라이언트 (작업별 모델 선택, 재시도) | `ClaudeClient`, `ClaudeResponse` |
| `exceptions.py` | 커스텀 예외 계층 | `StockRichError` → `ConfigError`, `APIError`, `CollectionError`, `AnalysisError`, `DatabaseError`, `ContentError` 등 7개 |
| `cache_manager.py` | Parquet/JSON 캐시 (TTL 기반 만료) | `CacheManager` — `get()`, `put()`, `invalidate()` |

---

## src/collectors/ — 데이터 수집

### src/collectors/news/ — 뉴스 수집

| 파일 | 설명 | 주요 클래스 |
|------|------|------------|
| `base.py` | 뉴스 수집기 추상 클래스 | `BaseNewsCollector(BaseCollector)` |
| `rss_collector.py` | RSS 피드 파싱 + 중복 제거 + DB 저장 | `RSSNewsCollector` — feedparser, BeautifulSoup 사용 |
| `dedup.py` | 제목 유사도 기반 뉴스 중복 필터 (0.85 임계값) | `TitleDeduplicator` — difflib.SequenceMatcher |

### src/collectors/market/ — 시장 데이터 수집

| 파일 | 설명 | 주요 클래스 |
|------|------|------------|
| `base.py` | 시장 수집기 추상 클래스 | `BaseMarketCollector(BaseCollector)` |
| `korea_collector.py` | 한국 시장 수집 (KOSPI, KOSDAQ) | `KoreaMarketCollector` — pykrx 사용 |
| `us_collector.py` | 미국 시장 수집 (S&P500, NASDAQ, DOW, VIX) | `USMarketCollector` — yfinance 사용 |

---

## src/analyzers/ — 분석 엔진

| 파일 | 설명 | 주요 클래스/함수 | 출력 |
|------|------|-----------------|------|
| `base.py` | 분석기 추상 클래스 | `BaseAnalyzer` — `analyze()` | — |
| `technical.py` | 기술 분석 (순수 pandas 지표 계산) | `TechnicalAnalyzer`, `_sma()`, `_ema()`, `_rsi()`, `_macd()`, `_bbands()` | 0-100 종합 점수 |
| `fundamental.py` | 기본 분석 (PER, PBR, ROE, 성장률) | `FundamentalAnalyzer` — yfinance 기업 데이터 | 0-100 점수 (밸류33+수익33+성장34) |
| `sentiment.py` | 뉴스 감성 분석 (Claude Haiku) | `SentimentAnalyzer` | -1.0 ~ +1.0 점수 |
| `screener.py` | 종합 스크리닝 (기술+기본 가중 복합) | `StockScreener` | 추천등급 (strong_positive/positive/neutral/negative) |
| `trend.py` | 트렌드 지표 (순수 pandas) | `_atr()`, `_adx()`, `_supertrend()` | ADX 수치, Supertrend 방향 |
| `market_sentiment.py` | 시장 심리 Fear/Greed 인덱스 | `compute_fear_greed()` | 0-100 (VIX 40% + RSI 30% + 모멘텀 30%) |

---

## src/generators/ — 콘텐츠 생성

| 파일 | 설명 | 주요 클래스 | 사용 모델 |
|------|------|------------|----------|
| `base.py` | 생성기 추상 클래스 (Jinja2, 품질검증, 면책조항) | `BaseGenerator` — `render_template()`, `validate_content()`, `add_disclaimer()` | — |
| `article.py` | 기사 생성 (4종: 모닝/장마감/종목/주간) | `ArticleGenerator`, `ArticleContext` | Sonnet (일반) / Opus (심층) |
| `summary.py` | 텍스트 요약 (저비용/저지연) | `SummaryGenerator` | Haiku |
| `hashtag.py` | 해시태그 생성 (설정 기본값 + 티커 + AI 토픽) | `HashtagGenerator` | Haiku |
| `insight.py` | SNS용 한줄 시장 코멘트 | `InsightGenerator`, `InsightContext` | Sonnet |
| `image.py` | matplotlib 차트 이미지 (PNG) | `ImageGenerator` | 없음 (matplotlib만) |

---

## src/storage/ — DB 저장소

| 파일 | 설명 | 주요 클래스 | 커스텀 메서드 |
|------|------|------------|-------------|
| `base.py` | 제네릭 CRUD 리포지토리 (TypeVar) | `BaseRepository[T]` — `create()`, `read()`, `update()`, `delete()`, `get_many()` | — |
| `news_repository.py` | 뉴스 저장소 | `NewsRepository` | `get_latest()`, `get_by_market()` |
| `market_snapshot_repository.py` | 시장 스냅샷 저장소 | `MarketSnapshotRepository` | `get_latest()`, `get_by_date()` |
| `stock_analysis_repository.py` | 종목 분석 저장소 | `StockAnalysisRepository` | `get_by_ticker()` |
| `article_repository.py` | 기사 저장소 | `ArticleRepository` | `get_by_type()`, `get_latest()` |
| `sns_post_repository.py` | SNS 게시물 저장소 | `SNSPostRepository` | `get_by_platform()`, `get_by_status()` |
| `research_report_repository.py` | 리서치 리포트 저장소 | `ResearchReportRepository` | `get_by_type()` |

---

## src/exporters/ — 엑셀 출력

| 파일 | 설명 | 주요 함수 | 생성 시트/차트 |
|------|------|---------|--------------|
| `base.py` | 공통 스타일, 색상 팔레트, 차트 유틸 | `style_cell()`, `apply_chart_gridlines()`, `apply_y_axis_padding()`, `apply_x_axis_tick_interval()`, `add_right_y_axis()`, `style_line_series()` 등 | — |
| `dashboard_builder.py` | Overview 시트 빌더 | `build_overview_sheet()` | 정규화 성과 비교 차트 + 6개 미니 차트 |
| `index_detail_builder.py` | 지수 상세 시트 빌더 (리포트 + 5종 차트) | `build_index_detail_sheet()` | Price+SMA+BB, RSI, MACD+Hist, ADX+DI, Volume |
| `constituents_builder.py` | 구성 종목(Top Stocks) 시트 빌더 | `build_constituents_sheet()` | 기술점수 테이블 |
| `sentiment_builder.py` | 감정 분석 시트 빌더 | `build_sentiment_sheet()` | VIX History 차트 + Fear/Greed + 트렌드 + 진단 |

---

## scripts/ — 실행 스크립트

| 파일 | 설명 | 실행 방법 |
|------|------|---------|
| `generate_dashboard.py` | 종합 시장 대시보드 엑셀 생성 (메인 스크립트) | `PYTHONPATH="." python scripts/generate_dashboard.py [--period 6mo] [--no-cache]` |
| `export_nvda.py` | NVIDIA 상세 리포트 생성 | `PYTHONPATH="." python scripts/export_nvda.py` |
| `export_sp500_top20.py` | S&P 500 Top 20 대시보드 생성 | `PYTHONPATH="." python scripts/export_sp500_top20.py` |

---

## templates/ — Jinja2 템플릿

### templates/prompts/ — Claude API 프롬프트 템플릿

| 파일 | 설명 | 사용처 |
|------|------|-------|
| `morning_briefing.j2` | 모닝브리핑 프롬프트 (시장데이터 + 뉴스 → 800-1200자) | `ArticleGenerator` |
| `closing_review.j2` | 장마감 리뷰 프롬프트 | `ArticleGenerator` |
| `stock_analysis.j2` | 종목 심층 분석 프롬프트 | `ArticleGenerator` |
| `weekly_review.j2` | 주간 리뷰 프롬프트 | `ArticleGenerator` |

### templates/articles/ — [미구현] 기사 출력 포맷

### templates/sns/ — [미구현] SNS 게시 포맷

---

## data/ — 데이터 디렉토리 (git ignored)

```
data/
├── cache/              # Parquet 캐시 + TTL 메타데이터
│   ├── indices/        #   지수 OHLCV (^GSPC, ^IXIC, KOSPI 등)
│   ├── stocks/         #   종목 OHLCV (AAPL, 005930 등)
│   └── sentiment/      #   감정 분석 캐시
├── db/
│   └── stock_rich.db   # SQLite 메인 DB (6개 테이블)
├── generated/
│   └── images/         # matplotlib 생성 PNG 차트
├── processed/
│   ├── dashboards/     # 엑셀 대시보드 출력물
│   ├── reports/        # 텍스트/JSON 리포트
│   └── stocks/         # 종목별 상세 리포트
└── raw/                # 원시 수집 데이터
```

---

## 루트 파일

| 파일 | 설명 |
|------|------|
| `CLAUDE.md` | 프로젝트 규칙/컨벤션 (언어, 코딩, 보안, Git, 디렉토리) |
| `PROJECT_MAP.md` | **이 파일** — 프로젝트 전체 구조 지도 |
| `task.md` | 작업 관리 트래커 (TODO/진행중/완료) |
| `pyproject.toml` | 프로젝트 메타데이터, 의존성, 도구 설정 |
| `.env.example` | 환경변수 템플릿 (API 키 등) |
| `.gitignore` | Git 제외 규칙 (.venv, .env, data/, logs/) |

---

## 아키텍처 패턴

### 상속 구조
```
BaseCollector → BaseNewsCollector → RSSNewsCollector
             → BaseMarketCollector → KoreaMarketCollector, USMarketCollector

BaseAnalyzer → TechnicalAnalyzer, FundamentalAnalyzer, SentimentAnalyzer, StockScreener

BaseGenerator → ArticleGenerator, SummaryGenerator, HashtagGenerator, InsightGenerator, ImageGenerator

BaseRepository[T] → NewsRepository, MarketSnapshotRepository, ... (6개)
```

### 데이터 흐름
```
수집(Collectors) → 분석(Analyzers) → 생성(Generators) → 게시(Publishers)
       ↓                ↓                  ↓                 ↓
    캐시/DB           분석결과            기사/이미지        SNS 게시물
  (Parquet/SQLite)   (점수/신호)       (Claude API)     (Instagram/X)
                                            ↓
                                    내보내기(Exporters)
                                      → 엑셀 대시보드
```

### 핵심 의존성
```
설정: pydantic + pydantic-settings + PyYAML
DB: SQLAlchemy (ORM) + SQLite
로깅: structlog (JSON)
AI: anthropic (Claude API) + tenacity (재시도)
수집: yfinance (미국) + pykrx (한국) + feedparser (RSS)
분석: pandas + numpy (순수 계산, 외부 지표 라이브러리 없음)
생성: jinja2 (템플릿) + matplotlib (차트)
출력: openpyxl (엑셀) + pyarrow (Parquet 캐시)
```

---

## 진행 상태 (Phase별)

| Phase | 영역 | 상태 | 해당 디렉토리 |
|-------|------|------|--------------|
| 1 | 기반 구축 | **완료** | `config/`, `agents/`, `src/core/` |
| 2 | 수집+분석+저장+내보내기 | **완료** | `src/collectors/`, `src/analyzers/`, `src/storage/`, `src/exporters/`, `scripts/` |
| 3 | 콘텐츠 생성 | **완료** | `src/generators/`, `templates/prompts/` |
| 4 | SNS 게시 | 미착수 | `src/publishers/` (없음) |
| 5 | 워크플로우 | 미착수 | `src/workflows/` (없음) |
| 6 | 템플릿 | 미착수 | `templates/articles/`, `templates/sns/` |
| 7 | 테스트 | 미착수 | `tests/` |
