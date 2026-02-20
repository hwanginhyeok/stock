# 주식부자프로젝트 - 프로젝트 규칙

## 프로젝트 개요
한국/미국 주식 시장 분석 + AI 콘텐츠 생성 + SNS 자동 게시 플랫폼

## 언어 규칙
- **코드**: 변수명, 함수명, 클래스명, 주석 → 영어
- **콘텐츠/문서**: 사용자 대면 콘텐츠, 문서, 커밋 메시지 → 한국어
- **설정 파일**: 키는 영어, 값은 용도에 따라 한국어/영어

## Python 컨벤션
- Python 3.11+ 필수
- PEP 8 준수 (black 포매터, ruff 린터)
- Type hints 모든 함수에 필수
- Google 스타일 docstring
- f-string 사용 (% 포매팅, .format() 금지)

## 코드 패턴
- **데이터 모델**: Pydantic BaseModel 사용
- **로깅**: structlog 사용, 구조화된 JSON 로깅
- **재시도**: tenacity 라이브러리로 API 호출 재시도 (max 3회, exponential backoff)
- **설정**: pydantic-settings로 환경변수 + YAML 통합 관리
- **DB**: SQLAlchemy ORM, 비동기 지원
- **상속**: 각 모듈은 base class를 정의하고 구체 구현은 상속

## 워크플로우 원칙
1. **수집** → **분석** → **생성** → **게시** 순서 엄수
2. 모든 단계의 결과는 DB에 저장
3. 생성된 콘텐츠에는 반드시 면책조항 포함
4. 투자 권유/추천 표현 금지

## 보안 규칙
- API 키 하드코딩 절대 금지 → `.env` 파일로 관리
- `.env` 파일은 `.gitignore`에 포함
- 로그에 API 키, 토큰 등 민감 정보 출력 금지
- 크롤링 시 robots.txt 준수, rate limiting 적용

## Git 컨벤션
- 커밋 메시지: `[카테고리] 내용` 형식
- 카테고리: `설정`, `수집`, `분석`, `생성`, `게시`, `인프라`, `테스트`, `문서`, `수정`
- 예시: `[설정] 프로젝트 초기 구조 생성`

## 디렉토리 구조
- `config/` - YAML 설정 파일
- `agents/` - 에이전트 역할 정의
- `src/core/` - 공통 인프라 (config, logger, models, db, claude_client)
- `src/collectors/` - 데이터 수집 (news, market)
- `src/analyzers/` - 분석 (technical, fundamental, sentiment, screener)
- `src/generators/` - 콘텐츠 생성 (article, summary, insight, image, hashtag)
- `src/publishers/` - SNS 게시 (instagram, x, formatter, media)
- `src/storage/` - DB CRUD, 테이블 정의
- `src/workflows/` - 오케스트레이션 (morning, closing, weekly, breaking, research)
- `templates/` - Jinja2 템플릿 (articles, sns, prompts)
- `data/` - 데이터 (raw, processed, cache, db) - git ignored
- `logs/` - 로그 파일 - git ignored
- `tests/` - 테스트
- `scripts/` - 유틸리티 스크립트

## 에이전트 역할
1. **뉴스분석가** - 뉴스 수집/분류/감성분석
2. **시장분석가** - 시장 데이터 수집/기술적·기본적 분석/스크리닝
3. **아티클작성가** - Claude API 기반 콘텐츠 생성/품질 관리
4. **SNS매니저** - Instagram/X 포맷 변환/게시/스케줄 관리
5. **리서치어시스턴트** - 온디맨드 심층 리서치/SWOT/비교분석
