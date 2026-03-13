# T-023: ADX + EMA 20/50/200 추세 분류 (Trend Regime Classification)

## 완료일: 2026-02-27

## 개요
ADX 추세 강도 + EMA 정배열/역배열 + DI 방향을 결합하여 5단계 추세 분류 구현.

## 분류 로직

| 조건 | ADX ≥ 25 | ADX 20~25 | ADX < 20 |
|------|----------|-----------|----------|
| +DI > -DI & EMA 정배열 | Strong Uptrend | Uptrend | Sideways |
| +DI < -DI & EMA 역배열 | Strong Downtrend | Downtrend | Sideways |
| 신호 혼재 | Transition | Transition | Sideways |

## 수정 파일 (6개)

1. `config/market_config.yaml` — `trend_ema_periods`, `adx_strong`, `adx_weak` 추가
2. `src/core/config.py` — `TechnicalConfig` 모델에 3개 필드 추가
3. `src/analyzers/trend.py` — `classify_trend_regime()` 함수 신규 추가
4. `src/analyzers/market_sentiment.py` — `compute_trend_strength()` 반환값에 5개 필드 추가
5. `scripts/generate_signal_report.py` — period `6mo`→`1y`, trend regime 콘솔 출력 추가
6. `src/exporters/signal_builder.py` — Section 1·2에 "Trend" 열 추가, 색상 매핑

## 설계 결정

- **기존 함수 재사용**: `_ema()`는 `technical.py`에서 import, `_adx()`는 같은 `trend.py` 내부 함수 사용
- **하위 호환**: `compute_trend_strength()`는 기존 6개 필드 유지 + 5개 필드 추가 (호출자 영향 없음)
- **period 변경**: 200일 EMA에 최소 200 거래일 필요 → `6mo`(≈126일)에서 `1y`(≈252일)로 변경
- **Trend 열 위치**: Section 2에서 ADX Trend 뒤, Tech Score 앞 (14번째 열)

## 검증 결과

- 구문 검증: 모든 import 정상
- 단위 테스트: classify_trend_regime() 정상 작동 (합성 데이터 + 실제 데이터)
- 통합 테스트: `--tickers AAPL NVDA TSLA --skip-sigma` 리포트 정상 생성
- 하위 호환: 기존 compute_trend_strength/compute_fear_greed/market_diagnosis 테스트 모두 통과
