# Ontology와 팔란티어 — 데이터에 의미를 심는 회사

> 상태: 아웃라인 / Claude / 2026-03-08
> 시리즈: 팔란티어 심층분석 [1편/3편]

## 핵심 질문
- 독자 질문: "팔란티어의 Ontology는 기존 데이터 플랫폼과 뭐가 다른가?"
- 글의 답: "Ontology는 데이터를 저장하는 것이 아니라, 조직이 세상을 이해하는 방식을 디지털화한 것이다. 이 구조 위에서 LLM이 비로소 기업 현실에 착륙한다."

## 소스 활용 계획
- **기존 초안 활용**: 007 (회사 개관), 008 (온톨로지 3계층, 공급망 시나리오, SaaS 비교, LLM 시너지)
- **신규 리서치 반영**: ontology_deep_dive.md (공식 기술 구조, OSv2, AIP Agent Studio)
- **기존 초안 제외**: 006 (철학/카프) → 3편으로 이동, 009 (버리) → 2편에 압축 통합

## 섹션 구조

### §1 도입 — 데이터는 넘치는데 의사결정은 왜 어려운가 (~35줄)
- 핵심 포인트: 기업은 데이터가 부족한 게 아니라 의미가 부족하다
- 시작: 2001년 9/11 — 정보 부재가 아니라 연결 실패
- 이 문제에 대한 응답으로 만들어진 회사
- 팔란티어 간략 소개: 2003년, 피터 틸 + 카프, 4개 플랫폼, $4.48B 매출
- 리듬 변화 도구 활용 (짧은 팩트 → 질문)

### §2 Ontology — 스프레드시트에 없는 것 (~80줄)
- 핵심 포인트: Ontology는 데이터를 저장하는 레이어가 아니라, 데이터의 의미와 관계를 저장하는 레이어
- "고객"이라는 열의 침묵 — 계약자? 구매자? 문의자?
- 3계층: Semantic / Kinetic / Dynamic
  - Semantic: 공급망 "납기 지연" — 부서별 정의 충돌 시나리오
  - Kinetic: 5년간 학습된 의사결정 로직 코드화
  - Dynamic: 인간이든 AI든 동일 권한 체계 적용, 결정 기록
- **NEW**: 공식 문서 기반 6대 구성 요소 (Object Type, Link Type, Action Type, Function, Interface, OSDK)
  - "행(row)"이 아니라 "비즈니스 객체(Object)" 단위
  - Action Type: 원자적 트랜잭션으로 데이터 변경 (파라미터, 규칙, 사이드이펙트)
  - Object-level RBAC: 객체/속성/액션 단위 권한 강제
- **NEW**: OSv2 — 단일 Object Type에 수백억 개 객체 지원
- 비유: "회사가 어떻게 결정을 내리는지에 대한 디지털화된 지식체계"
- 📎 시각화: Ontology 3계층 구조도

### §3 SaaS가 아닌 이유 (~45줄)
- 핵심 포인트: CRM 교체는 데이터 이전. Ontology 교체는 조직 재편.
- CRM(Salesforce → HubSpot): CSV 내보내기 → 임포트. 번거롭지만 데이터 이전
- Ontology: 5년간 정의·검증·수정해온 의미 구조는 옮길 수 없다
- NYPD 사례: 원시 데이터는 가져갈 수 있다. 지식 체계는 가져갈 수 없다.
- 악보 비유: 악보는 인쇄할 수 있다. 연주 스타일과 수십 년의 연습은 인쇄할 수 없다.
- NDR 139%: 벤더 잠금(100-110%) vs 가치 해자(130-140%+)

### §4 LLM 시너지와 Agentic AI (~60줄)
- 핵심 포인트: AI 모델이 교체되어도 Ontology는 남는다. 오히려 LLM이 강해질수록 Ontology의 가치가 커진다.
- OpenAI/Anthropic vs Microsoft Copilot vs Palantir AIP 비교
- 멀티 LLM 아키텍처: Claude, GPT, Llama, Gemini 플러그인
- 공급망 리스크 분석 시나리오: 일반 LLM vs AIP+Ontology 차이
- **NEW**: AIP Agent Studio — 4 Tier 에이전트 프레임워크
  - Tier 1: 사용자 주도 분석 → Tier 4: 완전 자율 에이전트
  - 6가지 에이전트 도구: Query Objects, Apply Actions, Call Function 등
- Agentic AI 피드백 루프: 에이전트 실행 → 결과 → Ontology에 기록 → 다음 에이전트가 더 정확
- 복리 비유: 의사결정의 결과가 다시 지식이 된다
- 📎 시각화: LLM + Ontology 시너지 구조도

### §5 마무리 — 출발점 (~30줄)
- 핵심 포인트: Ontology는 이론이다. 이 이론이 현장에서 작동하는가?
- Rule of 40 127%, US Commercial +137%, 고객 954개사
- 하지만 숫자는 주장이다. 증명은 현장에 있다.
- 다음 편 브릿지: "10초 만에 사기를 탐지한 Fannie Mae, $10B 단일 계약을 준 미 육군, '비밀 병기'라고 부른 건설회사 — Ontology가 만든 현장을 직접 들여다본다."
- 훅: "기술의 가치는 설명이 아니라 고객의 행동으로 증명된다."

## 총 예상 분량: ~250줄

## 📎 시각화 배치 계획
| 위치 | 파일 | 설명 |
|------|------|------|
| §2 후반 | visuals/01_ontology_architecture.png | Ontology 3계층 + 6대 구성 요소 구조도 |
| §4 중간 | visuals/02_llm_ontology_synergy.png | LLM + Ontology 시너지 흐름도 |
