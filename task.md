# Task Management

> **규칙**: 모든 작업은 시작 전에 "진행 중"으로 이동, 완료 후 "완료"로 이동할 것.

---

## 해야 할 일 (TODO)

### Phase 4: SNS 게시 (publishers)
- [ ] `src/publishers/base.py` — BasePublisher 추상 클래스
- [ ] `src/publishers/formatter.py` — ContentFormatter (플랫폼별 포맷 변환)
- [ ] `src/publishers/media.py` — MediaProcessor (이미지 리사이징/최적화)
- [ ] `src/publishers/instagram.py` — InstagramPublisher (instagrapi)
- [ ] `src/publishers/x.py` — XPublisher (tweepy)

### Phase 5: 워크플로우 (workflows)
- [ ] `src/workflows/base.py` — BaseWorkflow 추상 클래스
- [ ] `src/workflows/morning.py` — MorningBriefingWorkflow (모닝브리핑)
- [ ] `src/workflows/closing.py` — ClosingReviewWorkflow (장마감 리뷰)
- [ ] `src/workflows/weekly.py` — WeeklyReviewWorkflow (주간 리뷰)
- [ ] `src/workflows/breaking.py` — BreakingNewsWorkflow (속보)
- [ ] `src/workflows/research.py` — ResearchWorkflow (온디맨드 리서치)

### Phase 6: 템플릿
- [x] `templates/prompts/` — Claude 프롬프트 템플릿 (모닝브리핑, 장마감, 종목분석, 주간) ← Phase 3에서 완료
- [ ] `templates/articles/` — 기사 출력 포맷 템플릿
- [ ] `templates/sns/` — SNS 게시 포맷 템플릿 (Instagram, X)

### Phase 7: 테스트
- [ ] `tests/test_collectors/` — 수집기 단위 테스트
- [ ] `tests/test_analyzers/` — 분석기 단위 테스트
- [ ] `tests/test_generators/` — 생성기 단위 테스트
- [ ] `tests/test_exporters/` — 내보내기 단위 테스트
- [ ] `tests/test_workflows/` — 워크플로우 통합 테스트

### 기타
- [ ] 에이전트별 시작 전 체크리스트 작성 (`agents/checklists/`)
- [ ] 에이전트별 스킬 매뉴얼 작성 (`agents/manuals/`)
- [ ] CI/CD 파이프라인 구성 (GitHub Actions)
- [ ] Docker 컨테이너화
- [ ] 스케줄러 설정 (APScheduler / cron)

---

## 진행 중 (IN PROGRESS)

_(현재 진행 중인 작업 없음)_

---

## 완료 (DONE)

### Phase 1: 프로젝트 기반 구축
- [x] 프로젝트 초기 구조 생성 (디렉토리, pyproject.toml, .gitignore)
- [x] `CLAUDE.md` — 프로젝트 규칙/컨벤션 정의
- [x] `config/settings.yaml` — 앱 설정
- [x] `config/news_sources.yaml` — 뉴스 소스 설정
- [x] `config/market_config.yaml` — 시장 설정 (지수, 워치리스트, 기술/기본 분석 파라미터)
- [x] `config/content_config.yaml` — 콘텐츠 설정
- [x] `config/sns_config.yaml` — SNS 설정
- [x] `agents/` — 5개 에이전트 역할 정의서 (뉴스분석가, 시장분석가, 아티클작성가, SNS매니저, 리서치어시스턴트)
- [x] `src/core/config.py` — Pydantic-settings YAML 통합 설정 시스템
- [x] `src/core/logger.py` — structlog JSON 로깅
- [x] `src/core/models.py` — 도메인 모델 (NewsItem, MarketSnapshot, StockAnalysis 등 6개 + Enum 9개)
- [x] `src/core/database.py` — SQLAlchemy ORM 모델 + DB 관리
- [x] `src/core/claude_client.py` — Claude API 클라이언트 (모델 선택, 재시도, 토큰 추적)
- [x] `src/core/exceptions.py` — 에러 계층 구조 (StockRichError + 7개 서브클래스)
- [x] `src/core/cache_manager.py` — Parquet 캐시 (TTL, metadata 추적)

### Phase 2: 수집 + 분석 + 저장 + 내보내기
- [x] `src/collectors/news/base.py` — BaseNewsCollector 추상 클래스
- [x] `src/collectors/news/rss_collector.py` — RSS 뉴스 수집기
- [x] `src/collectors/news/dedup.py` — 제목 유사도 기반 중복 필터
- [x] `src/collectors/market/base.py` — BaseMarketCollector 추상 클래스
- [x] `src/collectors/market/korea_collector.py` — pykrx 한국 시장 수집
- [x] `src/collectors/market/us_collector.py` — yfinance 미국 시장 수집
- [x] `src/analyzers/base.py` — BaseAnalyzer 추상 클래스
- [x] `src/analyzers/technical.py` — 기술 분석 (SMA, RSI, MACD, BB, 0-100 점수)
- [x] `src/analyzers/fundamental.py` — 기본 분석 (PER, PBR, ROE, 0-100 점수)
- [x] `src/analyzers/sentiment.py` — 감성 분석 (Claude Haiku 기반)
- [x] `src/analyzers/screener.py` — 종합 스크리닝 (기술+기본 가중 복합 점수)
- [x] `src/analyzers/trend.py` — 트렌드 지표 (ATR, ADX, Supertrend)
- [x] `src/analyzers/market_sentiment.py` — 시장 심리 (Fear/Greed 인덱스)
- [x] `src/storage/base.py` — BaseRepository 제네릭 CRUD
- [x] `src/storage/news_repository.py` — NewsRepository
- [x] `src/storage/market_snapshot_repository.py` — MarketSnapshotRepository
- [x] `src/storage/stock_analysis_repository.py` — StockAnalysisRepository
- [x] `src/storage/article_repository.py` — ArticleRepository
- [x] `src/storage/sns_post_repository.py` — SNSPostRepository
- [x] `src/storage/research_report_repository.py` — ResearchReportRepository
- [x] `src/exporters/base.py` — Excel 스타일/유틸 + 차트 헬퍼 함수
- [x] `src/exporters/dashboard_builder.py` — Overview 시트 (정규화 차트 + 개별 미니차트)
- [x] `src/exporters/index_detail_builder.py` — 지수 상세 시트 (5개 차트 + 기준선)
- [x] `src/exporters/constituents_builder.py` — 구성 종목 시트
- [x] `src/exporters/sentiment_builder.py` — 감정 분석 시트 (VIX 기준선 포함)
- [x] `scripts/generate_dashboard.py` — 종합 대시보드 생성 스크립트
- [x] `scripts/export_nvda.py` — NVDA 상세 리포트 스크립트
- [x] `scripts/export_sp500_top20.py` — S&P 500 Top 20 대시보드 스크립트

### Phase 3: 콘텐츠 생성 (generators) + 프롬프트 템플릿
- [x] `src/generators/base.py` — BaseGenerator 추상 클래스 (Jinja2, 품질검증, 면책조항)
- [x] `templates/prompts/morning_briefing.j2` — 모닝브리핑 프롬프트 템플릿
- [x] `templates/prompts/closing_review.j2` — 장마감 리뷰 프롬프트 템플릿
- [x] `templates/prompts/stock_analysis.j2` — 종목분석 프롬프트 템플릿
- [x] `templates/prompts/weekly_review.j2` — 주간 리뷰 프롬프트 템플릿
- [x] `src/generators/article.py` — ArticleGenerator (4종 기사 통합, Claude API 기반)
- [x] `src/generators/summary.py` — SummaryGenerator (Haiku 요약)
- [x] `src/generators/hashtag.py` — HashtagGenerator (config + ticker + AI 토픽)
- [x] `src/generators/insight.py` — InsightGenerator (SNS용 한줄 코멘트)
- [x] `src/generators/image.py` — ImageGenerator (matplotlib 차트 이미지)
- [x] `src/generators/__init__.py` — 패키지 export

### 엑셀 차트 개선
- [x] X/Y축 라벨 추가 (축 제목 + 숫자 포맷)
- [x] Y축 10% 패딩 (가격 범위 여유 공간)
- [x] 10등분 눈금 + 숫자 표시 (Y축 majorUnit, X축 tickLblSkip)
- [x] 축 라벨 가시성 수정 (delete=False 명시, yyyy-mm Excel 호환 포맷)
- [x] VIX/RSI 기준선 (참조 라인 시리즈)

### 문서 / 기타
- [x] `PROJECT_MAP.md` — 프로젝트 전체 구조 지도 (디렉토리/파일별 설명)
- [x] GitHub 리포지토리 연동 (`hwanginhyeok/stock`)

---

## 진행률

| Phase | 영역 | 상태 | 비율 |
|-------|------|------|------|
| 1 | 기반 구축 (core, config, agents) | **완료** | 100% |
| 2 | 수집 + 분석 + 저장 + 내보내기 | **완료** | 100% |
| 3 | 콘텐츠 생성 (generators) + 프롬프트 템플릿 | **완료** | 100% |
| 4 | SNS 게시 (publishers) | 미착수 | 0% |
| 5 | 워크플로우 (workflows) | 미착수 | 0% |
| 6 | 템플릿 (templates) | 미착수 | 0% |
| 7 | 테스트 (tests) | 미착수 | 0% |

**전체 진행률: ~55% (Phase 1-3 완료, Phase 4-7 미착수)**
