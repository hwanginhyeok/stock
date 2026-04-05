# 바이오 기술 리뷰 #10: 합성생물학 — 기전, 임상 데이터, 투자 분석

> **Technical Review Series** | 2026-04-05
> 합성생물학(Synthetic Biology)의 DNA 조립 방법론, 유전자 회로 설계 원리, 대사 플럭스 분석,
> 무세포 시스템, 임상 파이프라인, 시장 전망, 그리고 AI 통합 현황을 학술적 수준에서 종합 분석한다.

---

## 1. 기술 개요: 합성생물학의 분자적 기전

합성생물학은 생물학적 시스템을 공학적 원리(모듈화, 표준화, 추상화)로 설계·구축·테스트하는 학제간 분야이다. 전자공학의 회로 설계 패러다임을 생물학에 적용하여, DNA를 "코드"로, 세포를 "하드웨어"로 간주하는 **설계-구축-테스트-학습(Design-Build-Test-Learn, DBTL)** 사이클을 핵심 방법론으로 채택한다[1].

### 1.1 합성생물학의 계층 구조

합성생물학은 다음의 추상화 계층을 따른다:

```
DNA 부품(Parts) → 장치(Devices) → 시스템(Systems) → 세포 공장(Cell Factory)
     ↓                  ↓               ↓                    ↓
프로모터, RBS,      토글 스위치,     대사 경로,          미생물 약물 생산,
터미네이터         오실레이터       신호 전달 네트워크    바이오센서 세포
```

각 계층의 부품은 표준화된 인터페이스(BioBrick, MoClo, CIDAR)를 통해 조합 가능하며, 이것이 합성생물학을 전통적 유전공학과 구분하는 핵심이다.

### 1.2 합성생물학의 중심 교리: DBTL 사이클

Ginkgo Bioworks의 바이오파운드리는 DBTL 사이클의 산업적 구현을 대표한다[2]:

1. **Design**: 표적 기능(약물 생산, 센서 등)을 수행할 유전자 회로/대사 경로 설계
2. **Build**: DNA 합성 + 조립(Gibson, Golden Gate) → 세포에 형질전환
3. **Test**: 고속 스크리닝(HTS), 대사체 분석, 표현형 측정
4. **Learn**: 데이터 분석 → ML 모델 학습 → 다음 사이클 설계 개선

Ginkgo의 파운드리(290,000+ sq. ft, BSL2)에서는 **10-18일 사이클**로 수만 건의 DBTL 반복을 병렬 수행하며, 이는 학술 시설의 30-60일 대비 3-6배 빠르다.

---

## 2. 핵심 기술 세부

### 2.1 DNA 조립 방법론

합성생물학의 물리적 기반은 DNA 단편의 정밀한 조립이다. 전통적 제한효소/라이게이스 클로닝의 한계를 극복하는 현대적 방법론이 핵심이다.

#### Gibson Assembly

Gibson 등이 2009년 *Nature Methods*에 보고한 등온 조립법(isothermal assembly)으로, 단일 튜브, 단일 온도(50도C)에서 다수의 DNA 단편을 심리스(seamless)하게 접합한다[3].

**반응 메커니즘 (3효소 시스템)**:
1. **T5 엑소뉴클레아제**: 각 DNA 단편의 5' 말단을 씹어내어(chew back) 3' 단일가닥 돌출부(overhang) 생성
2. **Phusion DNA 폴리머라제**: 돌출부 간 상보적 어닐링 후, 갭을 채움(gap filling)
3. **Taq DNA 리가아제**: 닉(nick)을 봉합하여 완전한 이중가닥 DNA 생성

**장점**: 제한효소 인식 서열 불필요(scarless), 15-30bp 중복(overlap) 영역만 필요
**최적 범위**: 2-5개 단편, 총 15kb 이하
**한계**: 단편 수 증가 시 효율 급감, 반복 서열에 취약

#### Golden Gate Assembly

Type IIS 제한효소(BsaI, BpiI 등)를 이용한 방향성 조립법이다[4]. Type IIS 효소는 인식 서열 외부를 절단하여 사용자 정의 4bp 돌출부를 생성하므로, **단일 반응에서 최대 52개 단편**의 방향성 조립이 가능하다.

**반응 메커니즘**:
1. Type IIS 제한효소가 인식 서열 외부를 비대칭 절단
2. 각 단편에 고유한 4bp 돌출부가 생성 (방향성 보장)
3. T4 DNA 리가아제가 상보적 돌출부를 접합
4. 효소 절단 + 라이게이션을 동시에 수행(one-pot cycling) → 효율 극대화

**장점**: 높은 정확도(>95%), 다수 단편 동시 조립, 모듈형 표준(MoClo, GoldenBraid)과 호환
**한계**: Type IIS 인식 서열이 삽입물 내부에 존재하면 문제 발생 (domestication 필요)

#### Gibson vs Golden Gate 비교

| 특성 | Gibson Assembly | Golden Gate Assembly |
|------|----------------|---------------------|
| 원리 | 등온 엑소뉴클레아제 | Type IIS 제한효소 |
| 온도 | 50도C 등온 | 37도C/16도C 사이클링 |
| 최적 단편 수 | 2-5개 | 6-52개 |
| Scarless 여부 | 예 | 아니오 (4bp scar) |
| 방향성 | 중복 서열 의존 | 돌출부 서열로 보장 |
| 표준화 | 중간 | 높음 (MoClo 호환) |
| 대규모 조립 적합성 | 낮음 | 높음 |

### 2.2 유전자 회로 설계

합성생물학의 정보 처리 단위는 **유전자 회로(genetic circuit)**이다. 전자 회로의 논리 게이트에 비유되며, 전사인자, RNA, 단백질 분해 등을 논리 요소로 활용한다.

#### 토글 스위치 (Toggle Switch)

Gardner, Cantor, Collins가 2000년 *Nature*에 보고한 합성 양안정(bistable) 스위치이다[5]. 두 개의 억제 전사인자(repressor)가 서로의 발현을 억제하는 상호 억제(mutual repression) 구조로, 전자공학의 SR 래치에 해당한다.

**분자적 구조**:
- **Repressor A** (예: LacI): Promoter B를 억제
- **Repressor B** (예: λcI): Promoter A를 억제
- 외부 자극(inducer)으로 한쪽 억제를 해제하면 반대쪽이 우세해져 상태 전환

**핵심 설계 조건** (양안정성 유지):
1. 두 프로모터의 강도가 유사해야 함
2. 단백질 분해 속도의 균형 필요
3. 양성 피드백(positive cooperativity) — Hill 계수 > 1

**응용**: 합성 메모리 유닛, 바이오제약 생산 ON/OFF 스위치, CAR-T 세포의 안전 스위치

#### 리프레실레이터 (Repressilator)

Elowitz와 Leibler가 2000년 *Nature*에 보고한 합성 오실레이터이다[6]. 세 개의 억제 전사인자가 **순환 억제 네트워크(cyclic repression network)**를 형성:

```
LacI ⊣ TetR ⊣ λcI ⊣ LacI
```

각 억제인자가 후속 억제인자의 발현을 억제하며, 이 순환 구조가 진동(oscillation) 행동을 생성한다. 초기 리프레실레이터는 노이즈가 크고 진동이 불규칙했으나, 회로 복잡성 감소와 유전자 발현 노이즈 저감 요소 도입으로 수백 세대에 걸쳐 지속적 진동을 유지하는 **강건한 오실레이터**가 구축되었다.

**최신 발전**: CRISPRi (dCas9) 기반의 토글 스위치 및 리프레실레이터가 구현되어, 전사인자 대신 가이드 RNA 교체만으로 표적 유전자를 전환할 수 있는 유연한 회로 설계가 가능해졌다[7].

### 2.3 대사 플럭스 분석 (Metabolic Flux Analysis, MFA)

미생물 세포 공장의 성능 최적화를 위해 대사 네트워크 내 물질 흐름을 정량하는 기법이다.

#### 제약 기반 모델링 (Constraint-Based Modeling)

- **화학양론적 행렬(Stoichiometric matrix) S**: 대사 네트워크의 모든 반응을 행렬로 표현
- **정상 상태 가정**: S · v = 0 (대사체 농도 변화율 = 0)
- **플럭스 균형 분석(FBA)**: 선형 계획법으로 목적 함수(보통 바이오매스 생산) 최대화하는 플럭스 분포 계산

Varnerlab의 E. coli 무세포 단백질 합성(CFPS) 모델은 해당과정, 오탄당인산경로, 에너지 대사, 아미노산 생합성/분해를 포함하는 코어 대사 네트워크에 서열 특이적 전사/번역 기술을 통합하였다[8]. 63개 대사체의 시간 분해 절대 농도 측정치와 효소 동역학 정보를 결합하여 단백질 생산의 동적 플럭스 진화를 시뮬레이션한다.

### 2.4 무세포 시스템 (Cell-Free Systems)

무세포 단백질 합성(CFPS)은 살아있는 세포 없이 전사/번역 기구만으로 단백질을 생산하는 시스템이다.

**핵심 구성요소**:
- 세포 추출물(lysate): 리보솜, tRNA, 아미노아실-tRNA 합성효소 등 번역 기구
- 에너지 재생 시스템: ATP, GTP 공급 (PEP, creatine phosphate 등)
- 주형 DNA/mRNA: 표적 단백질 유전자

**장점**:
1. 비자연 아미노산(ncAA) 도입 용이
2. 독성 단백질 생산 가능 (세포 생존 불필요)
3. 반응 조건 직접 조절 가능
4. 프로토타이핑 속도: 수 시간 내 결과 확인

**응용**: 바이오센서 프로토타이핑, point-of-care 진단, 교육/연구, 대사 경로 프로토타이핑

---

## 3. 임상 데이터

### 3.1 Absci + Twist: AI 기반 de novo 항체 설계

Absci Corporation과 Twist Bioscience는 2024년 10월 생성 AI를 활용한 신규 치료 항체 공동 설계 협력을 발표하였다[9].

**핵심 파이프라인 (Absci)**:
- **ABS-101** (anti-TL1A 항체): 염증성 장질환(IBD) 치료 — 2025년 5월 건강 자원자 대상 무작위배정 Phase 1 시험 개시
- **ABS-201** (anti-PRLR 항체): 안드로겐성 탈모증 — 비인간 영장류 데이터 확보, 2025년 12월 Phase 1/2a 계획

**기술적 혁신**: Absci의 생성 AI 플랫폼은 동물 면역화(immunization) 과정 없이 표적에 결합하는 항체를 처음부터(de novo) 설계한다. 주당 수십억 개 세포를 스크리닝하여 AI 설계 항체에서 습식 실험 검증 후보까지 **6주 내 도출** 가능하다.

### 3.2 Ginkgo Bioworks: 바이오파운드리 플랫폼

Ginkgo의 바이오파운드리 실적[2]:
- **290,000+ sq. ft** BSL2 파운드리
- **DBTL 사이클**: 10-18일 (학술 30-60일 대비)
- **응용 분야**: 바이오제약, 농업, 식품, 산업 화학
- **파이프라인**: Advanced Medicine Partners를 통한 바이러스 벡터 GMP 생산 (2025 Q1)

### 3.3 Codexis: 효소 공학의 임상적 성공

Codexis의 CodeEvolver 플랫폼은 지향 진화(directed evolution)를 통해 의약품 제조용 효소를 최적화한다[10].

**대표 사례 — Novartis Entresto (Sacubitril)**:
- 심부전 치료제 sacubitril의 키랄 아미노산 중간체 합성용 트랜스아미나제 개발
- 초기 효소: 원하는 부분입체이성체에 대해 미량의 활성만 존재
- 1회 엔지니어링으로 원하는 선택성의 효소 확인
- 이후 **10라운드의 진화**: 활성 **500,000배** 향상, 기질 내성, 열안정성 개선
- 최종 효소: 26개 아미노산 돌연변이 포함
- Codexis 효소가 적용된 상용 제품: **50개 이상**

### 3.4 CAR-T 세포의 합성생물학적 안전 장치

합성생물학 유전자 회로가 세포 치료에 적용된 사례:

| 안전 장치 | 메커니즘 | 임상 적용 |
|----------|---------|----------|
| 자살 유전자 (iCasp9) | AP1903 투여 시 caspase-9 이합체화 → 세포 사멸 | Bellicum Phase 1/2 |
| ON 스위치 | 소분자 약물 존재 시에만 CAR 활성화 | Calibr/AbbVie Phase 1 |
| 산소 감지 회로 | 저산소 종양 미세환경에서만 활성화 | 전임상 |
| 항원 논리 게이트 (AND) | 두 항원 동시 존재 시에만 활성화 | Kite Pharma 전임상 |

### 3.5 Synlogic: 합성 생체 치료제 (Synthetic Biotic Medicines)

Synlogic의 SYNB1618은 페닐케톤뇨증(PKU) 치료를 위해 E. coli Nissle 1917에 페닐알라닌 분해 경로(PAL + LAAD)를 장착한 합성 생체 치료제이다.

**Phase 2 결과 (NCT04015570)**:
- 혈중 페닐알라닌 농도의 용량 의존적 감소 확인
- 그러나 Synlogic은 2023년 재정적 어려움으로 운영 중단 — 합성생물학 치료제 상업화의 어려움을 보여주는 사례

---

## 4. 시장 분석

### 4.1 시장 규모 및 성장률

| 연도 | 시장 규모 | CAGR | 출처 |
|------|----------|------|------|
| 2024 | $19.9B | — | Straits Research |
| 2025 | $23.6-23.9B | — | 다수 |
| 2030 | $42-66B | 21.6% | Grand View Research |
| 2033 | $53.1B | ~11% | Straits Research |

시장 규모 추정치의 편차(2030 기준 $42-66B)는 합성생물학의 범위 정의에 따라 달라진다. 좁은 정의(DNA 합성, 유전자 편집 도구)에서 넓은 정의(바이오제조, 세포 치료 포함)까지 스펙트럼이 넓다.

### 4.2 경쟁 환경

#### 플랫폼 기업 ("삽과 곡괭이")

| 기업 | 티커 | 포지셔닝 | 매출 (FY2025) | 시가총액 |
|------|------|---------|--------------|---------|
| Twist Bioscience | TWST | 실리콘 기반 DNA 합성 | ~$300M | ~$4B |
| Ginkgo Bioworks | DNA | 세포 프로그래밍 파운드리 | ~$250M | ~$1.5B |
| Thermo Fisher | TMO | 합성생물학 인프라/시약 | $44B+ (전체) | ~$200B |

#### AI + 합성생물학

| 기업 | 티커 | 기술 | 단계 |
|------|------|------|------|
| Absci | ABSI | AI de novo 항체 설계 | Phase 1 (ABS-101) |
| Codexis | CDXS | AI 지향 진화 효소 공학 | 50+ 상용 제품 |
| GenScript | 1548.HK | CRO + 합성생물학 서비스 | 매출 $800M+ |

#### 리스크 사례: Amyris 파산

Amyris(합성생물학 소비재 기업)는 2023년 Chapter 11 파산 — 기술적 우수성에도 불구하고 스케일업, 마진 관리, 시장 채택에서 실패하였다. 합성생물학 기업의 **기술 리스크보다 사업 모델 리스크가 더 크다**는 교훈.

### 4.3 세그먼트별 기회

| 세그먼트 | TAM (2030E) | 성숙도 | 대표 기업 |
|---------|-------------|--------|----------|
| DNA 합성/조립 | $5-8B | 상업화 | Twist, GenScript |
| 효소 공학 | $3-5B | 상업화 | Codexis, Novozymes |
| 바이오제약 응용 | $10-15B | 초기-중기 | Absci, Ginkgo |
| 농업/식품 | $5-10B | 초기 | Ginkgo, Pivot Bio |
| 산업 화학 | $5-8B | 초기 | LanzaTech, Genomatica |

---

## 5. AI 적용

### 5.1 AI 기반 유전자 회로 설계

- **자동화 설계**: Cello(MIT) 등의 소프트웨어가 원하는 논리 기능의 유전자 회로를 자동 설계하며, 최신 버전은 부품 간 상호작용(context dependency)까지 고려한다
- **노이즈 하 최적화**: 확률적 시뮬레이션(Gillespie algorithm)과 결합한 ML 최적화로, 분자 노이즈 존재 하에서도 강건한 회로 성능 보장[7]

### 5.2 AI 기반 대사 경로 최적화

- **대사 플럭스 예측**: 그래프 신경망(GNN)으로 대사 네트워크의 플럭스 분포 예측 — FBA 대비 10-100배 빠른 추론
- **최적 경로 탐색**: 강화학습으로 수천 가지 대사 경로 조합 중 목표 산물 수율을 최대화하는 경로 자동 선택
- **레트로신테시스(retrosynthesis)**: 목표 화합물에서 출발하여 효소 반응을 역추적하는 AI 시스템

### 5.3 AI de novo 단백질 설계

AlphaFold 이후, 생성 AI(generative AI)를 활용한 자연에 존재하지 않는 단백질의 de novo 설계가 합성생물학의 차세대 프론티어로 부상하였다.

- **RFdiffusion** (David Baker 연구실): 확산 모델로 단백질 백본 구조 생성
- **ProteinMPNN**: 설계된 백본에 최적 아미노산 서열 할당
- **Absci IgDesign**: 항체의 CDR(상보성결정영역)을 de novo 생성 — 동물 면역화 완전 대체

### 5.4 DBTL 사이클 자동화

Ginkgo, Zymergen(현 Ginkgo 인수) 등의 바이오파운드리에서는 **로봇 + AI**로 DBTL 사이클을 자동화한다:
- 액체 핸들링 로봇이 수천 건의 실험을 병렬 수행
- ML 모델이 실험 결과를 학습하여 다음 사이클의 설계를 제안
- 능동 학습(active learning)으로 실험 공간을 효율적으로 탐색

---

## 6. 투자 시사점

### 6.1 핵심 투자 테제

1. **플랫폼 > 응용**: 응용 기업의 실패(Amyris, Synlogic)가 반복되는 반면, 플랫폼/인프라(Twist, TMO)는 안정적 성장
2. **AI + 합성생물학 = 최강 시너지**: Absci의 6주 항체 파이프라인이 전통 18-24개월을 대체할 잠재력
3. **제약 응용이 최고 가치**: 소비재/산업 화학 대비 치료제 응용의 마진과 지적재산 가치가 압도적
4. **상업적 검증이 핵심**: 기술 우수성만으로는 투자 성공 불가 — 매출, 마진, 고객 채택 확인 필수
5. **대형 인프라 기업이 안전한 배팅**: Thermo Fisher(TMO), Danaher(DHR)는 합성생물학 성장의 수혜

### 6.2 투자 전략 매트릭스

| 시계 | 전략 | 대표 종목 |
|------|------|----------|
| 단기 (1-3년) | 매출 성장 기업 | Twist (TWST), Codexis (CDXS) |
| 중기 (3-5년) | AI + 바이오 임상 진입 | Absci (ABSI), GenScript (1548.HK) |
| 장기 (5-10년) | 파운드리 플랫폼 | Ginkgo (DNA) |
| 인프라 | 삽과 곡괭이 | Thermo Fisher (TMO), Danaher (DHR) |

---

## 참고문헌

[1] Cameron DE, Bashor CJ, Collins JJ. "A brief history of synthetic biology." *Nature Reviews Microbiology*. 2014;12:381-390. doi:10.1038/nrmicro3239.

[2] Ginkgo Bioworks. "Automated Foundry and DBTL Platform Capabilities." https://www.ginkgo.bio/ ; Ginkgo Bioworks IARPA Capability Profile. https://www.iarpa.gov/images/PropsersDayPDFs/TEI-REX/GinkgoBioworks_CapabilitiesProfile.pdf

[3] Gibson DG, et al. "Enzymatic assembly of DNA molecules up to several hundred kilobases." *Nature Methods*. 2009;6:343-345. doi:10.1038/nmeth.1318.

[4] Potapov V, et al. "A User's Guide to Golden Gate Cloning Methods and Standards." *ACS Synthetic Biology*. 2023;12(11):3109-3121. doi:10.1021/acssynbio.2c00355. https://pubs.acs.org/doi/10.1021/acssynbio.2c00355

[5] Gardner TS, Cantor CR, Collins JJ. "Construction of a genetic toggle switch in Escherichia coli." *Nature*. 2000;403:339-342. doi:10.1038/35002131.

[6] Elowitz MB, Leibler S. "A synthetic oscillatory network of transcriptional regulators." *Nature*. 2000;403:335-338. doi:10.1038/35002125.

[7] Arenas-Sanz A, et al. "Genetic circuits in synthetic biology: broadening the toolbox of regulatory devices." *Frontiers in Synthetic Biology*. 2025. doi:10.3389/fsybi.2025.1548572. https://www.frontiersin.org/journals/synthetic-biology/articles/10.3389/fsybi.2025.1548572/full

[8] Vilkhovoy M, et al. "Sequence Specific Modeling of E. coli Cell-Free Protein Synthesis." *ACS Synthetic Biology*. 2018;7(8):1844-1857. doi:10.1021/acssynbio.7b00465. https://pubs.acs.org/doi/10.1021/acssynbio.7b00465

[9] Absci Corporation & Twist Bioscience. "Absci and Twist Bioscience Collaborate to Design Novel Antibody using Generative AI." GlobeNewswire. 2024-10-31. https://www.globenewswire.com/news-release/2024/10/31/2972557/0/en/Absci-and-Twist-Bioscience-Collaborate-to-Design-Novel-Antibody-using-Generative-AI.html

[10] Huffman MA, et al. "The Evolving Nature of Biocatalysis in Pharmaceutical Research and Development." *JACS Au*. 2023;3(5):1201-1212. doi:10.1021/jacsau.2c00712. https://pmc.ncbi.nlm.nih.gov/articles/PMC10052283/

[11] Dela Pena Silva R, et al. "A comparative review of DNA assembly strategies: From traditional to modern." *Journal of Biotechnology*. 2025. doi:10.1016/j.jbiotec.2025. https://www.sciencedirect.com/science/article/abs/pii/S2452014425002493

[12] Principles of Genetic Circuit Design. *ACS Synthetic Biology*. 2014. https://pmc.ncbi.nlm.nih.gov/articles/PMC4230274/

[13] Varner JD, et al. "Dynamic Sequence Specific Constraint-Based Modeling of Cell-Free Protein Synthesis." *Processes*. 2018;6(8):132. doi:10.3390/pr6080132. https://www.mdpi.com/2227-9717/6/8/132

[14] Synthetic biology: applications come of age. *Nature Reviews Genetics*. 2010;11:367-379. https://www.nature.com/articles/nrg2775

---

*본 리뷰는 투자 권유가 아닌 기술 분석 목적으로 작성되었습니다. 투자 결정은 개인의 판단과 책임 하에 이루어져야 합니다.*
