# 1-20 크립토 이메일 Section 5 확장

> 완료일: 2026-03-01

## 작업 요약

모닝 이메일 Section 5 (크립토 시장)에 시장 심리 3개 지표 추가.

## 추가된 지표

| 지표 | 소스 | 엔드포인트 | 인증 |
|---|---|---|---|
| BTC 도미넌스 | CoinGecko | `/api/v3/global` → `data.market_cap_percentage.btc` | 없음 (무료) |
| ETH/BTC 비율 | 계산 | `eth.price / btc.price` (기존 yfinance 데이터 재사용) | — |
| 공포탐욕지수 | alternative.me | `/fng/?limit=1` | 없음 (무료) |

## 설계 결정

### CoinGecko vs CoinMarketCap (BTC Dominance)
- CoinMarketCap은 무료 티어라도 API Key 발급 필요, 월 10,000 call 제한
- CoinGecko `/global`은 인증 없이 단일 호출로 `btc_dominance` + `eth_dominance` + 전체 시총 동시 반환
- **→ CoinGecko 채택**

### ETH/BTC 비율 계산 방식
- yfinance에서 BTC-USD, ETH-USD를 이미 수집 중이므로 추가 API 호출 없이 나눗셈으로 처리
- 외부 소스(CoinGecko 별도 엔드포인트)를 쓸 이유 없음
- **→ 기존 가격 데이터 재사용**

### alternative.me Fear & Greed
- Glassnode, Santiment 등 온체인 소스보다 합성 지표라 노이즈가 적음
- 크립토 업계 표준 소스로 널리 인용됨
- **→ alternative.me 채택**

## 변경 파일

- `src/collectors/crypto/crypto_collector.py`
  - `_fetch_btc_dominance()` 추가
  - `_fetch_fear_greed()` 추가
  - `collect()` 반환값에 `eth_btc_ratio`, `btc_dominance`, `fear_greed` 추가
- `templates/email/morning_report.html.j2`
  - Section 5 하단에 3-칸 카드 행 추가 (TVL 카드 아래)
  - 공포탐욕 점수 범위별 4단계 색상 코딩 (≤24 빨강 / ≤49 주황 / ≤74 초록 / 그외 밝은초록)

## 실측값 (2026-03-01 기준)

| 지표 | 값 |
|---|---|
| BTC 도미넌스 | 56.1% |
| ETH/BTC | 0.02986 |
| 공포탐욕지수 | 14 (Extreme Fear) |
