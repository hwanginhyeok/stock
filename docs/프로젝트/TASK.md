# TASK 관리 v2.0

> **규칙**: 작업 흐름 속에서 실시간으로 갱신한다.
> 번호 체계: `{분야코드}-{순번}` — 1=시스템, 2=코드, 3=분석, 4=아티클, 5=리서치
> 상태: `예정` → `요청` → `진행` → `완료`

---

## 🔥 현재 진행 중

| # | 분야 | 작업 | 담당 | 진행 상황 | 다음 할 일 |
|---|------|------|------|-----------|------------|
| 4-3 | 아티클 | 블록체인 생태계 #1: 비트코인 편 | 사용자 + AI | Phase 1 완료 (역사 raw 노트, 테제 확정) | 아웃라인 → 롱폼 초안 |
| 4-4 | 아티클 | 블록체인 생태계 #2: 이더리움 편 | 사용자 + AI | Phase 1 완료 (역사 raw 노트, 테제 확정) | 아웃라인 → 롱폼 초안 |
| 4-5 | 아티클 | 팔란티어 심층분석 시리즈 (6편) | 사용자 + AI | 전 편 초안 완료 + 도입편 시각화 3개 완료 + 게시 스케줄 확정 (PUBLISH_SCHEDULE.md) | 도입편 최종 퇴고 → 3/11 X 게시 |
| 4-6 | 아티클 | 블록체인 생태계 #3: BMNR — ETH 트레저리 편 | 사용자 + AI | Phase 1 완료 (심층 리서치 완료) | 테제 확정 → 아웃라인 → 롱폼 초안 |
| 4-7 | 아티클 | 블록체인 생태계 #4: CRCL — USDC 디지털달러 편 | 사용자 + AI | Phase 1 완료 (심층 리서치 완료) | 테제 확정 → 아웃라인 → 롱폼 초안 |
| 4-15 | 아티클 | HOOD — Robinhood 리테일 관문 편 | 사용자 + AI | Phase 1 리서치 진행 중 | 리서치 완료 → 테제 확정 → 아웃라인 |
| 4-11 | 아티클 | KR-03~06: 현대차 시리즈 (4편, 재구성) | 사용자 + AI | 1편·2편 게시 완료 (2026-03-29) | 3편 리서치 보강 → v1 초안 |
| 4-12 | 아티클 | KR-07: 곱셈이 사라진다 — 1, 0, -1과 반도체의 미래 | 사용자 + AI | 리서치 완료 (15개 기술 + BitNet-삼성3진법 연결) | **사용자 구조안 확정** → 아웃라인 → 초안 |
| 4-16 | 아티클 | 026 TeraFab의 시작 — 팹을 가장 빨리 짓는 법 | 사용자 + AI | v1 초안 완료 (271줄, Samsung 브릿지 반영) | 퇴고 → v2 → 시각화 → 게시 |
| 4-17 | 아티클 | 027 파운드리의 역설 — 애플이 가장 잘 만드는 회사가 될 수 없는 이유 | 사용자 + AI | 아웃라인 제안 완료, 승인 대기 | 아웃라인 확정 → v1 초안 |
| 4-18 | 아티클 | 테슬라·xAI·SpaceX의 테라팹 — 일론 머스크 생태계와 제조 혁신 | 사용자 + AI | 예정 | 리서치 → 테제 확정 → 아웃라인 → 초안 |
| 4-13 | 아티클 | 일론머스크 생태계 카드뉴스 | 사용자 + AI | 기획 단계 | 콘셉트·포맷·범위 확정 → 리서치 → 제작 |
| 4-14 | 아티클 | 일론머스크 생태계 상상콘텐츠 (웹 룰렛) | 사용자 | 요구사항 문서 완료 (`task/4-14_elon_ecosystem_roulette.md`) → 별도 프로젝트에서 구현 중 | 웹앱 구현 → 호스팅 → X 공유 |
| 3-1 | 분석 | 지표 장단점·맹점 분석 + 해석 체계 고도화 | 사용자 + AI | Q6 완료, 해석 원칙 8개 정립 | Tech Score 역발상 편향 개선/해석 방향 논의 |

### 4-3 블록체인 생태계 #1: 비트코인 편

**테제**: 비트코인은 목적(P2P 현금)과 현실(디지털 금)이 반대로 수렴한 자산. 이 역설 안에 가치가 있다.
**비유**: 금:구리 = 비트코인:이더리움 (쓰지 않아서 가치 있는 것 vs 써야 가치 있는 것)
**타겟**: 한국인 미국주식/코인 투자자 | **플랫폼**: X 아티클(롱폼), 인스타 카드뉴스

#### Phase 1: 리서치 ✅ 완료
- [x] `raw/01_bitcoin_history.md` — 역사 타임라인 (2008~2025)
- [x] `drafts/thesis.md` — 테제 확정

#### Phase 2: 검증 / Phase 3: 아웃라인 / Phase 4: 초안
- [ ] `verified/claims.md` — 핵심 주장 검증
- [ ] `drafts/outline.md` — 아웃라인
- [ ] `drafts/x_article_v1.md` — X 롱폼 초안

**관련 파일**: `data/research/articles/003_bitcoin-history/`, `data/articles/002_BTC_블록체인-생태계-비트코인편/`

---

### 4-4 블록체인 생태계 #2: 이더리움 편

**테제**: 이더리움은 계속 변하는 것이 가치인 자산. The Merge는 그 철학의 극적 증명이다.
**비유**: 인터넷:웹사이트 = 이더리움:DApp (플랫폼의 가치는 위에서 돌아가는 것들의 합)
**타겟**: 한국인 미국주식/코인 투자자 | **플랫폼**: X 아티클(롱폼), 인스타 카드뉴스

#### Phase 1: 리서치 ✅ 완료
- [x] `raw/02_ethereum_history.md` — 역사 타임라인 (2013~2025)
- [x] `drafts/thesis.md` — 테제 확정

#### Phase 2: 검증 / Phase 3: 아웃라인 / Phase 4: 초안
- [ ] `verified/claims.md` — 핵심 주장 검증
- [ ] `drafts/outline.md` — 아웃라인
- [ ] `drafts/x_article_v1.md` — X 롱폼 초안

**관련 파일**: `data/research/articles/004_ethereum-history/`, `data/articles/003_ETH_블록체인-생태계-이더리움편/`

---

### 4-6 블록체인 생태계 #3: BMNR — ETH 트레저리 편

**테제 (초안)**: 월가의 큰손들이 ETH를 기업 트레저리에 쌓기 시작했다. Tom Lee의 5% 전략은 단순 코인 매수가 아니라 스테이킹 수익 + 기관 금융 통합이라는 새 비즈니스 모델을 만드는 시도다.
**비유 (초안)**: 마이크로스트래티지:BTC = BMNR:ETH (차이는 ETH가 '쓸 수 있다'는 것)
**타겟**: 한국인 미국주식/코인 투자자 (BMNR 주주의 ~10%가 한국인) | **플랫폼**: X 아티클(롱폼), 인스타 카드뉴스

#### Phase 1: 리서치 ✅ 완료
- [x] `raw/03_bmnr_bitmine.md` — Tom Lee 비전, ETH 매입 타임라인, 주주총회 상세, 투자자 구성, MAVAN 수익 시나리오

#### Phase 2: 테제 확정 / Phase 3: 아웃라인 / Phase 4: 초안
- [ ] `drafts/thesis.md` — 테제 확정
- [ ] `verified/claims.md` — 핵심 주장 검증 (ETH 보유량, 스테이킹 수익, 투자자 지분)
- [ ] `drafts/outline.md` — 아웃라인
- [ ] `drafts/x_article_v1.md` — X 롱폼 초안

**관련 파일**: `data/research/articles/005_blockchain-players/raw/03_bmnr_bitmine.md`, `data/articles/004_BMNR_블록체인-생태계-ETH트레저리편/` (미생성)

---

### 4-7 블록체인 생태계 #4: CRCL — USDC 디지털달러 편

**테제 (초안)**: Circle은 "달러를 인터넷 위에 올려놓는" 회사다. USDC는 DeFi의 피가 됐고, Arc 블록체인은 기관 금융의 결제 레이어가 되려 한다. 탈중앙화 생태계의 핵심이 가장 중앙화된 달러라는 역설.
**비유 (초안)**: USDC는 PayPal이 아니라 달러 자체를 블록체인에 이식한 것
**타겟**: 블록체인/핀테크/달러 패권에 관심 있는 투자자 | **플랫폼**: X 아티클(롱폼), 인스타 카드뉴스

#### Phase 1: 리서치 ✅ 완료
- [x] `raw/02_circle.md` — 기본 역사, USDC 타임라인, 수익 구조
- [x] `raw/04_crcl_circle_updated.md` — 창업 스토리, SVB 사태 재구성, Coinbase 수익 배분 구조, Arc 블록체인, GENIUS Act

#### Phase 2: 테제 확정 / Phase 3: 아웃라인 / Phase 4: 초안
- [ ] `drafts/thesis.md` — 테제 확정
- [ ] `verified/claims.md` — 핵심 주장 검증 (USDC 시총, 수익 구조, SVB 디페그 수치)
- [ ] `drafts/outline.md` — 아웃라인
- [ ] `drafts/x_article_v1.md` — X 롱폼 초안

**관련 파일**: `data/research/articles/005_blockchain-players/raw/04_crcl_circle_updated.md`, `data/articles/005_CRCL_블록체인-생태계-USDC편/` (미생성)

---

### 4-2 상세 체크리스트

**테제**: 스마트폰→자동차→로봇→우주, 제품이 복잡해질수록 SW+HW 수직통합 기업(지배자)과 조립 기업(추격자)의 시총 격차가 벌어진다.

**타겟**: 한국인 미국주식 투자자 | **플랫폼**: X 아티클(롱폼), 인스타 카드뉴스

#### Phase 1: 리서치 ✅ 완료
- [x] 스마트폰 역사 (Apple/Samsung/Google 시총, 점유율, OS)
- [x] EV + NVIDIA (Tesla/Hyundai, DRIVE 채택, 자동차 매출)
- [x] 로봇 (Optimus/Atlas/Isaac, 배치 현황, TAM)
- [x] 제로 투 원 + 수직통합 프레임워크
- [x] 스마트폰 보급/거래 데이터 (출하량, ASP, 중고, 교체주기)
- [x] 자동차/EV 보급/거래 데이터 (판매, 중고차, EV 전환)
- [x] 로켓/우주 데이터 (발사 횟수, 비용, SpaceX, Starship)
- [x] 로봇 보급/트렌드 (밀도, 휴머노이드, 가격, 고용 대체)

#### Phase 2: 데이터 검증 ✅ 완료
- [x] 시가총액 최신화 (2026.02.25 CompaniesMarketCap 기준)
- [x] 테제 claim별 검증 (claims.md)
- [x] 반론/뉘앙스 정리

#### Phase 3: 초안 작성 — 진행 중
- [x] X 아티클 롱폼 v1 초안 (구조 확정)
- [ ] X 아티클 v2 (피드백 반영 수정)
- [ ] 인스타 카드뉴스 초안

#### Phase 4: 시각화 — 예정
- [ ] 히어로 테이블 (추격자/지배자/플랫폼 시총 비교)
- [ ] 시총 바 차트 (Apple vs Samsung vs Alphabet)
- [ ] Tesla 데이터 피드백 루프 플로우 차트
- [ ] 복잡도 스펙트럼 차트 (비용/거래량/배율 곡선)
- [ ] SpaceX 발사 비용 비교 바 차트
- [ ] 타임라인 (스마트폰→자동차→로봇→우주)

#### Phase 5: 최종 게시 — 예정
- [ ] X 아티클 최종본 확정
- [ ] 인스타 카드뉴스 최종본 확정
- [ ] 시각화 이미지 제작/삽입
- [ ] 면책조항 확인
- [ ] 출처 검증 최종 확인
- [ ] 게시

#### 리서치 파일 위치
```
data/research/articles/001_apple-samsung-google_tesla-hyundai-nvidia/
├── raw/
│   ├── 01_smartphone_history_research.md
│   ├── 02_ev_nvidia_research.md
│   ├── 03_robot_market_research.md
│   ├── 04_zero_to_one_vertical_integration.md
│   ├── 05_smartphone_volume_data.md
│   ├── 06_auto_ev_volume_data.md
│   ├── 07_rocket_space_data.md
│   └── 08_robot_deployment_data.md
├── verified/
│   └── claims.md (시가총액 검증 + claim별 판정)
├── visuals/ (예정)
└── drafts/
    ├── thesis.md (3중 패러렐 + 수직통합 테제)
    ├── x_thread_v1.md (구버전 — 스레드 형식)
    └── x_article_v1.md (현재 — 롱폼 아티클 v1, 구조 확정)
```

---

### 4-9 HIMS — 약은 누구나 팔 수 있다

**테제**: HIMS는 컴파운딩 약국이 아니라 의료 민주화 플랫폼이다. GLP-1은 관문이었을 뿐, 플랫폼이 본질이다.
**비유**: Amazon:책 = HIMS:GLP-1 (관문 상품으로 만든 플랫폼이 진짜 해자)
**타겟**: 한국인 미국주식 투자자 | **플랫폼**: X 아티클(롱폼) | **단독 아티클** (시리즈 아님)

#### Phase 1: 리서치 ✅ 완료
- [x] `data/research/stocks/hims/hims_comprehensive_research.md` — 회사 본질, 재무, 경쟁, 밸류에이션
- [x] `data/research/stocks/hims/glp1_global_landscape_research.md` — 글로벌 GLP-1 규제, 특허 만료, 각국 현황

#### Phase 2: 초안 ✅ 완료
- [x] `drafts/thesis.md` — 테제 확정
- [x] `drafts/outline.md` — 8섹션 아웃라인
- [x] `drafts/x_article_v1.md` — v1 초안

#### Phase 3: 퇴고 ✅ 완료
- [x] `drafts/review_v1.md` — 자가 퇴고 (11개 이슈, 8단계 우선순위)
- [x] `drafts/x_article_v2.md` — v2 (★★★ 위반사항 7건 수정)
- [x] 트럼프 섹션 수정 — TrumpRx.gov + MFN 행정명령 프레이밍
- [x] 📎 마커 5곳 배치 + 교차 검증 (v2 = x_publish = X_IMAGE_GUIDE)
- [x] 재무 비용구조 리서치 → `research/hims_cost_structure.md`
- [x] Bear Case 제거 → 글로벌 플랫폼 테제 강화
- [x] 넷플릭스 비유 추가 (DVD→스트리밍→오리지널 = 약 전달→데이터→자체공장→맞춤처방)
- [x] 2026 가이던스 Eucalyptus 미반영 → 업사이드 프레이밍
- [x] 누락 출처 2건 추가 (Cleveland Clinic 65%, 리텐션 82%)

#### Phase 4: 팩트체크 ✅ 완료
- [x] `published/019_HIMS_의료민주화-플랫폼/sources.md` — 1차 자료 14건, 데이터 20건 전수 검증 ✅

#### Phase 5: 시각화 ✅ 완료
- [x] `visuals/01_glp1_price_comparison.png` — GLP-1 가격 비교 수평 바 차트 (9개 항목, 빅파마/TrumpRx/HIMS/제네릭)
- [x] `visuals/02_global_expansion.png` — 글로벌 확장 3열 카드 (ZAVA/Livewell/Eucalyptus)
- [x] `images/` — 인터넷 수집 이미지 7개 (Hims 바이알, GLP-1 제품, TrumpRx 스크린샷, 노보/릴리 로고 등)
- [x] `generate_visuals.py` — 생성 스크립트 + QA 통과

#### Phase 6: 최종 게시 — ⏸️ 사용자 게시 대기
- [x] x_publish 변환 (테이블→텍스트, 📎→이미지 가이드)
- [x] `published/019_HIMS_의료민주화-플랫폼/` 패키지 생성 (v2, x_publish, X_IMAGE_GUIDE, sources.md, visuals/, images/)
- [x] 면책조항/출처 최종 확인
- [x] 네이버 HTML 변환 + naver/ 패키징 완료 (이미지 5개 번호순 + README + 태그)
- [ ] **X Notes 게시** (3/6 예정)

**관련 파일**: `data/articles/019_HIMS_의료민주화-플랫폼/`

---

### 4-11 KR-03~06: 현대차 시리즈 (4편, 재구성)

**현황 (2026-03-15)**: 1편 게시 대기, 2편 게시 대기 (§5-7 재구성 완료)

**서사 아크**: 강점 → 철학의 차이 → 제품에서 드러나는 증거 → 돈으로 최종 검증

| 편 | KR# | 제목(가제) | 핵심 | 폴더 | 상태 |
|----|-----|------------|------|------|------|
| 1편 | KR-03 | 바꾸지 않아도 되는 것 | 정주영→현대속도→메타플랜트 | 022 | **게시 대기** (v2+시각화+x_publish+published 완료) |
| 2편 | KR-04 | 빠르게 만드는 것과 다르게 만드는 것 | Tesla 5단계, 자율주행 센서, 730만 대 데이터 | 017 | **게시 대기** (§5-7 재구성, 시각화 2+이미지 3) |
| 3편 | KR-05 | 요구조건을 의심하라 | Atlas/Atria/MobED 5단계 검증 + 경쟁자 비교 | 018 | 기획 완료, 초안 미작성 |
| 4편 | KR-06 | $110B의 행방 | 투자 분석 + 인사 + 시리즈 종합 | 017 | 기존 초안 활용 예정 |

**1편 (022) — KR-03 "바꾸지 않아도 되는 것"**
- [x] 정주영 회장 조선소 에피소드 오프닝 추가
- [x] 기존 022 초안 내용 재구성 (현대속도, 메타플랜트, 1억대, RMAC)
- [x] v1 초안 완료 — `022_KR_현대차-제조DNA/drafts/kr-03_hyundai_dna_v1.md`
- [x] 퇴고 → v2 완료 (Ford BlueOval 팩트 수정: "5년 넘도록"→"6년+ 전망")
- [x] 시각화 2개 완료 (`visuals/01_factory_speed.png`, `02_manufacturing_dna.png`)
- [x] 출처 검증 완료 — sources.md 대폭 갱신 (D22-D26 추가, 18건 검증, 1건 수정)
- [x] 📎 마커 4곳 배치 (정주영.jpg + 차트 2개 + 아트라스.avif)
- [x] x_publish 변환 + X_IMAGE_GUIDE 작성
- [x] `published/022_KR_현대차-제조DNA/` 패키지 생성
- [x] **X Notes 게시** (2026-03-29)

**2편 (017) — KR-04 "빠르게 만드는 것과 다르게 만드는 것"**
- [x] Tesla 5단계 제조 철학 리서치
- [x] v1 초안 완료
- [x] 퇴고 → v2 완료 (시각적 호흡 16곳, 오타 수정)
- [x] **§5-7 전면 재구성 (2026-03-15)**:
  - §5 애플→자율주행 센서 (비전 온리 vs 센서 퓨전, LiDAR 출처 추적, 서라운드 카메라 우위)
  - §6 Tesla 생태계→730만 대 데이터 (라벨링, "선생 없는 교실" 비유, 새만금)
  - §7 축소·정리 (3도메인 패턴 요약 → KR-05 브릿지)
  - 다음 편 예고 수정: KR-05 제품 검증 방향 구체화
- [x] sources.md 전면 재작성 — 1차 자료 9건, 데이터 21건, 인용문 3건, 미검증 3건
- [x] 시각화 2개: `01_tesla_5steps.png`, `02_sensor_comparison.png` (matplotlib)
- [x] 인터넷 이미지 3개: Giga Press 주조물, Waymo 6세대, Tesla 카메라 화각
- [x] 📎 마커 5곳 배치 + X_IMAGE_GUIDE 정합 (5/5)
- [x] x_publish 변환 완료
- [x] `published/017_KR_현대차-철학비교/` 패키지 생성
- [x] **X Notes 게시** (2026-03-29)

**3편 (018) — KR-05 "요구조건을 의심하라"**
- [x] 기획 완료 (Atlas/Atria/MobED 제품별 5단계 검증 구조)
- [ ] 리서치 보강 (각 제품 상세 스펙, 경쟁자 비교 데이터)
- [ ] v1 초안

**4편 (017) — KR-06 "$110B의 행방"**
- [x] 기존 017 초안 (110조 분석) + 018 초안 (인사) 내용 통합 예정
- [ ] 시리즈 종합 결론 구성
- [ ] v1 초안 (통합본)

**관련 파일**:
- `data/articles/022_KR_현대차-제조DNA/` (1편)
- `data/articles/017_KR_현대차-철학비교/` (2편)
- `data/articles/018_KR_현대차-인사/` (3편)
- `data/articles/017_KR_현대차-110조/` (4편)

---

### 4-12 KR-07: 곱셈이 사라진다 — 1, 0, -1과 반도체의 미래

**테제**: AI 산업이 $1,000억을 쏟아붓는 GPU는 부동소수점 곱셈에 최적화되어 있다. 그런데 LLM weight가 {-1, 0, +1}이면 그 곱셈 자체가 필요 없다. 소프트웨어(BitNet b1.58)와 하드웨어(삼성/UNIST 3진법 반도체)가 독립적으로 같은 답에 도착했다. 아무도 이 연결을 말하지 않는다.

**KR-02와의 관계**: KR-02가 "HBM이 왜 어려운가" (진단)라면, 이 글은 "HBM의 한계를 어떻게 돌파하는가" (처방전). 같은 병목에서 출발하지만 방향이 정반대.

**핵심 수치**:
- 1.58 bits/weight (log₂3) vs 16 bits (FP16) = **10x 메모리 축소**
- 행렬곱 에너지 **71.4x 절감** (곱셈 → 덧셈)
- TENET ASIC vs A100 GPU: 에너지 효율 **21.1x**
- Taalas HC1: **17,000 tok/s** (H100 ~150)
- 추론 시장 비중: 2023년 1/3 → 2026년 **2/3** (Deloitte)
- 커스텀 ASIC 성장률 **44.6%** vs GPU **16.1%** (2026)

**구조안**:
```
§1  문제 제기 — HBM의 벽 (열, 수율, 대역폭 격차)
§2  1.58비트 — 곱셈이 사라지는 순간 (BitNet b1.58, 수치로 증명)
§3  하드웨어가 먼저 도착해 있었다 (삼성/UNIST 3진법, 터넬 T-CIM)
§4  추론 경제학 — GPU의 존재 이유가 흔들린다 (TENET, Taalas, ASIC vs GPU)
§5  세 갈래 — 아직 끝나지 않은 경주
    경로 A: 파이프를 넓혀라 (HBM4, CXL, 광 인터커넥트)
    경로 B: 보내지 않는다 (PIM, 칩렛/UCIe)
    경로 C: 매체를 바꾼다 (ternary, 포토닉, 뉴로모픽)
§6  한국의 좌표 (SK하이닉스, 삼성, Rebellions, FuriosaAI, 터넬)
§7  투자자의 시간표 (근거리/중거리/먼 미래)
```

**시각화 후보**:
1. 곱셈 vs 덧셈 에너지 비교 (71.4x)
2. 3갈래 경로도 + 시간축 + 한국기업 위치
3. 1.58-bit 메모리 축소 (14GB → 1.4GB)
4. 추론 시장 역전 (학습 vs 추론 + ASIC vs GPU 성장률)

**리서치 완료**:
- [x] `data/research/korea/sectors/semiconductor/next_gen_semiconductor_tech_research.md` — 15개 기술 조사
- [x] BitNet b1.58 + 삼성 3진법 + 터넬 T-CIM 연결 리서치

**다음 단계**:
- [ ] 사용자 구조안 확정
- [ ] 아티클 폴더 생성 (`023_KR_차세대-반도체/`)
- [ ] 아웃라인 작성
- [ ] v1 초안

**관련 파일**: `data/research/korea/sectors/semiconductor/next_gen_semiconductor_tech_research.md`

---

### 4-16 026 TeraFab의 시작 — 팹을 가장 빨리 짓는 법

**테제**: 반도체 팹 건설은 6단계(부지→건설→장비→시생산→수율→양산)를 거친다. Tesla는 각 단계의 병목을 어떻게 압축하는가 — 그리고 압축할 수 없는 것은 무엇인가.

**025와의 관계**: 025가 "팹이 왜 비싼가" (구조 분석)라면, 026은 "어떻게 가장 빨리 짓는가" (실행론).

**핵심 발견**:
- Samsung Taylor $165억 계약 → TeraFab 완성까지의 브릿지 역할
- 중고 장비 시장 (비EUV) + Intel IFS 49% 매각 가능성
- 압축 가능: 부지(skip), 건설(Dirty Fab), 장비(병렬 발주)
- 압축 불가: 수율 (경험의 함수, 시간만이 가르침)

**완료**:
- [x] 아웃라인 (`026_TSLA_테라팹-시작/drafts/outline.md`)
- [x] 리서치 + 출처 (`research/sources.md`)
- [x] v1 초안 (271줄, 10,915자) — Samsung 브릿지, 중고 장비, Intel IFS 반영

**다음 단계**:
- [ ] 퇴고 → v2
- [ ] 시각화 (간트차트: 일반 팹 vs TeraFab 타임라인)
- [ ] x_publish 변환
- [ ] 게시

**관련 파일**: `data/articles/026_TSLA_테라팹-시작/`

---

### 4-17 027 파운드리의 역설 — 애플이 가장 잘 만드는 회사가 될 수 없는 이유

**테제**: 파운드리 모델이 fabless 기업을 세계 최고로 만들었지만, 동시에 최적화의 상한선을 결정한다. PDK의 감옥, 범용 공장의 대가, 끊어진 피드백 루프.

**026과의 관계**: 026이 "직접 짓는다" (수직통합 실행론)라면, 027은 "직접 짓지 않으면 어떤 한계가 있는가" (파운드리 모델의 구조적 역설).

**아웃라인 제안 완료** (사용자 승인 대기):
- §1 애플 실리콘의 성공과 fabless 신화
- §2 PDK의 감옥 — 남의 주방에서 요리하는 셰프
- §3 범용 공장의 대가 — 534개 고객, 12,682개 제품
- §4 설계-제조 피드백 루프의 단절
- §5 평화의 역설 — 집중과 취약성
- §6 결론 — 최적화의 상한선

**다음 단계**:
- [ ] 아웃라인 확정 (사용자 승인)
- [ ] v1 초안
- [ ] 퇴고 → v2

**관련 파일**: `data/articles/027_AAPL_파운드리-역설/` (미생성)

---

### 4-10 012 의식을 우주로 확장한다는 것

**현황 (2026-03-06)**:
- [x] 리서치 완료 (`research/sources.md` — 1차 자료 16건, 데이터 44건, 인용문 3건)
- [x] 인터넷 이미지 수집 (A: Starship 타워캐치 CC BY 2.0, B: Shackleton Crater NASA PD)
- [x] 시각화 4개 QA 통과 (`visuals/01~04*.png`)
- [x] v4 재구성 → v5 완전 재기획 (인문학→공학 전환 구조)
- [x] **v6 퇴고 완료** (243줄, 7,425자):
  - v4→v5: 제목 "의식을 우주로 확장한다는 것", 구조 전면 변경 (§1 소년의 질문 → §2 의식의 빛 → §3 물리환경 → §4 정책 병목 → §5 $100/kg → §6 Tesla)
  - v5→v6: 6항목 자가 퇴고 — TSMC AZ 팩트 수정, 라우든 카운티 표현 정확화, 희토류 수치 정확화, 예고편 강화
  - sources.md 44개로 확장 (§3/§4 신규 데이터 전수 등재 + 팩트체크 완료)
- [ ] x_publish 변환 (테이블→텍스트)
- [ ] X Notes 게시

**향후 시리즈 방향 (사용자 확정)**:
- 012: 의식을 우주로 확장한다는 것 (현재)
- 013: 궤도 데이터센터
- 014: 달 반도체 공장

**관련 파일**: `data/articles/012_TSLA_SpaceX-비용혁명과-달/`

---

### 1-24 자동 시황 브리핑 시스템 (오선 스타일)

**우선순위**: P1 (가장 중요)
**레퍼런스**: [오선의 미국 증시 라이브](https://www.youtube.com/@futuresnow) — 본장 전 시황 브리핑, 주요 뉴스/실적/경제일정 정리

**목표**: 매일 자동으로 한국/미국 시황 브리핑을 생성하는 시스템

**스케줄**:
| 시간 | 내용 |
|------|------|
| **오전 6시** | 한국시장 시작 준비 + 미국 시황 마감 정리 |
| **오후 6시** | 미국시장 시작 준비 + 한국시장 마감 정리 |

**브리핑 스타일 (오선 참고)**:
- 주요 뉴스 요약 (Bloomberg, CNBC, Reuters, WSJ 등)
- 기업 실적 발표 일정
- 주요 경제 지표/이벤트
- 선물/지수 동향
- 크립토 동향

**구현 방향 (설계 필요)**:
- [ ] 데이터 소스 확정 (기존 뉴스 수집기 활용 + 추가 소스)
- [ ] 브리핑 포맷/템플릿 설계
- [ ] 자동 생성 파이프라인 (cron 스케줄)
- [ ] 출력 채널 확정 (이메일? 텔레그램? 파일?)

**관련 기존 시스템**:
- `scripts/collect_news.py` — 뉴스 수집
- `src/collectors/` — 시장 데이터 수집
- 모닝 이메일 시스템 (1-13) — 참고 아키텍처

---

### 1-25 뉴스 온톨로지 + 제1원칙 분석 + 타임라인

**목표**: 수집된 뉴스를 팔란티어 온톨로지 형식으로 정리하고, 일론 머스크의 제1원칙 사고로 분석하여 타임라인을 생성

**팔란티어 온톨로지 구조**:
- **Entity** — 기업, 인물, 기관 (이름, 유형, 티커, 시장)
- **Event** — 사건 (제목, 유형, 심각도, 상태)
- **Link** — Entity↔Event↔News 관계 (유형, 신뢰도, 근거)
- **Action/Evaluation** — 분석 결과 (제1원칙 분해)

**제1원칙 분석 레이어**:
1. 통념 식별 — 시장이 당연시하는 가정
2. 근본 진실 분해 — 가정을 제거하고 남는 팩트
3. Gap 발견 — 통념과 현실 사이의 괴리
4. 가능성 추론 — Gap에서 투자 기회 도출

**타임라인 생성**:
- politics-stat `remotion/templates/Timeline.tsx` 참고 (Remotion 애니메이션)
- 이벤트 시계열 → 시각적 타임라인 렌더링

**참조 파일 (이 프로젝트)**:
- `scripts/ontology_io.py` — Entity/Event/Link 추출/적용 CLI
- `scripts/story_io.py` — 뉴스 스토리 분류/추적
- `src/storage/ontology_repository.py` — DB CRUD
- `src/core/models.py` — OntologyEntity, OntologyEvent, OntologyLink 모델

**참조 파일 (politics-stat)**:
- `/home/gint_pcd/politics-stat/lib/domains/ontology/types.ts` — 팔란티어식 4블록 타입
- `/home/gint_pcd/politics-stat/lib/domains/ontology/services.ts` — 등급/색상/필터 서비스
- `/home/gint_pcd/politics-stat/remotion/templates/Timeline.tsx` — 타임라인 컴포넌트

**다음 단계**:
- [ ] 기존 ontology_io.py 현황 점검 (DB 데이터 유무)
- [ ] 제1원칙 분석 프롬프트/파이프라인 설계
- [ ] 타임라인 출력 형식 확정 (matplotlib PNG? Remotion 영상? HTML?)
- [ ] 1-24 브리핑 시스템과 연동 방안

---

### 3-1 지표 분석 상세

**목표**: 리포트의 각 지표가 실제로 얼마나 예측력이 있는지 검증하고, 해석 체계를 정립.

**완료 (2026-02-28)**:
- [x] S&P 500 499개 종목 지표 데이터 수집 (`indicator_analysis_20260228.csv`)
- [x] 10개 지표별 예측력 분석 (ADX, DI, RSI, MACD, Supertrend, EMA, BB, Volume, EMA200, Regime)
- [x] 핵심 발견 3가지 도출 (역발상 불일치, 모멘텀 우세, 최적 조합)
- [x] Q6으로 `signal_interpretation_notes.md`에 기록
- [x] 해석 원칙 8개로 확대

**이어서 할 것**:
- [ ] 발견 사항을 코드/리포트에 반영할지 논의
- [ ] Tech Score 역발상 편향 문제 → 개선 or 해석으로 보완할지 결정
- [ ] DI Spread 리포트 표시 여부 논의
- [ ] 추가 질문/검증 사항 발굴

**관련 파일**:
- `docs/프로젝트/signal_interpretation_notes.md` (Q1~Q6 + 해석 원칙 8개)
- `data/processed/dashboards/indicator_analysis_20260228.csv` (499개 종목 원본 데이터)
- `data/processed/dashboards/shape_validation_20260228.csv` (차트 형태 검증 데이터)

---

### 5-1 Tesla 펀더멘탈 리서치 허브 상세

**목표**: Tesla의 펀더멘탈 방향성을 지속 추적하고 아티클로 발전시키는 리서치 베이스 구축

**완료 (2026-03-02)**:
- [x] 디렉토리 구조 생성 (`data/research/stocks/tesla/`)
- [x] Master Plan Part 1 (2006) 정리
- [x] Master Plan Part Deux (2016) 정리
- [x] Master Plan Part 3 (2023) 정리
- [x] 재무 지표 (`financials.md`) 채우기 — FY 2025 실적, 분기별 추이, 밸류에이션
- [x] 사업부문별 현황 (`business_segments.md`) 채우기 — 3개 세그먼트 + 미래 사업 4개
- [x] Bull Case 테제 작성 — 수직통합/에너지/Robotaxi/Optimus 4대 논거
- [x] Bear Case 테제 작성 — 밸류에이션/둔화/CEO리스크/경쟁 3대 논거 + Stress Test

**관련 파일**:
```
data/research/stocks/tesla/
├── README.md
├── fundamentals/
│   ├── financials.md          ✅
│   ├── business_segments.md   ✅
│   ├── master_plan_part1.md   ✅
│   ├── master_plan_part2.md   ✅
│   ├── master_plan_part3.md   ✅
│   └── earnings/
├── thesis/
│   ├── bull_case.md           ✅
│   └── bear_case.md           ✅
└── articles/
```

---

## ⏸️ 사용자 액션 대기

| # | 분야 | 작업 | 남은 사용자 액션 |
|---|------|------|-----------------|

---

## 작업 현황

### ── P1 긴급 ──

| # | 분야 | 작업 | 중요도 | 담당 | 발행일 | 상태 | 비고 |
|---|------|------|--------|------|--------|------|------|
| 5-8 | 리서치 | 이란 전쟁 지정학 온톨로지 — 나라별 연관관계 + 히스토리 + 지속 추적 | P1 | AI + 사용자 | 2026-03-28 | 진행 | 6개 문서 + 대시보드 완성. Phase 2(자동 추적) 미착수 |
| 1-29 | 시스템 | 이란 전쟁 대시보드 design review — gstack /design-review 실행 | P2 | AI | 2026-03-28 | 예정 | 집에서 대시보드 확인 후 느낌/방향 확정 → 리뷰+수정 |

### ── P2 즉시 착수 가능 ──

| # | 분야 | 작업 | 중요도 | 담당 | 발행일 | 상태 | 비고 |
|---|------|------|--------|------|--------|------|------|
| 1-23 | 시스템 | 크립토 생태계 기업 모니터링 이메일 섹션 추가 | P2 | AI | 2026-03-01 | 예정 | COIN/HOOD/BMNR/SQ/BLK/MSTR 주가+뉴스, Circle 뉴스 추적. 상세 → task/1-23.md |
| 1-24 | 시스템 | 시황 브리핑 cron 자동화 (오전 6시 + 저녁 6시) | P2 | AI | 2026-03-22 | 요청 | run_briefing.sh 경로 수정 + cron 등록. 텔레그램 봇 연결은 PM이 담당. 야간작업 예정 |


### ── P2 선행 작업 대기 ──

| # | 분야 | 작업 | 중요도 | 담당 | 발행일 | 상태 | 비고 |
|---|------|------|--------|------|--------|------|------|
| 3-2 | 분석 | 두 축 연결 체계 — 레짐별 포지션 원칙 정립 | P2 | 사용자 + AI | 2026-03-01 | 예정 | ⏳ 선행: 3-1 완료 후. Risk-On/Off 기준, 진입·청산 원칙 문서화 |

### ── P3 향후 ──

| # | 분야 | 작업 | 중요도 | 담당 | 발행일 | 상태 | 비고 |
|---|------|------|--------|------|--------|------|------|
| 1-14 | 시스템 | `templates/articles/` 기사 출력 포맷 템플릿 | P3 | 아티클작성가 | 2026-02-24 | 예정 | Phase 6 |
| 1-15 | 시스템 | 에이전트별 시작 전 체크리스트 작성 | P3 | — | 2026-02-24 | 예정 | `agents/checklists/` |
| 1-16 | 시스템 | 에이전트별 스킬 매뉴얼 작성 | P3 | — | 2026-02-24 | 예정 | `agents/manuals/` |
| 1-17 | 시스템 | CI/CD 파이프라인 구성 | P3 | — | 2026-02-24 | 예정 | GitHub Actions |
| 1-18 | 시스템 | Docker 컨테이너화 | P3 | — | 2026-02-24 | 예정 | |
| 1-19 | 시스템 | 스케줄러 설정 | P3 | — | 2026-02-24 | 예정 | APScheduler / cron |

---

## TODO (글감 메모)

### 아티클 #002 글감: "현실 데이터의 중요성"

> **하나의 글로 엮을 소재들** — 아래 소재들은 개별 주제가 아니라 하나의 테제를 뒷받침하는 레이어들

**소재 모음:**
- 꿈속의 꿈 "인셉션"
- 시뮬레이션의 시뮬레이션
- 학습의 학습 "picasso like paintings"
- Hallucination
- 자기참조, 프랙탈, 메타 구조 등

**결론 방향 (raw 메모):**

결국 현실에서의 데이터가 필요하다. 혹은 중요하다.
어쩌면 더 나아가서는 인간의 1차 필터, 즉 감각 기관 그리고 뇌에서의 자극을 받아들여서 나오는 1차 생산물인 생각이 중요하다.
생각의 생각을 낳고 더 들어가면 왜곡이 된다.
그래서 이론을 세우거나 가정의 간단한 입증, 방향성을 세우거나 하는 정도의 의미에서 생각의 생각은 좋다.
물론 올바르게 사고 실험을 한다면 더 좋다.
모든 증명은 결국 현실에서 이루어진다.
인간이 만들어 내는 물리적인 something은 결국 다른 인간의 시각, 후각, 청각, 촉각, 미각, 그리고 그것들이 만들어내는 생각 정도에 영향을 끼친다.

---

### 아티클 #003 글감: "AI n차 생산물과 토큰화 자산의 지위"

> AI로 만들어진 n차 생산물에서의 토큰화 자산의 지위

**참고 기업:**
- **Opendoor (NYSE: OPEN)** — iBuyer 모델. 집을 즉시 매입→현금 지급→재판매. 부동산 거래에서 자금 흐름 자체를 극적으로 빠르게 만든 기업

---

## 완료

| # | 분야 | 작업 | 완료일 | 비고 |
|---|------|------|--------|------|
| 4-10 | 아티클 | 012 의식을 우주로 확장한다는 것 | 2026-03-29 | X Notes 게시 완료, 네이버 게시 완료, published/ 이동 완료 |
| 1-28 | 테스트 | 뉴스 수집기 단위 테스트 17건 | 2026-03-26 | TickerExtractor 9건 + NewsPipeline 6건 + BreakingDetection 2건 |
| 1-27 | 코드 | RSS 수집기 안정성 보강 — 실패 소스 추적 | 2026-03-26 | failed_sources 속성, PipelineResult 연동, 테스트 7건 |
| 1-26 | 수정 | 모닝 이메일 Graceful Degradation | 2026-03-26 | 부분 실패 허용, [일부 누락] 접두사, 템플릿 누락 배너, 테스트 7건 |
| 1-25 | 시스템 | 뉴스 온톨로지 + 제1원칙 분석 + 타임라인 | 2026-03-23 | 2레이어 구조 (매크로 6 + 종목 104), 교차링크(impacts), 타임라인 PNG, FPA 모델 |
| 1-24 | 시스템 | 자동 시황 브리핑 시스템 (오선 스타일) | 2026-03-23 | cron 05:53/17:47 KST 평일, 네이버 HTML 변환, 팩트 카테고리별 리니어 포맷 |
| 2-11 | 코드 | 뉴스 팩트 추출 파이프라인 | 2026-03-23 | 규칙 기반 추출 + enrich(URL 스크래핑) + CLI 7커맨드 + 보안 검토 완료 |
| 2-9 | 코드 | US 시그마 병렬화 + KR VKOSPI 프록시 추가 | 2026-03-19 | ThreadPoolExecutor 15-thread 병렬 (8-20분→~2분), `_compute_hv_from_df()` 재사용으로 HV 중복 HTTP 제거, KODEX200 HV20 VKOSPI 프록시, `--sigma-workers` CLI, US cron `--skip-sigma` 제거 |
| 2-8 | 코드 | 시그널 리포트 확장: US 풀 유니버스 + KR 시장 + cron 스케줄링 | 2026-03-19 | `--market us\|kr`, `--universe full\|watchlist`, KR Top200 (FinanceDataReader), HV20 시그마, cron 17:00 KR / 06:00 US |
| 4-9 | 아티클 | 019 HIMS — 약은 누구나 팔 수 있다 | 2026-03-06 | X Notes 게시 완료 |
| 4-8 | 아티클 | ~~KR-01~~ → 020 KR-02 반도체 기술 딥다이브 X 게시 | 2026-03-05 | KR-01 삭제(중복), 020으로 대체 게시 |
| 2-7 | 코드 | generate_naver_html.py 자동 의미 간격 추가 | 2026-03-09 | `_add_spacer()` 함수 추가 — h1/h2/h3/hr 앞, blockquote 앞뒤, table 뒤에 `<p>&nbsp;</p>` 자동 삽입. 네이버 에디터 margin 무시 문제 해결. naver-html.md 규칙 갱신 |
| 2-6 | 코드 | generate_naver_html.py 개선 + 워크플로우 규칙 정비 | 2026-03-05 | 면책조항 disc 스타일 자동 적용, blockquote 상태 메타데이터 자동 제거, 연속 빈 줄→시각 간격 변환, QA 체크리스트·이미지 교차검증·시각적 호흡 규칙 추가, 적정 분량 가이드라인(250~300줄) + X 글자제한(25,000자) 추가, 이미지 소싱 워크플로우 확정 |
| 5-6 | 리서치 | HIMS 종합 리서치 + GLP-1 글로벌 규제 조사 | 2026-03-02 | 회사 본질/재무/경쟁/밸류에이션 + 9개국 GLP-1 규제·특허 만료 타임라인 |
| 5-7 | 리서치 | 크립토 생태계 기업 19사 리서치 | 2026-03-02 | 7카테고리 TIER 1-3 분류, Circle IPO·BitGo IPO 확인, `data/research/crypto/ecosystem_stocks_research.md` |
| 4-2 | 아티클 | 아티클 #001 TSLA — "복잡해질수록, 통합한 자가 이긴다" | 2026-03-02 | X 게시 완료 (3/2), published 이동, 네이버 변환 미완 |
| 5-1 | 리서치 | Tesla 펀더멘탈 리서치 허브 구축 | 2026-03-02 | Master Plan 1~3 + financials + business_segments + Bull/Bear Case 완성, `data/research/stocks/tesla/` |
| 5-3 | 리서치 | ETH 펀더멘탈 리서치 허브 구축 | 2026-03-01 | overview·ecosystem·roadmap·Bull/Bear 작성, `data/research/crypto/ethereum/` |
| 5-2 | 리서치 | BTC 펀더멘탈 리서치 허브 구축 | 2026-03-01 | overview·adoption·on_chain·Bull/Bear 작성, `data/research/crypto/bitcoin/` |
| 5-5 | 리서치 | 한국시장 채널 구축 + KR-01 HBM 병목 리서치 | 2026-03-01 | 채널 테마 확정 (하드웨어 병목), 섹터 지도 작성, 리서치 허브 구조 생성, hbm_bottleneck_research.md 완료 |
| 5-4 | 리서치 | Palantir 펀더멘탈 리서치 허브 구축 | 2026-03-01 | 재무/사업부문/타임라인/Bull-Bear/이슈타임라인/기술구조 완료, Excel 대시보드 생성 |
| 1-22 | 시스템 | MMF 주간 데이터 소스 FRED → ICI 직접 파싱 교체 | 2026-03-01 | ICI XLS 직접 파싱, 23일 앞섬, 전체 $7.8T 기준, 연도 fallback 로직 포함 |
| 1-21 | 시스템 | 이메일 레이아웃 개선 — 차트 섹션별 배치 + 데이터 기준일 표시 | 2026-03-01 | Section 6 제거, 각 섹션 말미 인라인 차트, FRED 행별/섹션별 날짜 표시 |
| 1-20 | 시스템 | 크립토 이메일 Section 5 확장 (BTC.D / ETH/BTC / 공포탐욕) | 2026-03-01 | CoinGecko /global + alternative.me /fng/, ETH/BTC 계산, 3-칸 카드 추가 |
| 1-13 | 시스템 | 글로벌 유동성 모니터링 + 모닝 이메일 발송 | 2026-03-01 | FRED+FX+섹터ETF 수집, 5개 차트, Gmail 자동발송, 섹터 다기간 테이블(1W/1M/3M/1Y) |
| 2-5 | 코드 | 종목 패턴 분류 (Breakout / Pullback / Consolidation) | 2026-02-28 | 4파일 수정, classify_stock_pattern(), ADX 5일 변화, BB 스퀴즈, 거래량 비율 |
| 2-4 | 코드 | 계층적 가중 시장 레짐 점수 + 포트폴리오 익스포저 대시보드 | 2026-02-28 | 3파일 수정, Composite Score, Net/Gross/Long/Short, Exposure Dashboard |
| 2-3 | 코드 | ADX + EMA 20/50/200 추세 분류 (Trend Regime) | 2026-02-27 | 5단계 분류, 6파일 수정, Section 1·2에 Trend 열 추가 |
| 2-2 | 코드 | 통합 시그널 리포트 Excel 생성 | 2026-02-27 | `signal_builder.py` + `generate_signal_report.py`, 3섹션 (시장→종목→시그마) |
| 4-1 | 아티클 | 아티클 #001 로켓/우주 리서치 | 2026-02-25 | 발사 횟수/비용/SpaceX/Starship |
| 1-12 | 시스템 | 아티클 리서치 스킬 정의 | 2026-02-25 | `.claude/skills/article-research.md` |
| 1-11 | 시스템 | 옵션 체인 IV 수집기 + Expected Move 분석기 | 2026-02-24 | yfinance 옵션 체인, 1σ/2σ 가격 범위, IV skew/rank, term structure, 48 tests |
| 1-10 | 시스템 | 백테스트 프레임워크 + OHLCV 10년치 수집 인프라 | 2026-02-24 | data/strategy/engine/metrics/report 5모듈, 41 tests |
| 1-9 | 시스템 | 감성 데이터 DB 모델 + 리포지토리 + 백필 스크립트 | 2026-02-24 | SentimentRecord/CommunitySentiment/TrendsRecord ORM, 백필 CLI |
| 1-8 | 시스템 | Google Trends 수집기 | 2026-02-24 | US+KR, spike ratio 감성 프록시 |
| 1-7 | 시스템 | Reddit 커뮤니티 수집기 | 2026-02-24 | WSB/stocks/investing, 트렌딩 티커 |
| 2-1 | 코드 | 자체 F&G 6컴포넌트 확장 | 2026-02-24 | 동적 가중치, CNN 참조 분리 |
| 1-6 | 시스템 | AAII 투자자 설문 수집기 | 2026-02-24 | 주간 XLS 다운로드 |
| 1-5 | 시스템 | StockTwits 수집기 | 2026-02-24 | 무료 API, Bullish/Bearish 태그 |
| 1-4 | 시스템 | 네이버 종목토론실 스크래퍼 | 2026-02-24 | 공감/비공감 기반 감성 |
| 1-3 | 시스템 | CBOE Put/Call Ratio 수집기 | 2026-02-24 | 3종 CSV (total/equity/index) |
| 1-2 | 시스템 | CNN Fear & Greed 수집기 | 2026-02-24 | `fear-and-greed` 패키지 + 직접 API |
| 1-1 | 시스템 | CLAUDE.md 분리 + TASK 관리 체계 구축 | 2026-02-24 | rules/skills 구조, TASK.md 신설 |
| 1-0 | 시스템 | Phase 1~3·5·7 + 엑셀 차트 개선 + PROJECT_MAP | 2026-02 | 프로젝트 기반 전체, 290 tests, 51% coverage |
