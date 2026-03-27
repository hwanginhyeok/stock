# 궤도 데이터센터 — 심층 리서치 보충자료

> 수집일: 2026-03-02
> 용도: 아티클 013 리서치 보충 — 기존 02_orbital_datacenter.md의 갭 보완
> 범위: 전력 위기 구체 수치, 기업별 딥다이브, 물리학 상세, Starlink 기술, 시장 규모, 반론

---

## 1. 글로벌 데이터센터 전력 위기 — 구체 수치

### 1-1. 전력 소비량 추이

| 연도 | 글로벌 DC 전력 (TWh) | 비중 | 출처 |
|------|---------------------|------|------|
| 2022 | ~360 | ~1.3% | IEA |
| 2024 | **415** | **~1.5%** | IEA Energy and AI Report (2025.10) |
| 2026E | 650~1,050 | ~2% | IEA 범위 추정 |
| 2030E | **945** (Base Case) | **~3%** | IEA Base Case |
| 2035E | 1,193 | — | IEA 장기 전망 |

- 2024→2030 연평균 성장률: **~15%/년** (전체 전력 소비 성장의 4배 이상)
- 미국+중국이 글로벌 성장의 **~80%** 차지
- 미국: 2024 대비 **+240 TWh (+130%)**
- 중국: 2024 대비 **+175 TWh (+170%)**

**출처**: [IEA - Energy demand from AI](https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai), [S&P Global - Data center power demand to double](https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/041025-global-data-center-power-demand-to-double-by-2030-on-ai-surge-iea), [DCD - IEA 945TWh](https://www.datacenterdynamics.com/en/news/iea-data-center-energy-consumption-set-to-double-by-2030-to-945twh/)

### 1-2. AI의 전력 수요 기여

| 지표 | 수치 | 출처 |
|------|------|------|
| 2023 글로벌 DC 임계 전력 | ~50 GW | Goldman Sachs |
| 2026E 글로벌 DC 임계 전력 | **96 GW** (거의 2배) | Goldman Sachs |
| AI 운영 비중 (2026E) | 전체 DC 전력의 **40%+** | Goldman Sachs |
| AI DC 연간 전력 (2026E) | **90 TWh** (2022 대비 10배) | Deloitte |
| 2027E AI DC 전력 수요 | **68 GW** | RAND |
| 2030E AI DC 전력 수요 | **327 GW** | Goldman Sachs |
| 2022 전체 DC 용량 (비교용) | 88 GW | Goldman Sachs |

- Goldman Sachs: 2025~2028 CAGR **17%**, 2027년까지 **92 GW** 도달
- 미국만: 2026년에 DC가 총 전력의 **6% (260 TWh)** 차지 예상

**출처**: [Goldman Sachs - AI to drive 165% increase](https://www.goldmansachs.com/insights/articles/ai-to-drive-165-increase-in-data-center-power-demand-by-2030), [RAND - AI Power Requirements](https://www.rand.org/pubs/research_reports/RRA3572-1.html), [Deloitte - GenAI Power Consumption](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2025/genai-power-consumption-creates-need-for-more-sustainable-data-centers.html)

### 1-3. 전력 부족으로 인한 지연 사례

| 사례 | 상세 | 출처 |
|------|------|------|
| **xAI Colossus (테네시)** | 2024.07 가동 시작, 필요 155MW 중 50MW만 TVA 계약. 150MW 변전소는 2024.11에야 완공. 수개월간 디젤 발전기 임시 운영 | Tom's Hardware (2025) |
| **OpenAI/Oracle (텍사스 Abilene)** | 인허가 요건으로 지연 보도 | Bloomberg (2026.02.25) |
| **Northern Virginia 전체** | Dominion Energy: 2023.07~2025.07 계약 용량 **185% 증가**. 50MW 이상 프로젝트는 PJM 연방 승인 필요 → 수개월~수년 지연 | DCD, TheRegister |
| **아일랜드 (더블린)** | 2021년 신규 DC 전력 연결 모라토리엄 발효. DC가 국가 전력의 **5% (2015) → 22% (2024)** 차지. 2025.12 조건부 해제 (자체 발전/배터리 필수) | Politico, EnergyConnects |
| **싱가포르** | DC 신규 건설 모라토리엄 시행 | ScienceDirect |
| **암스테르담** | DC 신규 건설 모라토리엄 시행 | Bisnow |
| **미국 전체** | 2025년 말 건설 중 용량 5.99 GW (전년 6.35 GW 대비 **첫 감소**) | Bloomberg (2026.02.25) |

**PJM 용량시장 가격 폭등**: $30/MW-day → **$270/MW-day** (2024.12), 현재 **$330/MW-day**

**출처**: [Bloomberg - US DC Construction Drops](https://www.bloomberg.com/news/articles/2026-02-25/us-data-center-construction-fell-amid-permit-and-power-delays), [The Register - Power shortages cap DC growth](https://www.theregister.com/2026/01/14/datacenter_expansion_power_limit/), [Tom's Hardware - US grid thin](https://www.tomshardware.com/tech-industry/artificial-intelligence/u-s-electricity-grid-stretches-thin-as-data-centers-rush-to-turn-on-onsite-generators-meta-xai-and-other-tech-giants-race-to-solve-ais-insatiable-power-appetite)

### 1-4. 빅테크의 원자력 전력 확보 경쟁

| 딜 | 상세 | 규모 | 시기 |
|----|------|------|------|
| **Microsoft + Constellation Energy** | Three Mile Island Unit 1 재가동. "Crane Clean Energy Center"로 리브랜딩. 20년 PPA. **2028년 재가동 목표**. Constellation $1.6B 투자 | **835 MW** | 2024.09 발표 |
| **Amazon + Talen Energy** | Susquehanna 원전 인접 960MW DC 캠퍼스. $650M 부지 인수. 10년 계약 | **수백 MW** | 2024 |
| **Google + Kairos Power** | 차세대 소형 모듈 원자로(SMR) 파트너십. 2030년대 초 **500 MW** 배치 목표 | **500 MW** | 2024 |
| **Meta** | 원자력 전력 확보 움직임 보도 | 미공개 | 2024~2025 |

- 빅테크 전체: 지난 1년간 미국에서 **10 GW 이상** 신규 원전 용량 계약
- DC가 미국 전력의 **~4%** 차지, 2030년까지 두 배 이상 증가 전망

**출처**: [Data Center Frontier - Nuclear Power Update](https://www.datacenterfrontier.com/energy/article/55239739/data-center-nuclear-power-update-microsoft-constellation-aws-talen-meta), [EIA - DC owners turn to nuclear](https://www.eia.gov/todayinenergy/detail.php?id=63304), [Introl - Nuclear power for AI](https://introl.com/blog/nuclear-power-ai-data-centers-microsoft-google-amazon-2025)

### 1-5. 하이퍼스케일러 CapEx 폭증

| 기업 | 2024 CapEx | 2025E CapEx | YoY |
|------|-----------|------------|-----|
| Amazon | $83B | **$100B** | +20% |
| Google | $52B | **$85B** | +63% |
| Microsoft | — | **$80B** | — |
| 빅5 합계 | — | **$350B** | — |
| 빅5 합계 (2026E) | — | **$600B+** | +36% |

- 전력 그리드 업그레이드 예상 비용: 2030년까지 **$720B**

**출처**: [DCPulse - Hyperscaler CapEx $315B](https://dcpulse.com/statistic/the-great-ai-infrastructure-race-hyperscaler-capex), [IEEE ComSoc - $400B in 2025](https://techblog.comsoc.org/2025/11/01/ai-spending-boom-accelerates-big-tech-to-invest-invest-an-aggregate-of-400-billion-in-2025-more-in-2026/), [Introl - Hyperscaler CapEx $600B 2026](https://introl.com/blog/hyperscaler-capex-600b-2026-ai-infrastructure-debt-january-2026)

---

## 2. 우주 데이터센터 기업 딥다이브

### 2-1. Starcloud (구 Lumen Orbit) — 선두주자

**창업자 & 팀**:
- **Philip Johnston** (CEO) — 전 McKinsey 어소시에이트, 이커머스 벤처 Opontia 공동 창업
- **Ezra Feilden** (CTO) — Oxford Space Systems, Airbus Defence and Space 엔지니어 출신
- **Adi Oltean** (수석 엔지니어) — SpaceX Starlink 시설(레드먼드) 수석 소프트웨어 엔지니어 출신

**펀딩 히스토리**:
| 라운드 | 금액 | 투자자 | 시기 |
|--------|------|--------|------|
| 시드 | $11M | NFX, Y Combinator, FUSE, Soma Capital, a16z/Sequoia 스카우트 | 2024 |
| 추가 시드 | $10M | (추가 투자자) | 2025 |
| **누적** | **$21M** | "YC 역사상 최대 시드 라운드 중 하나" | — |

- 200개 이상 VC가 $11M 시드 라운드 참여를 원함 (TechCrunch 보도)

**기술 접근**:
- 소형 위성 + 상용 GPU (NVIDIA H100) + 태양광 패널 + 복사 냉각
- 학습도 궤도에서 수행 (추론만이 아님)

**위성 사양 — Starcloud-1**:
| 항목 | 사양 |
|------|------|
| 질량 | 60 kg |
| 크기 | 소형 냉장고 크기 |
| 버스 | Corvus-Micro |
| GPU | NVIDIA H100 1기 (우주 최초 H100) |
| 태양광 | 1 kW |
| 궤도 | LEO, 325 km 고도 |
| 수명 | 11개월 (이후 제어 재진입) |
| 발사 | 2025.11 (SpaceX Falcon 9) |

**핵심 성과 (2025.12)**:
- **우주 최초 LLM 학습**: NanoGPT (Andrej Karpathy 작)를 셰익스피어 전집으로 궤도에서 학습 → 셰익스피어체 영어 생성
- **우주 최초 LLM 실행**: Google Gemma 모델을 궤도에서 실행+쿼리
- 이전 우주 GPU 대비 **100배** 강력한 컴퓨팅 파워 시연

**다음 단계 — Starcloud-2 (2026~2027)**:
- NVIDIA H100 복수기 + **Blackwell 플랫폼** 탑재
- Starcloud-1 대비 **100배** 전력 생성
- "빌드+발사 비용보다 더 많은 수익 창출" 목표
- 2026.10 발사 예정

**장기 비전**:
- 5 GW 궤도 데이터센터
- 태양광+냉각 패널: 약 4km x 4km 규모
- 용량 인자 **95%+** (밤/날씨 없음)

**경제성 주장 (백서)**:
- 40MW 클러스터 10년 운영 비용: 지구 $167M vs 우주 **$8.2M** (20배 절감)
- 우주 에너지 비용: 발사비 포함해도 지상 대비 **10배 저렴**
- 전제: 발사비 $30/kg (논쟁적)
- 5 GW DC 배치 시 200회 미만 발사 필요 (비판자: 단일 발사 아닌 22회 발사로 40MW 클러스터)

**출처**: [TechCrunch - 200 VCs wanted in](https://techcrunch.com/2024/12/11/200-vcs-wanted-to-get-into-lumen-orbits-11m-seed-round/), [GeekWire - Lumen Orbit rebrand](https://www.geekwire.com/2025/lumen-orbit-starcloud-10m-space-data-centers/), [CNBC - First AI model in space](https://www.cnbc.com/2025/12/10/nvidia-backed-starcloud-trains-first-ai-model-in-space-orbital-data-centers.html), [NVIDIA Blog - Starcloud](https://blogs.nvidia.com/blog/starcloud/), [GeekWire - Next moves](https://www.geekwire.com/2025/starcloud-power-training-ai-space/), [IEEE Spectrum - H100 in space](https://spectrum.ieee.org/nvidia-h100-space), [Starcloud Whitepaper](https://starcloudinc.github.io/wp.pdf)

### 2-2. Axiom Space — ISS 기반 접근

**AxDCU-1 (Data Center Unit-1)**:
- 2025년 가을 ISS에 배치
- Red Hat Device Edge 기반 프로토타입
- 클라우드 컴퓨팅, AI/ML, 데이터 퓨전, 우주 사이버보안 테스트
- 지구 독립적 클라우드 스토리지 + 엣지 프로세싱 시연

**궤도 데이터센터 노드 (ODC) 1 & 2**:
- **2026.01.11** LEO 발사 성공
- 우주 기반 클라우드 컴퓨팅의 기초 구축
- 위성·우주선에 직접 보안 클라우드 스토리지+처리+AI/ML 제공

**향후 계획**:
- 2027년: ISS에 광학 연결된 ODC 인프라 구축 (Axiom + Spacebilt 협력)
- 파트너: Kepler Space, Skyloom (통신 인프라)
- 헝가리 통신사 4iG: Axiom 궤도 DC에 **$100M 투자** 검토

**출처**: [Axiom Space - ODC Launch](https://www.axiomspace.com/release/axiom-space-to-launch-orbital-data-center-nodes-to-support-national-security-commercial-international-customers), [Axiom Space - AxDCU-1](https://www.axiomspace.com/release/red-hat-teams-up-with-axiom-space-to-launch-optimize-axiom-spaces-data-center-unit-1-on-orbit), [DCK - ISS DC Launch](https://www.datacenterknowledge.com/next-gen-data-centers/iss-data-center-launch-tests-edge-computing-at-400km-above-earth)

### 2-3. Aethero — 우주 엣지 컴퓨팅 하드웨어

**개요**: "우주 산업의 Intel 또는 NVIDIA"를 목표로 하는 하드웨어 스타트업

**현재 제품 — NxN Edge Computing Module**:
| 항목 | 사양 |
|------|------|
| 기반 칩 | NVIDIA Orin NX 또는 Nano |
| 연산력 | **100 TOPS** |
| 플랫폼 | 상용 NVIDIA Jetson |
| 형태 | 우주선 탑재용 다양한 포맷 |

**개발 중인 제품**:
- **NxA-ECM**: NVIDIA AGX Orin 기반 (출시 TBD)
- **1세대 RISC-V 커스텀 실리콘**: 인-센서 연산용 (출시 TBD)
- **Intel 협업 우주 프로세서**: ~2026년 제조 목표

**펀딩**:
- 2025.06: **$8.4M 시드** — Kindred Ventures 리드, Neo, Giant Step, O'Shaughnessy Ventures, Alumni Ventures 참여

**임무 일정**:
- 2026.02: 데모 미션 (NVIDIA Super Orin NX SoM 탑재 업그레이드 컴퓨터)
- 3차 미션: ESPA급 우주선에 탑재 예정

**포지션**: DC를 직접 짓는 것이 아닌, 궤도 컴퓨팅의 **칩/보드 공급자** 역할

**출처**: [TechCrunch - Aethero Intel/NVIDIA of space](https://techcrunch.com/2024/03/14/aethero-wants-to-become-the-space-industrys-intel-or-nvidia/), [Via Satellite - $8.4M Seed](https://www.satellitetoday.com/finance/2025/06/11/space-computing-startup-aethero-raises-8-4m-seed-round/), [BusinessWire - Aethero $8.4M](https://www.businesswire.com/news/home/20250610441726/en/Aethero-Secures-$8.4M-to-Build-the-Next-Generation-of-Space-Based-Computing-and-Autonomous-Spacecraft)

### 2-4. Rivada Space Networks — 레이저 메쉬 네트워크

**구조**: 600기 LEO 위성 + 위성 간 레이저 링크 + 온보드 라우팅 = "Outernet"

**기술 상세**:
- MEF(Metro Ethernet Forum) 준수 광학 메쉬 네트워크
- 위성 간 레이저 + 고급 온보드 처리/라우팅
- 글로벌 저지연 P2P 연결

**타임라인**:
| 시점 | 이벤트 |
|------|--------|
| 2023 | 위성 제조 계약 (Terran Orbital) |
| 2024 | Terran Orbital과 분쟁 → 수주 잔량에서 제거 |
| 2025.12 | 중국계 기업과의 위성 주파수 권리 분쟁 승소 (CEO Declan Ganley) |
| 2026 | 데모 미션 발사 예정 |
| 2027 | 운용 컨스텔레이션 발사 시작, 연말 전체 배치 완료 목표 |

**비즈니스**:
- 33개국 시장 접근 확보
- **$16B+ 서비스 계약** 체결 (정부, 기업, 국가)
- 미 해군 계약 포함
- 구축 비용: 최소 **$2.4B**

**출처**: [PRNewswire - Rivada $16B](https://www.prnewswire.com/news-releases/rivada-expands-outernet-access-to-33-countries-secures-16-billion-in-global-business-302439966.html), [SpaceNews - Rivada US government](https://spacenews.com/rivada-eyes-u-s-government-contracts-as-it-prepares-to-deploy-600-satellite-network/), [Payload Space - Demo 2026](https://payloadspace.com/rivada-to-fly-outernet-demo-mission-in-2026/)

### 2-5. Microsoft Azure Orbital

**현재 역량**:
- **Azure Orbital Ground Station**: 위성 운영자가 Azure VNet에 직접 데이터 다운링크
- **Azure Orbital Space SDK**: 개발자가 클라우드에서 개발 → 궤도에 배포하는 컨테이너화 컴퓨트 인프라 (프라이빗 프리뷰)
- **Loft Orbital 파트너십**: 첫 Azure 지원 Loft 위성 발사 (정부/기업이 Azure 환경에서 우주 하드웨어에 소프트웨어 배포)
- **Thales Alenia Space 파트너십**: 궤도 컴퓨터 + 고성능 지구관측 센서 배치 → 기후 데이터 처리

**포지션**: 자체 궤도 DC가 아닌, **지상-우주 하이브리드 클라우드 플랫폼** 제공자

**출처**: [Azure Blog - Orbital Space SDK](https://azure.microsoft.com/en-us/blog/any-developer-can-be-a-space-developer-with-the-new-azure-orbital-space-sdk/), [Azure Blog - Space products](https://azure.microsoft.com/en-us/blog/new-azure-space-products-enable-digital-resiliency-and-empower-the-industry/)

### 2-6. Google Project Suncatcher — 하이퍼스케일러 최초 진출

**발표**: 2025.11 (Google Research Blog)

**개요**: 태양광 + TPU + 위성 간 레이저 링크 = 궤도 ML 인프라 연구 프로젝트

**기술 설계**:
- Google TPU (Trillium v6e) 탑재 위성
- **81기 위성 클러스터** 반경 1km 배치 구상
- 위성 간 자유공간 광학(Free-Space Optics) 고대역 링크
- 태양 동기 궤도 → **거의 연속 태양광** 수집

**타임라인**:
| 시점 | 이벤트 |
|------|--------|
| 2025.11 | 연구 논문 + 프로젝트 발표 |
| ~2027 초 | **Planet Labs와 파트너십**: 2기 위성 발사 |
| — | TPU 우주 성능 테스트 + 위성 간 고대역 링크 시연 |

**핵심 수치**:
- 궤도 태양광: 지상 대비 **최대 8배** 효율 (NASA/JAXA 연구에서는 13배 인용)
- **방사선 테스트**: Google Trillium TPU v6e가 LEO 5년 미션 방사선 수준 견딤 확인
- 경제성 성립 조건: 발사비 **$200/kg** 도달 시 발사비 상각분이 DC 에너지 비용과 비슷 → Google은 이를 **2035년** 달성 가능으로 전망 (Starship 연 180회 발사 전제)

**Sundar Pichai 발언**: "궤도 데이터센터가 앞으로 10년 안에 새로운 표준이 될 것" (Fortune, 2025.12)

**출처**: [Google Research Blog - Suncatcher](https://research.google/blog/exploring-a-space-based-scalable-ai-infrastructure-system-design/), [DCD - Suncatcher TPUs](https://www.datacenterdynamics.com/en/news/project-suncatcher-google-to-launch-tpus-into-orbit-with-planet-labs-envisions-1km-arrays-of-81-satellite-compute-clusters/), [Fortune - Sundar Pichai](https://fortune.com/2025/12/01/google-ceo-sundar-pichai-project-suncatcher-extraterrestrial-data-centers-environment/), [Singularity Hub - Will 2027 be the year](https://singularityhub.com/2025/12/19/data-centers-in-space-will-2027-really-be-the-year-ai-goes-to-orbit/)

### 2-7. Crusoe Energy — 최초의 우주 클라우드 운영자

**개요**: 잉여/재생 에너지 활용 DC 전문 → 궤도로 확장

**Starcloud 파트너십 (2025.10 발표)**:
- Crusoe Cloud를 Starcloud 위성에 배치
- **2026년 말 발사**, 2027년 초부터 **제한적 GPU 용량** 우주에서 제공
- 고객이 우주 인프라에서 AI 워크로드 배포 및 운영 가능

**포지션**: 인프라는 Starcloud가 제공, Crusoe는 **클라우드 플랫폼 운영자** 역할

**출처**: [Crusoe - First Cloud Operator in Space](https://www.crusoe.ai/resources/newsroom/crusoe-to-become-first-cloud-operator-in-space-through-partnership-with-starcloud), [DCD - Crusoe Starcloud 2026](https://www.datacenterdynamics.com/en/news/crusoe-to-deploy-in-starcloud-satellite-data-center-in-late-2026-offer-limited-gpu-capacity-in-space-from-2027/)

### 2-8. K2 Space — 대형 위성 플랫폼

**개요**: 차세대 대형 고출력 위성 "Mega Class" 제조

**펀딩**:
- 2025.12: **$250M Series C** (Redpoint 리드), 기업가치 **$3B**
- 투자자: T. Rowe Price, Hedosophia, Altimeter, Lightspeed, Alpine Space Ventures
- 고객 계약: **$500M+** 체결 (상업+미 정부)

**GRAVITAS 위성**:
- K2 최초 Mega Class 위성
- **2026.03 발사** 예정
- Falcon 9, Vulcan, Ariane 6 호환
- 동급 위성 대비 **~10배 전력** 출력
- 멀티 궤도(LEO, MEO, GEO) 운용 가능

**궤도 DC와의 관계**: 직접 DC를 운영하는 게 아니라, 궤도 컴퓨팅에 필요한 **고출력 위성 버스 플랫폼** 제공

**출처**: [PRNewswire - K2 Space $250M](https://www.prnewswire.com/news-releases/k2-space-raises-250m-at-3b-valuation-to-roll-out-a-new-class-of-high-capability-satellites-302638936.html), [SpaceNews - K2 $250M](https://spacenews.com/k2-space-raises-250-million-to-scale-high-power-satellite-line/)

### 2-9. Lonestar Data Holdings — 달 데이터센터

**개요**: 달 궤도/표면에 데이터 재해복구(DR) 센터 구축 목표

**펀딩**:
- 2023: $5M 시드 + $825K Pre-Series A
- 2026.01: **$6.6M** 추가 (Atypical Ventures, The Veteran Fund 리드)

**성과 (2025)**:
- "Freedom" 데이터센터 페이로드가 Intuitive Machines Athena 달 착륙선에 탑재
- **30만 km 이동**, 달 궤도 도달 — 상업 달 DC 최초 운용 테스트 성공

**향후**:
- Sidus Space와 **$120M** 확대 계약: 달 데이터 저장 위성 6기 설계·페이로드 통합·발사·궤도 지원

**포지션**: 연산보다 **데이터 저장/재해복구** 초점. 궤도 DC와는 다른 접근

**출처**: [DCD - Lonestar $6.6M](https://www.datacenterdynamics.com/en/news/lunar-data-center-firm-lonestar-data-raises-66m-swaps-ceo/), [DCF - Lonestar IM-1](https://www.datacenterfrontier.com/edge-computing/article/33037610/lonestar-data-makes-it-to-the-moon-on-im-1-lunar-lander), [Sidus Space - $120M Agreement](https://investors.sidusspace.com/news-events/press-releases/detail/240/sidus-space-advances-120m-agreement-with-lonestar-selects)

### 2-10. SpaceX — 100만 위성 궤도 DC

**FCC 신청 (2026.01.30)**:
- **최대 100만 기** 위성으로 분산 컴퓨팅 노드 구성
- 궤도: 500~2,000 km 다중 셸
- "고대역 광학 링크" 활용
- 연산 밀도: 미터 톤당 **~100 kW** 컴퓨팅
- 트래픽: Starlink 네트워크 통해 인가 지상국으로 전송
- 최적화 대상: **대규모 AI 추론**

**FCC 일정**:
- 의견 접수: ~2026.03.06
- 응답: ~2026.03.16
- 재응답: ~2026.03.23

**반응 & 논쟁**:
- Harvard 천체물리학자 Jonathan McDowell: "100만 위성은 천문학에 큰 도전. 더 높은 궤도는 더 나쁘다"
- DarkSky International: FCC에 공식 이의 제기 촉구
- 능동 위성 수 **~70배** 증가 우려

**출처**: [GeekWire - SpaceX FCC 1M](https://www.geekwire.com/2026/spacex-fcc-million-data-center-satellites/), [SpaceNews - SpaceX 1M constellation](https://spacenews.com/spacex-files-plans-for-million-satellite-orbital-data-center-constellation/), [The Register - FCC opens for comment](https://www.theregister.com/2026/02/05/spacex_1m_satellite_datacenter/), [Fortune - SpaceX FCC](https://fortune.com/2026/02/01/spacex-fcc-approval-filing-data-center-constellation-space-construction-ai/)

---

## 3. 우주 냉각의 물리학 — 상세 공학

### 3-1. 복사 냉각의 원리 — Stefan-Boltzmann 법칙

**기본 공식**: P = εσAT⁴

- P: 방출 전력 (W)
- ε: 방사율 (0~1, 이상적 흑체 = 1)
- σ: Stefan-Boltzmann 상수 = 5.67 × 10⁻⁸ W/m²K⁴
- A: 방사 면적 (m²)
- T: 절대 온도 (K)

**이론적 계산 (이상적 흑체)**:
- T = 350 K (77°C, 서버 운영 온도) → σT⁴ ≈ **850 W/m²**
- T = 320 K (47°C) → σT⁴ ≈ **595 W/m²**
- T = 400 K (127°C) → σT⁴ ≈ **1,452 W/m²**

**1 MW 방열에 필요한 이론적 면적**:
- 350 K 기준: 1,000,000 / 850 ≈ **1,176 m²** (이상적)
- 320 K 기준: 1,000,000 / 595 ≈ **1,681 m²** (이상적)

### 3-2. 이론 vs 현실 — 실제 방열판 설계

**현실적 성능 저하 요인**:
1. **방사율 (ε)**: 실제 재질 ε ≈ 0.8~0.9 (흑체 아님)
2. **시야 인자 (View Factor)**: 패널이 지구, 다른 위성, 태양에 노출 → 열 흡수
3. **태양 입사**: 일조 궤도에서 패널 한 면이 태양열 흡수
4. **운영 온도 제한**: GPU → 냉매 → 방열판 각 단계 온도 구배

**실제 우주 방열판 성능** (~300 K 기준):
- 실제 방열: **100~350 W/m²**
- → 1 kW 방열에 **1~3 m²** 필요
- → 1 MW 방열에 **1,000~3,000 m²** 필요
- → 1 GW 방열에 **1~3 백만 m²** 필요

**2 MW 시설 구체 계산** (320 K, 비이상적 조건):
- 필요 방열판: **~3,950 m²**
- 방열판 질량 (5~10 kg/m²): **19,750~39,500 kg**
- → 컴퓨팅 장비 자체 질량 초과 가능

### 3-3. ISS 열관리 시스템 — 레퍼런스

**ISS External Active Thermal Control System (EATCS)**:

| 항목 | 사양 |
|------|------|
| 방열 용량 | **70 kW** |
| 방열판 수 | 6개 배치 어레이 |
| 패널 크기 | 3.33 m × 2.64 m (패널당) |
| 패널 구성 | 어레이당 8개 패널 |
| 냉매 | 암모니아 단상 유체 루프 2개 |
| 배관 재질 | Inconel 718 (암모니아 동결/해동 압력 내성, 부식 내성) |
| 배관 구조 | 22개 병렬 유량관 + 2 공급/2 반환 매니폴드 (이중 독립 경로) |

**비교 시사점**:
- ISS는 겨우 **70 kW** 방열에 대규모 인프라 필요
- 궤도 DC 1 MW = ISS의 **~14배**
- 궤도 DC 100 MW = ISS의 **~1,430배**

**출처**: [Wikipedia - External Active Thermal Control System](https://en.wikipedia.org/wiki/External_Active_Thermal_Control_System), [NASA - ATCS Overview (PDF)](https://www.nasa.gov/wp-content/uploads/2021/02/473486main_iss_atcs_overview.pdf), [NSS - Thermal Management in Space](https://www.nss.org/settlement/nasa/spaceresvol2/thermalmanagement.html)

### 3-4. PUE (Power Usage Effectiveness) 비교

| 시설 유형 | PUE | 의미 |
|-----------|-----|------|
| 업계 평균 | **1.56** | 1W 연산에 0.56W 오버헤드 |
| Google (2024 플릿 평균) | **1.09** | 업계 최고 수준 |
| Google (2025 Q1 분기) | **1.08** | — |
| AWS (2024 글로벌) | **1.15** | — |
| AWS (유럽 최적 사이트) | **1.04** | — |
| Meta (2024) | **1.08** | — |
| Microsoft (2024) | **1.16** | — |
| Equinix (2024) | **1.39** | 코로케이션 |
| 하이퍼스케일 범위 | 1.09~1.20 | — |
| 엔터프라이즈 범위 | 1.5~1.8 | — |
| 코로케이션 범위 | 1.3~1.6 | — |
| 엣지 컴퓨팅 | 1.5~2.0 | — |
| **이론적 궤도 DC** | **~1.0** | 냉각에 에너지 안 씀 (태양광 직접) |

**냉각이 차지하는 에너지 비율**:
- 냉각: 총 DC 에너지의 **30~40%** (37% 중앙값)
- IT 장비: **40~60%**
- PUE 1.56 = 냉각+기타 오버헤드가 IT 부하의 56%

**아티클 포인트**: 궤도 DC는 PUE **~1.0** 달성 가능. 지구 최고 수준(Google 1.08)보다도 낮다. 냉각에 0 에너지 사용.

**출처**: [Google Data Centers - PUE](https://datacenters.google/efficiency/), [Statista - Global PUE](https://www.statista.com/statistics/1229367/data-center-average-annual-pue-worldwide/), [AIRSYS - DC Energy Efficiency](https://airsysnorthamerica.com/data-center-energy-efficiency-which-metrics-matter-most/)

### 3-5. 태양광 에너지 이점

| 항목 | 지구 표면 | 궤도 (LEO SSO) |
|------|-----------|---------------|
| 태양 복사 조도 | ~1,000 W/m² (최대, 맑은 날) | **1,366 W/m²** |
| 용량 인자 | ~15~25% (밤, 날씨, 계절) | **>95%** |
| 연간 에너지 비 | 1x | **8~13x** |
| 밤/날씨 영향 | 있음 | **없음** (SSO "터미네이터" 궤도) |

- NASA/JAXA 연구: 궤도 태양광 설비는 지상 동일 설비 대비 **연간 13배** 이상 에너지 생산 가능
- 태양 동기 궤도(SSO) "터미네이터" 궤도: 연 **99%** 일조 시간

**출처**: [SatNews - Orbital vs Terrestrial Solar](https://news.satnews.com/2026/02/01/orbital-vs-terrestrial-solar-the-math-of-energy-density-and-capacity-factors/), [Wikipedia - Space-based solar power](https://en.wikipedia.org/wiki/Space-based_solar_power)

---

## 4. Starlink 기술 상세 — 궤도 DC 백본

### 4-1. 컨스텔레이션 규모 (2026.01 기준)

| 항목 | 수치 |
|------|------|
| 총 위성 수 | **9,422+기** |
| 레이저 ISL 탑재 | **9,000+기** |
| 레이저 수 (위성당) | **3기** |
| 총 우주 레이저 수 | **~27,000개** |

### 4-2. 레이저 ISL 대역폭

| 사양 | 수치 |
|------|------|
| 레이저당 최대 속도 | **~200 Gbps** |
| 일일 전송량 | **42 PB/일** (42,000,000 GB) |
| 총 ISL 처리량 | **5.6 Tbps** |
| "미니 레이저" (3rd party용) | **25 Gbps** (최대 4,000 km) |

### 4-3. 네트워크 총 용량

| 항목 | 수치 |
|------|------|
| 현재 총 용량 (2025 중반) | **~450 Tbps** |
| 2025년 추가 용량 | +270 Tbps (V2 Mini 3,000+기 배치) |

### 4-4. V3 위성 사양 (2026년 상반기 발사 예정)

| 항목 | V2 Mini | V3 |
|------|---------|-----|
| 다운링크 | ~100 Gbps | **1 Tbps** (10배) |
| 업링크 | ~6 Gbps | **200 Gbps** |
| Starship 발사당 | — | **~60기, ~60 Tbps 추가** |
| 궤도 고도 | — | 더 낮음 (지연 시간 단축) |

### 4-5. 레이턴시 비교 — 장거리 경로

**물리적 이점**: 진공에서 빛 = c. 광섬유에서 빛 = **~0.66c** (30% 느림)

| 경로 | 광섬유 (해저 케이블) | Starlink 레이저 (이론) | 절감 |
|------|---------------------|----------------------|------|
| 뉴욕-런던 | ~65 ms | ~40 ms | **~38%** |
| 일반 장거리 | — | — | **최대 50%** |
| 일반 사용자 (단거리) | 1~5 ms | 20~40 ms | 열위 |

**핵심 인사이트**:
- 단거리: 광섬유가 압도적 우위 (업/다운링크 hop 때문)
- **장거리 (대륙 간)**: Starlink 레이저가 더 빠를 수 있음 — 직선 경로 + 진공 광속
- 궤도 DC 사이의 통신: 지상 경유 없이 **엔드-투-엔드 우주 레이저** → 극도로 낮은 레이턴시

**궤도 DC 백본으로서의 Starlink**:
- 궤도 DC에서 생성된 데이터는 **Starlink ISL 메쉬** 통해 직접 라우팅 가능
- 지상 사용자 → 가장 가까운 Starlink 위성 → ISL → 궤도 DC → 응답
- SpaceX FCC 신청서에도 "Starlink 네트워크 통해 인가 지상국으로 트래픽 전송" 명시

**출처**: [Hackaday - 42M GB/day](https://hackaday.com/2024/02/05/starlinks-inter-satellite-laser-links-are-setting-new-record-with-42-million-gb-per-day/), [DCD - SpaceX mini laser](https://www.datacenterdynamics.com/en/news/spacex-developing-laser-to-connect-starlink-satellites-with-third-party-satellites/), [DCD - Starlink V3 terabit](https://www.datacenterdynamics.com/en/news/starlink-targets-2026-for-terabit-satellites-for-launch-with-starship/), [DISHYtech - Starlink 2025](https://www.dishytech.com/starlink-just-had-a-massive-2025-and-2026-could-be-even-bigger/)

---

## 5. 시장 규모 & 투자 테제

### 5-1. 글로벌 데이터센터 시장

| 연도 | 시장 규모 | CAGR | 출처 |
|------|----------|------|------|
| 2024 | **$347~379B** | — | Fortune BI, Arizton |
| 2025E | **$386~418B** | — | — |
| 2030E | **$627~692B** | 8.7~11.2% | 다수 리서치 기관 |

**출처**: [Fortune BI - DC Market](https://www.fortunebusinessinsights.com/data-center-market-109851), [Arizton - DC Market 2030](https://www.arizton.com/market-reports/data-center-market-investment-forecast), [BCC Research - DC Market](https://www.bccresearch.com/market-research/information-technology/data-centre-market.html)

### 5-2. 클라우드 컴퓨팅 시장

| 기업 | Q2 2025 분기 매출 | 연간 런레이트 | YoY 성장 |
|------|------------------|-------------|---------|
| AWS | $30.9B | **$124B** | +17% |
| Microsoft Intelligent Cloud | $29.9B | **$120B** | +26% |
| Google Cloud | $13.6B | **$54B** | +32% |
| **3사 합계 (IaaS/PaaS)** | — | **~$259B** | +26% |

- 2025 예상: AWS $126.6B, Azure $87.7B, GCP $28.3B

**출처**: [Holori - Cloud Market 2024](https://holori.com/cloud-market-share-2024-aws-azure-gcp/), [SiliconANGLE - Cloud Quarterly](https://siliconangle.com/2025/08/09/cloud-quarterly-azure-ai-pop-aws-supply-pinch-google-execution/), [CloudWards - Q2 2025](https://www.cloudwards.net/news/aws-azure-and-google-cloud-lead-q2-2025-cloud-market-earnings/)

### 5-3. 냉각/전력이 차지하는 비용 비중

| 항목 | 비중 |
|------|------|
| 냉각 | **30~40%** (중앙값 37%) |
| IT 장비 (서버/스토리지) | 40~60% (중앙값 42%) |
| 나머지 (조명, 보안 등) | ~20% |

- 글로벌 DC 인프라 지출 (2024): **~$290B**
- 2025년: **$400B+** (+40%)
- 냉각 관련 비용만: 연 $290B × 37% ≈ **$107B** (2024)

### 5-4. TAM 시나리오 — 우주 DC가 1% 점유 시

| 시나리오 | 시장 기준 | 1% 점유 |
|----------|----------|---------|
| 2024 DC 시장 | $370B | **$3.7B** |
| 2030 DC 시장 | $660B | **$6.6B** |
| 2030 클라우드 시장 (3사) | ~$500B+ | **$5.0B+** |
| 냉각/전력 비용만 (2024) | $107B | **$1.07B** |
| 냉각/전력 비용만 (2030) | ~$200B+ | **$2.0B+** |

### 5-5. 우주 컴퓨팅 VC/기관 투자 (2024~2026)

| 기업/프로젝트 | 투자 규모 | 시기 |
|--------------|----------|------|
| **K2 Space** Series C | **$250M** ($3B 밸류) | 2025.12 |
| **Loft Orbital** Series C | **$170M** | 2025.01 |
| **Starcloud** 누적 시드 | $21M | 2024~2025 |
| **Aethero** 시드 | $8.4M | 2025.06 |
| **Lonestar** 누적 | ~$12.4M | 2023~2026 |
| Google **Project Suncatcher** | 내부 R&D (규모 미공개) | 2025.11 |
| **SpaceX + xAI** 합병 | **$1.25T 밸류** | 2026.02 |
| 4iG → Axiom Space | **$100M** 검토 | 2025~2026 |
| Sidus Space + Lonestar | **$120M** 계약 | 2025 |
| **우주 컴퓨팅 VC 총 투자** (2023~) | **$1.2B+** | 다수 |

**트렌드 변화**:
- 2021~2024: 소규모 투기적 투자 (Lumen Orbit $2.4M pre-seed 등)
- 2025+: **대규모 통합 시스템 투자** (K2 $250M, Google Suncatcher, SpaceX 1M 위성)

**출처**: [EnkiAI - Orbital DCs 2026 Capital](https://enkiai.com/ai-market-intelligence/orbital-data-centers-2026-capital-shifts-to-infrastructure), [EnkiAI - Rush to Space](https://enkiai.com/ai-market-intelligence/orbital-data-centers-2026-the-rush-to-space-for-ai)

---

## 6. xAI + SpaceX 합병 — 궤도 DC 시사점

### 6-1. 딜 구조

| 항목 | 내용 |
|------|------|
| 발표일 | 2026.02.02 |
| 구조 | SpaceX가 xAI 인수 (합병) |
| SpaceX 밸류 | $1T |
| xAI 밸류 | $250B |
| 합산 밸류 | **$1.25T** — 역대 최대 합병 |
| xAI 포함 자산 | xAI (Grok AI) + X (구 Twitter) |

### 6-2. 전략적 근거

머스크 발언: "내 추정으로, 2~3년 안에 AI 연산의 **최저비용** 방식은 우주가 될 것"

**수직통합 시너지**:
- **연산**: xAI (Grok AI, 멤피스 슈퍼클러스터)
- **수송**: SpaceX (Falcon 9, Starship)
- **통신**: Starlink (9,000+기, 레이저 ISL)
- **전력**: 우주 태양광 (24/7, 8~13x 효율)
- **발사**: FCC 100만 위성 신청 — "분산 처리 노드" 명시

### 6-3. IPO와 궤도 DC

- SpaceX CFO Bret Johnsen: **2026년 IPO** 타겟
- 예상 밸류에이션: 최대 **$1.5T**
- IPO 수익금: 궤도 DC 개발에 사용 예정

### 6-4. 회의론

- CNBC (2026.02.02): "xAI는 SpaceX의 자금에 더 절실. 궤도 DC는 아직 꿈"
- 분석가: "실질적 진전까지 수년 소요"
- Via Satellite: 기회와 리스크 병존

**출처**: [SpaceNews - SpaceX acquires xAI](https://spacenews.com/spacex-acquires-xai-in-bid-to-develop-orbital-data-centers/), [CNBC - xAI needs SpaceX for money](https://www.cnbc.com/2026/02/02/musks-xai-needs-spacex-for-money-data-centers-in-space-are-a-dream.html), [CNBC - $1.25T merger](https://www.cnbc.com/2026/02/03/musk-xai-spacex-biggest-merger-ever.html), [TechCrunch - SpaceX acquires xAI](https://techcrunch.com/2026/02/02/elon-musk-spacex-acquires-xai-data-centers-space-merger/), [Via Satellite - Opportunities and Risks](https://www.satellitetoday.com/finance/2026/02/18/the-opportunities-and-risks-of-spacexs-xai-deal-and-data-center-in-space-ambitions/)

---

## 7. 반론 & 리스크

### 7-1. 대역폭 병목 — 학습 데이터 업로드

**문제의 규모**:
- GPT-4 분산 학습: 25,000 GPU, **시간당 400 TB** 네트워크 트래픽 발생
- All-reduce 통신이 분산 학습 대역폭의 **89%** 소비
- 현대 AI 학습 클러스터: 노드간 **800 Gbps~1.6 Tbps** 연결 필요
- 레이턴시 임계: 밀리초가 아닌 **나노초** 수준

**Starlink 업링크 한계**:
- 현재 총 용량: ~450 Tbps (다운+업 합산)
- 업링크/다운링크 비율: **25/75** (업링크 = 총 용량의 1/4)
- V3 위성 업링크: 200 Gbps/기 (개선되었으나 여전히 분산 학습 요건 미충족)

**현실적 대안 — 타협 모델**:
1. 학습은 지상, **추론만 궤도** (데이터 전송량 극소)
2. 시간 비민감 학습: 데이터를 **배치로 사전 업로드** 후 궤도에서 학습 (Starcloud 접근)
3. 궤도 위성 간 학습: 데이터를 한 번 올리면 **ISL로 GPU 간 통신** (SpaceX 1M 위성 구상)

### 7-2. 방사선 — GPU/메모리 손상

**방사선 유형 & 영향**:

| 유형 | 메커니즘 | 피해 |
|------|---------|------|
| **SEU (Single Event Upset)** | 하전 입자가 트랜지스터 관통 → 전류 펄스 (~600 ps) → 비트 플립 | 데이터 오류 (비파괴적) |
| **SEL (Single Event Latch-up)** | CMOS 기생 바이폴라 트랜지스터 형성 → 전원-접지 저저항 경로 | **영구 손상** 가능 |
| **TID (Total Ionizing Dose)** | 누적 방사선 → 트랜지스터 특성 변화 | 장기 성능 저하 |

**NVIDIA H100 취약성**:
- **방사선 경화(Rad-Hard)가 아님**
- 4nm 제조 공정 → 극도로 미세한 트랜지스터 → 방사선에 **더 취약**
- 큰 실리콘 다이 면적 → 방사선 충돌 빈도 면적에 비례하여 증가

**LEO 환경**:
- 지구 자기권 내부 (GEO보다 양호)
- **남대서양 이상대(SAA)**: 방 앨런 벨트가 지구에 근접 → 위성이 통과 시 SEU 급증
- Google TPU v6e: LEO 5년 미션 방사선 수준 **견딤 확인** (방사선 테스트 완료)

**완화 전략**:
| 전략 | 설명 |
|------|------|
| ECC 메모리 | DRAM 비트 플립 감지/정정 |
| 체크포인트/재시작 | 학습 중 주기적 상태 저장 → SEU 시 롤백 |
| TMR (삼중 모듈 중복) | 3개 동일 연산 → 다수결 |
| 차폐 | 물리적 방사선 차단 (질량 증가 트레이드오프) |
| 워치독 시스템 | 이상 감지 → 자동 리셋 |

**아티클 포인트**: 방사선은 "새로운 물리학"이 필요한 문제가 아니다. ISS에서 수십 년간 컴퓨터 운용. 해결 가능한 공학 문제. Starcloud-1 H100이 궤도에서 정상 동작 중.

**출처**: [New Space Economy - H100 Radiation](https://newspaceeconomy.ca/2025/11/03/an-analysis-of-radiation-protection-in-the-nvidia-h100-gpu/), [Physics World - Cosmic challenge](https://physicsworld.com/a/cosmic-challenge-protecting-supercomputers-from-an-extraterrestrial-threat/), [Springer - Radiation tolerant GPU](https://link.springer.com/article/10.1007/s12567-020-00321-9), [Taranis - DCs in space terrible idea](https://taranis.ie/datacenters-in-space-are-a-terrible-horrible-no-good-idea/)

### 7-3. 유지보수 & 수리

**문제**:
- 고장 시 현장 수리 불가 (초기)
- 인간 개입 비용 극히 높음 (EVA = 수백만 달러)
- 위성 수명 한계 (Starcloud-1: 11개월)

**완화**:
- **모듈식 교체**: 고장 위성 → 재진입 → 새 위성 발사
- Starship $100/kg이면 교체 비용이 수리보다 경제적
- 소프트웨어 업데이트는 OTA로 가능
- 장기: 로봇 서비싱 (NASA OSAM-1 기술 등)

### 7-4. 실시간 애플리케이션 레이턴시

**경로 레이턴시 분해**:
1. 사용자 → 가장 가까운 Starlink 위성: ~5-10 ms (LEO 550 km)
2. Starlink ISL → 궤도 DC: 수 ms~수십 ms (hop 수에 따라)
3. 궤도 DC 처리: 수 ms
4. 역경로: 동일
5. **총 왕복**: 추정 **30~100 ms**

| 애플리케이션 | 요구 레이턴시 | 궤도 DC 가능? |
|-------------|-------------|-------------|
| HFT (초고빈도 거래) | <1 ms | **불가** |
| 실시간 게이밍 | <20 ms | **어려움** |
| 영상 통화 | <150 ms | **가능** |
| AI 추론 (챗봇 등) | <500 ms | **가능** |
| AI 학습 (배치) | 시간 무관 | **최적** |
| 배치 처리/렌더링 | 시간 무관 | **최적** |

**아티클 포인트**: 궤도 DC는 모든 워크로드를 대체하려는 게 아니다. 레이턴시 비민감 + 연산 집약 작업에 최적. AI 학습이 그 정의에 딱 맞는다.

### 7-5. 데이터 주권 & 규제

**우주조약 (1967년, Outer Space Treaty)**:
- 어떤 국가도 우주 공간에 대한 **주권을 주장할 수 없다**
- 그러나: 우주 물체가 등록된 국가가 해당 물체에 대한 **관할권과 통제권** 보유
- 주권(sovereignty) ≠ 관할권(jurisdiction)

**데이터 주권 문제**:
- EU GDPR: 개인 데이터가 EU 역외로 전송될 때 규제
- 중국 데이터 보안법: 핵심 데이터의 역외 이전 제한
- 궤도의 데이터센터는 **어느 나라에 "위치"** 하는가?
- 위성이 여러 국가 상공을 지나감 → 데이터가 어느 관할권에?

**현재 법적 프레임워크**:
- 등록국의 법이 적용 (우주조약 제8조)
- 미국 등록 위성 → 미국법 적용
- 그러나: 데이터가 **물리적으로 어디에 있는가**에 대한 국제적 합의 부재
- 새로운 법적 프레임워크 필요

**출처**: [UNOOSA - Outer Space Treaty](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html), [Columbia STLR - Space Data](https://journals.library.columbia.edu/index.php/stlr/blog/view/302)

### 7-6. 우주 잔해 (Space Debris)

**현 상황 (ESA 2025 보고서)**:
- LEO 인공 물체: **11,800+기** (대부분 Starlink)
- 400~1,000 km 모든 고도에서 불안정 임계점 초과
- 520~1,000 km에서 대부분 **폭주 임계점** 초과
- 추가 발사 없이도 잔해 수 자연 증가 중

**충돌 회피**:
- ISS: 2024.11에 6일 내 2회 회피 기동 실시
- 매년 충돌 회피 절차 증가 중

**100만 위성 추가 시**:
- 능동 위성 수 **~70배** 증가
- 천문학 관측 심각한 영향
- 케슬러 증후군 가속 우려

**출처**: [ESA - Space Environment Report 2025](https://www.esa.int/Space_Safety/Space_Debris/ESA_Space_Environment_Report_2025), [The Conversation - Google Suncatcher debris](https://theconversation.com/googles-proposed-data-center-in-orbit-will-face-issues-with-space-debris-in-an-already-crowded-orbit-270410)

---

## 8. 아티클 핵심 수치 정리 (업데이트)

| 수치 | 값 | 출처 |
|------|-----|------|
| 글로벌 DC 전력 (2024) | 415 TWh | IEA |
| 글로벌 DC 전력 (2030E) | 945 TWh (2배) | IEA |
| AI DC 전력 비중 (2026E) | 40%+ | Goldman Sachs |
| DC 냉각 에너지 비중 | 30~40% (37% 중앙값) | 다수 |
| Google PUE (최고) | 1.08 | Google DC |
| 궤도 DC PUE (이론) | ~1.0 | 물리학 |
| 태양 복사 조도 (궤도) | 1,366 W/m² | NASA |
| 궤도 태양광 vs 지상 | 8~13배 | NASA/JAXA |
| 하이퍼스케일러 CapEx (2025) | $350B | 다수 |
| 하이퍼스케일러 CapEx (2026E) | $600B+ | Introl |
| MS+Constellation 원전 | 835 MW, $1.6B | DCF |
| Starlink 위성 수 | 9,422+기 | SpaceX |
| Starlink 레이저 ISL 수 | 9,000+기 | SpaceX |
| Starlink 일일 전송량 | 42 PB/일 | SpaceX |
| Starlink 총 용량 | ~450 Tbps | 다수 |
| V3 위성 다운링크 | 1 Tbps/기 | SpaceX |
| 뉴욕-런던 Starlink vs 광섬유 | 40ms vs 65ms (~38% 절감) | 다수 |
| SpaceX FCC 1M 위성 신청 | 2026.01.30 | FCC |
| SpaceX+xAI 합병 밸류 | $1.25T | CNBC |
| Starcloud 우주 첫 H100 | 2025.11 | CNBC/NVIDIA |
| Starcloud 우주 첫 LLM 학습 | 2025.12 | CNBC |
| Google Suncatcher 발사 | 2027 초 | Google |
| Axiom ODC 노드 1&2 | 2026.01.11 발사 | Axiom |
| K2 Space 밸류 | $3B ($250M Series C) | PRNewswire |
| 글로벌 DC 시장 (2024) | $347~379B | 다수 |
| 글로벌 DC 시장 (2030E) | $627~692B | 다수 |
| 우주 컴퓨팅 VC 투자 (2023~) | $1.2B+ | EnkiAI |
| 아일랜드 DC 전력 비중 | 22% (2024) | 아일랜드 정부 |

---

## 9. 비판적 분석 소스 (균형을 위해)

| 소스 | 핵심 주장 | URL |
|------|----------|-----|
| Taranis.ie | "우주 DC는 끔찍하고 나쁜 아이디어" — 방열, 방사선, 대역폭 문제 | [Link](https://taranis.ie/datacenters-in-space-are-a-terrible-horrible-no-good-idea/) |
| Pivot to AI | "왜 우주 DC가 작동하지 않는가" | [Link](https://pivot-to-ai.com/2025/12/01/ai-data-centres-in-space-why-dcs-in-space-cant-work/) |
| Chaotropy | "Jeff Bezos가 틀린 이유" | [Link](https://www.chaotropy.com/why-jeff-bezos-is-probably-wrong-predicting-ai-data-centers-in-space/) |
| Aravolta | "우주 DC의 진짜 제약" | [Link](https://www.aravolta.com/blog/datacenters-in-space) |
| Marc Bara (Medium) | "궤도 DC: 비싼 제안의 기술 분석" | [Link](https://medium.com/@marc.bara.iniesta/orbital-data-centers-a-technical-analysis-of-an-expensive-proposition-1006ff9733d1) |
| TechCrunch | "궤도 AI의 경제학이 잔인한 이유" | [Link](https://techcrunch.com/2026/02/11/why-the-economics-of-orbital-ai-are-so-brutal/) |
| CNBC | "xAI는 SpaceX의 돈이 필요. 우주 DC는 아직 꿈" | [Link](https://www.cnbc.com/2026/02/02/musks-xai-needs-spacex-for-money-data-centers-in-space-are-a-dream.html) |
| Angadh Nanjangud | "Starcloud가 $8.2M으로 Starship에 DC를 넣는 건 불가능" | [Link](https://angadh.com/space-data-centers-1) |

---
