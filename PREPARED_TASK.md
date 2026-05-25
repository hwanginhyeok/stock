# Prepared Tasks

> **InvestOS 인프라 + 테슬라 entity 체계 집중** — HIH_2 업무 entity 패턴을 stock에 적용
> 아티클 작업은 전부 보류, 인프라/데이터 파이프라인 우선

## P1 — 활성

| # | 태스크 | 우선순위 | depends | 비고 |
|---|--------|----------|---------|------|
| 1-46 | `stock-notion-sync` 스킬 — Notion DB 연동 PoC | P1 | 1-43, 1-44 | hih-notion-sync 복제. 이슈 DB 1개부터 |
| 1-53 | 빗각·채널 기반 시그널 (인범 매매법) | P1 | 1-49 | 빗각 터치=매수 대기, 이탈 후 회복=강한 매수, 채널 상단=익절 |
| 1-71 | 1-47 Phase 3 — tesla_api.py DB 전환 + dual-read 1주일 + FK 보강 | P1 | 1-47 ✅ | Hermes Phase 1 §8-B + §8-C 권고. tesla_api.py 5개 함수 (list_issues/get_issue_detail/list_tagged_issues/count_tagged_issues + ...)를 DB read로 전환. CSV/DB dual-read 단계 1주일 후 CSV read 제거. TeslaMilestoneDB FK 컬럼 추가 + PRAGMA foreign_keys=ON. PM 발주 대기 |
| 1-48 | Tesla 보조 데이터 (essence_scores/master_plan/moat_status/thesis/timeline/topics/portfolio 7파일) → SQLite ORM 마이그 | P2 | 1-47 ✅ | 1-47 Phase 1 §8-D 권고. JSON 4개 + CSV 3개. 각각 도메인 ORM 신설 또는 generic key-value 테이블 전략 선택. tesla_api.py가 사용 중이므로 호환 유지 필요. Phase 1: 매핑표 → Phase 2: 마이그 → Phase 3: tesla_api 듀얼 read |
| 1-67 | sentiment archive 잔여 부채 정리 — analyzers + 테스트 5파일 | P2 | — | `src/analyzers/expected_move.py` + `src/analyzers/market_sentiment.py` + `tests/test_collectors/test_sentiment/` 5파일이 archived 6 클래스(AAII/GoogleTrends/NaverCommunity/OptionsIV/Reddit/StockTwits) 참조. cron 경로 외라 운영 영향 0이지만 해당 모듈 사용 시 ImportError 재발. 1-68 cron fix PR의 잔여 부채 보고로 발견 |

## 보류 (InvestOS 인프라 집중 전환으로 일시 중단)

### 아티클 보류 (4-x)
| # | 태스크 | 우선순위 | 비고 |
|---|--------|----------|------|
| 4-16 | 026 TeraFab — 테슬라·xAI 칩 공장 | P1 | ⏸️ v1 271줄 완료, 퇴고 대기 |
| 4-17 | 027 파운드리의 역설 | P1 | ⏸️ 아웃라인 대기 |
| 4-18 | 테슬라·xAI·SpaceX 테라팹 | P1 | ⏸️ 리서치 대기 |
| 4-19 | 029 GEOPO — 호르무즈/이란/IMEC | P1 | ⏸️ v1 280줄, 지정학 |

### 리서치 보류 (5-x)
| # | 태스크 | 우선순위 | 비고 |
|---|--------|----------|------|
| 5-11 | 바이오 섹터 리서치 허브 | P1 | ⏸️ 테슬라 집중 전환으로 보류 |

### P1 보류 (기존)
| # | 태스크 | 우선순위 | depends | 비고 |
|---|--------|----------|---------|------|
| 4-5 | 팔란티어 심층분석 시리즈 (6편) | P1 | user: X 게시 | ⏸️ 보류 |
| 4-11 | KR-03~06: 현대차 시리즈 (4편) | P1 | | ⏸️ 보류 |
| 4-6 | 블록체인 #3: BMNR — ETH 트레저리 | P1 | | ⏸️ 보류 |
| 4-7 | 블록체인 #4: CRCL — USDC 디지털달러 | P1 | | ⏸️ 보류 |
| 5-8 | 이란 전쟁 지정학 온톨로지 Phase 2 | P1 | | ⏸️ 보류 |

### P2 보류
| # | 태스크 | 우선순위 | depends | 비고 |
|---|--------|----------|---------|------|
| 1-40 | 엔티티 타임라인 병합 | P2 | 1-39 완료 | ⏸️ 보류 |
| 4-12 | KR-07: 곱셈이 사라진다 — 반도체 | P2 | user: 구조안 | ⏸️ 보류 |
| 4-15 | HOOD — Robinhood 리테일 | P2 | | ⏸️ 보류 |
| 4-13 | 일론머스크 생태계 카드뉴스 | P2 | | ⏸️ 일단 보류 (테슬라 콘텐츠는 4-18로 통합) |
| 3-1 | 지표 해석 체계 고도화 | P2 | | ⏸️ 보류 |
| 3-2 | 두 축 연결 체계 — 레짐별 포지션 | P2 | 3-1 | ⏸️ 보류 |
| 1-29 | 이란 전쟁 대시보드 design review | P2 | | ⏸️ 보류 |

### P3 보류
| # | 태스크 | 우선순위 | depends | 비고 |
|---|--------|----------|---------|------|
| 4-14 | 일론머스크 생태계 상상콘텐츠 (웹 룰렛) | P3 | | ⏸️ 보류 |
| 1-14 | articles/ 기사 출력 포맷 템플릿 | P3 | | ⏸️ 보류 |
| 1-15 | 에이전트별 시작 전 체크리스트 | P3 | | ⏸️ 보류 |
| 1-16 | 에이전트별 스킬 매뉴얼 | P3 | | ⏸️ 보류 |
| 1-17 | CI/CD 파이프라인 | P3 | | ⏸️ 보류 |
| 1-18 | Docker 컨테이너화 | P3 | | ⏸️ 보류 |
| 1-19 | 스케줄러 설정 | P3 | | ⏸️ 보류 |
