# 바이오 기술 리뷰 #3: 면역세포 조종 (Immune Manipulation) — 기전, 임상 데이터, 투자 분석

> **Review Article** | 2026-04-05
> 키워드: PD-1/PD-L1, 면역관문억제제, bispecific antibody, CAR-T, 암 백신, 종양 미세환경, T세포

---

## 목차

1. [기술 개요](#1-기술-개요)
2. [핵심 기술 세부](#2-핵심-기술-세부)
3. [임상 데이터](#3-임상-데이터)
4. [시장 분석](#4-시장-분석)
5. [AI 적용](#5-ai-적용)
6. [참고문헌](#6-참고문헌)

---

## 1. 기술 개요

### 1.1 암 면역학의 분자생물학적 기반

면역 조종(immune manipulation) 치료의 이론적 토대는 **암 면역편집(cancer immunoediting)** 가설에 기반한다. 이 가설에 따르면, 면역계와 종양 사이의 상호작용은 세 단계를 거친다:

1. **Elimination (제거)**: 선천면역(NK세포, 대식세포)과 적응면역(CD8+ CTL, CD4+ Th1)이 초기 종양 세포를 인식·살해
2. **Equilibrium (평형)**: 면역 선택압에 의해 일부 종양 변이체가 생존, 면역계와 동적 균형 유지
3. **Escape (회피)**: 면역 회피 기전을 획득한 종양 클론이 면역 감시를 돌파하여 임상적 암으로 진행

면역관문(immune checkpoint)은 **Escape** 단계의 핵심 기전이다. 종양 세포가 면역관문 리간드를 과발현하여 T세포에 억제 신호를 전달함으로써 항종양 면역 반응을 무력화한다.

### 1.2 면역 조종 치료의 분류 체계

| 접근법 | 메커니즘 | 대표 치료 | 표적 |
|--------|---------|----------|------|
| 면역관문 차단 | T세포 억제 신호 해제 | Anti-PD-1/PD-L1, Anti-CTLA-4 | PD-1, PD-L1, CTLA-4 |
| 이중특이성 항체 | T세포-종양세포 강제 연결 | Blinatumomab, Tarlatamab | CD19×CD3, DLL3×CD3 |
| 세포 치료 | 조작된 면역세포 투여 | CAR-T, TCR-T, TIL | CD19, BCMA, HER2 |
| 암 백신 | 네오항원 면역 기억 유도 | mRNA-4157, BNT122 | 환자별 네오항원 |
| 사이토카인 치료 | 면역세포 직접 활성화 | IL-2, IL-15 | 면역세포 수용체 |

---

## 2. 핵심 기술 세부

### 2.1 PD-1/PD-L1 축: 분자 기전과 면역 시냅스

#### 2.1.1 PD-1 수용체의 구조와 신호전달

PD-1(Programmed Death-1, CD279)은 288개 아미노산의 1형 막관통 단백질로, 면역글로불린 superfamily에 속한다 [1, 2].

**구조적 특성:**
- **세포외 도메인**: IgV-like 도메인 — PD-L1/PD-L2와의 결합 부위
- **막관통 도메인**: 단일 α-helix
- **세포내 도메인**: 두 개의 티로신 잔기 — ITIM(Immunoreceptor Tyrosine-based Inhibitory Motif)과 ITSM(Immunoreceptor Tyrosine-based Switch Motif)

**억제 신호전달 캐스케이드:**

1. **PD-L1 결합**: 종양 세포 표면의 PD-L1(B7-H1, CD274)이 T세포의 PD-1에 결합 (Kd ~8.2 μM for PD-1/PD-L1)
2. **ITSM 인산화**: Lck(lymphocyte-specific kinase)이 PD-1의 ITSM(Y248)을 인산화
3. **SHP-2 모집**: 인산화된 ITSM이 SHP-2(Src homology region 2-containing protein tyrosine phosphatase 2)를 모집 — 이것이 PD-1 억제 신호의 핵심 매개자
4. **TCR 마이크로클러스터 탈인산화**: SHP-2가 TCR 신호 복합체의 CD3ζ 사슬과 ZAP-70을 탈인산화
5. **PI3K-AKT 억제**: SHP-2가 CD28 공동자극 수용체도 탈인산화 → PI3K-AKT-mTOR 경로 차단
6. **Ras-MEK-ERK 억제**: TCR 하위 Ras-MAPK 경로 차단
7. **기능적 결과**: T세포 증식 정지, 사이토카인(IL-2, IFN-γ, TNF-α) 생산 감소, 세포독성 기능 소실, 결국 T세포 소진(exhaustion)

**PD-L1 발현 조절:**
- **유전적 증폭**: 9p24.1 유전자좌(PD-L1/PD-L2/JAK2 포함) 증폭 → 호지킨 림프종에서 흔함
- **종양유전자 신호**: EGFR 활성 변이, ALK 전좌, MYC 과발현 → PD-L1 전사 촉진
- **IFN-γ 유도**: 종양 침윤 T세포가 분비하는 IFN-γ가 JAK1/2-STAT1 경로를 통해 PD-L1 전사 유도 (적응 면역 저항)
- **후성유전적**: PD-L1 프로모터 탈메틸화, EZH2 억제

#### 2.1.2 CTLA-4의 차별적 기전

CTLA-4(CD152)는 PD-1과 다른 면역 관문을 형성한다:

| 특성 | PD-1 | CTLA-4 |
|------|------|--------|
| 발현 시기 | 항원 만남 후 | T세포 활성화 초기 |
| 주요 발현 세포 | 효과기 T세포, NK, B세포 | 활성 T세포, Treg |
| 리간드 | PD-L1, PD-L2 | B7-1(CD80), B7-2(CD86) |
| 작용 위치 | 말초 조직/종양 | 림프절 (프라이밍 단계) |
| 억제 기전 | SHP-2 매개 탈인산화 | CD28과 B7 리간드 경쟁 + 세포내 PP2A 활성화 |
| 투여 시 독성 | 상대적 낮음 | 높음 (자가면역 부작용) |

#### 2.1.3 차세대 면역관문 표적

| 표적 | 기전 | 임상 단계 | 대표 약물 |
|------|------|---------|----------|
| LAG-3 (CD223) | MHC II 결합 → T세포 억제 | FDA 승인 (Relatlimab) | Opdualag (nivolumab+relatlimab) |
| TIGIT | CD155(PVR) 결합 → NK/T세포 억제 | Phase 3 (혼재 결과) | Tiragolumab (Roche) |
| TIM-3 (HAVCR2) | Galectin-9, CEACAM1 결합 | Phase 2 | Sabatolimab (Novartis) |
| VISTA | 산성 pH에서 활성화 → TME 특이적 | Phase 1/2 | HMBD-002 |

### 2.2 이중특이성 항체와 TCR-CD3 가교(Crosslinking) 기전

#### 2.2.1 T세포 이동체(T-Cell Engager) 작동 원리

이중특이성 항체(bispecific antibody)의 T-cell engager(TCE) 서브클래스는 하나의 분자가 두 가지 항원을 동시에 인식한다 [3, 4]:

- **Arm 1 (종양 결합)**: 종양 관련 항원(TAA) — 예: CD19, CD20, BCMA, DLL3, HER2
- **Arm 2 (T세포 결합)**: CD3ε 서브유닛 — TCR-CD3 복합체의 구성 요소

**면역 시냅스 형성 과정:**

1. **표적 세포 결합**: Arm 1이 종양 세포 표면 항원에 결합
2. **T세포 모집**: Arm 2가 인접한 T세포의 CD3ε에 결합
3. **강제 근접(forced proximity)**: 종양 세포와 T세포가 물리적으로 근접하여 면역 시냅스(immunological synapse) 형성
4. **CD3 클러스터링**: CD3 가교 → ITAM(Immunoreceptor Tyrosine-based Activation Motif) 인산화
5. **ZAP-70 활성화**: 인산화된 ITAM에 ZAP-70이 모집/활성화
6. **하위 신호 캐스케이드**: LAT/SLP-76 인산화 → PLCγ1 활성화 → IP3/DAG 생성
7. **세포독성 과립 방출**: Ca2+ 신호에 의한 세포독성 과립(perforin/granzyme) 극성 분비(polarized secretion)
8. **종양세포 사멸**: Perforin이 표적세포 막에 pore 형성 → Granzyme B 유입 → Caspase 3/7 활성화 → 아포토시스

핵심적으로, TCE는 **TCR의 MHC 의존적 항원 인식을 우회**한다. 이는 MHC class I 하향조절(면역 회피의 주요 기전)에도 불구하고 T세포 살해를 유도할 수 있음을 의미한다.

#### 2.2.2 BiTE vs. IgG-like 형식 비교

| 특성 | BiTE (Blinatumomab) | IgG-like (Teclistamab) |
|------|--------------------|-----------------------|
| 구조 | 2개 scFv 직렬 연결 (~55 kDa) | 전장 IgG 기반 (~150 kDa) |
| 반감기 | ~2시간 → 연속 주입 필요 | 수일-수주 → 간헐 투여 |
| Fc 기능 | 없음 (ADCC/CDC 불가) | 있음/없음 (설계에 따라) |
| CRS 위험 | 중간 | 높음 (초회 투여 시) |
| 조직 침투 | 우수 (작은 크기) | 제한적 |

### 2.3 CAR 구조물의 세대별 진화 (1세대→4세대)

CAR(Chimeric Antigen Receptor)는 T세포 표면에 발현시키는 합성 수용체로, 항체의 항원 인식력과 T세포의 살해 기능을 결합한다 [5, 6].

#### 2.3.1 CAR 구조의 모듈 설계

```
[scFv] — [힌지/스페이서] — [막관통 도메인] — [공동자극 도메인(들)] — [CD3ζ 활성화 도메인]
```

- **scFv (Single-chain variable fragment)**: VH + VL을 유연 링커(보통 (G4S)3)로 연결. 표적 항원 인식.
- **힌지/스페이서**: CD8α 또는 IgG4 유래. 유연성과 길이가 면역 시냅스 간격을 결정.
- **막관통 도메인**: CD8α 또는 CD28 유래. CAR의 막 고정과 이량체화에 관여.

#### 2.3.2 세대별 진화

| 세대 | 세포내 도메인 구조 | 특성 | 한계 |
|------|------------------|------|------|
| **1세대** | CD3ζ만 | 항원 인식 + 활성화 신호(Signal 1)만 | 불충분한 T세포 활성화, 빠른 소진 |
| **2세대** | CD28 또는 4-1BB + CD3ζ | Signal 1 + Signal 2 (공동자극) | 현재 상용화 제품의 표준 |
| **3세대** | CD28 + 4-1BB + CD3ζ | 이중 공동자극 → 이론적 우월성 | 과도한 활성화 위험, 임상 우월성 미입증 |
| **4세대 (Armored/TRUCK)** | 2세대 + 사이토카인/수용체 유전자 | IL-12, IL-18, 또는 CD40L 분비 | TME 리모델링 가능 |

**CD28 vs. 4-1BB 공동자극의 차이:**

| 특성 | CD28 | 4-1BB (CD137) |
|------|------|---------------|
| 활성화 동역학 | 빠름 (급격한 확장) | 느림 (점진적 확장) |
| 효과기 기능 | 강한 세포독성, 높은 사이토카인 | 중간 세포독성 |
| T세포 표현형 | Effector Memory (TEM) 편향 | Central Memory (TCM) 편향 |
| 지속성 | 짧음 (빠른 소진) | 길음 (장기 잔존) |
| CRS 위험 | 높음 | 낮음 |
| 대표 제품 | Yescarta (CD28) | Kymriah, Breyanzi (4-1BB) |

#### 2.3.3 고형암 진출의 기술적 장벽과 해결 전략

CAR-T가 고형암에서 제한적인 이유와 극복 전략:

| 장벽 | 기전 | 극복 전략 |
|------|------|---------|
| **물리적 침투** | Dense stroma, 비정상 혈관 | 국소 투여, 항-VEGF 병용, ECM 분해 효소 |
| **항원 이질성** | 종양 내 항원 발현 불균일 | 이중/삼중 표적 CAR, tandem CAR |
| **면역억제 TME** | TGF-β, IL-10, PD-L1, Treg | TGF-β 수용체 dominant negative, PD-1 KO |
| **T세포 소진** | 만성 항원 자극 → PD-1/TIM-3/LAG-3 상향 | 4-1BB 선택, 에피유전적 리프로그래밍 |
| **트래피킹 결함** | 종양으로의 화학주성 부족 | 케모카인 수용체(CXCR1/2) 발현 |

2025년 ASCO에서 발표된 고형암 CAR-T 데이터: B7-H3 CAR-T 세포의 교모세포종(GBM) Phase I에서 종양내+뇌실내 투여 시 중앙 OS **14.6개월** 달성 (기존 표준 ~8개월) [6].

### 2.4 종양 미세환경(TME)의 면역 억제 기전

TME는 면역치료의 효능을 결정하는 핵심 전장이다:

#### 2.4.1 면역 억제 세포 구성

| 세포 유형 | 기전 | 면역치료에 대한 영향 |
|----------|------|-------------------|
| **Treg (조절 T세포)** | CTLA-4, IL-10, TGF-β 분비 → CTL 억제 | ICI 반응 저하 |
| **MDSC (골수 유래 억제 세포)** | Arginase-1, iNOS → T세포 대사 억제 | CAR-T 기능 소실 |
| **TAM (M2 대식세포)** | IL-10, VEGF → 면역 억제 + 혈관 신생 | 냉종양(cold tumor) 유지 |
| **CAF (암관련 섬유아세포)** | ECM 침착, CXCL12 분비 → T세포 배제 | 물리적 장벽 |

#### 2.4.2 "냉종양(Cold Tumor)" vs. "열종양(Hot Tumor)"

| 특성 | Hot Tumor | Cold Tumor |
|------|----------|-----------|
| T세포 침윤 | 풍부 | 결핍 |
| PD-L1 발현 | 높음 | 낮음 |
| TMB | 높음 | 낮음 |
| ICI 반응률 | 높음 (40-60%) | 낮음 (<10%) |
| 대표 암종 | 흑색종, 신장암, MSI-H 대장암 | 췌장암, 교모세포종, 전립선암 |

냉종양을 열종양으로 전환하는 전략: 방사선, 항VEGF, 종양용해 바이러스, STING 작용제, 암 백신 등이 조합적으로 연구되고 있다.

---

## 3. 임상 데이터

### 3.1 면역관문억제제

#### KEYNOTE-024 (NCT02142738): NSCLC 1차 치료 — 5년 데이터

Pembrolizumab vs. 화학요법, PD-L1 TPS ≥50% [7]:

| 항목 | Pembrolizumab | 화학요법 | 통계량 |
|------|-------------|---------|--------|
| 5년 OS율 | **31.9%** | 16.3% | HR 0.62 |
| 중앙 OS | 26.3개월 | 13.4개월 | — |
| 5년 PFS율 | 12.8% | 미보고 | — |

#### KEYNOTE-522 (NCT03036488): 조기 삼중음성 유방암 — 5년 데이터

Pembrolizumab + 화학요법 → 수술 → Pembrolizumab 유지 [7]:

| 항목 | Pembro + Chemo | Placebo + Chemo |
|------|---------------|----------------|
| 60개월 OS | **86.6%** | 81.7% |
| pCR률 | 63.0% | 55.6% |

#### KEYNOTE-671 (NCT03425643): 조기 NSCLC — 5년 데이터

Pembrolizumab 수술 전후 사용 [7]:

| 항목 | Pembro + Chemo | Chemo only |
|------|---------------|------------|
| 5년 OS율 | **64.6%** | 53.6% |
| 사망 위험 감소 | **26%** (HR 0.74) | — |

#### CheckMate 067 (NCT01844505): 흑색종 — 10년 데이터

Nivolumab + Ipilimumab 병용의 장기 추적 [8]:

| 항목 | Nivo + Ipi | Nivo 단독 | Ipi 단독 |
|------|-----------|----------|---------|
| 10년 OS율 | **43%** | 36% | 22% |
| 중앙 OS | 72개월+ | 36.9개월 | 19.9개월 |

### 3.2 이중특이성 항체

#### DeLLphi-301 (NCT05060016): Tarlatamab — SCLC

DLL3×CD3 BiTE, Phase 2 [3]:

| 항목 | Tarlatamab 10mg |
|------|----------------|
| ORR | **40.4%** |
| 중앙 PFS | 4.9개월 |
| 중앙 OS | **15.2개월** |
| 12개월 OS율 | 56.7% |
| 중앙 반응 기간 | 미도달 |
| CRS (전체/Grade 3) | 51.1% / 0.8% |

SCLC에서 FDA 가속 승인을 획득한 최초의 바이스페시픽 항체. 기존 2차 화학요법 OS ~7-8개월 대비 거의 2배의 생존 개선.

#### TOWER (NCT02013167): Blinatumomab — B-ALL

CD19×CD3 BiTE, Phase 3 [3]:

| 항목 | Blinatumomab | 표준 화학요법 |
|------|-------------|-------------|
| 중앙 OS | **7.7개월** | 4.0개월 (HR 0.71; 95% CI 0.55-0.93) |
| CR율 | **34%** | 16% |
| 6개월 EFS | 31% | 12% (HR 0.55) |

### 3.3 CAR-T 세포 치료

#### CARTITUDE-4 (NCT04181827): Carvykti — 다발성 골수종 2차

BCMA CAR-T, Phase 3 [9]:

| 항목 | Carvykti | 표준 치료(DPd/PVd) | 통계량 |
|------|---------|-------------------|--------|
| PFS | **미도달** | 11.8개월 | HR 0.26 (P<0.001) |
| 30개월 OS율 | **76%** | 64% | HR 0.55 (P=0.0009) |
| ORR | 84.6% | 67.3% | — |
| CR/sCR | 73.1% | 21.8% | — |
| MRD 음성률 | 60.6% | 15.6% | — |

최초로 세포치료가 표준 치료 대비 **전체 생존 이점**을 입증한 Phase 3 시험.

#### CAR-T in 자가면역질환 — 2025년 데이터

CD19 CAR-T의 전신성 홍반 루푸스(SLE) 적용 [10]:

| 항목 | 수치 (145명 메타분석) |
|------|---------------------|
| SLEDAI 점수 변화 | 13.1 → **2.3** (6개월) |
| DORIS 관해율 | **70%** |
| 저질병활성도 | **89%** |
| 약물 중단 후 무약물 관해 | 일부 환자에서 달성 |
| CRS (Grade 1-2) | 56% |
| Grade 3+ CRS | <1% |
| 신경독성 | 3% (혈액암 27%와 대조적) |

#### 알로제닉(기성품) CAR-T: FT819

iPSC 유래 CD19 CAR-T (Fate Therapeutics) [10]:
- SLE 환자 1명이 6개월에 DORIS 및 완전 신장 반응 달성
- 15개월 추적에서 스테로이드 무사용 DORIS 유지
- Off-the-shelf 세포 치료의 자가면역 적용 가능성 입증

### 3.4 mRNA 암 백신

#### KEYNOTE-942/mRNA-4157 (NCT03897881): V940 — 고위험 흑색종

Moderna/Merck의 개인화 mRNA 네오항원 백신 + Pembrolizumab [11]:

| 항목 | V940 + Pembro | Pembro 단독 |
|------|-------------|------------|
| 재발 또는 사망 위험 감소 (RFS) | **49% 감소** (5년 추적) | — |
| 원격 전이 위험 감소 | **65% 감소** (Phase 2b) | — |
| Phase 3 진행 | INTerpath-001 (NCT06197360) | — |
| 예상 규제 제출 | **2026년** | — |

V940은 환자별 종양 네오항원 최대 34종을 코딩하는 맞춤형 mRNA 백신으로, 각 환자의 전체 엑솜/RNA 시퀀싱 → AI 네오항원 예측 → mRNA 합성 → LNP 전달의 워크플로우를 거친다.

---

## 4. 시장 분석

### 4.1 TAM

| 모달리티 | 2025 시장 | 2030 전망 | 2035 전망 | CAGR |
|---------|----------|----------|----------|------|
| 면역관문억제제 | $66.2B | ~$150B | $303.9B | 16.6% |
| 이중특이성 항체 | $11.2B | ~$80B | $448.6B | 44.5% |
| CAR-T 세포치료 | $12.9-20.5B | ~$60B | $193.6-268B | 29.3-29.8% |
| 개인화 암 백신 | $0.2B | ~$2B | $8.5B | 44.9% |

이중특이성 항체의 CAGR 44.5%는 바이오텍 내 최고 성장률이며, 고형암으로의 적응증 확대가 핵심 성장 동인이다.

### 4.2 경쟁 구도

#### 면역관문억제제 시장

| 약물 | 기업 | 연 매출 | 특허 만료 | 전략 |
|------|------|---------|----------|------|
| Keytruda | Merck (MRK) | ~$30B | **2028** | SC 제형, ADC 병용 |
| Opdivo | BMS (BMY) | ~$9B | 2028 | LAG-3 병용 (Opdualag) |
| Tecentriq | Roche (RHHBY) | ~$4B | 2029 | 바이스페시픽 전환 |
| Imfinzi | AZ (AZN) | ~$4B | 2030 | 트레멜리무맙 병용 |
| Libtayo | Regeneron (REGN) | ~$1B | 2032 | 피부암 니치 |

**Keytruda 특허 절벽(2028)**: 바이오시밀러 진입 시 $10B+ 시밀러 시장 형성. Merck의 방어 전략:
- 피하주사(SC) Keytruda 개발 → 새 특허
- Keytruda + ADC(MK-2140) 병용 → 새 적응증
- Keytruda + 차세대 IO 병용

#### CAR-T 시장

| 약물 | 기업 | 표적 | 연 매출 | 적응증 |
|------|------|------|---------|--------|
| Yescarta | Gilead (GILD) | CD19 | ~$2B | DLBCL, FL |
| Carvykti | J&J (JNJ) | BCMA | ~$1.5B | 다발성 골수종 (급성장) |
| Breyanzi | BMS (BMY) | CD19 | ~$0.8B | DLBCL |
| Kymriah | Novartis (NVS) | CD19 | ~$0.5B | ALL, DLBCL |

### 4.3 핵심 투자 테마

1. **Keytruda 후 세계(Post-Keytruda era)**: 2028 특허 만료 후 IO 시장 재편 — 바이오시밀러 vs. 차세대 IO
2. **바이스페시픽의 고형암 확장**: Tarlatamab의 SCLC 성공이 선례 → 다른 고형암 TCE 개발 가속
3. **CAR-T의 자가면역 피봇**: SLE, 경피증 등 자가면역에서의 강력한 데이터 → TAM 재정의
4. **알로제닉 세포치료**: 제조 비용 $300K+ → $30K 이하 목표 → 대중화의 열쇠
5. **mRNA 암 백신 2026-2027 분수령**: V940 Phase 3 결과 → 새로운 모달리티 탄생 여부

---

## 5. AI 적용

### 5.1 TME 프로파일링과 환자 선별

- **다중오믹스 TME 분석**: 단일세포 RNA 시퀀싱(scRNA-seq) + 공간 전사체(spatial transcriptomics) 데이터를 AI가 통합 분석하여 TME 유형 분류
- **IO 반응 예측**: PD-L1 TPS 단독(정확도 ~60%)에서 → AI 기반 다변수 모델(TMB, T세포 염증 서명, HLA 유전형, 장내 미생물 등 통합)로 예측 정확도 80%+ 달성 목표
- **2026년 미국 주요 암센터**: AI 의사결정 지원 도구 도입 → IO 선택/순서 최적화 [2]

### 5.2 바이스페시픽 설계

- **이중표적 조합 발굴**: AI가 TCGA(The Cancer Genome Atlas) + 단일세포 데이터에서 종양 특이적 항원 쌍을 체계적 탐색
- **분자 설계**: 두 팔의 결합력(affinity), 안정성, 제조성을 동시 최적화하는 multi-objective ML 모델
- **면역 시냅스 시뮬레이션**: agent-based 모델링으로 T세포-종양세포 접촉 효율, CRS 위험 예측

### 5.3 CAR 설계 최적화

- **scFv 라이브러리 설계**: De novo AI 생성으로 기존 라이브러리(~10^4) → 가상 라이브러리(~10^12) 탐색
- **공동자극 도메인 엔지니어링**: ML이 CD28/4-1BB 변이체의 T세포 소진(exhaustion) 프로파일 예측
- **제조 최적화**: 바이오리액터 조건(온도, 사이토카인 농도, 확장 기간)을 AI가 실시간 최적화 → T세포 수율/품질 향상

### 5.4 네오항원 예측과 백신 설계

V940/mRNA-4157의 핵심 기술 스택 [11]:
1. **종양 시퀀싱**: WES(whole exome sequencing) + RNA-seq → 체세포 변이 검출
2. **AI 네오항원 예측**: HLA 결합 친화도 예측(NetMHCpan), 면역원성 스코어링, 클로널 빈도 분석
3. **에피토프 우선순위화**: AI가 최대 34개 최적 네오항원 선별
4. **mRNA 코돈 최적화**: AI가 번역 효율 극대화를 위한 코돈 사용 최적화
5. **LNP 제형 최적화**: 이온화 지질, 콜레스테롤, PEG 비율을 ML로 최적화

---

## 6. 참고문헌

[1] Han Y, et al. "Advancing Cancer Treatment: A Review of Immune Checkpoint Inhibitors and Combination Strategies." *Cancers*. 2025;17(9):1408. https://www.mdpi.com/2072-6694/17/9/1408

[2] Ziogas DC, et al. "Overcoming resistance to PD-1 and CTLA-4 blockade mechanisms and therapeutic strategies." *Front Immunol*. 2025;16:1688699. https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2025.1688699/full

[3] Middelburg J, et al. "Trial Watch - bispecific T cell engagers and higher-order multispecific immunotherapeutics." *OncoImmunology*. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12915878/

[4] Ahn MJ, et al. "Tarlatamab for Patients with Previously Treated Small-Cell Lung Cancer." *N Engl J Med*. 2023;389:2063-2075. NCT05060016. https://www.nejm.org/doi/full/10.1056/NEJMoa2307980

[5] Wang Y, et al. "CAR-T cells in solid tumors: Challenges and breakthroughs." *Cell Reports Medicine*. 2025. https://www.cell.com/cell-reports-medicine/fulltext/S2666-3791(25)00426-4

[6] Zhou X, et al. "Emerging advances in CAR-T therapy for solid tumors: latest clinical trial updates from 2025 ASCO annual meeting." *J Hematol Oncol*. 2025;18:1760. https://jhoonline.biomedcentral.com/articles/10.1186/s13045-025-01760-9

[7] Reck M, et al. "Five-Year Outcomes With Pembrolizumab Versus Chemotherapy for Metastatic Non-Small-Cell Lung Cancer With PD-L1 Tumor Proportion Score ≥50%." *J Clin Oncol*. 2021;39:2339-2349. NCT02142738. https://ascopubs.org/doi/10.1200/JCO.21.00174 / Schmid P, et al. "Overall Survival with Pembrolizumab in Early-Stage Triple-Negative Breast Cancer." *N Engl J Med*. 2024. NCT03036488. https://pubmed.ncbi.nlm.nih.gov/39282906/

[8] Wolchok JD, et al. "Long-Term Outcomes With Nivolumab Plus Ipilimumab or Nivolumab Alone Versus Ipilimumab in Patients With Advanced Melanoma (CheckMate 067)." *J Clin Oncol*. 2022. NCT01844505.

[9] San-Miguel J, et al. "Ciltacabtagene autoleucel versus standard of care in lenalidomide-refractory multiple myeloma (CARTITUDE-4)." *N Engl J Med*. 2024. NCT04181827. https://www.jnj.com/media-center/press-releases/carvykti-is-the-first-and-only-cell-therapy-to-significantly-extend-overall-survival-versus-standard-therapies-for-patients-with-multiple-myeloma-as-early-as-second-line

[10] Mackensen A, et al. "CAR-T cell therapy in systemic lupus erythematosus." ACR Convergence 2025 analysis (145 patients, 16 studies). https://rheumatology.org/press-releases/car-t-cell-therapies-show-promise-for-autoimmune-disease-at-acr-convergence-2025 / Nature Cell Research. "Allogeneic anti-CD19 CAR-T cells induce remission in refractory systemic lupus erythematosus." 2025. https://www.nature.com/articles/s41422-025-01128-1

[11] Merck/Moderna. "5-Year Data for Intismeran Autogene in Combination With KEYTRUDA: Sustained Improvement in RFS." January 2026. NCT03897881. https://www.merck.com/news/moderna-merck-announce-5-year-data-for-intismeran-autogene-in-combination-with-keytruda-pembrolizumab-demonstrated-sustained-improvement-in-the-primary-endpoint-of-recurrence-free-survival-i/

[12] Li Q, et al. "Chimeric Antigen Receptor T Cell Therapy in Systemic Lupus Erythematosus: Mechanisms, Clinical Advances, and Future Directions — a Comprehensive Review." *PMC*. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12660391/

[13] Amgen. "Tarlatamab Sustained Clinical Benefit and Safety in Previously Treated SCLC: DeLLphi-301 Extended Follow-up." *J Thorac Oncol*. 2024. https://www.sciencedirect.com/science/article/pii/S1556086424009316

[14] Novaone Advisor. "Personalized Cancer Vaccine Market $8.5B by 2034." https://www.novaoneadvisor.com/report/personalized-cancer-vaccine-market

[15] GM Insights. "Immune Checkpoint Inhibitors Market Growth 2026-2035." https://www.gminsights.com/industry-analysis/immune-checkpoint-inhibitors-market

---

> **면책조항**: 본 리뷰는 기술적 분석 목적으로 작성되었으며, 특정 종목의 매수/매도를 권유하지 않습니다. 투자 결정은 전문가 자문을 통해 독립적으로 이루어져야 합니다.
