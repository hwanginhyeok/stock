# 야간 브리핑 — 2026-04-07

## 완료 항목

### 1-35: InvestOS 이벤트 체계 대개편

#### 1-1. EventType geo/stock 분리 ✅
- `src/core/models.py` EventType enum 확장
  - Geo: diplomatic, military, sanctions, energy, trade, territorial, war, policy
  - Stock: earnings, analyst, product, regulatory, macro, deal, sector
- `deep_analysis.py` 프롬프트에서 카테고리별 분기 적용

#### 1-2. 이벤트 스토리 체이닝 ✅
- OntologyEvent 모델 + DB에 `story_thread` 필드 추가 (VARCHAR(200))
- `deep_analysis.py`에서 기존 thread 목록을 Ollama에 제공 → 이어쓰기 유도
- 새 이벤트 생성 시 story_thread 저장

#### 1-3. 과거 7일 이벤트 백필 ✅
- `deep_analysis.py --hours 168`로 7일치 뉴스 기반 이벤트 추출
- story_thread 연결 포함

#### 1-4. InvestOS UI 타임라인 뷰 ✅
- API: `/api/issues/{id}/timeline` → story_thread별 그룹핑 반환
- UI: 스레드별 타임라인 + severity 색상 (critical=빨강, major=주황, moderate=파랑, minor=회색)
- 이벤트 카테고리를 event_type 기반으로 변경 (기존 제목 prefix 추론 제거)

### 1-36: 관계도 복잡성 해소

#### 2-1+2-2. 관계도 Top N 필터 + UX 개선 ✅
- **대안 조사 결과**: Top N 필터가 가장 빠르고 효과 큼
  - 클러스터링은 D3 force graph와 호환성 문제
  - 레이어 뷰는 구현 복잡도 높음
  - 관계 설명 개선은 추후 단계
- **구현**:
  - API: `/api/issues/{id}/graph?top=10` 파라미터 추가
  - degree(관계 수) 기준 상위 N개 엔티티만 표시
  - UI: 드롭다운 (Top 10 / 20 / 50 / 전체) + 카운트 라벨
  - 관계 색상: 기존 유지 (ally=파랑, hostile=빨강, trade=노랑 등)

## 커밋 이력

| 커밋 | 내용 |
|------|------|
| `4e16d45` | EventType geo/stock 분리 |
| `e4a400c` | story_thread 필드 + 체이닝 로직 |
| `59cc80e` | 관계도 Top N 필터 + 카테고리 확장 |
| `27c8d27` | 타임라인 story_thread별 그룹 뷰 |

## 남은 이슈

1. **관계 설명 UX**: 관계선 클릭 시 사이드패널에 evidence 표시 — 다음 단계
2. **백필 퀄리티**: Ollama gemma3:4b의 story_thread 네이밍 일관성 모니터링 필요
3. **이벤트 중복**: 12시간마다 심층분석이 돌면서 유사 이벤트 생성 가능 → 중복 체크 로직 필요
4. **기존 101개 이벤트**: 3/28 시드 데이터에 story_thread 없음 → 수동 또는 일괄 할당 필요

## DB 스키마 변경 (DDL)

- `ALTER TABLE ontology_events ADD COLUMN story_thread VARCHAR(200) DEFAULT ""`
- `CREATE INDEX ix_ont_event_story_thread ON ontology_events(story_thread)`
- 비파괴적 변경, 기존 데이터 보존됨
