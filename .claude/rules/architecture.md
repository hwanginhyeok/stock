# Architecture

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
- `docs/프로젝트/` - TASK 관리 + 상세 로그

## 에이전트 역할

0. **팀장** - 워크플로우 오케스트레이션/품질 게이트/예외 처리/에이전트 지휘
1. **뉴스분석가** - 뉴스 수집/분류/감성분석
2. **시장분석가** - 시장 데이터 수집/기술적·기본적 분석/스크리닝
3. **아티클작성가** - Claude API 기반 콘텐츠 생성/품질 관리
4. **SNS매니저** - Instagram/X 포맷 변환/게시/스케줄 관리
5. **리서치어시스턴트** - 온디맨드 심층 리서치/SWOT/비교분석

### AI 모델 정책
- **Opus**: 아티클작성가, 리서치어시스턴트 (글쓰기·심층 분석 — 품질이 곧 산출물)
- **Sonnet**: 팀장, 뉴스분석가, 시장분석가, SNS매니저 (오케스트레이션·수집·포맷 변환)
- 태스크별 max_tokens / temperature 차별화로 파라미터 조절
- 설정: `config/settings.yaml` → `claude.models`
