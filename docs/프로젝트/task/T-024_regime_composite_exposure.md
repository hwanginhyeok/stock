# T-024: 계층적 가중 시장 레짐 점수 + 포트폴리오 익스포저 대시보드

**완료일**: 2026-02-28
**수정 파일**: 3개

---

## 설계 결정

### 가중치 구조
```
Composite = Trend × 2.0 + Breadth × 1.5 + VIX × 1.0 + Sentiment × 0.5
```
- Trend(40%): 가장 안정적인 시그널 — SPY의 ADX+EMA 기반 추세 분류
- Breadth(25%): 시장 폭 — 200DMA 위 종목 비율
- VIX(20%): 변동성/공포 지수
- Sentiment(15%): F&G 역발상 — Extreme Greed → 숏, Extreme Fear → 롱

### Sentiment 역발상 근거
- 행동재무학: Extreme Greed(≥75) → 과열 경고(-1), Extreme Fear(≤25) → 저점 기회(+1)
- 버핏 원칙 "다른 사람이 두려워할 때 탐욕적이 되라"

### Net Exposure 매핑
| 합산 점수 | Net Exposure | 레짐 |
|:---------:|:-----------:|------|
| +5 ~ +7 | 75% | 강한 강세 (Strong Bull) |
| +3 ~ +4 | 55% | 일반 강세 (Normal Bull) |
| +1 ~ +2 | 35% | 신중한 (Cautious) |
| -1 ~ 0 | 15% | 방어적 (Defensive) |
| -3 ~ -2 | -5% | 중립/약숏 (Neutral/Mild Short) |
| -8 ~ -4 | -25% | 적극 숏 (Active Short) |

### Long/Short 공식
```
Long  = (Gross + Net) / 2
Short = (Gross - Net) / 2
```
Gross 기본값 130% (중간 수준 레버리지)

---

## 수정 내역

### 1. `src/analyzers/market_sentiment.py`
- `compute_regime_composite()` 신규 함수 추가
- 4개 지표 점수화 → 가중 합산 → Net Exposure 매핑 → Long/Short 배분

### 2. `scripts/generate_signal_report.py`
- `_fetch_stock_data()` 반환 dict에 `price_vs_ema200` 필드 추가
- Step 3.5: breadth 계산 (price_vs_ema200 > 0인 종목 비율)
- ^GSPC trend_regime을 SPY 프록시로 사용
- `compute_regime_composite()` 호출 → `market_data["exposure"]`에 저장
- 콘솔에 Composite Score, Regime, Net/Gross, Long/Short, Breadth 출력

### 3. `src/exporters/signal_builder.py`
- `_component_color()`, `_component_fill()` 헬퍼 추가
- `_build_exposure_dashboard()` 신규 함수: Section 1 Diagnosis 하단에 표시
  - 서브섹션 헤더 "Portfolio Exposure"
  - Regime 라벨 + Composite Score (색상 코딩)
  - 4개 컴포넌트 블록 (2열 merge, 양수=초록/0=회색/음수=빨강)
  - Net/Gross/Long/Short/Breadth label-value 쌍

---

## 검증 결과

- 단위 테스트: 4개 시나리오 (Strong Bull, Normal Bull, Sideways, Active Short) 전부 통과
- Long+Short=Gross, Long-Short=Net 수학 검증 통과
- 통합 테스트: `--tickers AAPL NVDA TSLA --skip-sigma` 정상 실행
- Excel 생성 및 Exposure Dashboard 표시 확인
