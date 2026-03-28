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

### Step 3: 제1원칙 분석 (자동)

```python
from src.analyzers.first_principle_analyzer import analyze_top_events, format_analysis_report

# 상위 이벤트 자동 분석 (Claude Sonnet 사용)
analyses = analyze_top_events(hours=24, market="kr", max_events=5)
print(format_analysis_report(analyses))
```

또는 CLI:
```bash
python -c "
from src.analyzers.first_principle_analyzer import analyze_top_events, format_analysis_report
analyses = analyze_top_events(hours=24, max_events=5)
print(format_analysis_report(analyses))
"
```

### Step 4: 테제 후보 추출 (아티클 연결)

분석 결과에서 Gap이 충분히 구체적인 항목을 아티클 테제 후보로 추출:

```python
from src.analyzers.first_principle_analyzer import extract_thesis_candidates

candidates = extract_thesis_candidates(analyses)
for c in candidates:
    print(f"  {c['title']}: {c['thesis']}")
```

### Step 5: 타임라인 생성

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

## 설정

스토리 클러스터와 엔티티 분류는 `config/ontology_config.yaml`에서 관리.
새 테마(예: "AI 수출규제", "테라팹")나 인물 추가 시 YAML만 수정하면 됨. 코드 변경 불필요.

## 관련 파일

| 파일 | 역할 |
|------|------|
| `config/ontology_config.yaml` | 스토리 클러스터 + 엔티티 분류 + 분석 설정 |
| `src/analyzers/ontology_builder.py` | 팩트→온톨로지 자동 구축 (config 기반) |
| `src/analyzers/first_principle_analyzer.py` | 이벤트→제1원칙 분석 (Claude) + 테제 후보 추출 |
| `src/core/models.py` | `FirstPrincipleAnalysis` 모델 |
| `scripts/ontology_io.py` | 온톨로지 CRUD CLI |
| `scripts/generate_timeline.py` | 타임라인 시각화 |
