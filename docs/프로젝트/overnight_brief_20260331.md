# 야간작업 브리핑 — 2026-03-31

## 작업 요약

GeoInvest 플랫폼 대규모 확장. 한 세션에서 아이디어 → 구현 → 10개 이슈 라이브까지 완료.

## 완료 항목

### 1. GeoInvest 기본 구현 (Step 1-2)
- [x] 벤치마크 스크립트 (`scripts/benchmark_geoinvest.py`) — F1 측정 완료
  - 뉴스: Entity F1=0.478, Rel F1=0.450 / Gold: Entity F1=0.647, Rel F1=0.561
  - **Approach C (하이브리드) 확정**
- [x] Enum 확장 (EntityType +2, EventType +3, EventStatus +1, LinkType +6)
- [x] DB 마이그레이션 (aliases, source_urls, geo_issue_id, entity_ids)
- [x] GeoIssue 모델 + Repository
- [x] FastAPI 웹 서버 (`src/web/app.py`) — 4개 API
- [x] D3.js 3칸럼 인터랙티브 UI (다크 테마)

### 2. 10개 이슈 시딩
| # | 이슈 | 엔티티 | 관계 | 이벤트 | severity |
|---|------|--------|------|--------|----------|
| 1 | 이란 전쟁 | 22 | 26 | 4 | critical |
| 2 | 비트코인 지정학 | 19 | 23 | 4 | major |
| 3 | IMEC 회랑 | 16 | 16 | 3 | critical |
| 4 | 트럼프 관세전쟁 2.0 | 16 | 19 | 5 | critical |
| 5 | AI/반도체 패권전쟁 | 17 | 22 | 4 | critical |
| 6 | 러시아-우크라이나 전쟁 | 9 | 10 | 3 | critical |
| 7 | 대만 해협 위기 | 8 | 7 | 2 | critical |
| 8 | 유럽 정치 위기 | 6 | 6 | 3 | major |
| 9 | 글로벌 AI 규제 경쟁 | 9 | 8 | 3 | major |
| 10 | 일본 금리 전환 (BOJ) | 7 | 5 | 3 | major |

### 3. 핫 종목 연결
- US: NVDA, TSLA, PLTR, LMT, XOM (+ 기존 TSMC, ASML 등)
- KR: 삼성전자, SK하이닉스, 한화에어로스페이스, 현대차, HD현대

### 4. 스마트 뉴스 수집
- [x] 15분 cron 뉴스 수집 + 키워드 분류 (AI 토큰 0)
- [x] 1시간 cron AI 추출 (Claude Opus)
- [x] 소스 점수 시스템 (관련 기사 비율 추적)
- [x] 지정학 특화 RSS 8개 추가 (Reuters, Al Jazeera, BBC, CoinDesk 등)
- [x] LIVE 뉴스 티커 + 이슈 컬러 태그

### 5. 이슈별 관계선 분리
- [x] `OntologyLink.geo_issue_id` 추가 — 같은 엔티티 쌍이 이슈별로 다른 관계 가능
- [x] graph API: geo_issue_id 필터링

### 6. 디자인 리뷰
- [x] 이란 대시보드 리뷰: B / AI Slop: A
- [x] GeoInvest 와이어프레임 리뷰: B- / AI Slop: A

## 이벤트 실제 날짜 보정
- [x] 11개 이벤트 started_at → 실제 발생일 수정 (시딩 시점이 아닌 사건 발생일)

## 미완료 / 다음 작업

### 아키텍처 전환 (사용자 의견 반영, 다음 세션)
> "뉴스에서 팩트를 가져온다 → 타임라인으로 정리 → 관계도 자동 파생"
> 이러면 타임라인을 별도로 안 만들어도 됨

현재: 수동 시딩 → 고정 관계 → 그래프
목표: 뉴스 → 팩트(시간, 엔티티, 사건) → 타임라인 자동 → 관계도 자동 파생

기존 `extract_facts.py` + `fact_extractor.py`를 연결하면 됨.

### 기타 TODO
- [ ] 팩트 기반 아키텍처 전환 설계
- [ ] 포트폴리오 영향 스트립 데이터 연결
- [ ] 테스트 작성 (~15개)
- [ ] 자동 이슈 그룹핑 로직

## 커밋 로그
```
cbbca4c [코드] GeoInvest 벤치마크 스크립트
a441637 [코드] GeoInvest Step 2 — enum + 스키마 + GeoIssue + 마이그레이션
4bb5e78 [코드] GeoInvest Step 2 — FastAPI + D3.js + Repository
87c9028 [코드] 이란 전쟁 데이터 시딩 + graph API 수정
819a004 [코드] 비트코인+IMEC + 뉴스 티커 + 자동 업데이트
8471e86 [코드] 이슈별 필터링 — entity_ids
80ee0b9 [수정] IMEC 이란 관계 → hostile
bae346c [코드] 관세전쟁 + AI/반도체 + 스테이블코인 + 티커 속도
c5e90cc [수정] 이벤트 날짜 보정 + 티커 속도
7a13a1e [코드] 이슈별 관계선 분리 — geo_issue_id
8376201 [코드] 스마트 뉴스 수집 — 15분 cron + 분류기 + 소스 점수
8d4c9d8 [코드] 야간작업 — 5개 신규 이슈 + 핫 종목 + 키워드 확장
```

## 서버 실행
```bash
uvicorn src.web.app:app --reload --port 8200
# http://localhost:8200 에서 10개 이슈 관계도 확인
```
