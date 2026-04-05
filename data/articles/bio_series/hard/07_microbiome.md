# 바이오 기술 리뷰 #7: 마이크로바이옴 — 기전, 임상 데이터, 투자 분석

> 장내 생태계에서 정밀 치료제까지: 16S rRNA 분석, 대사물질-면역 상호작용, FMT에서 정의형 컨소시엄까지의 기술 전환

---

## 1. 기술 개요: 마이크로바이옴의 분자 생물학적 기반

### 1.1 인간 마이크로바이옴의 규모와 역할

인간의 장내에는 약 3.8 x 10¹³ 개의 미생물이 서식하며, 이는 인체 세포 수(약 3.0 x 10¹³)와 동등한 규모이다 [1]. 장내 마이크로바이옴은 1,000종 이상의 세균으로 구성되며, 전체 유전체(metagenome)는 인간 유전체의 약 150배에 달하는 330만 개 이상의 유전자를 보유한다.

이 생태계는 단순한 공생 집합이 아니라, 숙주의 면역 시스템, 에너지 대사, 신경 기능에 능동적으로 관여하는 "초유기체(superorganism)"의 일부이다. 주요 기능:

- **면역 조절**: 장 관련 림프 조직(GALT)의 성숙과 기능에 필수. 무균(germ-free) 마우스는 Peyer's patch 미발달, IgA 분비 감소, Treg 세포 분화 이상
- **영양 대사**: 숙주가 분해하지 못하는 식이 섬유를 발효하여 단쇄지방산(SCFA) 생산 (부티레이트, 프로피오네이트, 아세테이트)
- **병원체 저항성**: 집락화 저항성(colonization resistance)을 통해 병원성 세균의 정착을 방지
- **장-뇌 축(Gut-Brain Axis)**: 신경전달물질 전구체 생산, 미주신경(vagus nerve) 신호 전달, 면역 매개 경로를 통한 중추신경계 기능 조절

### 1.2 디스바이오시스(Dysbiosis)의 정의와 질병 연관

디스바이오시스는 장내 미생물 생태계의 조성과 기능이 정상 상태에서 이탈한 상태를 의미한다. 이는 세 가지 유형으로 분류된다:
1. **유익균 감소**: Faecalibacterium prausnitzii, Akkermansia muciniphila 등 항염증성 세균의 감소
2. **병원성 세균 증식**: Clostridioides difficile, Enterobacteriaceae 등의 과다 증식
3. **다양성 감소**: 전체 미생물 종 다양성(alpha diversity)의 저하

디스바이오시스는 감염성 질환(C. difficile 감염), 염증성 장질환(IBD), 대사 질환(비만, 2형 당뇨), 자가면역 질환, 신경 정신 질환(우울증, 자폐 스펙트럼 장애), 암(특히 면역항암제 반응)과 연관된다 [2].

---

## 2. 핵심 기술 세부

### 2.1 16S rRNA 시퀀싱: 마이크로바이옴 분석의 표준 도구

#### 2.1.1 16S rRNA 유전자의 구조적 특성

16S ribosomal RNA 유전자는 원핵생물의 소단위(30S) 리보좀을 구성하는 약 1,542 bp 길이의 유전자로, 마이크로바이옴 분류학적 프로파일링의 골드 스탠더드이다. 이 유전자가 분류학적 마커로 사용되는 이유:

1. **보존 영역(Conserved regions)**: 모든 세균에서 높은 서열 유사성을 보이는 9개 영역 → 범용 프라이머(universal primer) 설계 가능
2. **가변 영역(Variable regions, V1-V9)**: 종 및 속 수준에서 서열 다양성이 큰 9개 초가변 영역 → 분류학적 식별에 활용
3. **수평 유전자 전달(HGT) 빈도 낮음**: 다른 기능 유전자에 비해 종간 서열 전달이 드물어 계통학적 추적에 적합

#### 2.1.2 시퀀싱 워크플로우

**Short-read 16S 시퀀싱** (Illumina MiSeq):
- V3-V4 또는 V4 영역을 PCR 증폭 후 paired-end 시퀀싱 (2 x 300 bp)
- OTU(Operational Taxonomic Unit, 97% 유사성 기준) 또는 ASV(Amplicon Sequence Variant, 단일 뉴클레오타이드 해상도) 기반 분류
- 장점: 높은 처리량, 낮은 비용, 확립된 파이프라인(QIIME 2, mothur, DADA2)
- 한계: 특정 V region만 증폭하므로 종(species) 수준 해상도 제한, PCR 편향(amplification bias)

**Full-length 16S 시퀀싱** (PacBio, Oxford Nanopore):
- 전체 ~1.5 kb 16S 유전자를 long-read로 시퀀싱
- 종 및 아종(strain) 수준의 해상도 달성 가능 [3]
- 최근 2025년 연구에서 full-length 16S rRNA 시퀀싱이 short-read 대비 유의하게 높은 분류학적 해상도를 제공함이 확인됨

#### 2.1.3 Shotgun Metagenomics와의 비교

16S 시퀀싱이 "누가 있는가(who is there)"를 알려준다면, 전체 메타게놈 시퀀싱(shotgun metagenomics)은 "무엇을 할 수 있는가(what can they do)"를 알려준다. Shotgun 방법은:
- 분류학적 프로파일링 + 기능적 유전자(항생제 내성 유전자, 대사 경로 등) 정보 동시 획득
- 바이러스, 진균, 고세균 등 16S PCR에 포착되지 않는 미생물도 검출
- 비용이 높고 분석 복잡도가 증가

### 2.2 대사물질-면역 상호작용

#### 2.2.1 단쇄지방산(SCFA)의 면역 조절 기전

장내 세균이 식이 섬유를 혐기 발효하여 생산하는 단쇄지방산(Short-Chain Fatty Acids)은 마이크로바이옴-숙주 상호작용의 핵심 매개체이다 [4]:

**부티레이트(Butyrate)**:
- **장 상피 에너지원**: 대장 상피세포(colonocyte)의 주 에너지원으로, 세포 대사의 60-70%를 담당
- **장벽 기능 강화**: tight junction 단백질(claudin, occludin, ZO-1) 발현 촉진하여 장 투과성(leaky gut) 방지
- **Treg 세포 분화 촉진**: 히스톤 탈아세틸화 효소(HDAC) 억제를 통해 Foxp3+ 조절 T세포 분화 유도 → 장내 면역 관용 유지
- **항염증**: NF-kB 경로 억제, IL-10 생산 촉진, GPR109A 수용체 활성화
- 주요 생산균: Faecalibacterium prausnitzii, Roseburia intestinalis, Eubacterium rectale

**프로피오네이트(Propionate)**:
- 간 포도당 신생(gluconeogenesis) 조절, 콜레스테롤 합성 억제
- GPR41/GPR43 수용체를 통한 장 호르몬(GLP-1, PYY) 분비 촉진 → 포만감과 에너지 대사 조절
- 면역 세포의 히스톤 변형 조절

**아세테이트(Acetate)**:
- 가장 풍부한 SCFA, 말초 조직의 에너지 기질
- 장 미주신경 구심 경로를 통한 식욕 조절

#### 2.2.2 트립토판 대사와 세로토닌

장내 미생물은 필수 아미노산인 트립토판의 대사에 깊이 관여한다:

- **세로토닌 생산**: 체내 세로토닌의 약 90%가 장의 장크롬친화세포(enterochromaffin cell)에서 합성된다. 장내 미생물(특히 Clostridium 속의 spore-forming bacteria)이 tryptophan hydroxylase 1(TPH1) 발현을 촉진하여 세로토닌 합성을 증가시킨다 [5]
- **키누레닌 경로(Kynurenine pathway)**: 트립토판의 95%가 이 경로로 대사됨. 장내 세균이 IDO1(indoleamine 2,3-dioxygenase) 발현을 조절하여 키누레닌/세로토닌 균형에 영향
- **인돌 유도체**: 장내 세균이 트립토판에서 인돌, 인돌-3-아세트산(IAA), 인돌-3-프로피온산(IPA) 등을 생산. 이들은 aryl hydrocarbon receptor(AhR)의 리간드로 작용하여 장벽 무결성 유지, IL-22 생산 촉진, 장내 면역 항상성에 기여

#### 2.2.3 담즙산 대사

- 1차 담즙산(간에서 합성)이 장내 세균의 bile salt hydrolase(BSH)에 의해 탈접합
- 7α-dehydroxylation에 의해 2차 담즙산(데옥시콜산, 리토콜산)으로 전환
- 2차 담즙산은 FXR(farnesoid X receptor)와 TGR5 수용체를 통해 포도당/지질 대사, 에너지 소비, 면역 반응을 조절
- 담즙산 대사의 변화가 C. difficile 감염의 재발과 직결 — 건강한 미생물에 의한 2차 담즙산 생산이 C. difficile 포자 발아를 억제

### 2.3 FMT(Fecal Microbiota Transplantation) 기전

#### 2.3.1 작용 메커니즘

FMT는 건강한 기증자의 분변 미생물을 환자에게 이식하여 파괴된 장내 생태계를 복원하는 치료법이다. 그 작용 기전은 다층적이다 [6]:

1. **집락화 저항성 복원**: 이식된 건강한 미생물이 영양소와 접착 부위를 경쟁적으로 점유하여 C. difficile 등 병원체의 증식을 억제 (niche competition)
2. **담즙산 대사 정상화**: 이식된 세균(Clostridium scindens 등)이 1차 담즙산을 2차 담즙산으로 전환 → C. difficile 포자 발아 억제 및 영양형 성장 차단
3. **SCFA 생산 복원**: 부티레이트 생산균의 재정착으로 장 상피 에너지 공급과 장벽 기능 회복
4. **면역 재조정**: Treg/Th17 균형 복원, 장 점막 면역 정상화, 전신 염증 감소
5. **박테리오파지 전달**: FMT에 포함된 박테리오파지가 병원성 세균을 선택적으로 용해

#### 2.3.2 투여 경로와 표준화 문제

| 투여 경로 | 방법 | 장점 | 단점 |
|----------|------|------|------|
| 대장 내시경 | 맹장/상행결장에 직접 주입 | 가장 높은 치료 효과 | 침습적, 장 준비 필요 |
| 직장 관장 | 직장을 통한 주입 | REBYOTA 제형 | 대장 원위부에 제한 |
| 경구 캡슐 | 동결건조 포자 캡슐 | VOWST 제형, 비침습 | 위산 노출, 용량 제한 |
| 비위관(NG tube) | 상부 위장관 주입 | 빠른 투여 | 흡인 위험 |

표준화 과제: 기증자 스크리닝(감염병 검사, 마이크로바이옴 프로파일링), 제조 공정(혐기 조건 유지, 저장 안정성), 품질 관리(생존 세균 수, 병원체 부재 확인)가 FMT의 규제 승인과 상업적 확장의 핵심 장벽이다.

### 2.4 정의형 컨소시엄(Defined Consortia) vs. 단일 균주

#### 2.4.1 FMT의 한계와 차세대 접근

FMT는 기증자 의존성, 배치(batch) 간 변동성, 알려지지 않은 병원체 전파 위험 등의 근본적 한계를 갖는다. 이를 극복하기 위한 차세대 접근법:

**정의형 컨소시엄(Defined Consortia)**:
- 특정 치료 효과가 검증된 순수 분리 균주들을 설계된 비율로 조합
- 클론 세포은행(clonal cell bank)에서 GMP 조건으로 대량 생산 → 배치 일관성 보장
- 기증자 의존성 제거, 각 균주의 안전성 프로파일 개별 검증 가능
- 대표 기업: **Vedanta Biosciences (VE303)** — 8개 Clostridium 속 균주로 구성된 정의형 컨소시엄

**단일 균주(Single Strain) 프로바이오틱스**:
- 특정 기전이 규명된 단일 균주를 치료제로 개발
- Akkermansia muciniphila: 장벽 강화, 대사 개선
- 기전의 명확성이 높으나, 복잡한 생태계 복원에는 한계

**풀드 도너(Pooled Donor) 표준화**:
- 여러 기증자의 미생물을 혼합하여 개별 기증자 변동성을 평균화
- 대표 기업: **MaaT Pharma (MaaT013)** — AI 기반 기증자 풀링으로 표준화된 "full-ecosystem" 치료제

#### 2.4.2 설계 원리의 비교

| 특성 | FMT | 정의형 컨소시엄 | 단일 균주 |
|------|-----|---------------|---------|
| 조성 복잡도 | 수백-수천 종 | 5-20종 | 1종 |
| 배치 일관성 | 낮음 | 높음 | 매우 높음 |
| 기전 이해 | 불완전 | 부분적 | 명확 |
| 안전성 예측 | 어려움 | 가능 | 용이 |
| 규제 경로 | 생물 의약품/이식 | 생물 의약품 | 프로바이오틱/약물 |
| 생태계 복원력 | 높음 | 중간 | 낮음 |

---

## 3. 임상 데이터: 주요 시험 결과

### 3.1 승인 치료제

#### 3.1.1 REBYOTA (fecal microbiota, live-jslm) — 세계 최초 마이크로바이옴 치료제

- **승인**: 2022년 11월, FDA
- **적응증**: 재발성 C. difficile 감염(rCDI), 항생제 치료 완료 후 재발 방지
- **투여**: 직장 관장, 단회 투여
- **임상 근거 (PUNCH CD3, Phase 3)**: 표준 항생제 치료 후 REBYOTA를 투여한 군에서 8주 시점 rCDI 부재율이 70.6% vs. 위약 57.5% (치료 차이 13.1%, p=0.024) [7]
- **기전**: 건강한 기증자의 전체 장내 생태계를 이식하여 집락화 저항성과 담즙산 대사 복원

#### 3.1.2 VOWST (SER-109, fecal microbiota spores, live-brpk) — 최초 경구 마이크로바이옴 치료제

- **승인**: 2023년 4월, FDA
- **적응증**: rCDI, 항생제 치료 완료 후 재발 방지
- **투여**: 경구 캡슐, 3일간 4캡슐/일 (총 12캡슐)
- **구성**: 건강한 기증자 분변에서 정제한 Firmicutes 포자(spore)

**ECOSPOR III (Phase 3, NCT03183128)** [8]:
- 8주 시점 rCDI 재발률: SER-109군 12% vs. 위약군 40% (상대 위험 감소 70%, p<0.001)
- 반응자에서 16S rRNA 시퀀싱으로 확인한 Firmicutes 비율의 유의한 증가
- ECOSPOR I 선행 연구에서 87% (26/30) 참가자가 8주 시점 무재발 달성

### 3.2 개발 단계 치료제

#### 3.2.1 VE303 (Vedanta Biosciences) — 정의형 컨소시엄의 선두

- **구성**: 8개의 순수 분리 Clostridium 속 균주로 구성된 정의형 컨소시엄
- **CONSORTIUM (Phase 2)**: 고용량 VE303이 rCDI 재발 위험을 위약 대비 80% 이상 감소 [9]
- **추가 데이터 (2024, Nature Medicine 게재)**: VE303 치료가 환자 장내 미생물의 항생제 내성 유전자(ARG) 수준을 유의하게 감소시킴 — 항생제 내성 위기에 대한 잠재적 해결책
- **RESTORATiVE303 (Phase 3)**: 2024년 첫 환자 등록, 결과는 2026년 예상

#### 3.2.2 MaaT013/Xervyteg (MaaT Pharma) — 이식편대숙주병(GVHD)

**ARES (Phase 3, 단일군)** [10]:
- 적응증: 스테로이드 및 ruxolitinib 불응 급성 위장관 GVHD
- 대상: 50개 유럽 센터, 66명 성인 환자
- 1차 평가변수: Day 28 위장관 전체 반응률(GI-ORR) — **62%** (사전 설정 38% 기대치 대비 유의, p<0.0001)
- 완전 반응(CR): 38%, 매우 양호한 부분 반응(VGPR): 20%
- 12개월 전체 생존률: **54%** (반응자 67% vs. 비반응자 28%, p<0.0001)
- 제형: 풀드 도너 기반 full-ecosystem 관장 치료제, ButyCore(항염증 대사물질 생산 세균군) 포함
- **규제**: 2025년 6월 EMA 시판허가 신청, 2026년 중반 결정 예상

#### 3.2.3 장-뇌 축(Gut-Brain Axis) 임상 연구

- 마이크로바이옴 기반 정신건강 치료는 대부분 전임상~Phase 1 단계
- 주요 연구 방향: FMT를 통한 우울증, 불안, 자폐 스펙트럼 장애 증상 개선
- 기전적 근거: SCFA-미세아교세포(microglia) 경로, 트립토판-세로토닌 경로, 미주신경 구심 신호 [5]
- 상업화까지 10년+ 시계로, 현재는 기초 과학 단계

---

## 4. 시장 분석

### 4.1 시장 규모

| 세그먼트 | 2025 | 2031-2034 전망 | CAGR |
|---------|------|---------------|------|
| 마이크로바이옴 치료제 | $250M | $3.4B (2034) | ~33% |
| 인간 마이크로바이옴 전체 | $630M | $2.13B (2031) | ~16% |
| C. difficile 관련 | 대부분 | — | — |

### 4.2 경쟁 구도와 주요 기업

| 기업 | 티커 | 기술 | 대표 제품 | 단계 |
|------|------|------|----------|------|
| Seres Therapeutics | MCRB | 포자 정제 | VOWST (SER-109) | 상용화 |
| Ferring Pharma | 비상장 | 전체 생태계 FMT | REBYOTA | 상용화 |
| MaaT Pharma | MAAT.PA | AI 풀드 도너 | MaaT013/Xervyteg | Phase 3 완료, EMA 심사 |
| Vedanta Biosciences | 비상장 | 정의형 컨소시엄 | VE303 | Phase 3 진행 |
| BiomeBank | 비상장 | 표준화 FMT | 호주 TGA 승인 | 상용화(호주) |

### 4.3 핵심 투자 테제

1. **아직 극초기 시장**: 승인 약물 2개, 연 매출 합계 $수억 수준. 블록버스터 부재.
2. **C. difficile 넘어 IBD/GVHD로 확장이 전환점**: IBD(크론병, 궤양성 대장염) 환자 수 수천만 명 → 임상 성공 시 TAM 폭발. MaaT013의 GVHD 성공이 첫 번째 확장 신호.
3. **정의형 컨소시엄이 산업의 미래**: FMT의 기증자 의존성과 표준화 문제를 해결. VE303의 Phase 3 결과가 이 접근의 상업성을 검증할 핵심 이벤트.
4. **대부분 비상장/소형주**: 순수 마이크로바이옴 투자 기회가 제한적. MCRB(Seres)와 MAAT.PA(MaaT)가 거의 유일한 상장 순수주.
5. **빅파마의 관심은 낮으나 증가 추세**: Nestle의 Seres 인수(VOWST), Ferring의 자체 개발(REBYOTA) 등 제한적 참여. 임상 성공이 쌓이면 대형 M&A 가능성.

---

## 5. AI 적용: 마이크로바이옴 연구와 치료제 개발에서의 인공지능

### 5.1 생태계 분석과 분류학적 프로파일링

- **딥러닝 기반 분류**: 16S rRNA 서열로부터 CNN/RNN 모델이 속(genus)~종(species) 수준 분류를 수행. QIIME 2의 q2-feature-classifier와 같은 Naive Bayes 분류기가 표준이나, 딥러닝 모델이 species-level 해상도에서 우위
- **다중 오믹스 통합**: 메타게노믹스, 메타트랜스크립토믹스, 대사체학(metabolomics) 데이터를 통합하는 ML 모델이 질병 특이적 디스바이오시스 시그니처를 식별 [11]

### 5.2 균주 선별과 컨소시엄 설계

- **기계학습 기반 최적 균주 조합 예측**: 치료 효과에 기여하는 핵심 균주를 수천 종의 후보에서 선별하는 ML 모델. Vedanta Biosciences가 VE303의 8개 균주 선별에 이 접근을 활용
- **대사 모델링**: Genome-scale metabolic model(GEM)과 flux balance analysis(FBA)를 결합하여 컨소시엄 내 균주 간 대사 상호작용(교차 급식, 경쟁)을 예측
- **인공 미생물 컨소시엄(AMC) 설계**: AI가 특정 대사 산물(예: 부티레이트) 생산을 최대화하거나 특정 병원체를 억제하도록 균주 조합과 비율을 최적화

### 5.3 환자 층화와 반응 예측

- **마이크로바이옴 프로파일 기반 환자 선별**: 치료 전 장내 미생물 조성으로 FMT/컨소시엄 치료 반응을 예측하는 ML 분류기
- **면역항암제 반응 예측**: 장내 Akkermansia muciniphila, Bifidobacterium longum 등의 존재가 anti-PD-1 면역항암제 반응과 양의 상관 — 이를 AI가 통합 예측 [12]
- **MaaT Pharma의 AI 기반 기증자 풀링**: 최적의 미생물 다양성과 기능적 조성을 달성하도록 기증자 조합을 AI가 선택

### 5.4 대사물질-미생물 상관관계 분석

- **mmvec 알고리즘**: 마이크로바이옴과 대사체학 데이터 간의 상관관계를 neural network 기반으로 분석하여 미생물-대사물질 연결 네트워크 구축 [11]
- **메타볼릭 플럭스 예측**: 미생물 조성으로부터 SCFA, 담즙산, 트립토판 대사물질 프로파일을 예측하여 치료 기전 이해와 바이오마커 발굴에 활용

---

## 6. 참고문헌

[1] Sender R, Fuchs S, Milo R. "Revised Estimates for the Number of Human and Bacteria Cells in the Body." *Cell*. 2016;164(3):337-340.
https://www.cell.com/cell/fulltext/S0092-8674(16)00053-2

[2] Lynch SV, Pedersen O. "The Human Intestinal Microbiome in Health and Disease." *New England Journal of Medicine*. 2016;375(24):2369-2379.
https://www.nejm.org/doi/full/10.1056/NEJMra1600266

[3] Johnson JS, Spakowicz DJ, Hong BY, et al. "Evaluation of 16S rRNA gene sequencing for species and strain-level microbiome analysis." *Nature Communications*. 2019;10:5029.
https://www.nature.com/articles/s41467-019-13036-1

[4] Silva YP, Bernardi A, Frozza RL. "The Role of Short-Chain Fatty Acids From Gut Microbiota in Gut-Brain Communication." *Frontiers in Endocrinology*. 2020;11:25.
https://pmc.ncbi.nlm.nih.gov/articles/PMC7005631/

[5] Morais LH, Schreiber HL IV, Bhatt AS. "The gut microbiota-immune-brain axis: Therapeutic implications." *Cell Reports Medicine*. 2025.
https://pmc.ncbi.nlm.nih.gov/articles/PMC11970326/

[6] Khoruts A, Sadowsky MJ. "Understanding the mechanisms of faecal microbiota transplantation." *Nature Reviews Gastroenterology & Hepatology*. 2016;13(9):508-516.
https://www.nature.com/articles/nrgastro.2016.98

[7] Orenstein R, Dubberke E, Hardi R, et al. "Safety and Durability of RBX2660 (Microbiota Suspension) in Recurrent Clostridioides difficile Infection: Results of the PUNCH CD3 Trial." *Clinical Infectious Diseases*. 2022;74(5):891-900.
https://academic.oup.com/cid/article/74/5/891/6280944

[8] Feuerstadt P, Louie TJ, Lashner B, et al. "SER-109, an Oral Microbiome Therapy for Recurrent Clostridioides difficile Infection." *New England Journal of Medicine*. 2022;386(3):220-229.
https://www.nejm.org/doi/full/10.1056/NEJMoa2106516

[9] Vedanta Biosciences. "Phase 2 VE303 Results Published in Nature Medicine." 2024.
https://www.vedantabio.com/press-release/vedanta-biosciences-publishes-additional-phase-2-ve303-results-in-nature-medicine/

[10] MaaT Pharma. "ARES Phase 3 Pivotal Trial Final Data — MaaT013 (Xervyteg) in Acute GvHD." ASH 2025.
https://www.businesswire.com/news/home/20251208466457/en/MaaT-Pharma-Presents-Pivotal-ARES-Phase-3-Results-for-MaaT013-Xervyteg-in-Acute-GvHD-at-ASH-2025-Annual-Congress-and-Announces-54-1-Year-Overall-Survival

[11] Yang Y, Liu Y. "Artificial Intelligence for Microbiology and Microbiome Research." *Cell Systems*. 2026.
https://arxiv.org/abs/2411.01098

[12] Routy B, Le Chatelier E, Derosa L, et al. "Gut microbiome influences efficacy of PD-1-based immunotherapy against epithelial tumors." *Science*. 2018;359(6371):91-97.
https://www.science.org/doi/10.1126/science.aan3706

[13] Gut microbiota shapes cancer immunotherapy responses. *npj Biofilms and Microbiomes*. 2025.
https://www.nature.com/articles/s41522-025-00786-8

---

*면책조항: 본 리뷰는 정보 제공 목적으로 작성되었으며, 특정 종목에 대한 투자 권유가 아닙니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.*
