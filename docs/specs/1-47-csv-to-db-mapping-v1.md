# 1-47 Tesla CSV → SQLite ORM 매핑표 v1

> **작성**: hermes pane 2 (Claude Opus 4.7), 2026-05-24
> **상태**: Phase 1 매핑표 v1 / 코드 작성 X / DB write X
> **검토**: PM → 사용자 결정 항목 §7 처리 → Phase 2 별도 발주

---

## 0. 요약 — 매핑 결정 요지

| Source | 권장 타겟 | 핵심 이유 |
|---|---|---|
| `issues.csv` (10건) | **신규 `TeslaIssueDB` ORM 신설** (옵션 C 추천) | `TeslaIssue` Pydantic이 이미 정의되어 있고 (line 501), CSV 컬럼이 Ontology* 일반 모델의 properties JSON에 강제로 욱여넣기엔 손실이 큼 (thesis_side / blocker / owner / deadline 같은 워크플로우 필드). 사용자가 enum까지 분리해 둔 의도가 Tesla 전용 테이블로 보임 |
| `milestones.csv` (24건) | **신규 `TeslaMilestoneDB` 또는 `OntologyEventDB` (story_thread=issue_id)** (옵션 비교 §3-B) | milestone은 시간축 있는 사건이라 `OntologyEvent` 의미와 일치. 다만 issue와의 1:N 관계를 `story_thread` 그루핑으로 갈지 `OntologyLink`로 갈지 결정 필요 |
| `tagged_issues.csv` (10건) | **사용자 결정 필요** — issues와 별개 stream인지, 같은 issue의 일간 view인지 불명 (§7 Q3) | ID 체계 / 컬럼셋 / sentiment 추가 필드 모두 issues와 다름. PM이 사용자에 문의 후 결정 |

전반적으로 **시나리오 C (신규 Tesla 도메인 테이블 신설)** 추천. 단점: ORM 추가 작업이 Phase 2 발주에 포함되어야 함 (그러나 `TeslaIssue` Pydantic은 이미 존재 → 매핑 자체는 1:1에 가까움).

---

## 1. 조사 결과 (Phase 1 SSOT)

### 1-A. Source CSV 실측

**issues.csv** (`data/research/stocks/tesla/issues.csv`, 10건)
- ID 체계: `TSLA-{E/P/C/F/I/R/M}-{NNN}` (7개 카테고리 모두 사용 — E=2, P=2, C=2, F/I/M/R=1)
- 19 컬럼: `issue_id, title, category, essence_component, status, severity, thesis_side, first_occurred_at, last_event_at, deadline, blocker, owner, related_topic_id, related_entity_ids, source_hint, notion_page_id, created_at, last_updated`
- 값 분포:
  - `status`: developing(8), resolved(2)
  - `severity`: critical(3), major(5), moderate(2)
  - `thesis_side`: bull(8), bear(2)
  - `essence_component`: vertical_integration / autonomy_robotics / first_principle_engineering / clean_energy_mission (enum value 그대로)

**milestones.csv** (24건)
- ID 체계: `{issue_id}-M{N}` (예: `TSLA-E-001-M1`)
- 9 컬럼: `milestone_id, issue_id, title, occurred_at, target_at, status, confidence, evidence_url, source_hint`
- `status` 분포: done(18), in_progress(3), planned(3)
- `issue_id`로 issues.csv와 1:N 외래키 관계 (`tesla_api.py:644-665`에서 이미 그렇게 사용 중)

**tagged_issues.csv** (10건)
- ID 체계: `TSLA-{I/P/...}-{NNN}` — issues.csv와 **별개 시리얼**
- 8 컬럼: `issue_id, title, category, essence_component, severity, sentiment, date, summary`
- `category` 분포: product(3), capability(2), essence(1), factory(1), initiative(1), musk_statement(1), regulatory(1)
  - issues.csv는 `TSLA-E` (접두사), tagged_issues.csv는 `essence` (풀네임). TeslaIssueCategory enum value(`E = "essence"`)는 **풀네임 쪽과 일치** → tagged_issues가 enum-aligned
- `sentiment` 분포: positive(7), negative(2), neutral(1) — issues.csv에 없는 필드

**보조 (Phase 1 범위 밖)**: essence_scores.csv(4), master_plan.csv, moat_status.csv, thesis.json, timeline_events.json, topics_quarterly.json, portfolio.json — Phase 3 별도 task로 분리 권장.

### 1-B. 타겟 ORM (read-only, 기존 정의)

| ORM | 핵심 컬럼 | 비고 |
|---|---|---|
| `OntologyEntityDB` (database.py:325) | id, name, entity_type, ticker, market, properties Text(JSON), aliases Text(JSON), status, created_at | "real-world entity" 정의 (회사/사람/자산) |
| `OntologyEventDB` (database.py:348) | id, title, summary, event_type, severity, market, started_at, last_article_at, status, article_count, story_thread, created_at | "시간축 있는 사건"; story_thread로 그루핑 |
| `OntologyLinkDB` (database.py:377) | id, link_type, source_type, source_id, target_type, target_id, confidence, evidence, source_urls Text(JSON), geo_issue_id, created_at | 2개 객체 간 typed/directional 관계 |
| (없음) `TeslaIssueDB` | — | **Pydantic만 존재(models.py:501), ORM 미생성** |

### 1-C. 기존 Pydantic 모델 (models.py)

- `TeslaIssue` (line 501): `issue_id, category, title, summary, essence_component, severity, status, related_entity_ids, related_event_ids`
- `TeslaEssenceComponent` enum: VERTICAL_INTEGRATION / FIRST_PRINCIPLE_ENGINEERING / CLEAN_ENERGY_MISSION / AUTONOMY_ROBOTICS
- `TeslaIssueCategory` enum: `E="essence"`, `P="product"`, `C="capability"`, `F="factory"`, `I="initiative"`, `R="regulatory"`, `M="musk_statement"`
- `Severity` enum: CRITICAL / MAJOR / MODERATE / MINOR
- `EventStatus` enum: DEVELOPING / RESOLVED / STALE / ESCALATING

### 1-D. BaseRepository CRUD (storage/base.py)

- `create(model)` / `create_many(models)` — insert만
- `get_by_id(id)` / `get_many(filters, ...)` / `count(filters)` — read
- `update(id, **updates)` — partial update
- `delete(id)`
- **upsert는 명시 메서드 없음** — 마이그 스크립트에서 `get_by_id → 있으면 update, 없으면 create` 수동 구현 필요

### 1-E. 역호환 검증 source (`src/web/tesla_api.py`)

| 함수 (line) | CSV 사용 | 의미 |
|---|---|---|
| `list_issues()` (570) | issues.csv 전체 + category/status/thesis_side/essence_component 필터 | API: /api/tesla/issues |
| `get_issue_detail()` (619) | issues.csv 1건 + 같은 issue_id의 milestones.csv 1:N | API: /api/tesla/issues/{id} |
| `list_tagged_issues()` (185) | tagged_issues.csv 전체 (date desc 정렬) | API: /api/tesla/tagged-issues |
| `count_tagged_issues()` (207) | tagged_issues.csv 카운트 | API 보조 |

→ Phase 3 (tesla_api DB 전환)에서 이 API들이 DB도 읽도록 변경 가능해야 함. 즉 매핑 결정은 이 API 응답 호환을 깨면 안 됨.

---

## 2. issues.csv 매핑 옵션 (핵심 결정점)

### 옵션 A — OntologyEntity로 강제 매핑

```
1 issue = 1 OntologyEntity (entity_type="tesla_issue")
properties JSON에 essence_component / thesis_side / severity / blocker / owner / deadline 등 보관
```

| 장점 | 단점 |
|---|---|
| 기존 ORM 재사용, 신규 테이블 0 | OntologyEntity 정의("real-world entity: company, person, asset, institution") 의미 왜곡 — issue는 entity가 아니라 watch-list/논쟁 항목 |
| `find_by_name()` 같은 쿼리가 그대로 동작 | thesis_side / blocker 등 워크플로우 컬럼이 indexed 안 됨 (properties JSON 내부) → 필터 쿼리 시 SQL JSON 함수 또는 row scan 필요 |
| 마이그 스크립트 짧음 | tesla_api 필터(`category, status, thesis_side, essence_component`)를 SQL where로 표현 불가 → 응답 호환 어려움 |

### 옵션 B — OntologyEvent로 강제 매핑

```
1 issue = 1 OntologyEvent (event_type="tesla_issue", story_thread=category)
title/summary/severity/status는 직접 매핑
나머지(thesis_side / deadline / owner / blocker / related_topic_id) → properties? 없음 → 신규 필드 필요?
```

| 장점 | 단점 |
|---|---|
| status/severity/started_at(=first_occurred_at)이 ORM 기존 컬럼과 일치 | OntologyEvent 정의("discrete event with a time axis") — issue는 "지속 상태"라 의미 약간 다름 |
| story_thread로 milestone 그루핑 가능 | OntologyEventDB에 properties JSON 컬럼 **없음** → thesis_side/blocker/owner/deadline을 보관할 자리 없음. summary 안에 JSON 박는 hack? |

### 옵션 C — 신규 `TeslaIssueDB` ORM 신설 ⭐ **추천**

```
1 issue = 1 TeslaIssueDB row
이미 TeslaIssue Pydantic(models.py:501)이 정의됨 → ORM/Repository 추가만 하면 1:1 매핑
CSV 컬럼 거의 그대로 → indexed where 가능, tesla_api 응답 호환 유지
```

| 장점 | 단점 |
|---|---|
| 도메인 정합성 — Tesla 전용 추적은 Tesla 테이블 | Phase 2에 ORM/Repo 신설 작업 추가 (≈ 80~120 LOC) |
| `category`/`status`/`thesis_side`/`essence_component` 모두 indexed column 가능 → tesla_api 필터 호환 | 다른 종목 확장 시 같은 패턴 반복 (`AAPLIssueDB`?) — but 현재 PRD가 Tesla 전용이라 비-블로커 |
| `TeslaIssue` Pydantic 활용 → BaseRepository[TeslaIssue] 패턴 그대로 | DB 스키마 변경(Alembic 마이그 등) 필요 — 새 task |

### 매핑 컬럼표 (옵션 C 기준)

| CSV 컬럼 | 변환 | 타겟 TeslaIssueDB 필드 | 비고 |
|---|---|---|---|
| `issue_id` | as-is | `id` (PK, String(20)) | TSLA-E-001 형식, PK로 그대로 사용 |
| `title` | as-is | `title` (String(500)) | |
| `category` | `category.split('-')[1]` → `TeslaIssueCategory(name)` | `category` (Enum, indexed) | "TSLA-E" → enum E → value="essence" |
| `essence_component` | `TeslaEssenceComponent(value)` | `essence_component` (Enum nullable, indexed) | enum value 그대로 매치 |
| `status` | `EventStatus(value)` 또는 신규 IssueStatus | `status` (Enum, indexed) | "developing"/"resolved" → DEVELOPING/RESOLVED. "open" 가능성 §7 Q4 |
| `severity` | `Severity(value)` | `severity` (Enum, indexed) | "critical"/"major"/"moderate" 매치 |
| `thesis_side` | as-is (StrEnum 신설?) | `thesis_side` (String(10), indexed) | "bull"/"bear" — enum 신설 옵션 §7 Q5 |
| `first_occurred_at` | `datetime.fromisoformat(d + "T00:00:00+09:00")` | `first_occurred_at` (DateTime, nullable) | KST → UTC 변환 정책 §7 Q6 |
| `last_event_at` | 동상 | `last_event_at` (DateTime, nullable) | |
| `deadline` | 동상 (빈 문자열 → None) | `deadline` (DateTime, nullable) | |
| `blocker` | as-is (빈 문자열 → "") | `blocker` (Text, default="") | |
| `owner` | as-is | `owner` (String(50), default="") | |
| `related_topic_id` | as-is | `related_topic_id` (String(50), default="") | |
| `related_entity_ids` | CSV 자체 빈 컬럼 다수 — 처리 정책 §7 Q7 | `related_entity_ids` (Text JSON, default="[]") | |
| `source_hint` | as-is | `source_hint` (Text, default="") | |
| `notion_page_id` | as-is (빈 문자열 다수) | `notion_page_id` (String(64), default="") | |
| `created_at` | 빈 값 → `_utcnow()` | `created_at` (DateTime, default=_utcnow) | CSV 대부분 비어있음 |
| `last_updated` | 빈 값 → `_utcnow()` | `updated_at` (DateTime, default=_utcnow) | |

---

## 3. milestones.csv 매핑 옵션

### 옵션 B-1 — 신규 `TeslaMilestoneDB` ORM

```
1 milestone = 1 TeslaMilestoneDB row, FK issue_id → TeslaIssueDB.id
```

| 장점 | 단점 |
|---|---|
| issues와 동일 도메인, FK 명확 | 신규 테이블 1개 추가 |
| tesla_api 1:N 응답 호환 (issue_id로 단순 where) | |

### 옵션 B-2 — `OntologyEventDB` + story_thread

```
1 milestone = 1 OntologyEvent (event_type="tesla_milestone", story_thread=issue_id, market="us")
title/summary/started_at(=occurred_at)/status는 직접 매핑
target_at / confidence / evidence_url / source_hint → ?? (OntologyEventDB에 자리 없음)
```

| 장점 | 단점 |
|---|---|
| 기존 ORM 재사용 | OntologyEventDB에 `confidence` / `target_at` 컬럼 없음 — summary에 JSON 박는 hack 또는 `properties` 신규 컬럼 추가 |
| story_thread로 그루핑 쿼리 가능 | event_type을 Tesla 전용 string으로 두면 EventType enum과 약간 부정합 (현재 EventType은 정의 안 본 상태) |

### 옵션 B-3 — 하이브리드: milestone을 OntologyEvent + OntologyLink

```
1 milestone = 1 OntologyEvent + 1 OntologyLink(link_type="involves", source=event, target=issue)
```

| 장점 | 단점 |
|---|---|
| Ontology 그래프 의미 충실 | 한 milestone 적재에 2개 INSERT — 트랜잭션 관리 필요 |
| 다른 entity와도 link 가능 (확장성) | 마이그 스크립트 복잡도 ↑ |

### 추천

**옵션 B-1** (신규 TeslaMilestoneDB). 옵션 C(issues 신규 테이블)와 정합, FK 명확, target_at/confidence/evidence_url 모두 indexed column 가능. issue와 milestone의 1:N은 직관적이고 tesla_api에서 이미 그렇게 사용 중 (`tesla_api.py:644-665`).

### 매핑 컬럼표 (옵션 B-1 기준)

| CSV 컬럼 | 변환 | 타겟 TeslaMilestoneDB 필드 | 비고 |
|---|---|---|---|
| `milestone_id` | as-is | `id` (PK, String(30)) | TSLA-E-001-M1 형식 |
| `issue_id` | as-is | `issue_id` (FK → TeslaIssueDB.id, indexed) | 1:N 외래키 |
| `title` | as-is | `title` (String(500)) | |
| `occurred_at` | datetime 변환 (빈 값 → None) | `occurred_at` (DateTime, nullable, indexed) | |
| `target_at` | datetime 변환 (빈 값 → None) | `target_at` (DateTime, nullable, indexed) | |
| `status` | 매핑 결정 필요 §7 Q4 | `status` (Enum or String(20)) | "done"/"in_progress"/"planned" — EventStatus enum에 "planned" 없음 |
| `confidence` | `int(value)` (0~100) | `confidence` (Integer, default=100) | percentage |
| `evidence_url` | as-is | `evidence_url` (Text, default="") | |
| `source_hint` | as-is | `source_hint` (Text, default="") | |
| (없음) | 적재 시점 | `created_at` (default=_utcnow) | |

---

## 4. tagged_issues.csv 매핑 옵션

### 옵션 T-1 — 신규 `TeslaTaggedIssueDB`, issues와 완전 별개

전제: tagged_issues는 issues와 **별개 stream** (예: 일간 자동 태깅 / 외부 import / 다른 분석가가 별도로 정리). issue_id 시리얼이 별개라는 사실이 이를 뒷받침.

### 옵션 T-2 — issues와 같은 테이블, sentiment 필드 추가

전제: tagged_issues는 issues의 가벼운 view. 사용자가 통합하려 했음. 8개 컬럼 모두 issues에 sub-set이고 sentiment만 신규.

문제: ID 시리얼이 별개 (TSLA-I-001이 issues.csv의 TSLA-I-001과 다른 row를 가리킬 가능성) — **데이터 충돌 가능성**.

### 옵션 T-3 — tagged_issues는 daily_tag/labels 같은 보조 테이블, FK issue_id → ??? (불명)

전제: tagged_issues가 issues의 일간 status snapshot.

→ **사용자 결정 필요** (§7 Q3).

### 권장 (PM이 사용자에 문의 후 결정)

옵션 T-1 (별개 테이블)이 안전. issues와 tagged_issues의 ID 시리얼이 다르고 컬럼셋이 다르다는 강한 증거. 사용자 의도가 옵션 T-2/T-3이면 매핑표 v2에서 재정의.

### 매핑 컬럼표 (옵션 T-1 가정)

| CSV 컬럼 | 변환 | 타겟 TeslaTaggedIssueDB 필드 | 비고 |
|---|---|---|---|
| `issue_id` | as-is | `id` (PK, String(20)) | TSLA-I-001 형식 (issues.csv와 별개 시리얼) |
| `title` | as-is | `title` (String(500)) | |
| `category` | `TeslaIssueCategory(value)` | `category` (Enum, indexed) | "essence"/"product"/... enum value 그대로 |
| `essence_component` | `TeslaEssenceComponent(value)` | `essence_component` (Enum nullable, indexed) | |
| `severity` | `Severity(value)` | `severity` (Enum, indexed) | |
| `sentiment` | 신규 enum 또는 String | `sentiment` (Enum or String(10), indexed) | "positive"/"negative"/"neutral" — 신규 enum §7 Q8 |
| `date` | datetime 변환 | `tagged_at` (DateTime, indexed) | KST → UTC 변환 §7 Q6 |
| `summary` | as-is | `summary` (Text, default="") | |
| (없음) | 적재 시점 | `created_at` (default=_utcnow) | |

---

## 5. Status / Enum 매핑 보완

### status 값 충돌

| 출처 | 관측 값 | Pydantic EventStatus | 매핑 결정 |
|---|---|---|---|
| issues.csv | developing, resolved | DEVELOPING, RESOLVED | 1:1 ✅ |
| issues.csv 추가 가능성 | open?, in_progress?, wontfix? | (TeslaIssue.status docstring에 명시) | 신규 IssueStatus enum 필요 §7 Q4 |
| milestones.csv | done, in_progress, planned | RESOLVED, DEVELOPING, ??? | "planned"는 EventStatus 없음 — 신규 MilestoneStatus 또는 String free-form §7 Q4 |

### category 표기 통일

issues.csv는 `TSLA-{E/P/...}` (prefix), tagged_issues.csv는 `{essence/product/...}` (value). enum value 기준이므로 issues 적재 시 `category.split('-')[1]`로 정규화 후 `TeslaIssueCategory[code]` lookup. tagged_issues는 그대로 `TeslaIssueCategory(value)`.

---

## 6. 마이그 스크립트 인터페이스 초안 (시그니처만, 코드 X)

```python
# scripts/migrate_tesla_csv_to_db.py
# Phase 2에서 구현. Phase 1 매핑표 v1 기준.

# CLI:
#   python3 scripts/migrate_tesla_csv_to_db.py --dry-run
#   python3 scripts/migrate_tesla_csv_to_db.py --confirm
#   python3 scripts/migrate_tesla_csv_to_db.py --csv-dir data/research/stocks/tesla/ --confirm
#   python3 scripts/migrate_tesla_csv_to_db.py --only issues   # 단일 CSV만 적재
#
# 동작:
#   1. CSV 디렉토리 스캔 — issues.csv, milestones.csv, tagged_issues.csv
#   2. 각 행을 Pydantic 모델로 변환 (TeslaIssue / TeslaMilestone / TeslaTaggedIssue)
#   3. 변환 에러는 행 단위 skip + 로그 (전체 실패시키지 않음)
#   4. --dry-run: 변환 결과 콘솔 출력 + 카운트 (적재 X)
#   5. --confirm: 적재 (멱등 upsert 패턴)
#   6. 검증: 적재 후 카운트 (예상 10/24/10) + 임의 1건 select 비교
#
# 멱등성 (BaseRepository에 upsert 메서드 없으므로 수동):
#   for row_pydantic in rows:
#       existing = repo.get_by_id(row_pydantic.id)
#       if existing:
#           repo.update(row_pydantic.id, **row_pydantic.model_dump(exclude={"id", "created_at"}))
#       else:
#           repo.create(row_pydantic)
#
# 트랜잭션 단위:
#   - CSV 1개 = 1 트랜잭션 (session begin/commit)
#   - 순서: issues → milestones (FK 의존) → tagged_issues (독립)
#   - 실패 시 해당 CSV rollback, 다음 CSV 시도
#
# 검증 (적재 후 자동 실행):
#   assert TeslaIssueRepository().count() == 10
#   assert TeslaMilestoneRepository().count(filters={"issue_id": "TSLA-E-001"}) >= 1
#   sample = TeslaIssueRepository().get_by_id("TSLA-E-001")
#   assert sample.title.startswith("수직통합")  # 또는 첫 row 비교
```

### Phase 2 작업 분해 (PM 발주 참고용)

| Sub-task | 추정 LOC | 의존 |
|---|---|---|
| (a) TeslaIssueDB / TeslaMilestoneDB / TeslaTaggedIssueDB ORM 추가 (database.py) | 60~80 | enum 사용자 결정 (§7 Q4/Q5/Q8) |
| (b) Pydantic 모델 보강 (TeslaMilestone / TeslaTaggedIssue / IssueStatus / MilestoneStatus / ThesisSide / Sentiment enum) | 40~60 | (a) |
| (c) Repository 클래스 (TeslaIssueRepository 등) — BaseRepository[T] 상속 | 30~50 | (a)+(b) |
| (d) `BaseRepository.upsert(model)` 메서드 추가 (선택, 또는 마이그 스크립트에서 수동 처리) | 15~25 | — |
| (e) 마이그 스크립트 `scripts/migrate_tesla_csv_to_db.py` | 150~220 | (a)~(d) |
| (f) DB 스키마 갱신 (`init_db()` 호출로 신규 테이블 생성 — Alembic 미사용 추정, 확인 필요) | 검증만 | (a) |
| (g) 단위 검증 + sample assert | 30~50 | (e) |

---

## 7. 사용자 결정 대기 항목 (PM이 사용자에 질문)

> 자식이 단독 결정 못 한다고 발주문에 명시된 도메인 항목. PM이 한 묶음으로 사용자 질문 후 답을 받아 Phase 2 발주에 반영.

### Q1. issues.csv 매핑 — 옵션 C (신규 TeslaIssueDB) 추천 OK?

- A: OK → Phase 2에 TeslaIssueDB / TeslaIssueRepository 신설 작업 포함
- B: 옵션 A/B (기존 Ontology* 재사용)를 선호 → 매핑표 v2 재작성

**자식 추천**: 옵션 C. 이유 §0.

### Q2. milestones.csv 매핑 — 옵션 B-1 (신규 TeslaMilestoneDB) 추천 OK?

- A: OK
- B: 옵션 B-2 (OntologyEvent + story_thread) 선호
- C: 옵션 B-3 (Event + Link 하이브리드) 선호

**자식 추천**: B-1. 이유 §3 추천 단락.

### Q3. tagged_issues.csv는 issues.csv와 어떤 관계인가?

옵션:
- T-1: **별개 stream** (예: 일간 자동 태깅 / 외부 import). 신규 TeslaTaggedIssueDB 추가, FK 없음.
- T-2: 같은 issue의 일간 view. 신규 issue_id 컬럼이 사실은 issues.csv의 issue_id를 가리킴 (현재 시리얼이 달라보이는 건 데이터 동기화 오류) — issues에 sentiment/date 컬럼 추가하고 tagged_issues 별도 테이블 X.
- T-3: 다른 의미. 사용자가 직접 설명.

**자식 관찰**: 시리얼이 명백히 다름(TSLA-I-001, TSLA-P-001 vs issues.csv의 TSLA-E-001 등). 컬럼셋도 다름. **T-1 옵션이 자료 근거 가장 강함**. 사용자가 의도 확인 필요.

### Q4. status / milestone status enum 처리

- `issues.status` 값: developing / resolved (관측) + "open" / "in_progress" / "wontfix" (TeslaIssue.status docstring 명시)
- `milestones.status` 값: done / in_progress / planned (관측)
- 기존 EventStatus enum (DEVELOPING/RESOLVED/STALE/ESCALATING)에 "planned"/"done"/"wontfix" 없음

옵션:
- A: 신규 enum 2개 신설 — `IssueStatus`, `MilestoneStatus`
- B: 두 테이블 모두 String free-form (검증 X)
- C: 기존 EventStatus 확장 (PLANNED, DONE, WONTFIX 추가)

**자식 추천**: A. EventStatus는 ontology 일반 모델용이라 의미 오염 우려, 도메인 분리 깔끔.

### Q5. thesis_side enum 처리

- 값: bull(8), bear(2) — 양극 binary
- 옵션 A: 신규 `ThesisSide` StrEnum (BULL/BEAR)
- 옵션 B: String(10) free-form

**자식 추천**: A. 검증 + IDE 자동완성 이득.

### Q6. timezone 정책

- CSV 날짜 컬럼이 `YYYY-MM-DD` 형식 (시각 없음). KST? UTC? 자정?
- DB `DateTime` 컬럼은 UTC 권장 (database.py 다른 모델 `_utcnow` 사용)

옵션:
- A: KST 자정 → UTC 변환 (예: 2026-04-20 → 2026-04-19T15:00:00Z)
- B: UTC 자정 (예: 2026-04-20 → 2026-04-20T00:00:00Z) — 더 단순, 날짜만 의미 있을 때 적합
- C: String 컬럼 (Date) — 시각 정보 버림

**자식 추천**: B (UTC 자정). 모든 날짜가 단순 "당일 이벤트"라 시각 정보 없음. KST 변환은 정보 추가가 아니라 추측. 사용자 확인 필요.

### Q7. 빈 컬럼 (deadline, related_entity_ids, notion_page_id, created_at, last_updated) 처리

issues.csv 대부분 행에서 위 컬럼이 비어있음. 정책:
- 빈 문자열 `""` → `None` 변환 (datetime/optional 컬럼)
- 빈 문자열 `""` → 기본값 (str default="")
- `related_entity_ids` CSV 자체 빈 컬럼 — JSON 빈 배열 `[]`

→ tesla_api.py가 이미 `_empty_str_to_none()` 사용. **그 정책 따르되 DB 컬럼 default 적용**. 사용자 확인 후 진행.

### Q8. tagged_issues.sentiment enum

- 값: positive / negative / neutral
- 옵션 A: 신규 `Sentiment` StrEnum (POSITIVE/NEGATIVE/NEUTRAL)
- 옵션 B: String

**자식 추천**: A.

### Q9. 매핑 후 CSV 처리

Phase 2 적재 성공 후 CSV를 어떻게 할 것인가?
- 옵션 A: 그대로 보존 (PM 발주문 "CSV 수정 X" 정신과 일치)
- 옵션 B: 아카이브 디렉토리로 이동 (예: `data/research/stocks/tesla/_migrated/`)
- 옵션 C: 삭제 (DB가 SSOT)

**자식 추천**: A. tesla_api.py가 여전히 CSV 읽으니 호환 유지. Phase 3 (tesla_api DB 전환) 후에 옵션 B/C 결정.

### Q10. 모듈 위치

신규 ORM/Repo/모델/스크립트 위치:
- `src/core/database.py`: TeslaIssueDB / TeslaMilestoneDB / TeslaTaggedIssueDB ← OK
- `src/core/models.py`: TeslaMilestone / TeslaTaggedIssue / IssueStatus / MilestoneStatus / ThesisSide / Sentiment Pydantic ← OK
- `src/storage/tesla_repository.py` (신규 파일) vs `src/storage/ontology_repository.py`에 추가?
- 스크립트: `scripts/migrate_tesla_csv_to_db.py` ← OK

**자식 추천**: 신규 `src/storage/tesla_repository.py` 별도. ontology_repository와 도메인 분리.

---

## 8. 자체 권고 (Hermes 추가 발견)

### 8-A. BaseRepository에 upsert 없음 — 마이그 패턴 표준화 권장

여러 곳에서 멱등 적재가 필요할 수 있음. Phase 2에 `BaseRepository.upsert(model)` 헬퍼 추가하면 마이그 스크립트뿐만 아니라 향후 자동 수집 cron에도 재사용 가능. (선택, 마이그 스크립트에 inline 구현해도 OK)

### 8-B. CSV → DB 단방향 SSOT 전환 시점에 tesla_api.py 듀얼 read 권장

Phase 2(DB 적재) 완료 후 Phase 3(tesla_api DB read)로 전환할 때, **CSV/DB 양쪽 읽고 비교하는 dual-read 단계** 1주일 두기 권장. 차이 발견 시 알람 → 신뢰 확보 후 CSV read 제거.

### 8-C. issue_id를 PK로 쓰는 안전성

- TSLA-E-001 같은 도메인 ID가 PK. 사용자가 수동 입력 → 오타/충돌 위험 있음.
- 단, ID가 의미 있는 식별자라 자동 generate UUID보다 운영 편함.
- **추천**: `id`(자동 UUID) + `issue_id`(unique constraint, 도메인 ID) 2 컬럼 분리. tesla_api는 `issue_id`로 조회, 내부 FK는 `id` 사용.
- 단, 발주문이 "issue_id 기준 upsert"라고 명시 — 사용자/PM이 도메인 ID를 PK로 쓰는 것을 기대했을 수도. §7 Q1과 묶어서 결정.

### 8-D. essence_scores.csv / master_plan.csv / moat_status.csv / thesis.json / timeline_events.json / topics_quarterly.json — Phase 3 task로 분리 권장

본 task가 "1-47 Tesla CSV → SQLite ORM 마이그"라는 큰 우산. tesla_api.py에서 위 파일들도 모두 사용 중이라 결국 마이그 대상. 단, Phase 1 매핑표 v1은 issues/milestones/tagged_issues 3개에 집중하고 위 6개는 별도 task로 PREPARED에 등록 (1-48 후보).

### 8-E. CSV는 사용자가 직접 작성 — Notion 동기화 신호 있음

`issues.csv`에 `notion_page_id`, `last_updated` 컬럼 + 일부 행 마지막에 비어있는 형태로 봐서 **Notion DB → CSV export** 워크플로우 추정. 마이그 후에도 Notion → CSV → DB 흐름이 유지된다면 cron 등록 필요 (Phase 3 후보).

---

## 9. 산출물 메타

- 작성 시각: 2026-05-24 ~20:00 KST
- 파일: `docs/specs/1-47-csv-to-db-mapping-v1.md`
- 코드 변경: **0** (read-only 조사)
- DB write: **0**
- CSV 수정: **0**
- 다음 단계: PM 검토 → 사용자 §7 Q1~Q10 결정 → Phase 2 발주 (ORM/Repo/Pydantic/마이그 스크립트 구현)
