# 바이오 기술 리뷰 #14: 메타볼로믹스 & 정밀영양 — 기전, 임상 데이터, 투자 분석

> **Nature Reviews Drug Discovery** 스타일 기술 리뷰
> 작성일: 2026-04-05

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

### 1.1 메타볼로믹스의 정의와 위치

메타볼로믹스(metabolomics)는 생물학적 시스템 내 저분자 대사물질(metabolites, 분자량 <1,500 Da)의 전체 프로파일을 체계적으로 측정하고 분석하는 오믹스 학문이다. 유전체학(genomics)이 "청사진"을, 전사체학(transcriptomics)이 "지시서"를, 단백질체학(proteomics)이 "기계"를 분석한다면, 메타볼로믹스는 **"표현형의 최종 산출물"**을 직접 측정한다. 이는 메타볼로믹스가 유전자-환경 상호작용의 통합적 결과를 가장 직접적으로 반영하는 오믹스 계층이라는 점에서 정밀의학(precision medicine)과 정밀영양(precision nutrition)의 핵심 기술로 부상한 이유다.

### 1.2 정밀영양의 과학적 기반

정밀영양은 **"같은 음식도 사람마다 다르게 대사한다"**는 관찰에 기반한다. Berry 등(2020)의 PREDICT 1 연구는 1,002명의 참가자에서 표준화된 식사에 대한 식후 반응의 **개인 간 변이**가 중성지방 103%, 포도당 68%, 인슐린 59%에 달함을 정량적으로 입증했다. 이 변이의 원인은 유전적 요인(포도당 반응 분산의 9.5%), 장내 마이크로바이옴(지질 반응의 7.1%), 식사 조성(지질 반응의 3.6%), 수면, 운동, 식사 타이밍 등 생활습관 요인이 복합적으로 작용한 결과다.

이러한 발견은 전통적 "하나의 영양 권고가 모든 사람에게 적합하다"는 가정의 한계를 분자적 수준에서 입증하며, 개인의 대사 프로파일에 기반한 맞춤형 식이 권고의 과학적 정당성을 제공한다.

### 1.3 멀티오믹스 통합의 필요성

단일 오믹스 계층의 분석만으로는 대사적 표현형의 복잡성을 포착할 수 없다. 현대 정밀영양은 다음 데이터 계층을 통합한다:

- **유전체(Genomics)**: SNP 기반 유전적 소인 — MTHFR, FTO, APOE 다형성
- **전사체(Transcriptomics)**: 유전자 발현의 동적 변화
- **단백질체(Proteomics)**: 효소 활성 및 신호전달 단백질 수준
- **대사체(Metabolomics)**: 최종 대사 산출물의 직접 측정
- **마이크로바이옴(Microbiome)**: 장내 미생물의 대사 기여 (단쇄지방산, 담즙산 변환 등)

이 멀티오믹스 데이터를 통합 분석하는 것이 정밀영양 2.0의 핵심이며, 이를 가능하게 하는 것이 AI와 기계학습 알고리즘이다.

---

## 2. 핵심 기술 세부

### 2.1 질량분석 플랫폼 (Mass Spectrometry Platforms)

#### 2.1.1 LC-MS/MS (Liquid Chromatography-Tandem Mass Spectrometry)

LC-MS/MS는 메타볼로믹스의 **골드 스탠다드** 플랫폼이다. 그 분석 원리는 다음과 같다:

**액체 크로마토그래피(LC) 분리**: 복합 생물학적 시료(혈장, 소변, 조직 추출물)의 대사물질들을 물리화학적 특성(극성, 크기, 전하)에 따라 분리한다. 역상(reverse-phase, C18) 컬럼은 중간-비극성 대사물질 분리에, HILIC(Hydrophilic Interaction Liquid Chromatography) 컬럼은 극성 대사물질 분리에 최적화된다. UHPLC(Ultra-High Performance LC)는 sub-2 um 입자 컬럼을 사용하여 분해능과 처리 속도를 획기적으로 향상시켰다.

**탠덤 질량분석(MS/MS) 검출**: 분리된 대사물질은 이온화 후 질량/전하비(m/z)로 검출된다:

1. **이온화**: ESI(Electrospray Ionization)가 가장 보편적. 용액 상태의 분석물을 미세 액적으로 분무하고, 용매 증발과 함께 이온화. 양이온 모드(양성자 첨가, [M+H]+)와 음이온 모드(양성자 제거, [M-H]-)로 분석하여 커버리지를 극대화한다.
2. **MS1 스캔**: 이온화된 분자를 m/z로 분리. Orbitrap 분석기는 >100,000의 질량 분해능(resolving power)을 달성하여 정확한 분자식 결정이 가능하다.
3. **충돌 유도 해리(CID, Collision-Induced Dissociation)**: 전구이온(precursor ion)을 불활성 기체(N2, Ar)와 충돌시켜 특이적 단편이온(fragment ion) 생성
4. **MS2 스캔**: 단편이온 패턴으로 분자 구조 확인 — 이 단편화 스펙트럼이 대사물질의 "지문(fingerprint)"으로 기능

**데이터 획득 모드**:
- **DDA (Data-Dependent Acquisition)**: MS1에서 가장 강한 이온을 선택하여 MS2 수행 — 높은 감도, 포괄성 제한적
- **DIA (Data-Independent Acquisition, SWATH)**: 모든 이온을 일정 m/z 윈도우로 순차 단편화 — 높은 재현성, 디컨볼루션 어려움
- **MRM/SRM (Multiple/Selected Reaction Monitoring)**: 특정 전구이온→단편이온 전이(transition)만 모니터링 — 최고 감도, 표적 대사물질 정량에 최적

LC-MS/MS의 감도는 femtomole (10^-15 mol) 수준에 도달하며, 선형 동적 범위는 4-6 자릿수(orders of magnitude)에 이른다. 2024년 Analytical Chemistry에 보고된 바에 따르면, 단일 LC-MS/MS 플랫폼으로 혈장 내 **235개 대사물질의 동시 정량**이 검증되었다.

#### 2.1.2 GC-MS (Gas Chromatography-Mass Spectrometry)

GC-MS는 **휘발성 및 열안정성** 대사물질의 분석에 특화된다:

- 시료 전처리: 비휘발성 대사물질(아미노산, 유기산, 당류)의 유도체화(derivatization) — 실릴화(TMS, BSTFA), 메톡시화(MOX) 등
- 분리: 모세관 컬럼(capillary column, 30-60 m)에서 끓는점 기반 분리
- 이온화: EI (Electron Ionization, 70 eV) — 재현성 높은 단편화 패턴 생성, 라이브러리 검색에 최적
- 검출: 사중극자(quadrupole) 또는 TOF(Time-of-Flight)

GC-MS의 강점은 EI 스펙트럼의 **높은 재현성**으로, NIST 라이브러리(300,000+ 화합물)와의 직접 비교가 가능하다. 그러나 유도체화 필요, 열불안정 화합물 분석 불가, 고분자량 대사물질 분석 한계 등의 제약이 있어, 현대 메타볼로믹스에서는 LC-MS/MS가 주류 플랫폼이 되었다.

#### 2.1.3 NMR (Nuclear Magnetic Resonance) 기반 메타볼로믹스

NMR은 질량분석에 비해 감도가 1-2 자릿수 낮지만 다음 고유 장점을 보유한다:
- **비파괴적(non-destructive)** 분석: 시료 회수 가능
- **절대 정량**: 내부 표준 없이 직접 정량 가능
- **높은 재현성**: 기기 간, 시간 간 재현성이 우수하여 대규모 역학 연구에 적합
- **시료 전처리 최소화**: 혈장/소변 희석 후 직접 측정 가능

Bruker의 IVDr (In Vitro Diagnostics research) 플랫폼은 혈장 NMR 메타볼로믹스를 표준화하여, 리포단백질 서브클래스, 아미노산, 지방산 등 약 150개 바이오마커의 자동화된 정량을 제공한다.

### 2.2 대사물질 데이터베이스

#### 2.2.1 HMDB (Human Metabolome Database)

HMDB는 인간 대사체의 **가장 포괄적인 참조 데이터베이스**다. 2022년 *Nucleic Acids Research*에 발표된 HMDB 5.0은 다음 규모를 포함한다:

- **217,920개 대사물질 항목**: 이전 버전(114,100)에서 약 2배 확장
- 각 항목에 화학 구조, 물리화학적 특성, 농도 참조값(정상/질병), 조직/체액 분포, 질병 연관성, 효소 반응, 대사 경로, MS/MS 및 NMR 스펙트럼 정보 포함
- 예측 MS 스펙트럼, 보유 지수(retention index), 충돌 단면적(collision cross section) 데이터의 대규모 추가
- KEGG, Reactome 등 일반 대사 데이터베이스와 달리, HMDB는 **임상적 맥락**(질병 연관 농도, 바이오마커 상태)을 제공하는 것이 차별점

#### 2.2.2 METLIN

METLIN은 Scripps Research Institute에서 운영하는 **실험적 MS/MS 스펙트럼 데이터베이스**로, 다음 특징을 가진다:

- **960,000+ 분자**의 MS/MS 스펙트럼 보유
- 양이온/음이온 모드, 다양한 충돌 에너지(CE: 10, 20, 40 eV)에서의 실험적 단편화 스펙트럼 제공
- **METLIN-CCS**: Ion Mobility Spectrometry 기반 충돌 단면적 데이터 추가
- 미지 대사물질의 구조 추정에 HMDB 대비 우수한 스펙트럼 매칭 능력

두 데이터베이스는 상호 보완적으로 사용된다: HMDB는 생물학적 해석과 임상 맥락에, METLIN은 미지 화합물 동정에 강점을 가진다.

#### 2.2.3 기타 주요 데이터베이스

- **MassBank**: 오픈소스 고해상도 MS 스펙트럼 데이터베이스 (일본 기원, 국제 컨소시엄 운영)
- **mzCloud**: Thermo Fisher 운영, 고해상도 다단계 MS 스펙트럼
- **GNPS (Global Natural Products Social Molecular Networking)**: 분자 네트워킹 기반 미지 화합물 탐색

### 2.3 CGM (Continuous Glucose Monitor) 센서 기술

#### 2.3.1 CGM의 작동 원리

CGM은 피하 간질액(interstitial fluid)의 포도당 농도를 **연속적으로 실시간 측정**하는 전기화학 바이오센서다. 핵심 구성 요소:

**효소 전극(Enzyme Electrode)**:
- 백금(Pt) 작업전극(working electrode) 위에 **포도당 산화효소(glucose oxidase, GOx)**가 고정화
- 반응: Glucose + O2 → [GOx] → Gluconolactone + H2O2
- 생성된 H2O2가 백금 전극에서 산화: H2O2 → O2 + 2H+ + 2e-
- 이 전류(amperometric signal)가 포도당 농도에 비례

**간섭 제거 막**: 아스코르브산, 요산, 아세트아미노펜 등 전기활성 간섭물질을 차단하는 폴리머 막(Nafion, cellulose acetate)

**데이터 전송**: 센서 → NFC 또는 Bluetooth → 스마트폰 앱. 측정 간격은 제품마다 다르나 통상 1-5분.

#### 2.3.2 주요 CGM 제품과 기술 사양

| 제품 | 제조사 | 착용 기간 | 보정 필요 | 정확도 (MARD) |
|------|--------|----------|----------|--------------|
| FreeStyle Libre 3 | Abbott | 14일 | 불필요 (공장 보정) | 7.9% |
| Dexcom G7 | Dexcom | 10일 | 불필요 | 8.2% |
| Guardian 4 | Medtronic | 7일 | 불필요 | 8.7% |
| Stelo (비당뇨) | Dexcom | 15일 | 불필요 | ~9% |

MARD(Mean Absolute Relative Difference)는 참조값(정맥혈 포도당) 대비 CGM 측정값의 평균 절대 상대 오차로, 10% 미만이면 임상적으로 정확하다고 간주한다.

#### 2.3.3 비당뇨인 건강관리 확장

Dexcom Stelo와 Abbott Lingo는 **비당뇨인 건강/웰니스 시장**을 대상으로 한 OTC(처방전 불필요) CGM이다. 이 시장 확장의 의미:
- 개인의 식후 혈당 반응(postprandial glycemic response, PPGR) 실시간 모니터링
- 개인화된 식이 권고의 데이터 기반 제공
- ZOE, DayTwo 등 정밀영양 플랫폼의 핵심 입력 데이터

### 2.4 식후 혈당 반응(Postprandial Glycemic Response) 모델링

#### 2.4.1 PPGR의 생리학

식사 후 혈당 반응은 다음 요인들의 복합적 상호작용으로 결정된다:

- **식사 구성**: 탄수화물 함량/유형(단당류 vs 복합 탄수화물), 지방(위 배출 지연), 단백질(인슐린 분비 자극), 식이섬유(위장관 통과 속도)
- **식사 순서**: 채소→단백질→탄수화물 순서가 탄수화물→나머지 순서 대비 혈당 피크 30-40% 감소
- **장내 마이크로바이옴**: 단쇄지방산(SCFA) 생산 능력, 담즙산 대사, 장 투과성에 영향
- **유전적 소인**: TCF7L2, SLC30A8 다형성이 인슐린 분비 및 포도당 처리에 영향
- **시간 생물학(chronobiology)**: 동일 식사도 오전 대비 오후/야간에 혈당 반응이 상승 (인슐린 감수성의 일중 변동)
- **신체 활동**: 식후 10분 보행이 혈당 피크를 20-30% 감소시키는 것으로 보고

#### 2.4.2 기계학습 기반 PPGR 예측 모델

**ZOE PREDICT 1 모델** (Berry et al., 2020, *Nature Medicine*):

1,002명의 쌍둥이 및 비관련 건강 성인 대상, 8가지 표준화 식사 + 자유 식사의 식후 반응 데이터를 수집. ML 모델은 다음 입력 변수를 사용:
- 식사 조성 (영양소, 식이섬유)
- 개인 특성 (BMI, 나이, 성별)
- 마이크로바이옴 프로파일 (16S rRNA)
- 식사 타이밍 및 순서
- 혈액 바이오마커 (공복 혈당, 인슐린, 지질)

모델 성능: 혈당 반응 r = 0.77, 중성지방 반응 r = 0.47. 유전적 변이(SNP)는 혈당 예측에 9.5%의 분산을 설명했으나, 마이크로바이옴과 식사 맥락(타이밍, 수면)이 더 큰 설명력을 보였다.

**Zeevi et al. (2015) 모델** (*Cell*):
800명의 이스라엘 참가자 대상, CGM + 장내 마이크로바이옴 + 혈액 검사 + 식사 일지 데이터를 **gradient boosting** 알고리즘으로 학습. 개인별 혈당 반응 예측 정확도 R^2 = 0.70. 이 모델 기반 개인화 식이 권고가 무작위 대조 시험에서 표준 영양사 권고 대비 우월한 혈당 조절을 달성.

---

## 3. 임상 데이터

### 3.1 PREDICT 연구 시리즈

#### 3.1.1 PREDICT 1 (2020, Nature Medicine)

- **설계**: 단일군, 다기관 중재 연구
- **참가자**: 영국 1,002명 (쌍둥이 + 비관련 성인)
- **프로토콜**: 14일간 CGM 착용, 표준화 식사 8종 + 자유 식사
- **핵심 발견**: 동일한 유전자를 공유하는 일란성 쌍둥이조차 식후 반응이 상이 → 환경/마이크로바이옴/생활습관의 결정적 역할 입증
- **CGM 재현성**: 동일 브랜드 CGM 반복 측정의 iAUC CV = 3.7%, 다른 브랜드 간 CV = 12.5%

#### 3.1.2 PREDICT 2/3

PREDICT 2는 미국까지 확장하여 11,000명 이상의 참가자를 등록했으며, PREDICT 3는 메타볼로믹스와 마이크로바이옴 데이터의 종단적(longitudinal) 분석에 초점을 맞추고 있다. 이 데이터는 ZOE의 상업적 정밀영양 플랫폼의 알고리즘 훈련에 사용된다.

### 3.2 CGM 기반 정밀영양의 임상적 근거

#### 3.2.1 비당뇨인 "Time in Range" 최적화

ZOE PREDICT 연구에서 비당뇨 참가자 4,805명의 CGM 데이터 분석 결과, 포도당 Time in Range(70-140 mg/dL) 최적화가 식이 품질 및 건강 지표와 유의하게 연관됨이 확인되었다. 이는 CGM이 비당뇨인에서도 식이 행동 개선의 바이오피드백 도구로 기능할 수 있음을 시사한다.

#### 3.2.2 Zeevi et al. (2015) 개인화 식이 RCT

이스라엘 Weizmann Institute의 연구에서, 마이크로바이옴+CGM 기반 ML 모델이 생성한 개인화 식이 권고가 전문 영양사의 표준 권고 대비 식후 혈당 반응을 유의하게 개선했다 (p < 0.001). 이 연구는 정밀영양의 **인과적 효과(causal effect)**를 입증한 첫 번째 RCT 중 하나다.

### 3.3 메타볼로믹스 기반 질병 바이오마커

| 질환 | 바이오마커 후보 | 임상 단계 | 참고 |
|------|---------------|----------|------|
| 2형 당뇨 | 분지쇄아미노산(BCAA), 2-aminoadipic acid | 검증됨 | Framingham Heart Study |
| 심혈관 질환 | TMAO (trimethylamine N-oxide) | 독립적 위험 인자 | Cleveland Clinic, NEJM |
| 대장암 | 식이섬유 유래 단쇄지방산(butyrate) 수준 | 탐색적 | 다수 코호트 |
| 비알코올성 지방간(NAFLD) | 아실카르니틴 프로파일 | 탐색적 | 멀티코호트 검증 중 |
| 조기 신부전 | 요 대사체 패널 | 임상 검증 중 | CRIC Study |

### 3.4 약물 대사 예측 (Pharmacometabolomics)

대사체 프로파일링은 약물 반응의 개인 간 변이를 예측하는 데 활용된다:
- **스타틴 반응**: 치료 전 대사체 프로파일이 LDL-C 감소 효과를 예측 (Kaddurah-Daouk et al., 2011)
- **아스피린 저항성**: 혈소판 유래 대사물질 패턴으로 아스피린 비반응자 사전 식별
- **항우울제**: 세로토닌 경로 대사물질로 SSRI 반응 예측

---

## 4. 시장 분석

### 4.1 시장 규모와 성장 전망

| 세그먼트 | 2025 | 2034-2035 전망 | CAGR |
|---------|------|---------------|------|
| 메타볼로믹스 서비스 | $3.97B | $10B+ | 11.1% |
| 멀티오믹스 통합 시장 | $3.24B | $13.22B (2035) | 15.4% |
| 개인화 영양 + 뉴트리지노믹스 | $17.67B | $83.4B (2034) | 18.1% |
| CGM 기기 (당뇨 + 비당뇨) | $8B+ | $20B+ | ~15% |

정밀영양 시장의 18.1% CAGR은 디지털 헬스 시장 전체(~12%) 대비 높은 성장률이며, 이는 소비자 인식 확산, CGM 기술 민주화, AI 모델 정확도 향상이 복합적으로 작용한 결과다.

### 4.2 주요 기업 분석

#### 4.2.1 소비자 플랫폼

| 기업 | 기술 스택 | 규모 | 투자 상태 |
|------|----------|------|----------|
| **ZOE** | 마이크로바이옴 + CGM + 혈액 대사체 → AI 맞춤 식단 | 250K+ 구독자 | $1.5B 밸류에이션 (2025 Series C), 비상장 |
| DayTwo | 마이크로바이옴 → 혈당 반응 예측 | — | 비상장 |
| Viome | RNA 메타트랜스크립토믹스 → 맞춤 보충제 | — | 비상장 |
| InsideTracker | 혈액 바이오마커 → AI 건강 권고 | — | 비상장 |

ZOE는 $1.5B 밸류에이션으로 소비자 정밀영양 분야의 명확한 선두주자이며, PREDICT 연구 시리즈에서 축적한 데이터가 핵심 해자(moat)다.

#### 4.2.2 인프라/장비 기업

| 기업 | 티커 | 핵심 제품 | 메타볼로믹스 관련성 |
|------|------|----------|-----------------|
| Thermo Fisher | TMO | Orbitrap MS, Q Exactive | LC-MS/MS 시장 리더 |
| Agilent Technologies | A | Q-TOF, Triple Quad | 크로마토그래피 + MS 통합 |
| Bruker | BRKR | NMR 분광기 | NMR 메타볼로믹스 |
| Waters Corporation | WAT | Xevo TQ-XS, ACQUITY UPLC | 제약 메타볼로믹스 |
| SCIEX (Danaher) | DHR | TripleTOF, QTRAP | 임상 MS 응용 |
| Illumina | ILMN | 시퀀싱 플랫폼 | 마이크로바이옴 분석 |

#### 4.2.3 CGM 기업

| 기업 | 티커 | 핵심 제품 | 비당뇨 시장 진출 |
|------|------|----------|----------------|
| Dexcom | DXCM | G7, Stelo | Stelo (OTC, 2024 출시) |
| Abbott | ABT | FreeStyle Libre 3, Lingo | Lingo (비당뇨 웰니스) |
| Medtronic | MDT | Guardian 4 | 당뇨 중심 |

### 4.3 투자 핵심 테제

1. **인프라 투자가 가장 안정적**: TMO, A, BRKR — 오믹스 장비/시약 수요는 연구 트렌드와 무관하게 성장
2. **CGM 비당뇨 시장이 다음 성장 엔진**: Dexcom Stelo, Abbott Lingo의 OTC 출시가 TAM을 5-10배 확장
3. **ZOE IPO 시 주목**: 소비자 정밀영양 분야에서 데이터 + AI + 구독 모델의 삼위일체
4. **제약 응용이 고부가가치**: 바이오마커 발견, 동반 진단(CDx)이 단위 매출/마진 최고
5. **순수 메타볼로믹스 상장 기업 부재**: Metabolon(비상장)이 서비스 리더지만, 투자자는 인프라 기업 또는 응용 기업 통해 간접 노출

---

## 5. AI 적용

### 5.1 식후 반응 예측 모델

**트랜스포머(Transformer) 아키텍처**: 시계열 CGM 데이터에 자연어 처리의 어텐션(attention) 메커니즘을 적용하여, 식사-운동-수면의 시간적 맥락을 포착한다. ZOE의 최신 모델은 개인 CGM 데이터 1주일 학습 후 식후 반응 예측 정확도 90%+를 달성한 것으로 보고되었다.

**그래프 신경망(GNN)**: 대사 경로를 그래프 구조로 표현하고, 대사물질(node)과 효소 반응(edge)의 관계를 학습하여, 식이 개입이 하류 대사 경로에 미치는 영향을 예측한다.

### 5.2 디지털 트윈 (Digital Twin)

AI가 개인의 **대사 디지털 트윈** — 유전체, 마이크로바이옴, 대사체, 생활습관 데이터를 통합한 가상 대사 모델 — 을 구축하여, "가상으로" 다양한 식이 개입의 효과를 시뮬레이션한다. 이 접근법은 실제 식이 실험 없이 최적 식단을 탐색하는 것을 가능하게 한다.

### 5.3 미지 대사물질 동정 (Unknown Identification)

메타볼로믹스에서 검출되는 피크 중 **50-80%는 동정 불가(unknown)**다. 이 "dark metabolome" 문제에 대해:
- **딥러닝 MS/MS 스펙트럼 예측**: 분자 구조로부터 MS/MS 스펙트럼을 예측하는 모델(CFM-ID, SIRIUS, MS-FINDER)
- **MetaboAnalystR 4.0** (2024, *Nature Communications*): 자동 최적화된 피처 검출 + MS2 디컨볼루션 + 화합물 동정 통합 파이프라인
- **분자 네트워킹**: 유사 MS/MS 스펙트럼을 가진 미지 화합물을 기존 동정 화합물과 그룹화하여 구조 클래스 추정

### 5.4 약물-식이 상호작용 예측

AI가 약물 대사에 영향을 미치는 식이 요인을 식별한다:
- 자몽 주스의 CYP3A4 억제 같은 알려진 상호작용을 넘어서
- 장내 마이크로바이옴 매개 약물 대사 (예: digoxin의 Eggerthella lenta 매개 불활성화) 예측
- 개인 대사 프로파일 기반 약물 용량 최적화

### 5.5 건강 지식 그래프

멀티오믹스 데이터와 의학 문헌을 통합하는 **대규모 지식 그래프(knowledge graph)**가 질병-식이-대사-마이크로바이옴의 복합적 관계를 매핑한다. 이 그래프에서 GNN 기반 링크 예측(link prediction)으로 새로운 식이-질환 관계를 발견한다.

---

## 6. 참고문헌

1. Berry, S.E., Valdes, A.M., Drew, D.A., et al. "Human postprandial responses to food and potential for precision nutrition." *Nature Medicine* 26, 964-973 (2020). https://www.nature.com/articles/s41591-020-0934-0

2. Zeevi, D., Korem, T., Zmora, N., et al. "Personalized nutrition by prediction of glycemic responses." *Cell* 163(5), 1079-1094 (2015). https://doi.org/10.1016/j.cell.2015.11.001

3. Wishart, D.S., Guo, A., Oler, E., et al. "HMDB 5.0: the Human Metabolome Database for 2022." *Nucleic Acids Research* 50(D1), D622-D631 (2022). https://academic.oup.com/nar/article/50/D1/D622/6431815

4. Pang, Z., Lu, Y., Zhou, G., et al. "MetaboAnalystR 4.0: a unified LC-MS workflow for global metabolomics." *Nature Communications* 15, 3675 (2024). https://www.nature.com/articles/s41467-024-48009-6

5. Ghafari, M. et al. "Challenges and recent advances in quantitative mass spectrometry-based metabolomics." *Analytical Science Advances* 5(1-2), e202400007 (2024). https://chemistry-europe.onlinelibrary.wiley.com/doi/full/10.1002/ansa.202400007

6. Menni, C., Zhu, J., Le Roy, C.I., et al. "Validity of continuous glucose monitoring for categorizing glycemic responses to diet: implications for use in personalized nutrition." *American Journal of Clinical Nutrition* 115(6), 1569-1576 (2022). https://academic.oup.com/ajcn/article/115/6/1569/6522168

7. Bermingham, K.M., et al. "Optimised glucose 'Time in Range' using continuous glucose monitors in 4,805 non-diabetic individuals is associated with favourable diet and health: the ZOE PREDICT studies." (2023). https://www.sciencedirect.com/science/article/pii/S2475299123210628

8. Kaddurah-Daouk, R., et al. "Metabolomic signatures for drug response phenotypes: pharmacometabolomics enables precision medicine." *Clinical Pharmacology & Therapeutics* 95(2), 154-167 (2014). https://doi.org/10.1038/clpt.2013.217

9. Moreira-Rosario, A., et al. "Metabolomics: a review of liquid chromatography mass spectrometry-based methods and clinical applications." *Turkish Journal of Biochemistry* 49(1), 1-18 (2024). https://www.degruyterbrill.com/document/doi/10.1515/tjb-2023-0095/html

10. An, J. "Pharmacokinetics and pharmacodynamics of GalNAc-conjugated siRNAs." *Journal of Clinical Pharmacology* 64(4), 422-434 (2024). https://accp1.onlinelibrary.wiley.com/doi/10.1002/jcph.2337

11. Kodra, D., et al. "Development and validation of targeted metabolomics methods using LC-MS/MS for the quantification of 235 plasma metabolites." *Molecules* 30(3), 706 (2025). https://www.mdpi.com/1420-3049/30/3/706

12. Kirk, D., Catal, C., Tekinerdogan, B. "Precision nutrition: A systematic literature review." *Computers in Biology and Medicine* 133, 104365 (2021). https://doi.org/10.1016/j.compbiomed.2021.104365

---

*본 리뷰는 투자 권유를 목적으로 하지 않으며, 면책조항이 적용됩니다. 모든 투자 판단은 개인의 책임하에 이루어져야 합니다.*
