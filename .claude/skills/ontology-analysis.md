# 온톨로지 분석 + 제1원칙 사고 스킬

> 뉴스 팩트 → 온톨로지 그래프 구축 → 제1원칙 분석 수행 절차.
> 팔란티어 온톨로지 4블록 (Entity → Event → Link → Analysis) 구조.

---

## 트리거

- "온톨로지 분석", "제1원칙 분석", "뉴스 분석" 지시 시
- 시황 브리핑 후 심층 분석 요청 시

---

## 워크플로우

### Step 1: 팩트→온톨로지 그래프 구축

```bash
# 팩트가 이미 추출되어 있어야 함 (extract_facts.py auto 선행)
python -c "
from src.analyzers.ontology_builder import build_ontology_from_facts
from src.core.database import init_db
init_db()
result = build_ontology_from_facts(hours=24)
print(result)
"
```

### Step 2: 온톨로지 현황 확인

```bash
python scripts/ontology_io.py briefing --market all
python scripts/ontology_io.py graph --market kr
```

### Step 3: 제1원칙 분석 (Claude Code 세션)

이벤트 목록에서 분석 대상을 선택하고, 아래 스키마로 분석 수행:

```json
{
    "event_id": "<온톨로지 이벤트 UUID>",
    "event_title": "KOSPI -6% 급락",
    "conventional_wisdom": "시장이 당연시하는 가정 — 예: '중동 전쟁이 한국 수출에 직격탄'",
    "fundamental_truths": [
        "가정을 제거하고 남는 팩트 1",
        "가정을 제거하고 남는 팩트 2",
        "가정을 제거하고 남는 팩트 3"
    ],
    "gap": "통념과 현실 사이의 괴리 — 예: '실제 수출은 50.4% 증가 중'",
    "opportunity": "Gap에서 도출한 투자 기회",
    "related_fact_ids": ["<팩트 UUID 1>", "<팩트 UUID 2>"],
    "market": "korea",
    "status": "draft"
}
```

### Step 4: 타임라인 생성

```bash
python scripts/generate_timeline.py --market kr --days 7
```

---

## 제1원칙 분석 패턴

### 통념 → 분해 → Gap → 가능성

1. **통념 식별**: 시장이 당연시하는 가정을 명시
2. **근본 진실 분해**: 가정을 제거하고 남는 순수한 팩트들 (숫자, 사실)
3. **Gap 발견**: 통념이 말하는 것과 팩트가 말하는 것 사이의 괴리
4. **가능성 추론**: Gap에서 투자 기회 도출

### 예시

```
통념: "중동 전쟁 → 한국 수출 타격 → 코스피 하락은 펀더멘탈 반영"

근본 진실:
  - 1~20일 수출 533억달러, YoY +50.4% (팩트)
  - SK하이닉스 HBM4 수율 85% (팩트)
  - 반도체가 수출 견인 (구조적)

Gap: 수출은 역대 최고인데 코스피는 -6%. 중동 리스크가 과대 반영.

가능성: 패닉 셀링 후 반도체 대장주 저점 매수 기회.
```

---

## 관련 파일

| 파일 | 역할 |
|------|------|
| `src/analyzers/ontology_builder.py` | 팩트→온톨로지 자동 구축 |
| `src/core/models.py` | `FirstPrincipleAnalysis` 모델 |
| `scripts/ontology_io.py` | 온톨로지 CRUD CLI |
| `scripts/generate_timeline.py` | 타임라인 시각화 |
