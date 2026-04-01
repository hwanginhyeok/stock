# 시그널 리포트 생성 스킬 (signal-report)

> **트리거**: 아래 표현이 나오면 이 스킬을 즉시 실행한다.
> - "시그널 리포트" / "signal report" / "리포트 생성"
> - "대시보드" / "dashboard" / "Excel 리포트"
> - 주간 리포트 생성 시

---

## 목적

시장 데이터를 수집하여 시그널 리포트(Excel)와 대시보드를 생성하고, 이상치를 검수한다.

---

## 관련 스크립트

| 스크립트 | 역할 |
|---------|------|
| `scripts/generate_signal_report.py` | 시그널 리포트 Excel 생성 |
| `scripts/generate_dashboard.py` | 대시보드 Excel 생성 |
| `src/analyzers/market_sentiment.py` | 공포탐욕, 레짐, 추세 강도 |
| `src/analyzers/technical.py` | RSI, EMA 등 기술적 분석 |
| `src/analyzers/trend.py` | ADX, Supertrend, 레짐 분류 |
| `src/exporters/base.py` | Excel 스타일링 (style_cell, score_fill 등) |

---

## 실행 순서 (순서 준수 필수)

### STEP 1 — 데이터 수집 상태 확인

```bash
cd /home/window11/stock
source .venv-wsl/bin/activate
```

실행 전 데이터 소스 가용성 확인:
- yfinance: 주가/지수/ETF
- FRED: 유동성 지표
- 장중/장외 시간대에 따른 IV 가용성

### STEP 2 — 시그널 리포트 생성

```bash
python scripts/generate_signal_report.py
```

출력 파일: `data/reports/signal_report_{날짜}.xlsx`

### STEP 3 — 대시보드 생성

```bash
python scripts/generate_dashboard.py
```

출력 파일: `data/reports/dashboard_{날짜}.xlsx`

### STEP 4 — Excel 검수 체크리스트

생성된 Excel을 검수한다:

```
📊 시그널 리포트 검수 — {날짜}

| # | 항목 | 확인 내용 | 결과 |
|---|------|----------|------|
| 1 | 날짜 정확성 | 리포트 날짜 = 최근 거래일 | |
| 2 | 종목 수 | 워치리스트 전체 포함 | |
| 3 | RSI 범위 | 0~100 이내 (NaN 없음) | |
| 4 | ADX 범위 | 0~100 이내 | |
| 5 | 시그마 값 | |σ| < 5 (극단치 이상 확인) | |
| 6 | 색상 코딩 | score_fill, pct_color_font 정상 | |
| 7 | 레짐 분류 | Risk-On/Off/Neutral 중 하나 | |
| 8 | 차트 생성 | 내장 차트 렌더링 정상 | |
```

### STEP 5 — 이상치 확인

| 이상치 패턴 | 원인 가능성 | 대응 |
|------------|-----------|------|
| NaN 값 | API 실패 또는 신규 종목 | 해당 데이터 소스 확인 |
| RSI = 0 또는 100 | 극단적 시장 또는 데이터 오류 | 원시 가격 데이터 확인 |
| σ > 3 | 급등/급락 | 뉴스 확인 후 정상 판정 |
| 전일 대비 레짐 변경 | 시장 전환 | 복수 지표 교차 확인 |

### STEP 6 — 결과 보고

```
📊 시그널 리포트 — {날짜}

파일: data/reports/signal_report_{날짜}.xlsx
      data/reports/dashboard_{날짜}.xlsx

검수: ✅ {N}/8 항목 통과
이상치: {있음/없음}
레짐: {Risk-On / Risk-Off / Neutral}
주요 시그널:
- TSLA: RSI 72 (과매수 근접), +1.2σ
- BTC: ADX 38 (강한 추세), Risk-On
```

---

## 판단 규칙

| 상황 | 행동 |
|------|------|
| 전체 정상 | 요약 + 주요 시그널 보고 |
| NaN 다수 | 데이터 수집 스크립트 재실행 |
| 레짐 전환 감지 | 원인 분석 + 포지션 시사점 논의 |
| Excel 스타일 깨짐 | `src/exporters/base.py` 확인 |
| 스크립트 에러 | 에러 메시지 분석 + 의존성 확인 |

---

## 주의사항

- matplotlib 차트 생성 시 `matplotlib.use("Agg")` 필수 (WSL 헤드리스)
- 한글 폰트: `NotoSansCJK-Regular.ttc` → `Noto Sans CJK JP` (coding.md 참조)
- Y축 스케일: `min - 10% ~ max + 10%` 패딩 필수 (coding.md 국룰)
- Excel 파일은 `data/reports/`에 저장 — git ignored
- 시그널 리포트 결과는 투자 판단 참고용이지 자동 매매 시그널이 아님
