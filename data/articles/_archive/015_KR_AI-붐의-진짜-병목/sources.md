# 출처 & 팩트체크 -- KR-01 AI 붐의 진짜 병목

> 검증일: 2026-03-02

---

## 1차 자료 (공식 문서/IR)

| # | 자료명 | URL | 발표일 |
|---|--------|-----|--------|
| S1 | Jensen Huang on AI's 'Five-Layer Cake' at Davos (NVIDIA Blog) | https://blogs.nvidia.com/blog/davos-wef-blackrock-ceo-larry-fink-jensen-huang/ | 2026-01-21 |
| S2 | A conversation between Larry Fink and Jensen Huang at Davos 2026 (WEF) | https://www.weforum.org/videos/ai-five-layer-cake-jensen-huang/ | 2026-01-21 |
| S3 | NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2026 | https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026 | 2026-02-26 |
| S4 | Epoch AI -- B200 Cost Breakdown | https://epoch.ai/data-insights/b200-cost-breakdown | 2025 |
| S5 | GB200 NVL72 (NVIDIA 공식) | https://www.nvidia.com/en-us/data-center/gb200-nvl72/ | 2024 |
| S6 | SK hynix Posts Record Annual Financial Results in 2025 | https://news.skhynix.com/sk-hynix-announces-fy25-financial-results/ | 2026-01-28 |
| S7 | SK hynix Announces Q3 2025 Financial Results | https://news.skhynix.com/sk-hynix-announces-3q25-financial-results/ | 2025-10-29 |
| S8 | Micron Technology Fiscal Q1 2026 Earnings (HBM 3:1 trade ratio) | https://investors.micron.com/static-files/5ea95475-639b-4cfc-91fd-b9b4a2bb5e63 | 2025-12-18 |
| S9 | OpenAI raises $110B at $730B valuation (TechCrunch) | https://techcrunch.com/2026/02/27/openai-raises-110b-in-one-of-the-largest-private-funding-rounds-in-history/ | 2026-02-27 |
| S10 | Anthropic raises $30B in Series G at $380B valuation | https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation | 2026-02-12 |
| S11 | Jetson Thor (NVIDIA 공식) | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/ | 2025 |
| S12 | McKinsey -- The cost of compute: A $7 trillion race to scale data centers | https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-cost-of-compute-a-7-trillion-dollar-race-to-scale-data-centers | 2025 |
| S13 | IDC -- Global Memory Shortage Crisis: Market Analysis | https://www.idc.com/resource-center/blog/global-memory-shortage-crisis-market-analysis-and-the-potential-impact-on-the-smartphone-and-pc-markets-in-2026/ | 2026-02 |
| S14 | Gartner -- AI PCs Will Represent 31% of Worldwide PC Market by End of 2025 | https://www.gartner.com/en/newsroom/press-releases/2025-08-28-gartner-says-artificial-intelligence-pcs-will-represent-31-percent-of-worldwide-pc-market-by-the-end-of-2025 | 2025-08-28 |
| S15 | Deloitte -- AI ROI: The paradox of rising investment and elusive returns | https://www.deloitte.com/global/en/issues/generative-ai/ai-roi-the-paradox-of-rising-investment-and-elusive-returns.html | 2025 |

---

## 데이터 & 수치 검증

| # | 주장 | 출처 | 검증 |
|---|------|------|------|
| 1 | 젠슨 황 다보스 2026 WEF -- 5레이어 케이크 / AI Factory 발언 | S1, S2 (NVIDIA Blog + WEF 공식 영상). 2026-01-21 Larry Fink과의 대담에서 5-Layer Cake(에너지/칩/인프라/모델/앱) + AI Factory 개념 제시 | ✅ 확인됨 |
| 2 | 하이퍼스케일러 2026 CapEx $6,000억+ | IEEE ComSoc, MUFG, Introl 등 다수 매체. Big Five(Amazon/Google/MS/Meta/Oracle) 합산 ~$602B~$630B 전망. Amazon $200B, Google $175-185B, Meta $115-135B 등 | ✅ 확인됨 |
| 3 | OpenAI 기업가치 $157B | 2024년 10월 라운드에서 $157B 밸류에이션 확인 (Hacker News/Bloomberg). 단, 2026년 2월 기준 $730B으로 대폭 상승 | ⚠️ 맥락 보완 필요 -- 아티클에서 $157B는 과거 시점 수치. 현재 밸류에이션($730B)과 괴리가 큼. "2024년 $157B"로 시점을 명시하거나, 최신 수치로 업데이트 권장 |
| 4 | Anthropic $60B+ | 2025년 3월 라운드에서 $61.5B 밸류에이션 확인. 2026년 2월 기준 $380B으로 상승 | ⚠️ 맥락 보완 필요 -- 3번과 동일. "2025년 초 기준 $60B+"로 명시하거나 최신 수치($380B)로 업데이트 권장 |
| 5 | NVIDIA B200 판매가 $30,000~$40,000 | Epoch AI, Northflank, Modal 등 다수. 단독 칩 기준 $30K-$40K. OEM 번들(8개 묶음) 기준 개당 $46K 수준 | ✅ 확인됨 |
| 6 | B200 제조원가 ~$6,400, HBM 45%, 로직다이 14% | S4 (Epoch AI). Monte Carlo 시뮬레이션 기반 추정. 범위 $5,700-$7,300, 중앙값 ~$6,400. HBM ~$2,900(45%), 로직다이 ~$900(14%) | ✅ 확인됨 |
| 7 | B200 마진 82% | S4 (Epoch AI). 판매가 $30K-$40K / 원가 $6,400 기준 칩 레벨 그로스마진 ~80-85%. 82%는 중앙 추정치. 실제 시스템 판매 시 마진은 낮을 수 있음 (NVIDIA 전사 GAAP 그로스마진 71.1%) | ⚠️ 맥락 보완 필요 -- "칩 레벨" 마진임을 명시 권장. 전사 마진(71%)과는 별도 |
| 8 | GB200 NVL72: 가격 ~$3.9M, GPU 72개, 1,360kg, 120kW | S5 + Introl/Hyperstack/Sunbird. 가격 ~$3.9M 확인. GPU 72개 + Grace CPU 36개 확인. 무게 1,360kg(3,000lbs) 확인. 전력: 랙 전체 132kW (liquid 115kW + air 17kW)로 120kW보다 약간 높음 | ⚠️ 맥락 보완 필요 -- 전력은 GPU만 기준 ~120kW, 랙 전체 132kW. "약 120kW" 표현은 맥락에 따라 수용 가능하나 정확한 수치는 132kW |
| 9 | 구리 케이블 5,184개, 3.2km | SemiAnalysis GB200 Hardware Architecture + FiberMall. NVLink 5.0 포트 1,296개 x 4 differential pairs = 5,184개. 총 길이 2 miles(3.2km)의 구리 케이블링 | ✅ 확인됨 |
| 10 | Year 1 총비용 70~87억원 | Introl Blog (GB200 NVL72 Deployment Guide). 랙 $3.9M + 시설인프라 $1-2M + 연간운영비 $0.5M+ 등. 환율 1,400원 기준 대략 70~87억원 범위 추정 가능 | ⚠️ 맥락 보완 필요 -- 구체적 "70~87억원" 단일 수치는 Introl 블로그 원문에서 직접 명시되지 않음. 각 비용 항목 합산 추정치. 환율·시설 조건에 따라 변동 |
| 11 | McKinsey $6.7조 AI 데이터센터 투자 전망 | S12 (McKinsey). 2030년까지 데이터센터 누적 CapEx $6.7T 전망 (AI $5.2T + 기존 IT $1.5T). 가속 시나리오 $7.9T, 보수 시나리오 $3.7T | ⚠️ 맥락 보완 필요 -- 아티클 표현("누적 $6.7조") 정확. 단, 60% IT장비/25% 에너지/15% 시설 비율은 McKinsey 원문의 중간 시나리오 기준 |
| 12 | HBM3e 웨이퍼 3~4배 소비 (Micron CEO) | S8 (Micron FQ1 2026 Earnings). CEO Sanjay Mehrotra: HBM3E는 같은 비트 수 대비 DDR5의 3배 실리콘 소비. HBM4/4E에서 4:1 이상으로 증가 예상 | ✅ 확인됨 |
| 13 | SK하이닉스 HBM 점유율 57%, 삼성 22%, Micron 21% | Counterpoint Research Q3 2025 데이터. SK하이닉스 57%, 삼성 22% (Q2 15%에서 상승), Micron 21% | ✅ 확인됨 |
| 14 | SK하이닉스 NVIDIA 납품 비중 ~90% | CNBC, DigiTimes, NotebookCheck 등 다수. "현재 NVIDIA HBM의 약 90%를 SK하이닉스가 공급". 2026년에는 삼성/Micron 확대로 50% 수준으로 하락 전망 | ⚠️ 맥락 보완 필요 -- 2025년 기준 ~90% 정확. 2026년에는 비중 하락 예상(~50-70%). 시점 명시 권장 |
| 15 | SK하이닉스 HBM3e 수율 80% vs 삼성 50% | TrendForce (2024-05): SK하이닉스 HBM3e 수율 "거의 80%" 달성 보도. 삼성 HBM3e 수율: 직접 "50%"로 명시된 출처 미확인. 업계 평균 HBM 수율 50-60% 범위 보도 있음. 삼성 초기 HBM3 수율은 10-20%로 SK하이닉스(60-70%)와 큰 격차 | ⚠️ 맥락 보완 필요 -- SK하이닉스 80%는 확인됨. 삼성 "50%"는 업계 평균 추정치에 가까움. "삼성 약 50%"보다 "업계 평균 50-60% 수준"으로 완화 표현 권장 |
| 16 | MR-MUF vs TC-NCF 공정 차이 | TweakTown, TrendForce, NomadSemi 등 다수. SK하이닉스 MR-MUF(Mass Reflow Underfill) 2019년 공개. 삼성 TC-NCF(Thermo-Compression Non-Conductive Film) 사용. 삼성은 향후 MR-MUF 기술 채택 전환 보도 | ✅ 확인됨 |
| 17 | HBM3e 2026 계약가 전년대비 +20%, HBM4 +50% 프리미엄 | TrendForce (2025-12-24): 삼성/SK하이닉스 HBM3E 2026 계약가 ~20% 인상 확인. HBM4: "생산원가 50% 증가" (TSMC 베이스다이 위탁 등). 판매가는 "HBM3E 대비 2배" 수준 보도 | ⚠️ 맥락 보완 필요 -- HBM3e +20% 확인됨. HBM4의 경우 "50% 프리미엄"보다 실제로는 "2배(100%+) 프리미엄" 보도가 다수. "생산원가 50% 증가"와 혼동 가능. 아티클 표현을 "50~100% 프리미엄"으로 조정하거나, "생산원가 50% 증가, 판매가 최대 2배"로 분리 표현 권장 |
| 18 | 삼성 DRAM 주문 70%만 충족 | DigiTimes (2025-10-28): "Memory shortage hits 70% order fulfillment". Samsung, NetworkWorld 등에서도 동일 보도 | ✅ 확인됨 |
| 19 | DDR5 가격 $6.84 -> $27.20 (3개월, 4배) | IntuitionLabs, Resell Calendar, NotebookCheck 등. 2025-09-20 16Gb DDR5 평균 $6.84 -> 2025-11 $24.83 -> 2025-12 $27.20. 세션 고점 $37까지. 약 4배(297% 상승) | ✅ 확인됨 |
| 20 | 2026 Q1 서버 DRAM +90%, PC DRAM +105~110% | TrendForce (2026-01-05, 2026-02-02). 서버 DRAM QoQ +90% (역대 최대 분기 상승), PC DRAM QoQ +105~110% (사실상 2배) | ✅ 확인됨 |
| 21 | SK하이닉스 영업이익률 스윙: 2023Q1 -67% -> 2025Q4 +58% | S6, S7 + TrendForce. 2023 Q1 영업손실 3.4조원, 영업이익률 -67%. 2025 Q4 영업이익 19.17조원, 영업이익률 58%. 125%p 스윙 | ✅ 확인됨 |
| 22 | SK하이닉스 2025 영업이익 47.21조원 | S6 (SK hynix FY2025 공식 IR). 연간 영업이익 47.2조원 사상 최대 실적, 삼성 제치고 세계 최대 메모리 기업 | ✅ 확인됨 |
| 23 | TrendForce 범용 DRAM OPM 70% 전망 | TrendForce (2025-11-12): "SK hynix Reportedly Poised for Over 70% Operating Margin for General-Purpose DRAM amid Tight Supply". 1995년 이후 약 30년 만 | ✅ 확인됨 |
| 24 | AI PC 2026년 1.43억대, 55% 점유율 (Gartner) | S14 (Gartner 2025-08-28). AI PC 출하 2025년 7,780만대(31%) -> 2026년 1.43억대(55%) 전망 | ✅ 확인됨 |
| 25 | Galaxy S25 전모델 12GB, iPhone 17 Pro 12GB | PhoneArena (Galaxy S25/S25 Ultra 12GB 확인), TrendForce (2025-05-06: iPhone 17 Pro 12GB DRAM 업그레이드 보도) | ✅ 확인됨 |
| 26 | Apple iPhone 18 DRAM 100% 가격 인상 수용 | MacRumors, WCCFtech, NotebookCheck, Tom's Guide 등 다수 (2026-02-26). Samsung이 LPDDR5X 100% 인상 제안, Apple 즉시 수용. 2025년 초 $25-29 -> 2025년 말 $70 | ✅ 확인됨 |
| 27 | Jetson Thor 128GB LPDDR5X | S11 (NVIDIA 공식). 128GB LPDDR5X @ 4266MHz, 273 GB/s bandwidth, 40-130W | ✅ 확인됨 |
| 28 | Tesla AI5 144GB (HW4의 9배) | NotATeslaApp, Wikipedia (Tesla Autopilot hardware), Digital Habitats 등. AI5: 144GB 메모리 (HW4 16GB의 9배), 8x compute, 5x memory bandwidth. 출시 2026년 말~2027년 | ✅ 확인됨 |
| 29 | RTX 50 시리즈 40% 감산 (GDDR7 부족) | WebProNews, PC Gamer, TweakTown, VideoCardz 등 다수 (2025-12~2026-01). H1 2026 공급 30-40% 감소 예상. GDDR7 포함 전반적 메모리 공급 부족 | ✅ 확인됨 |
| 30 | 2026 DRAM 수요 +35% vs 공급 +16% | TrendForce: 수요 +35% 전망. IDC: 공급 +16% YoY (역사적 평균 이하). 19%p 구조적 갭 | ✅ 확인됨 |
| 31 | NVIDIA FY2026 매출 $215.9B, 영업이익 $137B | S3 (NVIDIA 공식). 매출 $215.9B 확인. Non-GAAP 영업이익 $137.3B 확인. GAAP 영업이익 $130.4B. 마진 64%는 Non-GAAP OPM 63.6%에 가까움 | ⚠️ 맥락 보완 필요 -- $137B는 Non-GAAP 수치. GAAP은 $130.4B. "영업이익 $137B"라고만 쓰면 Non-GAAP임을 명시하거나, GAAP 기준 $130B으로 수정 권장. 마진 64% 표기도 63.6%(Non-GAAP) 반올림 |
| 32 | SK하이닉스 2026 컨센서스 영업이익 100조원+ | BusinessKorea, Seoul Economic Daily 등. 다이신증권 등 일부 증권사가 "100조원 시대 개막" 전망. SK그룹 최태원 회장도 "$100B(~145조원) 초과 가능" 언급. 단, 컨센서스 범위는 61~100조원+으로 넓음 | ⚠️ 맥락 보완 필요 -- 일부 증권사 낙관 전망 + 최태원 회장 발언 기반. 전체 컨센서스 중앙값은 이보다 낮을 수 있음. "일부 전망 100조원+"으로 완화하거나 컨센서스 범위 명시 권장 |

---

## 추가 검증: MIT AI 파일럿 95% 실패 + Deloitte 10%

| # | 주장 | 출처 | 검증 |
|---|------|------|------|
| A1 | MIT 연구 AI 파일럿 95% ROI 실패 | MIT NANDA "GenAI Divide: State of AI in Business 2025" 보고서. Fortune, Healthcare IT News, Legal.io 등 다수 보도. 150건 인터뷰 + 350명 설문 + 300건 공개 배포 분석. 단, 일부 비판 있음 -- 핵심 "95%" 수치는 52건 정성 인터뷰에서 추출, 연구진도 "방향적으로 정확(directionally accurate)"이라고만 표현 | ⚠️ 맥락 보완 필요 -- 방법론에 대한 비판 존재. "MIT 연구에 따르면"으로 충분하나, 절대적 수치로 인용 시 주의 |
| A2 | Deloitte 조사 유의미한 ROI 달성 기업 10% | S15 (Deloitte Global). 1,854명 임원 대상 설문. "10%만이 에이전틱 AI에서 유의미한 ROI 실현 중". 주로 유럽/중동 대상 조사 | ✅ 확인됨 |

---

## 참고 매체/리서치

| 매체 | URL | 인용 항목 |
|------|-----|-----------|
| Epoch AI (B200 원가분석) | https://epoch.ai/data-insights/b200-cost-breakdown | #5, #6, #7 |
| TrendForce (메모리 가격/전망) | https://www.trendforce.com/ | #17, #18, #19, #20, #23, #30 |
| TrendForce -- HBM3E Price Hike | https://www.trendforce.com/news/2025/12/24/news-samsung-sk-hynix-reportedly-plan-20-hbm3e-price-hike-for-2026-as-nvidia-h200-asic-demand-rises/ | #17 |
| TrendForce -- SK hynix 70% OPM | https://www.trendforce.com/news/2025/11/12/news-sk-hynix-reportedly-poised-for-over-70-operating-margin-for-general-purpose-dram-amid-tight-supply/ | #23 |
| TrendForce -- 1Q26 Memory Prices | https://www.trendforce.com/presscenter/news/20260202-12911.html | #20 |
| TrendForce -- Samsung 12H HBM3e NVIDIA 인증 | https://www.trendforce.com/news/2025/09/22/news-samsung-12h-hbm3e-reportedly-clears-nvidia-tests-after-18-month-setback-hbm4-reaches-final-phase/ | #15, #16 |
| TrendForce -- Memory Price Rally Past 2028 | https://www.trendforce.com/news/2025/12/02/news-memory-price-rally-may-run-past-2028-as-samsung-sk-hynix-reportedly-cautious-on-expansion/ | #18, #30 |
| TrendForce -- AI 20% DRAM Wafer Capacity | https://www.trendforce.com/news/2025/12/26/news-ai-reportedly-to-consume-20-of-global-dram-wafer-capacity-in-2026-hbm-gddr7-lead-demand/ | 섹션 5 |
| TrendForce -- Micron 3 Culprits | https://www.trendforce.com/news/2025/12/18/news-micron-reveals-three-culprits-behind-memory-crunch-and-why-it-wont-ease-soon/ | #12 |
| TrendForce -- Memory Industry Cautious CapEx | https://www.trendforce.com/presscenter/news/20251113-12780.html | #30 |
| Counterpoint Research (HBM 점유율) | https://counterpointresearch.com/en/insights/global-dram-and-hbm-market-share | #13 |
| IDC -- Global Memory Shortage Crisis | https://www.idc.com/resource-center/blog/global-memory-shortage-crisis-market-analysis-and-the-potential-impact-on-the-smartphone-and-pc-markets-in-2026/ | #30 |
| McKinsey -- Cost of Compute | https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-cost-of-compute-a-7-trillion-dollar-race-to-scale-data-centers | #11 |
| SemiAnalysis -- GB200 Hardware Architecture | https://semianalysis.com/2024/07/17/gb200-hardware-architecture-and-component/ | #9 |
| Introl -- GB200 NVL72 Deployment Guide | https://introl.com/blog/gb200-nvl72-deployment-72-gpu-liquid-cooled | #8, #9, #10 |
| IEEE ComSoc -- Hyperscaler CapEx $600B | https://techblog.comsoc.org/2025/12/22/hyperscaler-capex-600-bn-in-2026-a-36-increase-over-2025-while-global-spending-on-cloud-infrastructure-services-skyrockets/ | #2 |
| CNBC -- SK Hynix Q3 Record (sold out 2026) | https://www.cnbc.com/2025/10/29/sk-hynix-q3-profit-revenue-record-.html | #14 |
| CNBC -- SK Hynix Overtakes Samsung | https://www.cnbc.com/2026/01/29/sk-hynix-beats-samsung-2025-profit-ai-memory-hbm.html | #22 |
| DigiTimes -- Memory Shortage 70% Fulfillment | https://www.digitimes.com/news/a20251028PD216/dram-chip-shortage-price-market-demand.html | #18 |
| Fortune -- MIT 95% AI Pilot Failure | https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/ | A1 |
| Gartner -- AI PC 2026 | https://www.gartner.com/en/newsroom/press-releases/2025-08-28-gartner-says-artificial-intelligence-pcs-will-represent-31-percent-of-worldwide-pc-market-by-the-end-of-2025 | #24 |
| MacRumors -- Apple 100% DRAM Price Hike | https://www.macrumors.com/2026/02/26/apple-agrees-100-price-hike-samsung-ram/ | #26 |
| NotATeslaApp -- Tesla AI5 Specs | https://www.notateslaapp.com/news/3115/ | #28 |
| TweakTown -- SK hynix HBM3E Yield 80% | https://www.tweaktown.com/news/98504/sk-hynix-hbm3e-chip-yield-hits-80-which-has-help-cut-mass-production-times-down-by-50/index.html | #15 |
| TweakTown -- Samsung MR-MUF Adoption | https://www.tweaktown.com/news/96816/samsung-to-use-mr-muf-technology-like-sk-hynix-for-its-future-gen-hbm-products/index.html | #16 |
| WebProNews -- RTX 50 40% Production Cut | https://www.webpronews.com/nvidia-to-cut-rtx-50-series-gpu-production-40-in-2026-over-gddr7-shortages/ | #29 |
| BusinessKorea -- SK Hynix 100T Operating Profit Era | https://www.businesskorea.co.kr/news/articleView.html?idxno=260114 | #32 |
| Seoul Economic Daily -- SK Chairman $100B Warning | https://en.sedaily.com/finance/2026/02/22/sk-chairman-warns-100-billion-profit-could-turn-to-100 | #32 |

---

## 검증 요약

| 상태 | 건수 | 비율 |
|------|------|------|
| ✅ 확인됨 | 22 | 65% |
| ⚠️ 맥락 보완 필요 | 12 | 35% |
| ❌ 확인 불가 | 0 | 0% |

### ⚠️ 보완 필요 항목 정리

| # | 항목 | 권장 조치 |
|---|------|-----------|
| 3, 4 | OpenAI $157B / Anthropic $60B+ | 시점 명시("2024년/2025년 초 기준") 또는 최신 밸류에이션으로 업데이트 |
| 7 | B200 마진 82% | "칩 레벨 그로스마진" 명시 (전사 마진과 구분) |
| 8 | GB200 NVL72 전력 120kW | 랙 전체 132kW, GPU만 ~120kW. "약 120kW" 유지 가능하나 각주 권장 |
| 10 | Year 1 총비용 70~87억원 | 단일 출처에서 정확히 이 범위가 명시되지 않음. 각 비용 항목 합산 추정. 원출처 Introl 블로그 참조 표기 권장 |
| 11 | McKinsey $6.7조 | 정확. 다만 "60% IT장비/25% 에너지/15% 시설" 비율은 중간 시나리오 기준임을 인지 |
| 14 | NVIDIA 납품 비중 ~90% | 2025년 기준 정확. 2026년에는 하락 전망. "2025년 기준" 시점 명시 권장 |
| 15 | 삼성 수율 50% | SK하이닉스 80% 확인됨. 삼성 "50%"는 업계 평균 수치에 가까움. 직접적 삼성 공식 수치 아님 |
| 17 | HBM4 +50% 프리미엄 | 실제 보도는 "생산원가 50% 증가" + "판매가 2배(100%+ 프리미엄)". 혼동 가능성 있음 |
| 31 | NVIDIA 영업이익 $137B | Non-GAAP 수치. GAAP은 $130.4B. 기준 명시 권장 |
| 32 | SK하이닉스 2026 컨센서스 100조원+ | 낙관 전망 + 최태원 회장 발언 기반. 컨센서스 범위가 넓음 |
| A1 | MIT 95% 실패 | 방법론 비판 존재. "방향적으로 정확"이라는 연구진 자체 표현 참고 |
