# 바이오 기술 리뷰 #5: RNA 치료제 — 기전, 임상 데이터, 투자 분석

> RNA interference에서 자체 증폭 RNA까지: 유전자 발현 조절의 분자 기전과 임상 전환

---

## 1. 기술 개요: RNA 치료제의 분자 생물학적 기반

### 1.1 중심 교리(Central Dogma)와 RNA 개입 지점

분자생물학의 중심 교리는 DNA → mRNA → 단백질이라는 유전정보 흐름을 기술한다. RNA 치료제는 이 흐름의 중간 단계인 mRNA를 표적으로 삼아, 단백질 합성을 차단하거나(siRNA, ASO), 원하는 단백질을 직접 생산시키거나(mRNA 치료제), 스플라이싱 패턴을 변경하여 기능적 단백질을 복원하는(ASO splice-switching) 전략을 구사한다.

이러한 접근은 CRISPR 등 유전자 편집 기술과 근본적으로 다르다. RNA 치료제는 게놈 DNA를 영구적으로 변경하지 않으며, 효과가 일시적(transient)이다. 이는 안전성 측면에서 가역성(reversibility)을 보장하는 동시에, 만성 질환에서는 반복 투여가 필요하다는 한계를 동시에 갖는다.

### 1.2 RNA 간섭(RNAi) 경로의 발견

RNA interference는 1998년 Andrew Fire와 Craig Mello가 *Caenorhabditis elegans*에서 이중가닥 RNA(dsRNA)가 상동 mRNA의 분해를 유도함을 발견하면서 확립되었다 [1]. 이 발견은 2006년 노벨 생리의학상으로 이어졌으며, 진핵생물 전반에 보존된 유전자 침묵 메커니즘의 존재를 증명했다.

포유류 세포에서 긴 dsRNA는 비특이적 인터페론 반응을 유발하므로, 21-23 뉴클레오타이드 길이의 합성 small interfering RNA(siRNA)를 사용하여 특이적 유전자 침묵을 달성한다. 이 길이는 Dicer 효소의 절단 산물과 동일하며, 선천면역 회피와 RISC 복합체 로딩 효율 간의 최적점에 해당한다.

---

## 2. 핵심 기술 세부

### 2.1 RISC 복합체 기전: siRNA의 분자 수준 작용

#### 2.1.1 siRNA 구조와 RISC 로딩

합성 siRNA는 19-21 bp의 이중가닥 RNA로, 3' 말단에 2-nucleotide 오버행을 갖는다. 세포질에 도달한 siRNA는 RNA-Induced Silencing Complex(RISC)에 편입되는데, 이 과정은 다단계로 진행된다:

**1단계 — RISC Loading Complex(RLC) 형성**: siRNA 이중가닥은 TRBP(TAR RNA-binding protein)와 Dicer 단백질로 구성된 RLC에 의해 인식된다. RLC는 이중가닥의 열역학적 비대칭성(thermodynamic asymmetry)을 감지하여 가이드 가닥(guide strand, antisense strand)과 패신저 가닥(passenger strand, sense strand)을 구별한다 [2]. 5' 말단의 열역학적 안정성이 낮은 가닥이 가이드 가닥으로 선택된다.

**2단계 — Argonaute 2 로딩**: 가이드 가닥은 RISC의 촉매 핵심인 Argonaute 2(Ago2) 단백질에 로딩된다. Ago2는 PAZ 도메인으로 가이드 가닥의 3' 말단을, MID 도메인으로 5' 인산기를 각각 고정한다 [3]. 이 과정에서 패신저 가닥은 Ago2의 endonuclease 활성에 의해 절단되어 방출된다.

**3단계 — 표적 인식과 절단**: 활성 RISC는 가이드 가닥의 seed region(2-8번째 뉴클레오타이드)을 통해 표적 mRNA를 스캔한다. 완전 상보적 결합이 이루어지면, Ago2의 PIWI 도메인이 RNase H와 유사한 endonuclease 활성으로 표적 mRNA의 포스포디에스테르 결합을 가이드 가닥 5' 말단으로부터 10-11번째 위치에서 절단한다 [4].

**4단계 — 촉매 재순환**: 절단된 mRNA 단편은 방출되고, RISC-가이드 가닥 복합체는 새로운 표적 mRNA를 인식하여 반복적으로 절단한다. 단일 RISC 복합체가 수백 개의 mRNA 분자를 분해할 수 있어, siRNA는 촉매적(catalytic) 메커니즘으로 작용한다. 이러한 촉매 재순환(catalytic turnover)이 siRNA 치료제의 높은 효능과 장기 지속성의 분자적 기반이 된다.

#### 2.1.2 약리동력학적 의미

GalNAc-접합 siRNA의 직접적 약력학(PD) 구동자는 세포질 내 RISC에 로딩된 siRNA 농도이다. RISC-로딩 siRNA의 동력학이 관찰되는 PD 효과와 직접 대응하며, Tmax는 최대 PD 반응과 일치한다 [5]. 이 관계는 GalNAc-siRNA의 장기 지속적 효과(6개월 이상)를 설명한다 — RISC 복합체 내 siRNA의 반감기가 세포 분열 속도와 Ago2 단백질 턴오버에 의해 결정되기 때문이다.

### 2.2 GalNAc 접합 기술: 간 표적 전달의 표준

#### 2.2.1 ASGPR 매개 내재화

N-Acetylgalactosamine(GalNAc)은 간세포 표면에 고발현되는 asialoglycoprotein receptor(ASGPR)에 고친화도로 결합하는 탄수화물 리간드이다. ASGPR는 간세포당 약 500,000개가 발현되며, 15분마다 재순환하여 높은 내재화 용량을 제공한다.

GalNAc-접합 siRNA의 전달 경로:
1. **피하 투여 후 전신 순환 진입**: GalNAc-siRNA는 피하주사 후 림프계를 통해 혈류에 도달
2. **ASGPR 매개 수용체 내재화(receptor-mediated endocytosis)**: 3가(trivalent) GalNAc 리간드가 ASGPR의 3개 carbohydrate recognition domain(CRD)에 결합하여 clathrin-coated pit 형성 및 내재화 유도 [6]
3. **엔도좀 산성화와 방출**: pH 저하에 따라 ASGPR-리간드 결합이 해리되고, ASGPR은 세포 표면으로 재순환. 엔도좀에 갇힌 siRNA의 대부분은 리소좀으로 이동하여 분해되며, 극히 일부(<1%)만이 엔도좀 탈출(endosomal escape)을 통해 세포질에 도달
4. **세포질 RISC 로딩**: 탈출한 siRNA가 RISC에 편입되어 촉매적 유전자 침묵 개시

#### 2.2.2 화학적 변형 전략

Naked RNA는 혈장 내 nuclease에 의해 수분 내에 분해된다. GalNAc-siRNA는 다음의 화학적 변형으로 안정성을 확보한다:

- **2'-O-methyl(2'-OMe) 변형**: 리보스 2' 위치에 메틸기를 도입하여 nuclease 저항성 부여
- **2'-fluoro(2'-F) 변형**: 리보스 2' 위치에 플루오린을 도입하여 A-form 이중나선 구조 유지와 표적 결합력 강화
- **Phosphorothioate(PS) 결합**: 포스포디에스테르 결합의 비가교 산소를 황으로 치환하여 exonuclease 저항성과 혈장 단백질 결합력 증가
- **GNA(glycol nucleic acid) 변형**: seed region의 off-target 효과를 최소화하는 최신 변형 전략

Enhanced Stabilization Chemistry(ESC)와 ESC+ 설계는 이러한 변형의 조합을 최적화하여 in vivo 안정성과 RISC 로딩 효율을 극대화한다 [7].

### 2.3 지질 나노입자(LNP) 전달 시스템

#### 2.3.1 LNP 구성 요소

LNP는 mRNA 치료제와 siRNA(정맥투여 시)의 주요 전달체로, 네 가지 핵심 성분으로 구성된다:

1. **이온화 지질(Ionizable lipid)**: 생리적 pH(7.4)에서 전기적 중성이나 엔도좀의 산성 환경(pH 5.5-6.3)에서 양전하를 띠는 pH-반응성 지질. pKa 6-7 범위가 최적이다. 대표적 이온화 지질로 Dlin-MC3-DMA(Onpattro), SM-102(Moderna), ALC-0315(BioNTech) 등이 있다.

2. **구조 지질(DSPC)**: 1,2-distearoyl-sn-glycero-3-phosphocholine. LNP의 구조적 안정성과 지질 이중층 형성에 기여.

3. **콜레스테롤**: 입자 안정성, 세포막 융합 촉진, 체내 순환 시간 증가.

4. **PEG-지질**: 입자 표면에 친수성 PEG 층을 형성하여 면역계 회피(stealth effect), 응집 방지, 입자 크기 조절.

#### 2.3.2 엔도좀 탈출 메커니즘

LNP-매개 핵산 전달의 가장 큰 병목은 엔도좀 탈출이다. 현재까지의 연구에 따르면, 모든 LNP 제형에서 엔도좀 탈출 효율은 10% 미만이며 [8], 대부분의 화물(cargo)은 리소좀 분해 경로로 이동한다.

엔도좀 탈출의 분자 메커니즘:
1. 엔도좀 내 pH가 6.0 이하로 저하됨에 따라 이온화 지질이 양성자화(protonation)
2. 양전하를 띠게 된 이온화 지질이 엔도좀 막의 음전하 인지질(주로 bis(monoacylglycerol)phosphate)과 이온 쌍(ion pair)을 형성
3. 이온 쌍 형성이 엔도좀 막의 구조를 불안정화하여 비층상 상(non-lamellar phase, 특히 hexagonal HII phase)으로 전환
4. 막 구조 재편에 의한 미세 공극 형성을 통해 핵산 화물이 세포질로 방출

최근 연구는 ESCRT(endosomal sorting complexes required for transport) 경로와의 상호작용을 조명한다. 특정 이온화 지질은 수복 가능한 작은 엔도좀 공극을 생성하여 ESCRT 경로에 의한 막 수복을 허용하면서도 화물 방출을 달성함으로써, 염증 반응을 최소화할 수 있다 [9].

### 2.4 자체 증폭 RNA(saRNA): 차세대 플랫폼

#### 2.4.1 알파바이러스 유래 레플리카제 시스템

자체 증폭 RNA(self-amplifying RNA, saRNA)는 알파바이러스(주로 Venezuelan equine encephalitis virus, VEEV 또는 Sindbis virus) 게놈에서 유래한 설계이다. 바이러스의 구조 단백질 유전자를 관심 항원/치료 단백질 유전자로 교체하되, 비구조 단백질(nsP1-nsP4)을 코딩하는 레플리카제 유전자는 보존한다 [10].

saRNA의 세포 내 자체 증폭 과정:
1. **1차 번역**: 세포질에 도달한 saRNA(양성 가닥)가 리보좀에 의해 직접 번역되어 nsP1-nsP4 폴리프로테인 생성
2. **폴리프로테인 가공**: nsP1234 전구체가 순차적으로 절단되어 개별 nsP 단백질 생성
   - **nsP1**: 5' 캡핑 효소, 막 고정
   - **nsP2**: RNA helicase, 프로테아제
   - **nsP3**: 복제 복합체 조립 스캐폴드
   - **nsP4**: RNA-dependent RNA polymerase(RdRp), 핵심 복제 효소
3. **음성 가닥 합성**: nsP 복합체가 양성 가닥 saRNA를 템플릿으로 사용하여 전체 길이 음성 가닥 RNA 합성 (3' UTR의 서열 요소를 인식)
4. **양성 가닥 증폭**: 음성 가닥을 템플릿으로 전체 길이 게놈 양성 가닥과 서브게놈 양성 가닥을 합성. 서브게놈 프로모터(SGP)에 의해 관심 유전자를 포함하는 서브게놈 mRNA가 다수 전사됨
5. **항원 대량 생산**: 서브게놈 mRNA로부터 관심 단백질(항원)이 대량 번역

이 증폭 과정의 결과, 세포 당 투입된 소량의 saRNA로부터 기존 mRNA 대비 수십~수백 배의 단백질 발현이 가능하다. 동시에 복제 중간체인 dsRNA가 RIG-I/MDA5 경로를 활성화하여 type I interferon(IFN-I) 반응과 세포 사멸(apoptosis)을 유도하며, 이는 백신 맥락에서 자가 면역보조(self-adjuvanting) 효과로 작용한다 [11].

#### 2.4.2 saRNA의 임상 진입

2024년 기준, 두 개의 saRNA 백신이 규제 승인을 받았다:
- **ARCT-154 (Arcturus Therapeutics)**: 일본에서 COVID-19 부스터 백신으로 승인
- **GEMCOVAC-OM (Gennova Biopharmaceuticals)**: 인도에서 COVID-19 백신으로 승인

이 승인은 saRNA 플랫폼의 임상적 안전성과 면역원성을 검증하는 이정표이나, 비감염 적응증(종양학, 희귀질환)에서의 saRNA 적용은 아직 초기 임상 단계에 머물러 있다.

### 2.5 ASO(Antisense Oligonucleotide) 기전

ASO는 15-30 뉴클레오타이드 길이의 합성 단일가닥 올리고뉴클레오타이드로, 표적 pre-mRNA 또는 mRNA에 Watson-Crick 염기쌍으로 결합하여 다양한 메커니즘을 통해 유전자 발현을 조절한다:

**RNase H 의존적 분해**: Gapmer 디자인의 ASO는 DNA 갭(gap) 영역이 RNA-DNA 이중가닥을 형성하면 RNase H1이 RNA 가닥을 절단. 양쪽 날개(wing)는 2'-MOE 등으로 변형하여 결합 친화도와 nuclease 저항성 강화.

**스플라이스 전환(Splice-switching)**: ASO가 pre-mRNA의 스플라이싱 조절 서열(exonic/intronic splicing enhancer 또는 silencer)에 결합하여 특정 엑손의 포함(inclusion) 또는 배제(skipping)를 유도. Spinraza(nusinersen)가 대표적으로, SMN2 유전자의 인트론 7 내 intronic splicing silencer N1(ISS-N1)에 결합하여 엑손 7 포함을 촉진, 기능적 SMN 단백질 생산을 복원한다 [12].

---

## 3. 임상 데이터: 주요 시험 결과

### 3.1 siRNA 치료제

#### 3.1.1 Patisiran (Onpattro) — APOLLO / APOLLO-B

**APOLLO (Phase 3, NCT01960348)**:
- 적응증: hereditary transthyretin-mediated amyloidosis (hATTR) with polyneuropathy
- 결과: mNIS+7 복합점수가 patisiran군에서 기저치 대비 -6.0점 vs. 위약군 +28.0점 (차이 -34.0점, p<0.001). Norfolk QoL-DN 점수 -6.7 vs. +14.4 (p<0.001) [13]
- 의의: 세계 최초 siRNA 치료제 FDA 승인(2018년 8월)

**APOLLO-B (Phase 3, NCT03997383)**:
- 적응증: ATTR amyloidosis with cardiomyopathy
- 결과: 12개월 시점 6분 보행 시험(6MWT)에서 patisiran군이 위약군 대비 유의한 개선 (p=0.0162). NT-proBNP, troponin I, 좌심실 global longitudinal strain, 좌심실 질량, 박출량 모두 patisiran 유리. 이상반응 발생률은 patisiran 91.2% vs. 위약 94.4%로 유사 [14]

#### 3.1.2 Inclisiran (Leqvio) — ORION 프로그램

**ORION-10/ORION-11 (Phase 3)**:
- 적응증: 동맥경화성 심혈관질환(ASCVD) 또는 동등 위험의 고콜레스테롤혈증
- 용법: 284 mg 피하주사, 1일차, 90일차, 이후 6개월 간격
- 결과: 510일 시점 LDL-C 감소 — ORION-10에서 52.3% (95% CI 48.8-55.7), ORION-11에서 49.9% (95% CI 46.6-53.1) [15]
- 장기 데이터 (ORION-8, 2024): 약 5년 추적에서 LDL-C 평균 변화 -49.4%, 78.4%의 환자가 사전 설정 LDL-C 목표 달성. 시간 경과에 따른 효과 감쇠 없음 [16]

#### 3.1.3 Zilebesiran — KARDIA 프로그램

**KARDIA-2 (Phase 2, 2024)**:
- 적응증: 부적절 조절 고혈압 (표준 항고혈압제 병용)
- 대상: 672명의 성인 고혈압 환자
- 결과: 위약 대비 3개월 24시간 평균 이동 수축기혈압 감소 — indapamide 병용군 -12.1 mmHg (p<0.001), amlodipine 병용군 -9.7 mmHg (p<0.001), olmesartan 병용군 -4.0 mmHg (p=0.036). 6개월 시점까지 효과 지속 확인 [17]
- 의의: RNAi가 만성 대사질환 영역(고혈압, 10억+ 환자 풀)으로 확장하는 전환점. 연 2회 피하주사로 혈압 관리 가능성 입증

### 3.2 mRNA 치료제

#### 3.2.1 mRNA-4157/V940 — 개인화 암 백신

**KEYNOTE-942 (Phase 2b)**:
- 적응증: 완전 절제된 고위험(Stage III/IV) 흑색종
- 디자인: V940 + pembrolizumab vs. pembrolizumab 단독
- 2년 추적 결과: 무재발 생존(RFS) — 재발 또는 사망 위험 44% 감소, 원격 전이 또는 사망 위험 65% 감소 [18]
- 5년 추적 결과 (2025): RFS에서 재발 또는 사망 위험 49% 감소로 효과 지속 확인 [19]
- FDA Breakthrough Therapy Designation 획득

**INTerpath Phase 3 프로그램 (진행 중)**:
- INTerpath-001: 고위험 흑색종 (Stage IIB-IV)
- INTerpath-009: 절제 가능 NSCLC (Stage II, IIIA, IIIB-N2) — 868명 대상
- 최초 규제 승인은 2026년 말~2027년 예상

### 3.3 ASO 치료제

#### 3.3.1 Tofersen — SOD1 ALS

- 적응증: SOD1 변이 ALS
- 결과: neurofilament light chain(NfL) 바이오마커에서 유의한 감소, 기능 악화 속도 둔화
- 2023년 accelerated approval (FDA), 임상적 이점에 대한 확인 시험 진행 중

---

## 4. 시장 분석

### 4.1 전체 시장 규모(TAM)

| 세그먼트 | 2024-2025 | 2030 전망 | 2035 전망 | CAGR |
|---------|-----------|----------|----------|------|
| RNA 치료제 전체 | $15.1B | $23.5B | $103.1B | 9.2-14.3% |
| siRNA 치료제 | $2.55B | — | $12.38B (2033) | 17.4% |
| mRNA 치료/백신 | 변동 큼 | $31.3B | — | 17.05% |
| 올리고뉴클레오타이드(siRNA+ASO) | $9.1B | $15.7B | — | 11.5% |

*출처: Mordor Intelligence, Grand View Research, MetaTech Insights*

### 4.2 경쟁 구도

**Tier 1 — 플랫폼 리더:**
- **Alnylam Pharmaceuticals (ALNY)**: RNAi 플랫폼의 절대 강자. 승인 약물 5개(Onpattro, Amvuttra, Leqvio, Oxlumo, Givlaari) + fitusiran 상용화. GalNAc-ESC+ 기술이 업계 표준. 2025년 $250M 제조 시설 확장.
- **Ionis Pharmaceuticals (IONS)**: ASO 분야 20년+ 선구자. Spinraza, Wainua, Tofersen 등 핵심 약물. GSK와 $458M 파트너십.
- **Moderna (MRNA)**: mRNA 플랫폼 선도. COVID-19 매출 이후 종양학(V940), 감염병(RSV) 전환.
- **BioNTech (BNTX)**: mRNA 암 백신(BNT122), 감염병, IO 파이프라인.

**Tier 2 — 신흥 플레이어:**
- **Arcturus Therapeutics (ARCT)**: saRNA 플랫폼, 일본 COVID-19 백신 승인
- **Arrowhead Pharmaceuticals (ARWR)**: 간 외(extrahepatic) RNAi 전달 기술
- **Alnylam 2030 비전**: 연 매출 $1B+ 초과 약물 다수 예상 (Amvuttra, Leqvio, Wainua 등)

### 4.3 핵심 투자 테제

1. **GalNAc-siRNA 플랫폼의 승자 독식**: Alnylam의 GalNAc-ESC+ 기술이 간 표적 RNAi의 사실상 표준. 후발 주자의 진입 장벽 극히 높음.
2. **만성질환 확장이 TAM 폭발의 열쇠**: 고콜레스테롤(inclisiran), 고혈압(zilebesiran) 등 환자 풀이 억 단위인 대사질환으로 RNAi 확장 → 블록버스터 다수 창출 가능.
3. **mRNA 암 백신의 패러다임 전환**: V940의 Phase 3 성공 시 개인화 암 치료 시장($수십B) 개척. 면역항암제와의 병용이 핵심.
4. **전달 기술이 최종 병목**: 간 이외 조직(CNS, 근육, 폐)으로의 전달이 미해결 과제. 이 병목을 돌파하는 기술(extrahepatic LNP, exosome, 조직 특이적 리간드)이 차세대 가치 창출의 핵심.

---

## 5. AI 적용: RNA 치료제 개발에서의 인공지능

### 5.1 siRNA 서열 설계 최적화

전통적 siRNA 설계는 Tuschl 규칙, Reynolds 규칙 등 경험적 가이드라인에 의존했다. 현재 AI/ML 모델은:

- **표적 특이성과 안정성의 동시 최적화**: 딥러닝 모델이 siRNA 서열의 on-target 효능, off-target 확률, 열역학적 안정성, 면역자극 모티프를 동시에 예측하여 최적 후보를 선별
- **Off-target 예측**: Alnylam의 ESC+ 설계에서 GNA(glycol nucleic acid) 변형 위치를 AI가 seed region의 off-target 결합 열역학을 계산하여 최적화 [7]

### 5.2 mRNA 서열 및 구조 최적화

- **코돈 최적화 이상**: AI가 mRNA의 코돈 사용빈도, 2차 구조(최소 자유에너지), UTR 서열, polyA 꼬리 길이를 동시에 최적화하여 번역 효율과 안정성을 극대화
- **Moderna의 mRNA Design Studio**: 자체 ML 플랫폼으로 수천 개의 mRNA 서열 변이체를 in silico 스크리닝 후 최적 후보 선별

### 5.3 LNP 조성 생성적 설계

- **조합 폭발 문제**: 이온화 지질, 구조 지질, 콜레스테롤, PEG-지질의 4성분 조합 + 비율 변화 → 탐색 공간이 수십만 이상
- **Generative AI**: Variational autoencoder(VAE)와 Bayesian optimization을 결합하여 조직 특이적 LNP 조성을 탐색. 동물 실험 데이터로 학습한 모델이 간, 폐, 비장 등 표적 장기별 최적 LNP 조성을 예측
- **고속 스크리닝 연계**: DNA barcoded LNP 라이브러리와 AI 예측을 결합하여 in vivo 조직 분포를 고속으로 평가

### 5.4 독성 예측 및 안전성 평가

- AI 모델이 화학 변형 패턴과 간독성, 혈소판 감소 등 안전성 프로파일 간의 관계를 학습
- in silico 독성 예측으로 동물 실험 전 후보 선별, 개발 비용과 시간 절감

---

## 6. 참고문헌

[1] Fire A, Xu S, Montgomery MK, et al. "Potent and specific genetic interference by double-stranded RNA in *Caenorhabditis elegans*." *Nature*. 1998;391(6669):806-811.
https://www.nature.com/articles/35888

[2] Schwarz DS, Hutvagner G, Du T, et al. "Asymmetry in the assembly of the RNAi enzyme complex." *Cell*. 2003;115(2):199-208.
https://www.cell.com/cell/fulltext/S0092-8674(03)00759-1

[3] Rivas FV, Tolia NH, Song JJ, et al. "Purified Argonaute2 and an siRNA form recombinant human RISC." *Nature Structural & Molecular Biology*. 2005;12(4):340-349.
https://www.nature.com/articles/nsmb918

[4] Martinez J, Patkaniowska A, Urlaub H, et al. "Single-stranded antisense siRNAs guide target RNA cleavage in RNAi." *Cell*. 2002;110(5):563-574.
https://pubmed.ncbi.nlm.nih.gov/12230974/

[5] An G. "Pharmacokinetics and Pharmacodynamics of GalNAc-Conjugated siRNAs." *The Journal of Clinical Pharmacology*. 2024;64(4):422-438.
https://accp1.onlinelibrary.wiley.com/doi/10.1002/jcph.2337

[6] Nair JK, Willoughby JL, Chan A, et al. "Multivalent N-acetylgalactosamine-conjugated siRNA localizes in hepatocytes and elicits robust RNAi-mediated gene silencing." *Journal of the American Chemical Society*. 2014;136(49):16958-16961.
https://pubs.acs.org/doi/10.1021/ja505986a

[7] Hassler MR, Turanov AA, Alterman JF, et al. "Expanding Conjugate Space of RNAi Therapeutics: Ligand at the 3' End of the Antisense Strand." *Journal of Medicinal Chemistry*. 2024.
https://pubs.acs.org/doi/10.1021/acs.jmedchem.4c02250

[8] Gilleron J, Querbes W, Zeigerer A, et al. "Endosomal escape: A bottleneck for LNP-mediated therapeutics." *Proceedings of the National Academy of Sciences*. 2023;120(44):e2307800120.
https://www.pnas.org/doi/10.1073/pnas.2307800120

[9] Bhatt DK, Rasmussen MM, Bhatt DK, et al. "Limiting endosomal damage sensing reduces inflammation triggered by lipid nanoparticle endosomal escape." *Nature Nanotechnology*. 2025.
https://www.nature.com/articles/s41565-025-01974-5

[10] Blakney AK, Ip S, Geall AJ. "An Update on Self-Amplifying mRNA Vaccine Development." *Vaccines*. 2021;9(2):97.
https://pmc.ncbi.nlm.nih.gov/articles/PMC7911542/

[11] Bloom K, van den Berg F, Arbuthnot P. "Self-amplifying RNA vaccines for infectious diseases." *Gene Therapy*. 2021;28:117-129.
https://www.nature.com/articles/s41434-020-00204-y

[12] Finkel RS, Mercuri E, Darras BT, et al. "Nusinersen versus Sham Control in Infantile-Onset Spinal Muscular Atrophy." *New England Journal of Medicine*. 2017;377(18):1723-1732.
https://www.nejm.org/doi/full/10.1056/NEJMoa1702752

[13] Adams D, Gonzalez-Duarte A, O'Riordan WD, et al. "Patisiran, an RNAi Therapeutic, for Hereditary Transthyretin Amyloidosis." *New England Journal of Medicine*. 2018;379(1):11-21.
https://www.nejm.org/doi/full/10.1056/NEJMoa1716153

[14] Maurer MS, Schwartz JH, Gundapaneni B, et al. "Patisiran Treatment in Patients with Transthyretin Cardiac Amyloidosis." *New England Journal of Medicine*. 2023;389(17):1553-1565.
https://www.nejm.org/doi/full/10.1056/NEJMoa2300757

[15] Ray KK, Wright RS, Kallend D, et al. "Two Phase 3 Trials of Inclisiran in Patients with Elevated LDL Cholesterol." *New England Journal of Medicine*. 2020;382(16):1507-1519.
https://www.nejm.org/doi/full/10.1056/NEJMoa1912387

[16] Wright RS, Koenig W, Gencer B, et al. "Inclisiran administration potently and durably lowers LDL-C over an extended-term follow-up: the ORION-8 trial." *European Heart Journal*. 2024.
https://pmc.ncbi.nlm.nih.gov/articles/PMC11481169/

[17] Desai AS, Webb DJ, Bhatt DL, et al. "Zilebesiran in Combination With a Standard-of-Care Antihypertensive in Patients With Inadequately Controlled Hypertension (KARDIA-2)." Presented at ACC 2024.
https://www.acc.org/Latest-in-Cardiology/Clinical-Trials/2024/04/05/04/26/kardia-2

[18] Gillmore JD, Gane E, Taubel J, et al. "Individualised neoantigen therapy mRNA-4157 (V940) plus pembrolizumab versus pembrolizumab monotherapy in resected melanoma (KEYNOTE-942)." *The Lancet*. 2024;403(10427):632-644.
https://pubmed.ncbi.nlm.nih.gov/38246194/

[19] Merck/Moderna. "RFS Benefit Sustained at 5 Years for Intismeran Autogene in Melanoma." 2025.
https://www.targetedonc.com/view/rfs-benefit-sustained-at-5-years-for-intismeran-autogene-in-melanoma

---

*면책조항: 본 리뷰는 정보 제공 목적으로 작성되었으며, 특정 종목에 대한 투자 권유가 아닙니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.*
