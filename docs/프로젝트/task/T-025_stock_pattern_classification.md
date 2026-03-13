# T-025: 종목 패턴 분류 (Breakout / Pullback / Consolidation)

## 완료일: 2026-02-28

## 목적

Long 포지션 종목 선별을 위한 3가지 차트 패턴 자동 감지.
기존 Trend Regime(추세 분류)에 매매 타이밍용 패턴 분류를 추가.

## 수정 파일 (4개)

### 1. `src/analyzers/trend.py`
- `classify_stock_pattern()` 신규 함수 추가
- 13개 입력 파라미터 → 3패턴 각 5조건 체크 → ≥3 충족 시 분류
- 우선순위: Breakout > Pullback > Consolidation
- 반환: pattern, pattern_kr, pattern_score, pattern_signals

### 2. `src/analyzers/market_sentiment.py`
- `compute_trend_strength()` 수정
- `adx_change_5d` 필드 추가 (ADX 5일 전 값과 현재 값의 차이)
- 기존 `adx_df`에서 추출, 추가 API 호출 없음

### 3. `scripts/generate_signal_report.py`
- `_fetch_stock_data()` 확장
- 기존 미전달 필드 전달: ema_alignment, ema_200_slope, macd_histogram
- 신규 계산: vol_ratio (Volume / 20일 평균), bb_width_rank (BB폭 120일 백분위)
- `classify_stock_pattern()` 호출 → pattern, pattern_kr, pattern_score 추가
- 콘솔 출력에 Pattern 표시

### 4. `src/exporters/signal_builder.py`
- Section 2 열 16 → 17 (Pattern 열 추가)
- Legend 스팬 17열로 확장
- 패턴별 색상: Breakout=파랑, Pullback=초록, Consolidation=주황, —=회색
- Guide 시트에 "Pattern Classification" 섹션 추가 (10번)
- 활용 팁 3개 추가 (7, 8, 9번)

## 3가지 패턴 정의

| 패턴 | 조건 (5개 중 ≥3) |
|------|------------------|
| Breakout | ADX 상승(+3), 거래량 폭발(1.5x), MACD Bullish, ST Bullish, EMA200 위 |
| Pullback | Trend ≥ Uptrend, EMA 정배열, 1W% 음수, RSI 35~55, ST Bullish |
| Consolidation | ADX < 20, BB 스퀴즈(하위 25%), 거래량 감소(0.8x), EMA200 지지, MACD ≈ 0 |

## 설계 결정

- **MACD histogram threshold (0.5)**: Consolidation의 "MACD flat" 판정. 주가 수준과 무관한 절대값 기준이지만, 대부분 대형주에서 합리적. 소형주나 페니주에는 비율 기반이 나을 수 있음.
- **BB width rank lookback (120일)**: 6개월 기준으로 BB폭의 상대적 위치 판단. 1년(252일)보다 최근 변동성 변화를 더 잘 반영.
- **adx_change_5d index [-6]**: 5일 전 = iloc[-6] (현재 포함 6번째), 거래일 기준 5일 변화.

## 검증 결과

```
AAPL  → Pullback (Sideways but pullback conditions met)
NVDA  → Pullback
TSLA  → Consolidation (Transition + low BB width)
NFLX  → — (no pattern match)
COST  → — (no pattern match)
```
