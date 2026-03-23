# 뉴스 팩트 추출 스킬

> 뉴스에서 숫자와 사실만 추출하여 구조화된 데이터로 저장하는 절차.
> 규칙 기반 자동 추출 + Claude Code 세션 수동 추출 하이브리드.

---

## 트리거

- "팩트 추출", "뉴스 분석", "뉴스 정리" 지시 시
- `extract_facts.py` 실행 시
- 시황 브리핑 데이터 준비 시

---

## 워크플로우

### Step 1: 뉴스 수집 (선행)

```bash
python scripts/collect_news.py --market kr   # 또는 us, all
```

### Step 2: 규칙 기반 자동 추출

```bash
python scripts/extract_facts.py auto --market all --min-confidence 0.5
```

숫자/퍼센트/금액이 포함된 문장을 자동으로 추출. 엔티티 매칭이 되면 confidence=1.0, 숫자만 있으면 0.7.

### Step 3: 미처리 뉴스 확인 (Claude Code 세션)

```bash
python scripts/extract_facts.py unprocessed --market kr
```

자동 추출에서 놓친 뉴스(본문 없는 기사, 복잡한 맥락)를 Claude Code가 직접 읽고 추출.

### Step 4: Claude Code 수동 추출 → apply

unprocessed 출력을 읽고 아래 스키마에 맞춰 JSON 작성 후 적용:

```bash
python scripts/extract_facts.py apply --file /tmp/facts.json
```

### Step 5: 브리핑 확인

```bash
python scripts/extract_facts.py briefing --market kr --hours 12
```

### Step 6: JSON 내보내기 (선택)

```bash
python scripts/extract_facts.py export --market kr --hours 24
```

→ `data/facts/2026-03-23_korea.json` 생성

---

## 팩트 스키마

```json
{
  "facts": [
    {
      "news_id": "<원본 뉴스 UUID>",
      "fact_type": "numerical|earnings|policy|deal|forecast|event",
      "claim": "SK하이닉스 HBM4 수율 85% 달성",
      "entities": ["SK하이닉스"],
      "tickers": ["000660"],
      "numbers": {
        "raw_values": ["85%"],
        "count": 1
      },
      "source_quote": "원문에서 해당 문장 그대로 인용",
      "market": "korea",
      "confidence": 1.0,
      "published_at": "2026-03-23T09:00:00"
    }
  ]
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `news_id` | Y | 원본 뉴스 UUID (unprocessed 출력에서 복사) |
| `fact_type` | Y | 팩트 유형 (아래 분류표 참조) |
| `claim` | Y | 팩트 한 문장 요약 (120자 이내 권장) |
| `entities` | N | 관련 기업/인물/기관명 |
| `tickers` | N | 관련 티커 심볼 |
| `numbers` | N | 추출된 숫자 (raw_values 배열 + count) |
| `source_quote` | Y | 원문 인용 (팩트의 근거) |
| `market` | Y | korea / us |
| `confidence` | N | 0.0~1.0 (기본값 1.0) |
| `published_at` | N | 기사 발행일 (ISO 8601) |

### fact_type 분류표

| 타입 | 설명 | 키워드 예시 |
|------|------|------------|
| `numerical` | 일반 수치/통계 | 판매량, 시총, 비율, 규모 |
| `earnings` | 실적/재무 | 매출, 영업이익, EPS, 가이던스 |
| `policy` | 정책/규제 | 금리, 관세, 법안, 행정명령 |
| `deal` | 딜/계약/투자 | 인수, M&A, IPO, 파트너십 |
| `forecast` | 전망/예측 | 목표가, 전망, 예상, outlook |
| `event` | 이벤트/발표 | 출시, 발표, 공개, 중단 |

---

## QA 체크리스트

- [ ] claim이 검증 가능한 사실인가 (의견/관점 아님)
- [ ] source_quote가 원문에서 직접 가져온 것인가
- [ ] numbers에 실제 수치가 포함되어 있는가
- [ ] fact_type이 claim 내용과 일치하는가
- [ ] 같은 news_id에서 중복 팩트가 없는가

---

## 관련 파일

| 파일 | 역할 |
|------|------|
| `scripts/extract_facts.py` | CLI 진입점 |
| `src/analyzers/fact_extractor.py` | 규칙 기반 추출 엔진 |
| `src/core/models.py` | `NewsFact`, `FactType` 모델 |
| `src/storage/fact_repository.py` | DB CRUD |
| `data/facts/` | 일별 JSON 스냅샷 |
