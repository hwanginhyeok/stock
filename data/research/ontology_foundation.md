# 온톨로지 설계 원칙 — 이론적 기반 문서

> 태스크: 5-10 | 작성일: 2026-04-07
> 목적: InvestOS 온톨로지 시스템의 이론적 토대. 1-39(Stock 온톨로지 설계)의 선행 문서.

---

## 1. 핵심 원리: 본질적 속성

### 1.1 정의

> "그것이 없으면 그것이 존재하지 않는 속성"

- **아리스토텔레스**: *to ti en einai*(그것이 무엇이었음) — 과거형 ēn은 시간을 초월한 영속적 구조를 함축. 본질을 아는 것 = 그것이 왜 존재하는지(aition, 원인)를 아는 것
- **크립키**: 모든 가능세계에서 필연적인 속성. "물은 H2O" — 경험적 발견이지만 발견 후에는 필연적
- **킷 파인 (현대 핵심)**: "본질은 필연성보다 근본적. **그것이 무엇인지를 구성하는 속성**이 본질" — 필연적이지만 비본질적인 것을 걸러내는 더 미세한 체(finer mesh)

### 1.2 본질 vs 우연 vs 고유 (3단 구분)

| 구분 | 정의 | 제거 시 | 예시 (기업) | 예시 (국가) |
|------|------|---------|------------|------------|
| **본질적(essential)** | 없으면 그것이 아님 | 정체성 소멸 | 비즈니스모델, 경쟁우위 | 주권, 생존 추구 |
| **고유적(propria)** | 본질에서 필연적으로 도출되나 본질 자체는 아님 | 약화되지만 존속 | 매출성장률, 이익률 | 군사력 규모, GDP |
| **우연적(accidental)** | 있어도 되고 없어도 됨 | 정체성 유지 | 본사 위치, CEO 이름 | 뉴스 출처, 기사 수 |

### 1.3 본질성 판별 방법 (3가지 검증)

| 검증 | 질문 | 도구 |
|------|------|------|
| **반사실적 검증** | "이 속성이 없었다면 이것이 여전히 이것인가?" | 가능세계 사고실험 |
| **정보 이론적 검증** | "이 속성을 알 때 대상에 대한 불확실성이 얼마나 줄어드나?" | Mutual Information I(X;Y) |
| **구조적 검증** | "이 노드를 제거하면 그래프 연결성이 붕괴하나?" | Betweenness Centrality |

### 1.4 정량화 공식

**상호 정보량**: I(X;Y) = H(Y) - H(Y|X) — 높을수록 본질적
**엔트로피**: H(X) = -Σ p(x) log p(x) — 낮을수록 본질적 (예측 가능 = 안정적 정체성)
**구조적 중심성**: BC(v) = Σ σ(s,t|v)/σ(s,t) — 높을수록 구조적 핵심

---

## 2. 철학적 계보

```
아리스토텔레스 (BC 4C) — 10개 범주, 제1/2실체, 본질/우유성, 형상/질료
  │
포르피리오스 (3C) — 유→종차→종 계층, 5가지 술어 가능자
  │
중세 스콜라 (11-14C) — 보편자 논쟁 (실재론 vs 유명론)
  │
크립키 (1970) — 고정 지시어, 필연적 후천적 진리
  │
파인 (1994) — 본질 > 필연성, 정의적 본질
  │
BFO/DOLCE/SUMO (2001~) — 현대 형식 상위 온톨로지
  │
OWL (2004) — Class/Property/Individual, 아리스토텔레스의 형식적 구현
  │
팔란티어 (2013~) — Semantic/Kinetic/Dynamic 3계층, 운영 실행 온톨로지
```

### 2.1 아리스토텔레스 범주론 핵심

**제1실체(primary substance)**: 개별자. "이 사람", "이 말". 독립적으로 존재하는 기본 실재.
**제2실체(secondary substance)**: 보편자. "사람", "동물". 제1실체가 속하는 종과 유.

> "제1실체가 존재하지 않으면, 다른 어떤 것도 존재할 수 없다."

**형상(morphe)과 질료(hyle)**: 모든 감각적 실체는 형상+질료의 결합체. 형상 = 동일성의 원리 (이것을 이것이게 하는 것).

### 2.2 포르피리오스의 나무

```
실체 → 물질적/비물질적
  물체 → 유생/무생
    생물 → 감각적/비감각적
      동물 → 이성적/비이성적
        인간 → 소크라테스, 플라톤...
```

**종 = 유 + 종차**: "인간 = 동물 + 이성적" — 현대 분류 체계·객체 상속·의사결정 트리의 원형.

### 2.3 현대 상위 온톨로지 비교

| | BFO | DOLCE | SUMO |
|---|---|---|---|
| **입장** | 실재론 | 인지주의 | 절충적 |
| **핵심 구분** | continuant/occurrent | endurant/perdurant | Object/Process |
| **강점** | ISO 표준, 생물의학 650+ 채택 | 질 공간(quality space) 정교, 사회적 대상 | 방대한 커버리지, WordNet 매핑 |
| **규모** | ~36개 범주 | 중간 | ~1,000개 개념 |

**우리 시스템 적용**: BFO의 continuant(엔티티)/occurrent(이벤트) 구분이 우리 Entity/Event 모델과 직접 대응.

---

## 3. 도메인별 본질적 속성 체계

### 3.1 지정학 (GEO) — 이미 적용 중

**이론적 근거**:
- **투키디데스**: 국가 행위의 3동인 = 공포(deos), 명예(timē), 이익(ōpheleia)
- **미어샤이머**: 국가의 본질 = 생존(survival) + 권력 극대화(power maximization)
- **클라우제비츠**: 전쟁의 본질 = 폭력(국민) + 우연(군대) + 정치 종속(정부) 삼위일체

**현재 엔티티 속성**:
```
objectives  — 목표/원하는 것
strategy    — 어떻게 이루려 하는지
achievements — 달성한 것
failures    — 미달성/실패한 것
```

→ 이것은 투키디데스의 "이익" + 미어샤이머의 "생존+권력 극대화"를 속성으로 구현한 것.

### 3.2 금융 (Stock) — 설계 필요 (1-39)

**이론적 근거**:
- **버핏의 경제적 해자** = 기업의 본질적 속성 (모닝스타 5가지 원천)
- **내재가치(intrinsic value)** = 본질적 속성, 주가 = 우연적 속성
- **역량 범위(circle of competence)** = 온톨로지적 경계

**모닝스타 해자 5원천**:

| 원천 | 정의 | 온톨로지 해석 |
|------|------|-------------|
| 전환 비용(Switching Costs) | 고객이 이탈할 때 발생하는 장벽 | 관계 구조의 고착 |
| 네트워크 효과(Network Effects) | 사용자 증가 → 가치 증대 | 관계 구조 자체가 본질 |
| 무형자산(Intangible Assets) | 특허/브랜드/라이선스 | 비물질적 본질 |
| 비용 우위(Cost Advantage) | 경쟁사보다 낮은 생산 비용 | 생산 구조의 효율성 |
| 효율적 규모(Efficient Scale) | 시장이 소수만 수용 | 시장 크기가 진입장벽 |

**Stock 엔티티 본질적 속성 설계안**:

```
[기업]
  본질적: business_model, moat_source, capital_allocation
  고유적: revenue_growth, margin, valuation
  우연적: hq_location, ceo_name, quarterly_beat

[중앙은행]
  본질적: policy_objective, primary_tool, mandate
  고유적: current_rate, balance_sheet_size
  우연적: next_meeting_date, spokesperson

[지표]
  본질적: measurement_target, signal_direction, threshold
  고유적: current_value, trend, volatility
  우연적: data_source_url, update_frequency

[섹터]
  본질적: value_chain_position, cyclicality, growth_driver
  고유적: pe_ratio, market_cap
  우연적: etf_ticker, index_weight
```

### 3.3 팔란티어 실무 대응

| 본질 등급 | 팔란티어 visibility | UI 동작 | 우리 적용 |
|----------|-------------------|---------|----------|
| 본질적 | Prominent | 항상 표시 | 브리핑 요약에 반드시 포함 |
| 고유적 | Normal | 상세 보기에 표시 | 클릭 시 표시 |
| 우연적 | Hidden | 미표시 | API에만 존재 |

---

## 4. 온톨로지 공학 방법론

### 4.1 역량 질문 (Competency Questions) — 먼저 정의

> "온톨로지가 답해야 할 질문을 먼저 정의하고, 그 질문에 답할 수 있는 구조를 구축한다."
> — Grüninger & Fox (1995)

**우리 시스템의 역량 질문**:

| CQ | 필요한 온톨로지 구조 |
|----|-------------------|
| "이란의 전략적 목표는 무엇이고, 얼마나 달성했나?" | 엔티티 → objectives, achievements |
| "이 기업의 경쟁우위(해자)는 무엇인가?" | 기업 → moat_source |
| "Fed 금리 인상이 영향을 미치는 섹터는?" | 이벤트 → 섹터 인과 링크 |
| "이 뉴스가 BTC 가격에 미치는 방향은?" | 뉴스 → 엔티티 → 센티먼트 방향 |
| "동일 엔티티의 시간별 변화 추적" | 엔티티 → 타임라인 속성(시계열) |

### 4.2 구축 방법론: NeOn 선택

| 방법론 | 적합성 |
|--------|--------|
| Methontology | △ — 처음부터 구축에 최적화, 우리는 이미 기존 시스템 있음 |
| **NeOn** | **◎** — 재사용/정렬 중심, GEO+Stock 두 도메인 통합에 최적 |
| UPON | △ — UML 기반, 우리 스택과 안 맞음 |

**NeOn 적용 시나리오**:
- 시나리오 2 (온톨로지 재사용): FIBO 금융 표준 온톨로지 참조
- 시나리오 6 (디자인 패턴): N-ary Relation, Part-Whole 패턴 활용
- 시나리오 7 (정렬): GEO와 Stock 온톨로지 상위 통합

### 4.3 FIBO 참조 (금융 표준 온톨로지)

| FIBO 모듈 | 우리 대응 |
|-----------|----------|
| Foundations (FND) | 사람, 조직 → ontology_entities |
| Securities (SEC) | 주식, 채권 → Stock 엔티티 |
| Indices & Indicators (IND) | 시장 지수, 금리 → 지표 엔티티 |
| Business Entities (BE) | 법인, 소유관계 → 기업 엔티티 |

### 4.4 디자인 패턴

| 패턴 | 적용 |
|------|------|
| **N-ary Relation** | "이란이 2026-03-01에 호르무즈 봉쇄" → BlockadeEvent(actor, target, date, severity) |
| **Part-Whole** | 섹터 → 기업, 동맹 → 국가 |
| **Temporal** | 엔티티 속성의 시계열 변화 추적 (환율, 금리, 주가) |

### 4.5 안티패턴 (피해야 할 것)

| 안티패턴 | 우리 시스템 사례 |
|---------|----------------|
| **is-a 오용** | "TSLA"를 institution으로 분류 — 타입 체계 오류 |
| **불필요한 것의 최적화** | "$2.9B"를 asset 엔티티로 생성 — 머스크 Step 2 위반 |
| **중복 엔티티** | "미국"/"U.S."/"미 연방" 별도 존재 — 정렬 미수행 |

---

## 5. LLM + 온톨로지 결합

### 5.1 환각 감소 효과

| 접근법 | 환각률 |
|--------|--------|
| ChatGPT-4 (일반) | ~63% |
| 온톨로지 기반 KG + RAG | **1.7%** |

→ 온톨로지를 명시적으로 정의하면 Ollama 추출 품질도 대폭 개선 가능.

### 5.2 우리 시스템에의 적용

현재: Ollama 프롬프트에 타입 리스트만 전달 → 노이즈 엔티티 대량 생성
개선: **온톨로지 스키마(역량 질문 + 본질 속성 정의)를 프롬프트에 구조적으로 주입**
→ "이 뉴스에서 기업의 비즈니스모델/경쟁우위/자본배분에 관련된 엔티티만 추출하라"

---

## 6. 출처

### 철학
- Aristotle, *Categories*, *Metaphysics* (Stanford Encyclopedia of Philosophy)
- Porphyry, *Isagoge* (Wikipedia, Univ. of Washington)
- Kripke, *Naming and Necessity* (1980)
- Fine, "Essence and Modality" (1994, NYU)
- Quine, "Two Dogmas of Empiricism" (1951)
- Lowe, *The Four-Category Ontology* (Oxford, 2006)

### 상위 온톨로지
- BFO: ISO/IEC 21838-2:2021, GitHub (BFO-2020)
- DOLCE: LOA-ISTC-CNR (arXiv:2308.01597)
- SUMO: ontologyportal.org

### 온톨로지 공학
- Fernandez-Lopez et al., "METHONTOLOGY" (1997)
- Gomez-Perez & Suarez-Figueroa, "NeOn Methodology" (2009)
- Grüninger & Fox, "Methodology for the Design and Evaluation of Ontologies" (1995)
- FIBO: spec.edmcouncil.org/fibo

### 금융
- Morningstar Economic Moat Rating
- VanEck, "What Makes a Moat?" (2025)
- Buffett/Munger Circle of Competence (Farnam Street)

### 지정학
- Thucydides, *History of the Peloponnesian War*
- Mearsheimer, *The Tragedy of Great Power Politics* (2001)
- Clausewitz, *Vom Kriege* (1832)

### LLM + 온톨로지
- KG-RAG (NAACL 2025), GraphRAG (ACM 2025)
- Ontogenia (2025), CQbyCQ (2024)
- PLOS ONE, "Approaches to measure class importance in KGs" (2021)
