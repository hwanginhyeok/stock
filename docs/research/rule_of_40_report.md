# Rule of 40 스크리닝 보고서

> 생성일: 2026-05-12 00:24  
> Rule of 40 = Revenue Growth YoY (%) + Operating Margin (%)  
> 분석 대상: NASDAQ 100, S&P 500, Russell 2000 (S&P 400+600 proxy)  
> 데이터: yfinance (최근 분기 기준)

---

## 1. Top 30 - Rule of 40 초과 (Operating)

전체 수집 1323개 중 이상치 제외 1318개 분석, **255개**가 R40 >= 40% 달성. 상위 30개:

> 이상치 필터: 분기 매출 $10M 미만, 매출 성장률 ±1000% 초과, R40 ±500% 초과 종목 제외

| # | Ticker | Company | Sector | Rev Growth | Op Margin | R40(Op) | R40(FCF) | Index |
|---|--------|---------|--------|-----------|----------|---------|---------|-------|
| 1 | **SNDK** | Sandisk Corporation | Technology | +251.0% | 70.0% | **321.0** | 301.3 | NASDAQ100, SP500 |
| 2 | **MU** | Micron Technology, Inc. | Technology | +196.3% | 67.6% | **263.9** | 219.4 | NASDAQ100, SP500 |
| 3 | **MRP** | Millrose Properties, Inc. | Real Estate | +156.0% | 85.2% | **241.2** | 565.0 | RUSSELL2000_PROXY |
| 4 | **DLTR** | Dollar Tree, Inc. | Consumer Defensive | +209.0% | 12.7% | **221.7** | 226.8 | SP500 |
| 5 | **UNIT** | Uniti Group Inc. | Real Estate | +212.7% | 5.1% | **217.8** | 188.7 | RUSSELL2000_PROXY |
| 6 | **CELH** | Celsius Holdings, Inc. | Consumer Defensive | +137.7% | 18.3% | **156.0** | 146.1 | RUSSELL2000_PROXY |
| 7 | **HL** | Hecla Mining Company | Basic Materials | +100.4% | 55.3% | **155.7** | 138.0 | RUSSELL2000_PROXY |
| 8 | **MDU** | MDU Resources Group, Inc. | Utilities | +134.4% | 20.1% | **154.5** | 71.4 | RUSSELL2000_PROXY |
| 9 | **RGLD** | Royal Gold, Inc. | Basic Materials | +85.3% | 59.8% | **145.1** | 149.6 | RUSSELL2000_PROXY |
| 10 | **INSW** | International Seaways, In | Energy | +77.5% | 61.6% | **139.0** | 99.0 | RUSSELL2000_PROXY |
| 11 | **NVDA** | NVIDIA Corporation | Technology | +73.2% | 65.0% | **138.2** | 124.4 | NASDAQ100, SP500 |
| 12 | **APP** | Applovin Corporation | Communication Services | +59.0% | 78.2% | **137.1** | 129.1 | NASDAQ100, SP500 |
| 13 | **EXE** | Expand Energy Corporation | Energy | +100.3% | 36.4% | **136.7** | 138.7 | SP500 |
| 14 | **AVAV** | AeroVironment, Inc. | Industrials | +143.4% | -6.8% | **136.6** | 138.1 | RUSSELL2000_PROXY |
| 15 | **CTRE** | CareTrust REIT, Inc. | Real Estate | +72.8% | 58.7% | **131.5** | 180.7 | RUSSELL2000_PROXY |
| 16 | **PLTR** | Palantir Technologies Inc | Technology | +84.7% | 46.2% | **130.9** | 139.3 | NASDAQ100, SP500 |
| 17 | **SMCI** | Super Micro Computer, Inc | Technology | +123.4% | 3.7% | **127.1** | 115.9 | SP500 |
| 18 | **TER** | Teradyne, Inc. | Technology | +87.0% | 37.1% | **124.2** | 102.7 | SP500 |
| 19 | **VNOM** | Viper Energy, Inc. | Energy | +89.9% | 29.7% | **119.6** | -98.1 | RUSSELL2000_PROXY |
| 20 | **ALNY** | Alnylam Pharmaceuticals,  | Healthcare | +96.4% | 23.0% | **119.4** | 100.6 | NASDAQ100 |
| 21 | **ADEA** | Adeia Inc. | Technology | +53.3% | 63.1% | **116.4** | 62.2 | RUSSELL2000_PROXY |
| 22 | **ECPG** | Encore Capital Group Inc | Financial Services | +78.3% | 36.6% | **114.9** | 80.4 | RUSSELL2000_PROXY |
| 23 | **EQT** | EQT Corporation | Energy | +49.5% | 63.0% | **112.5** | 117.5 | SP500 |
| 24 | **LITE** | Lumentum Holdings Inc. | Technology | +90.1% | 21.7% | **111.8** | 99.9 | SP500 |
| 25 | **VICI** | VICI Properties Inc. | Real Estate | +3.5% | 107.5% | **111.0** | 65.5 | SP500 |
| 26 | **STRL** | Sterling Infrastructure,  | Industrials | +91.6% | 17.2% | **108.8** | 109.3 | RUSSELL2000_PROXY |
| 27 | **SANM** | Sanmina Corporation | Technology | +102.3% | 5.7% | **108.0** | 110.8 | RUSSELL2000_PROXY |
| 28 | **NEM** | Newmont Corporation | Basic Materials | +45.8% | 61.4% | **107.2** | 88.9 | SP500 |
| 29 | **LLY** | Eli Lilly and Company | Healthcare | +55.5% | 49.4% | **104.9** | 69.7 | SP500 |
| 30 | **HALO** | Halozyme Therapeutics, In | Healthcare | +51.6% | 53.3% | **104.9** | 36.1 | RUSSELL2000_PROXY |

## 2. Emerging 20 - R40 돌파 후보 (30~40% 구간)

R40 30~40% 구간 상위 20개 — 40% 돌파 잠재력이 높은 종목:

> yfinance 5분기 제한으로 추세 분석 불가. 단일 분기 R40 기준 정렬.

| # | Ticker | Company | Sector | Rev Growth | Op Margin | R40(Op) | R40(FCF) | Index |
|---|--------|---------|--------|-----------|----------|---------|---------|-------|
| 1 | **RBC** | RBC Bearings Incorporated | Industrials | +17.0% | 22.9% | **39.9** | 38.5 | RUSSELL2000_PROXY |
| 2 | **SKT** | Tanger Inc. | Real Estate | +11.1% | 28.7% | **39.9** | 35.3 | RUSSELL2000_PROXY |
| 3 | **APPF** | AppFolio, Inc. | Technology | +20.4% | 19.4% | **39.8** | 32.9 | RUSSELL2000_PROXY |
| 4 | **MKTX** | MarketAxess Holdings, Inc | Financial Services | +3.5% | 36.3% | **39.8** | 71.9 | RUSSELL2000_PROXY |
| 5 | **REGN** | Regeneron Pharmaceuticals | Healthcare | +19.0% | 20.7% | **39.7** | 41.2 | NASDAQ100, SP500 |
| 6 | **WSR** | Whitestone REIT | Real Estate | +7.3% | 32.4% | **39.7** | 43.3 | RUSSELL2000_PROXY |
| 7 | **ORA** | Ormat Technologies, Inc. | Utilities | +19.6% | 19.9% | **39.5** | 5.1 | RUSSELL2000_PROXY |
| 8 | **EBAY** | eBay Inc. | Consumer Cyclical | +19.5% | 19.8% | **39.3** | 48.5 | SP500 |
| 9 | **ZTS** | Zoetis Inc. | Healthcare | +2.9% | 36.3% | **39.3** | 15.8 | SP500 |
| 10 | **CR** | Crane Company | Industrials | +24.9% | 14.4% | **39.3** | 19.1 | RUSSELL2000_PROXY |
| 11 | **SHC** | Sotera Health Company | Healthcare | +4.6% | 34.7% | **39.3** | 21.8 | RUSSELL2000_PROXY |
| 12 | **BKNG** | Booking Holdings Inc. Com | Consumer Cyclical | +16.2% | 23.0% | **39.1** | 72.4 | NASDAQ100, SP500 |
| 13 | **YOU** | Clear Secure, Inc. | Technology | +16.7% | 22.4% | **39.1** | 94.6 | RUSSELL2000_PROXY |
| 14 | **MSI** | Motorola Solutions, Inc. | Technology | +12.3% | 26.8% | **39.0** | 46.0 | SP500 |
| 15 | **TTMI** | TTM Technologies, Inc. | Technology | +30.4% | 8.6% | **39.0** | 20.4 | RUSSELL2000_PROXY |
| 16 | **GRMN** | Garmin Ltd. | Technology | +14.2% | 24.6% | **38.8** | 41.0 | SP500 |
| 17 | **KEYS** | Keysight Technologies Inc | Technology | +23.3% | 15.5% | **38.8** | 48.7 | SP500 |
| 18 | **WWD** | Woodward, Inc. | Industrials | +23.4% | 15.4% | **38.8** | 26.9 | RUSSELL2000_PROXY |
| 19 | **DEA** | Easterly Government Prope | Real Estate | +16.4% | 22.5% | **38.8** | 46.2 | RUSSELL2000_PROXY |
| 20 | **GATX** | GATX Corporation | Industrials | +8.6% | 30.1% | **38.7** | 40.7 | RUSSELL2000_PROXY |

## 3. 인덱스별 분포

| Index | 구성종목 | 분석 성공 | R40 >= 40% | 비율 |
|-------|---------|----------|-----------|------|
| NASDAQ100 | 101 | 100 | 42 | 42.0% |
| SP500 | 503 | 456 | 115 | 25.2% |
| RUSSELL2000 PROXY | 1003 | 850 | 132 | 15.5% |

## 4. 섹터별 히트맵

| Sector | 종목수 | R40>=40 | 비율 | 평균 R40 | 중앙값 R40 |
|--------|-------|---------|------|---------|----------|
| Technology | 227 | 55 | 24% | 32.9 | 27.3 |
| Real Estate | 105 | 38 | 36% | 39.2 | 34.0 |
| Healthcare | 163 | 35 | 21% | 19.2 | 23.0 |
| Financial Services | 60 | 32 | 53% | 41.3 | 41.0 |
| Energy | 69 | 23 | 33% | 32.0 | 18.9 |
| Industrials | 237 | 18 | 8% | 20.4 | 20.3 |
| Consumer Cyclical | 203 | 17 | 8% | 14.1 | 15.3 |
| Utilities | 58 | 11 | 19% | 33.0 | 30.0 |
| Consumer Defensive | 82 | 10 | 12% | 21.4 | 14.8 |
| Communication Services | 48 | 9 | 19% | 21.5 | 19.9 |
| Basic Materials | 65 | 7 | 11% | 19.9 | 12.9 |
| N/A | 1 | 0 | 0% | 25.0 | 25.0 |

## 5. 투자 시사점

1. **R40 비율 상위 섹터**: Financial Services (32/60=53%), Real Estate (38/105=36%), Energy (23/69=33%) — 성장+수익성 균형이 우수한 기업 비율이 높다.
2. **NASDAQ 100 우위**: R40 돌파 비율 NASDAQ100(42/100), SP500(115/456), Russell2000 proxy(132/850) — 대형 테크 중심 인덱스가 우세.
3. **Emerging 30~40% 구간**: 190개 종목이 대기 중. 매출 성장 가속 또는 마진 개선 시 R40 진입 가능.
4. **반도체 사이클 효과**: SNDK, MU 등 메모리 반도체 종목이 상위권 — 업사이클 기반 매출 급증이 R40 끌어올림. 사이클 피크 주의.
5. **면책**: 본 보고서는 정보 제공 목적이며, 투자 권유가 아닙니다. 단일 분기 기준이므로 계절성/일회성/스핀오프 효과에 주의.

---

*데이터 소스: yfinance | 분석 도구: Python*