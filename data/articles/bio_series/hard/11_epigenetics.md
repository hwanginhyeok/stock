# 바이오 기술 리뷰 #11: 후성유전학 — 기전, 임상 데이터, 투자 분석

> **Technical Review Series** | 2026-04-05
> 후성유전학(Epigenetics)의 분자적 기전 — DNA 메틸트랜스퍼라제(DNMT), 히스톤 탈아세틸화효소(HDAC),
> 브로모도메인 리더, 후성유전 시계 — 을 PhD 수준에서 분석하고, FDA 승인 약물의 임상 데이터,
> 시장 전망, AI 적용 현황을 종합 리뷰한다.

---

## 1. 기술 개요: 후성유전학의 분자적 기전

후성유전학은 DNA 서열 변화 없이 유전자 발현을 조절하는 메커니즘을 연구하는 분야이다. Waddington이 1942년 최초로 제안한 이래, 후성유전적 변형이 발생, 분화, 노화, 질병에서 핵심적 역할을 수행함이 밝혀졌다. 후성유전적 변형의 핵심적 특성은 **가역성(reversibility)**이다 — 유전자 돌연변이와 달리, 후성유전적 변형은 약물로 되돌릴 수 있으며, 이것이 치료적 개입의 근거가 된다.

### 1.1 후성유전적 조절의 세 축

```
DNA 메틸화          히스톤 변형           비코딩 RNA
    ↓                   ↓                   ↓
CpG 메틸화 →        아세틸화, 메틸화,      miRNA, lncRNA,
유전자 침묵          인산화 등 →            circRNA →
                    크로마틴 리모델링       전사 후 조절
```

이 세 축이 상호작용하며 **후성유전체(epigenome)**를 구성하고, 같은 DNA 서열을 가진 세포가 뉴런, 간세포, 면역세포 등 전혀 다른 표현형을 나타내는 기반을 제공한다.

### 1.2 크로마틴 구조와 후성유전

뉴클레오솜(히스톤 옥타머 + 147bp DNA)은 크로마틴의 기본 단위이다. 히스톤 꼬리(tail)의 번역후 변형(PTM)이 크로마틴 접근성을 조절하며, 이를 통해 전사 활성/억제가 결정된다:

| 변형 | 위치 | 효과 | 관련 효소 |
|------|------|------|----------|
| H3K4me3 | 프로모터 | 활성화 | MLL/SET1 |
| H3K27me3 | 프로모터 | 억제 | EZH2 (PRC2) |
| H3K9me3 | 이질크로마틴 | 억제 | SUV39H1 |
| H3K27ac | 인핸서/프로모터 | 활성화 | CBP/p300 |
| H3K36me3 | 유전자 본체 | 전사 신장 | SETD2 |

**히스톤 코드 가설(Histone Code Hypothesis)**: 히스톤 변형의 특정 조합이 크로마틴 결합 단백질(reader)을 동원하여 하류 효과를 결정한다. Writer(기록)-Reader(판독)-Eraser(소거)의 삼원 시스템이 후성유전적 정보의 동적 조절을 가능하게 한다.

---

## 2. 핵심 기술 세부

### 2.1 DNA 메틸트랜스퍼라제 (DNMT1/DNMT3A/DNMT3B)

포유류의 DNA 메틸화는 CpG 디뉴클레오타이드의 5번 탄소에 메틸기(-CH3)를 부착하는 반응으로, S-adenosylmethionine (SAM)을 메틸 공여체로 사용한다. 세 가지 촉매적 DNMT가 존재하며, 각각 고유한 기능을 수행한다[1].

#### DNMT1: 유지 메틸화 (Maintenance Methylation)

- **기능**: DNA 복제 후 생성되는 반메틸화(hemimethylated) CpG 사이트를 인식하여 새로 합성된 딸 가닥에 메틸기를 복사
- **도메인 구조**: N-말단 조절 도메인(DMAP1 결합, PCNA 결합, RFTS 도메인, CXXC 도메인) + C-말단 촉매 도메인(methyltransferase domain)
- **RFTS 도메인**: 복제 포크에 DNMT1을 동원하여 복제 직후 메틸화 패턴 유지
- **UHRF1 의존성**: UHRF1(SRA 도메인)이 반메틸화 CpG를 인식 → DNMT1을 동원하는 플랫폼 역할
- **자가억제 메커니즘**: RFTS 도메인이 촉매 부위를 차단하여 비메틸화 DNA에 대한 비특이적 활성을 방지

#### DNMT3A: de novo 메틸화

- **기능**: 새로운 메틸화 패턴의 확립 — 배아 발생, 생식세포 분화에서 핵심
- **도메인 구조**: PWWP + ADD + 촉매 도메인 (DNMT3A/3B 간 촉매 도메인 서열 동일성 ~85%)[2]
- **PWWP 도메인**: H3K36me3(활발히 전사되는 유전자 본체)을 인식 → 유전자 본체 메틸화 유도
- **ADD 도메인**: H3K4me0(비메틸화 H3K4)을 인식 → 활성 프로모터(H3K4me3 보유)를 회피하는 메커니즘
- **DNMT3L과의 상호작용**: 촉매적으로 불활성인 DNMT3L이 DNMT3A와 이종사합체 형성 → 효소 활성 자극

#### DNMT3B: de novo 메틸화 (조직 특이성)

- **기능**: DNMT3A와 유사한 de novo 메틸화 활성, 그러나 조직 특이적 역할이 상이
- **ICF 증후군**: DNMT3B 돌연변이 → 위성 DNA의 저메틸화, 면역 결핍, 중심체 불안정, 안면 이형증
- **보완적 기능**: DNMT1 결핍 시 DNMT3B가 유지 메틸화를 일부 보상 — "유지 vs de novo" 이분법의 한계를 보여줌[1]

#### DNMT 억제제의 약리학

Azacitidine(Vidaza)과 decitabine(Dacogen)은 뉴클레오사이드 유사체로, DNA에 삽입된 후 DNMT와 공유결합을 형성하여 효소를 비가역적으로 포획(trapping)한다:

1. 세포 내 활성 대사체(5-aza-dCTP)가 DNA에 삽입
2. DNMT가 5-aza-시토신에 접근하여 공유결합 중간체 형성
3. 정상적 β-제거 반응이 차단 → DNMT-DNA 복합체 고착
4. DNMT 고갈 → 수동적 탈메틸화 → 침묵 유전자 재활성화

### 2.2 히스톤 탈아세틸화효소 (HDAC) 분류 I-IV

HDAC는 히스톤 라이신 잔기의 ε-아미노기에서 아세틸기를 제거하여 크로마틴 응축을 유도하고 유전자 발현을 억제하는 효소이다[3].

#### HDAC 분류 체계

| 클래스 | 구성원 | Zn²⁺ 의존 | 세포 내 위치 | 크기 |
|--------|--------|-----------|-------------|------|
| **Class I** | HDAC1, 2, 3, 8 | 예 | 핵 | 22-55 kDa |
| **Class IIa** | HDAC4, 5, 7, 9 | 예 | 핵-세포질 셔틀 | 120-135 kDa |
| **Class IIb** | HDAC6, 10 | 예 | 주로 세포질 | 100-131 kDa |
| **Class III** | Sirtuin 1-7 | 아니오 (NAD⁺) | 다양 | 34-47 kDa |
| **Class IV** | HDAC11 | 예 | 핵-세포질 | 39 kDa |

#### HDAC 억제제 구조-활성 관계

FDA 승인 HDAC 억제제의 화학 클래스:

1. **히드록삼산(Hydroxamic acid)**: Vorinostat (SAHA), Belinostat, Panobinostat — pan-HDAC 억제, Zn²⁺ 킬레이션
2. **고리형 펩타이드(Cyclic peptide)**: Romidepsin (FK228) — 프로드러그, 환원 시 이황화결합 절단 → thiol이 Zn²⁺ 킬레이트, **HDAC1/2 선택적**[3]
3. **벤즈아미드(Benzamide)**: Entinostat, tucidinostat — Class I 선택적
4. **단쇄 지방산(Short-chain fatty acid)**: Valproic acid — 약한 HDAC 억제, 주로 항경련제

**Vorinostat (Zolinza) 작용 기전**: Suberoylanilide hydroxamic acid (SAHA)는 HDAC 촉매 포켓의 Zn²⁺ 이온과 이좌배위(bidentate) 킬레이트를 형성. Pan-HDAC 억제(Class I + II)로 과아세틸화 → p21 발현 증가, 세포주기 정지, 세포 사멸 유도.

### 2.3 브로모도메인 리더 (Bromodomain Readers)

브로모도메인(bromodomain, BRD)은 아세틸화 라이신(Kac)을 특이적으로 인식하는 단백질 도메인으로, 후성유전적 "판독(reading)" 기능을 수행한다.

#### BET 패밀리 (BRD2, BRD3, BRD4, BRDT)

**BRD4의 분자적 역할**[4]:
1. **이중 브로모도메인(BD1, BD2)**: 아세틸화 히스톤(H3K27ac, H4Kac)에 결합
2. **전사 활성화**: Mediator 복합체 및 P-TEFb(CDK9/Cyclin T1)를 동원하여 RNA Pol II를 인산화 → 전사 신장(elongation) 촉진
3. **슈퍼 인핸서(Super-enhancer) 의존성**: BRD4는 암세포의 슈퍼 인핸서(MYC, BCL2 등 종양유전자)에 고밀도로 농축
4. **고유 HAT 활성**: BRD4 자체가 히스톤 아세틸트랜스퍼라제 활성을 보유

**BET 억제제의 약리학**:
BET 억제제(JQ1, I-BET762, OTX015 등)는 BD1/BD2의 Kac 결합 포켓에 경쟁적으로 결합하여 BRD4를 크로마틴에서 탈착시킨다. 그 결과:
- MYC, BCL2 등 종양유전자의 전사 급감
- 슈퍼 인핸서 의존적 유전자 프로그램 붕괴
- 암세포 선택적 세포주기 정지 및 사멸

**임상적 한계**: 단독 투여 시 제한적 효과, 혈소판감소증·빈혈·호중구감소증 등 혈액학적 부작용이 공통적[4]. BRD2 상향 조절이 BET 억제제 내성의 범암종 적응 기전으로 확인되었으며, 이를 극복하기 위한 PROTAC(단백질 분해 유도 키메라), 이중 BET/키나제 억제제 등 차세대 전략이 개발 중이다.

### 2.4 호바스 후성유전 시계 (Horvath Epigenetic Clock)

Steve Horvath가 2013년 *Genome Biology*에 발표한 후성유전 시계는 **353개의 CpG 사이트의 DNA 메틸화 수준**으로 생물학적 나이를 예측하는 머신러닝 모델이다[5].

#### 모델 구축

- **훈련 데이터**: 51개 건강 조직 및 세포 유형의 8,000개 샘플 (Illumina 450K BeadChip)
- **회귀 방법**: Elastic net regression (L1 + L2 정규화)
- **출력**: DNAm age (DNA 메틸화 나이)
- **정확도**: DNAm age와 연대기적 나이(chronological age) 간 상관계수 r = 0.97, 중앙값 절대 오차(MAE) = 2.9년

#### 핵심 발견

1. **범조직 적용성**: 하나의 모델로 혈액, 뇌, 간, 신장, 유방 등 다양한 조직의 나이 예측 가능
2. **후성유전 나이 가속(epigenetic age acceleration)**: DNAm age - 연대기 나이 > 0이면 "생물학적으로 늙었음"
3. **사망 예측**: 혈액의 DNAm age가 연대기 나이보다 높으면 전인 사망률(all-cause mortality) 증가[6]
4. **질병 연관**: 비만, 다운증후군, HIV 감염, 암 등이 후성유전 나이 가속과 연관
5. **iPSC 리프로그래밍**: iPSC는 DNAm age ≈ 0 — 완전한 후성유전적 회춘 확인

#### 차세대 시계

| 시계 | 연도 | CpG 수 | 특징 |
|------|------|--------|------|
| Horvath 1세대 | 2013 | 353 | 범조직, 연대기 나이 |
| Hannum | 2013 | 71 | 혈액 특이적 |
| PhenoAge (Levine) | 2018 | 513 | 표현형 나이 (질병 위험) |
| GrimAge | 2019 | 1,030 | 사망 예측 최적화 |
| DunedinPACE | 2022 | 173 | 노화 속도 (rate of aging) |
| 범포유류 시계 | 2023 | 수백 | 128종 포유류 공통 (Nature Aging)[7] |

---

## 3. 임상 데이터

### 3.1 DNMT 억제제: Azacitidine

**AZA-001 Phase 3 (고위험 MDS)** — Fenaux 등, *Lancet Oncology* 2009:
- **대상**: 고위험 MDS 환자 358명
- **설계**: Azacitidine 75 mg/m² SC x 7일/28일 사이클 vs conventional care (BSC, 저용량 ARA-C, 집중 화학요법)
- **중앙 OS**: Azacitidine **24.5개월** vs conventional care **15개월** (HR 0.58, p=0.0001)
- **2년 생존율**: Azacitidine 50.8% vs conventional care 26.2%

**Phase 3 고령 AML** — Dombret 등, *Blood* 2015[8]:
- **대상**: 65세 이상 신규 AML 환자 (>30% blasts)
- **중앙 OS**: Azacitidine **10.4개월** vs CCR **6.5개월** (p=0.1009)
- **민감도 분석 OS**: 12.1 vs 6.9개월

### 3.2 HDAC 억제제

**Vorinostat Phase IIb (CTCL)** — Olsen 등:
- **대상**: 2+ 전신 치료 후 진행/재발 CTCL 환자 74명
- **ORR**: **29.7%** (CR 1명, PR 21명)
- **중앙 반응 지속**: 168일 이상
- **주요 부작용**: 설사(49%), 피로(46%), 구역(43%), 혈소판감소증(26%)

**Romidepsin Phase II (PTCL)** — Coiffier 등:
- **대상**: 1+ 전신 치료 후 R/R PTCL 환자 130명
- **ORR**: **25%** (CR 15%)
- **중앙 반응 지속**: 17개월

**Panobinostat Phase III PANORAMA-1 (다발성 골수종)**:
- **설계**: Panobinostat + Bortezomib + Dexamethasone vs Placebo + Bortezomib + Dexamethasone
- **중앙 PFS**: 12.0개월 vs 8.1개월 (HR 0.63, p<0.0001)

### 3.3 EZH2 억제제: Tazemetostat

**Phase 2 (R/R 여포성 림프종)** — Morschhauser 등, *Lancet Oncology* 2020[9]:
- **EZH2 돌연변이 코호트**: ORR **69%** (95% CI 53-82, n=45)
- **EZH2 야생형 코호트**: ORR **35%** (95% CI 23-49, n=54)
- **중앙 반응 지속**: EZH2mut 10.9개월, EZH2WT 13.0개월
- **안전성**: 치료 관련 Grade 3+ AE 4%, 양호한 내약성

**Phase 1b/3 (R/R FL, Lenalidomide + Rituximab 병용)**[10]:
- **ORR**: **95%** (CR **50%**) — EZH2 돌연변이 상태와 무관
- NCT04224493 진행 중

### 3.4 BET 억제제 임상 현황

| 약물 | 적응증 | Phase | 결과 요약 |
|------|--------|-------|----------|
| Birabresib (OTX015) | AML, DLBCL | Phase 1 | SD 20-30%, 혈소판감소 용량 제한적 |
| Molibresib (GSK525762) | NMC | Phase 1 | ORR 25-36% NUT-양성 종양 |
| Pelabresib (CPI-0610) | 골수섬유증 | Phase 3 | MANIFEST-2: SVR35 달성률 66% vs ruxolitinib 단독 35% |

Pelabresib + ruxolitinib 병용이 골수섬유증에서 가장 진전된 BET 억제제 프로그램이며, 2025년 FDA 승인 검토 중이다.

### 3.5 액체생검: cfDNA 메틸화 기반 조기 진단

| 회사 | 검사명 | 적응증 | 기술 | 민감도/특이도 |
|------|--------|--------|------|--------------|
| GRAIL (Illumina→) | Galleri | 50+ 암종 조기 감지 | cfDNA 메틸화 | 51.5% 민감도 / 99.5% 특이도 (PATHFINDER) |
| Guardant Health | Shield | 대장암 스크리닝 | cfDNA 메틸화 | 83% 민감도 / 90% 특이도 (FDA 승인) |
| Exact Sciences | Cologuard Plus | 대장암 | DNA 메틸화 + 단백질 | 94% 민감도 / 91% 특이도 |

---

## 4. 시장 분석

### 4.1 시장 규모 및 성장률

| 세그먼트 | 2025-2026 | 2033-2034 | CAGR |
|---------|-----------|-----------|------|
| 후성유전학 시장 전체 | $19.6-22.6B | — | 15.3% |
| 후성유전 약물 | $16.2-19.4B | $80.8B (2034) | ~22% |
| 약물 + 진단 통합 | — | $46.3B (2033) | 18.6% |
| 액체생검 시장 | $6.5B (2025) | $20B+ (2030) | ~25% |

### 4.2 적응증별 시장 분포

| 적응증 | 시장 비중 | 성숙도 | 핵심 약물 |
|--------|----------|--------|----------|
| 혈액암 | **52%+** | 상용화 | Azacitidine, Vorinostat, Tazemetostat |
| 고형암 | 15-20% | 확장 중 | BET 억제제, EZH2 (2nd gen) |
| 진단 (액체생검) | 10-15% | 급성장 | GRAIL Galleri, Guardant Shield |
| 자가면역 | <5% | 연구 | — |
| 신경퇴행 | <5% | 연구 | — |
| 노화/장수 | <3% | 연구 | 후성유전 시계 기반 중재 |

### 4.3 경쟁 환경

**Tier 1: 승인 약물 보유 빅파마**
- Bristol-Myers Squibb (BMY): Azacitidine (Vidaza), Romidepsin (Istodax), Enasidenib (Idhifa)
- Merck (MRK): Vorinostat (Zolinza)
- Ipsen: Tazemetostat (Tazverik)

**Tier 2: 파이프라인 리더**
- Constellation/MorphoSys/Novartis (NVS): Pelabresib (BET 억제제, 골수섬유증)
- Epigenic Therapeutics: 후성유전 플랫폼 ($60M Series B, 2025.09)
- C4 Therapeutics (CCCC): Molecular glue 기반 후성유전 표적

**Tier 3: 진단/시계**
- GRAIL/Illumina: Galleri 범암종 스크리닝
- Guardant Health (GH): Shield 대장암 FDA 승인
- TruDiagnostic: 소비자향 후성유전 나이 검사

### 4.4 핵심 리스크 요인

1. **선택성 문제**: Pan-HDAC/DNMT 억제제의 광범위한 작용 → off-target 효과, 독성
2. **고형암 진출 어려움**: 혈액암에서 검증된 약물이 고형암에서는 제한적 효과
3. **경쟁 심화**: 면역항암제(IO), ADC, 이중특이 항체가 동일 적응증 경쟁
4. **후성유전 시계의 규제 불확실성**: 노화 바이오마커로서의 규제 경로 미확립

---

## 5. AI 적용

### 5.1 메틸화 패턴 분석

- **딥러닝 기반 메틸화 분류기**: CNN/Transformer 모델이 수백만 CpG 사이트의 메틸화 패턴에서 질병 특이적 시그니처를 식별
- **DeepCpG**: 단일 세포 메틸화 데이터의 결측값 보정(imputation) 및 예측
- **Nanopore 메틸화 콜링**: 나노포어 시퀀싱의 전기 신호에서 직접 5mC/5hmC를 검출하는 딥러닝 모델

### 5.2 액체생검 AI

- **GRAIL MCED (Multi-Cancer Early Detection)**: cfDNA 메틸화 패턴의 ML 분류로 50+ 암종 동시 검출 + 원발 부위(tissue of origin) 추정
- **Heptas AI**: AI 기반 cfDNA 후성유전 프로파일링 → 간 질환 조기 진단 (2025.11 런칭)

### 5.3 약물 발굴

- **드러거빌리티 예측**: 후성유전 표적(bromo, chromo, tudor, PWWP 도메인)의 구조 기반 드러거빌리티를 AI로 예측
- **선택적 억제제 설계**: 생성 AI(diffusion model)로 HDAC 아형 선택적(HDAC6, HDAC8) 억제제 de novo 설계
- **병용 최적화**: 후성유전 약물 + IO/표적치료 병용의 시너지를 in silico 예측

### 5.4 후성유전 시계와 ML

- **GrimAge/DunedinPACE**: 사망 예측 및 노화 속도 측정에 최적화된 차세대 ML 시계
- **범포유류 시계**: 128종 포유류의 공통 CpG를 이용한 종간(cross-species) 노화 시계 (Nature Aging 2023)[7]
- **치료 반응 예측**: 후성유전 바이오마커 기반 ML 모델로 DNMT/HDAC 억제제 반응 확률 사전 예측
- **노화 중재 평가**: 후성유전 시계가 항노화 중재(운동, 식이, 약물)의 효과를 정량적으로 측정하는 surrogate endpoint로 부상

---

## 6. 투자 시사점

### 6.1 핵심 투자 테제

1. **암 = 현재의 핵심 시장**: 8개 FDA 승인 약물, 52%+ 시장 점유 — 혈액암 중심의 검증된 영역
2. **액체생검이 가장 빠른 성장 경로**: Guardant Shield FDA 승인, GRAIL Galleri 대규모 전향적 시험 진행 — AI + cfDNA 메틸화의 수렴
3. **고형암 확장이 다음 트리거**: BET 억제제(Pelabresib), 차세대 EZH2 억제제, PROTAC 기반 후성유전 분해제
4. **노화 역전은 장기 비전**: Horvath 시계 기반 중재가 장수과학과 교차하며, 규제 경로 확립 시 폭발적 시장 형성 가능
5. **대부분 빅파마 포트폴리오 내**: 순수 후성유전 소형주가 제한적 — 바스켓 접근보다 빅파마(BMY, NVS) 또는 진단(GH) 권장

### 6.2 투자 전략 매트릭스

| 시계 | 전략 | 대표 종목 |
|------|------|----------|
| 단기 (1-3년) | 승인 약물 매출 성장 | BMS (BMY), Ipsen |
| 중기 (3-5년) | 파이프라인 트리거 | Constellation/NVS (Pelabresib) |
| 중기 (3-5년) | 액체생검 상업화 | Guardant Health (GH), Exact Sciences (EXAS) |
| 장기 (5-10년) | 노화/장수 | TruDiagnostic, Calico (비상장) |

---

## 참고문헌

[1] Auclair G, Weber M. "Mechanisms of DNA methylation and demethylation in mammals." *Biochimie*. 2012;94(11):2202-2211. ; Kim GD, et al. "Domain Structure of the Dnmt1, Dnmt3a, and Dnmt3b DNA Methyltransferases." *Genes*. 2024;15(4). doi:10.3390/genes15040454. https://pmc.ncbi.nlm.nih.gov/articles/PMC11025882/

[2] Gao L, et al. "Tissue-specific roles of de novo DNA methyltransferases." *Epigenetics & Chromatin*. 2024;17:38. doi:10.1186/s13072-024-00566-2. https://pmc.ncbi.nlm.nih.gov/articles/PMC11740433/

[3] Ropero S, Esteller M. "The role of histone deacetylases (HDACs) in human cancer." *Molecular Oncology*. 2007;1(1):19-25. ; Bolden JE, et al. "Anticancer activities of histone deacetylase inhibitors." *Nature Reviews Drug Discovery*. 2006;5:769-784. ; Grant C, et al. "Romidepsin: a novel histone deacetylase inhibitor for cancer." *Future Oncology*. 2011;7(10):1163-1174. https://pubmed.ncbi.nlm.nih.gov/21699444/

[4] Shi J, Bhatt D. "Bromodomain and extraterminal (BET) proteins: biological functions, diseases and targeted therapy." *Signal Transduction and Targeted Therapy*. 2023;8:420. doi:10.1038/s41392-023-01647-6. https://www.nature.com/articles/s41392-023-01647-6

[5] Horvath S. "DNA methylation age of human tissues and cell types." *Genome Biology*. 2013;14:R115. doi:10.1186/gb-2013-14-10-r115. https://pubmed.ncbi.nlm.nih.gov/24138928/

[6] Horvath S, Raj K. "DNA methylation-based biomarkers and the epigenetic clock theory of ageing." *Nature Reviews Genetics*. 2018;19:371-384. doi:10.1038/s41576-018-0004-3. https://www.nature.com/articles/s41576-018-0004-3

[7] Lu AT, et al. "Universal DNA methylation age across mammalian tissues." *Nature Aging*. 2023;3:1144-1166. doi:10.1038/s43587-023-00462-6. https://www.nature.com/articles/s43587-023-00462-6

[8] Dombret H, et al. "International phase 3 study of azacitidine vs conventional care regimens in older patients with newly diagnosed AML with >30% blasts." *Blood*. 2015;126(3):291-299. doi:10.1182/blood-2015-01-621664. https://ashpublications.org/blood/article/126/3/291/34530/

[9] Morschhauser F, et al. "Tazemetostat for patients with relapsed or refractory follicular lymphoma: an open-label, single-arm, multicentre, phase 2 trial." *Lancet Oncology*. 2020;21(11):1433-1442. doi:10.1016/S1470-2045(20)30441-1. https://pmc.ncbi.nlm.nih.gov/articles/PMC8427481/

[10] Hsi ED, et al. "Updated interim analysis of the randomized phase 1b/3 study of tazemetostat in combination with lenalidomide and rituximab in R/R FL." *Journal of Clinical Oncology*. 2022;40(16_suppl):7572. https://ascopubs.org/doi/abs/10.1200/JCO.2022.40.16_suppl.7572

[11] Bondarev AD, et al. "Recent developments of HDAC inhibitors: Emerging indications and novel molecules." *British Journal of Clinical Pharmacology*. 2021;87(12):4577-4597. doi:10.1111/bcp.14889. https://bpspubs.onlinelibrary.wiley.com/doi/10.1111/bcp.14889

[12] Epigenetic Clocks: Beyond Biological Age. *PMC*. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12539533/

---

*본 리뷰는 투자 권유가 아닌 기술 분석 목적으로 작성되었습니다. 투자 결정은 개인의 판단과 책임 하에 이루어져야 합니다.*
