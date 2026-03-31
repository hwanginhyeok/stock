# 1-30: GeoInvest — 세상 이슈 관계도 통합 플랫폼

> 발행일: 2026-03-31 | 상태: 진행 | 담당: 사용자 + AI

## 개요

세상 주요 지정학 이슈(이란 전쟁, 미중 관세, 러우전쟁 등)의 관계도를 AI로 자동 생성하고, 인터랙티브 웹 UI에서 보여주는 플랫폼.

## 완료된 것

- [x] /office-hours 디자인 문서 작성 + APPROVED
- [x] /plan-eng-review 엔지니어링 리뷰 통과
- [x] 와이어프레임 확정 (3칸럼 + 하단 투자영향 스트립)
- [x] 데이터 모델 설계 (Entity/Event/Link/GeoIssue)
- [x] 아키텍처 결정 (FastAPI + D3.js + 기존 온톨로지 확장)
- [x] Step 1 벤치마크 완료 — Approach C (하이브리드) 확정
  - 뉴스 입력: Entity F1=0.478, Rel F1=0.450
  - Gold 입력: Entity F1=0.647, Rel F1=0.561
  - 프롬프트 자체는 OK, 뉴스 정보밀도가 병목

## 현재 진행: Step 2 본 구현

### Step 1: throwaway 벤치마크 ✅ 완료

> 핵심: 기존 코드를 건드리지 않고, 독립 스크립트로 AI 추출 품질을 먼저 검증

1. **"벤치마크 돌려줘"라고 AI에게 말하면 됨**
   - AI가 throwaway 스크립트를 만들어서:
     - `data/research/geopolitics/iran_conflict/`의 5개 md 파일을 gold standard로 파싱
     - 같은 주제의 뉴스를 Claude API에 넣어 Entity/Event/Link 자동 추출
     - gold standard와 비교해서 F1 점수 계산
   - 결과를 보고 접근 방식 결정:
     - **F1 >= 0.70** → Approach B (풀 자동화) 진행
     - **F1 50-70%** → Approach C (하이브리드: AI 초안 + 사람 검수)
     - **F1 < 50%** → 프롬프트/접근 재설계

### Step 2: 결과에 따른 구현 (벤치마크 후)

벤치마크 통과 시 구현 순서:
1. enum/모델 확장 + DB 마이그레이션
2. GeoIssue 모델 + Repository
3. FastAPI 웹 서버 + 3개 API 엔드포인트
4. D3.js 프론트엔드 (3칸럼 UI)
5. 테스트 작성 (~15개)

## 핵심 설계 결정 (확정)

| 결정 | 선택 | 이유 |
|------|------|------|
| LinkType | 기존 6개 유지 + 신규 6개 추가 | 기존 뉴스 파이프라인 호환 |
| EntityType | +PROXY, +COMMODITY | 헤즈볼라, 원유 등 |
| Issue 모델 | 별도 GeoIssue | Event의 상위 그룹핑 개념 |
| 웹 서버 | src/web/ 구조 | FastAPI + static files |
| 프론트엔드 | vanilla D3.js (CDN) | 빌드 도구 없음 |
| 벤치마크 | throwaway 먼저 | 기존 코드 수정 전 리스크 검증 |
| 노드 제한 | MVP에서 없음 | 데이터 적으므로 |

## 참조 문서

- 디자인 문서: `~/.gstack/projects/hwanginhyeok-stock/window11-master-design-20260331-133101.md`
- 테스트 플랜: `~/.gstack/projects/hwanginhyeok-stock/window11-master-eng-review-test-plan-20260331-134500.md`
- 기존 이란 온톨로지: `data/research/geopolitics/iran_conflict/`
- 기존 온톨로지 코드: `scripts/ontology_io.py`, `src/storage/ontology_repository.py`

## 미결 TODO

- [ ] 자동 이슈 그룹핑 로직 설계 (MVP에서는 수동, 향후 AI 자동화)
- [ ] DB 마이그레이션 실패 시 복구 경로 (Alembic downgrade)
