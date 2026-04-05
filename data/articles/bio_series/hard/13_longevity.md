# 바이오 기술 리뷰 #13: 장수과학 / 노화 역전 — 기전, 임상 데이터, 투자 분석

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

### 1.1 노화의 재정의: 질병인가, 자연 과정인가

장수과학(longevity science)은 노화를 불가피한 생물학적 운명이 아닌 **치료 가능한 병리학적 과정**으로 재정의하는 패러다임 전환에 기반한다. 2013년 Carlos Lopez-Otin 등이 제시한 **노화의 9가지 특징(hallmarks of aging)**은 이 분야의 분자적 프레임워크를 확립했다: 게놈 불안정성(genomic instability), 텔로미어 마모(telomere attrition), 후성유전적 변화(epigenetic alterations), 단백질 항상성 소실(loss of proteostasis), 영양 감지 기능 이상(deregulated nutrient sensing), 미토콘드리아 기능 장애(mitochondrial dysfunction), 세포 노화(cellular senescence), 줄기세포 고갈(stem cell exhaustion), 세포 간 통신 변화(altered intercellular communication)이다.

각 hallmark은 독립적인 치료 축을 형성하며, 현재 전임상에서 Phase 2까지 다양한 단계의 중재(intervention)가 시도되고 있다. 그러나 FDA는 여전히 "노화(aging)"를 공식 적응증(indication)으로 인정하지 않기 때문에, 모든 임상시험은 특발성 폐섬유증(IPF), 경도인지장애(MCI), 골관절염(OA) 등 **특정 노화 관련 질환**으로 우회하여 설계된다.

### 1.2 분자 메커니즘의 통합적 이해

노화의 분자적 기전은 단일 경로가 아닌 **다층적 네트워크**로 구성된다. 텔로미어 단축이 DNA 손상 반응(DDR)을 활성화하고, DDR은 p53/p21 경로를 통해 세포주기 정지를 유도하며, 정지된 세포는 SASP(senescence-associated secretory phenotype)를 통해 주변 조직에 만성 염증을 전파한다. 동시에 mTOR 경로의 과활성화는 오토파지(autophagy)를 억제하여 손상된 단백질과 미토콘드리아의 축적을 초래하고, NAD+ 수준의 감소는 시르투인(sirtuin) 의존적 DNA 수복 기전을 약화시킨다.

이러한 경로 간 상호 연결성(crosstalk)이 장수과학의 핵심 도전 과제이자 기회다: 하나의 경로를 성공적으로 표적화하면 다른 경로에도 연쇄적 긍정 효과가 기대되지만, 동시에 예측하지 못한 부작용의 가능성도 존재한다.

---

## 2. 핵심 기술 세부

### 2.1 Hayflick 한계와 텔로미어 생물학

#### 2.1.1 Hayflick 한계의 분자적 기반

1961년 Leonard Hayflick이 발견한 **세포 분열 한계(Hayflick limit)**는 정상 체세포가 약 50-70회 분열 후 비가역적 성장 정지에 도달하는 현상이다. 이 한계의 분자적 기반은 **텔로미어(telomere)**에 있다. 텔로미어는 진핵세포 염색체 말단에 위치한 반복적 DNA 서열(인간의 경우 TTAGGG 반복)로, 각 세포 분열마다 50-200 bp씩 단축된다. 이는 DNA 중합효소가 라깅 가닥(lagging strand)의 3' 말단을 완전히 복제하지 못하는 **말단 복제 문제(end-replication problem)** 때문이다.

텔로미어가 임계 길이(약 4-6 kb) 이하로 단축되면, 탈보호된 염색체 말단이 DNA 이중쇄 절단으로 인식되어 ATM/ATR 키나제 의존적 DDR이 활성화된다. 이는 p53 안정화 → p21^CIP1 전사 유도 → CDK2 억제 → Rb 탈인산화 경로를 통해 G1/S 체크포인트에서 세포주기를 정지시킨다.

#### 2.1.2 텔로머레이스 복합체: TERT와 TERC

**텔로머레이스(telomerase)**는 텔로미어 단축을 상쇄하는 리보핵산단백질(ribonucleoprotein) 역전사효소다. 두 가지 핵심 구성 요소로 이루어진다:

- **TERT (Telomerase Reverse Transcriptase)**: 촉매 서브유닛으로, 역전사효소 활성을 가진다. TERT는 RNA 주형을 기반으로 텔로미어 반복 서열을 합성하며, 텔로미어 말단의 3' 오버행에 결합하여 신장(elongation)을 수행한다.

- **TERC (Telomerase RNA Component, TR)**: 텔로미어 반복 합성의 주형을 제공하는 451 nt 비암호화 RNA다. TERC는 TERT의 촉매 활성에 필수적이며, 5'-CUAACCCUAAC-3' 서열이 TTAGGG 반복의 직접적 주형으로 기능한다.

대부분의 정상 체세포에서 TERT 유전자 발현은 후성유전적으로 침묵되어 있으며, 이로 인해 텔로머레이스 활성이 검출 불가능한 수준이다. 반면, 줄기세포와 생식세포에서는 TERT가 활성화되어 텔로미어 길이를 유지한다. 주목할 만한 점은 **암세포의 약 85-90%에서 TERT가 재활성화**되어 무한 증식 능력을 획득한다는 것이다. 이러한 이유로 텔로머레이스 활성화 기반 항노화 전략은 종양 형성 위험이라는 본질적 딜레마를 안고 있다.

Blasco 그룹(2012)의 마우스 모델 연구에서, 유도성(inducible) TERT의 내인적 재활성화가 조기 노화 마우스의 다장기 기능을 회복시키고, 주요하게는 **종양 발생률 증가 없이** 수명을 연장했다는 결과는 이 접근법의 가능성과 안전성에 대한 중요한 전임상 근거를 제공한다.

### 2.2 세포 노화와 SASP (Senescence-Associated Secretory Phenotype)

#### 2.2.1 세포 노화의 분자 경로

세포 노화는 **비가역적 세포주기 정지** 상태로, 크게 두 가지 주요 종양 억제 경로에 의해 유도되고 유지된다:

**p53/p21 경로**: DDR이 ATM/ATR 키나제를 활성화하면, CHK1/CHK2를 통해 p53이 안정화된다. 안정화된 p53은 CDKN1A 유전자의 전사를 촉진하여 p21^CIP1 단백질을 발현시킨다. p21은 CDK2-cyclin E 복합체를 억제하여 Rb의 인산화를 방지하고, 이로써 E2F 전사인자의 방출이 차단되어 S기 진입이 불가해진다. 이 경로는 주로 노화 **개시(initiation)**에 관여한다.

**p16^INK4a/Rb 경로**: p16^INK4a (CDKN2A 유전자 산물)는 CDK4/CDK6-cyclin D 복합체에 직접 결합하여 그 키나제 활성을 억제한다. CDK4/6 억제는 Rb의 저인산화 상태를 유지시키고, 비활성 Rb-E2F 복합체 형성을 통해 세포주기를 G1기에 고착시킨다. p16 경로는 노화의 **유지(maintenance)**에 더 중요하며, 조직 내 p16 양성 세포의 축적은 생물학적 나이의 강력한 바이오마커로 사용된다.

두 경로는 상호 보완적이며, p53 경로의 실패 시에도 p16 경로가 노화를 유지할 수 있는 이중 안전장치를 구성한다.

#### 2.2.2 SASP의 분자적 구성과 조절

노화 세포는 단순히 '잠든' 세포가 아니라, **활발한 분비 프로그램**을 실행하는 세포다. SASP는 다음 구성 요소들의 복합적 분비체(secretome)다:

- **염증성 사이토카인**: IL-6, IL-8 (CXCL8), IL-1alpha, IL-1beta — 이들은 SASP의 가장 보존되고 강력한 구성 요소다. IL-6는 JAK/STAT3 경로를 통해 인접 세포에 염증 신호를 전달하고, paracrine senescence를 유도한다.
- **케모카인**: MCP-1 (CCL2), GROalpha (CXCL1), MIP-1alpha — 면역세포 동원(recruitment)에 관여
- **매트릭스 메탈로프로테이나아제(MMP)**: MMP-1, MMP-3, MMP-9 — 세포외기질 분해를 촉진하여 조직 구조를 와해
- **성장인자**: VEGF, HGF, TGF-beta — 조직 리모델링과 섬유화에 기여
- **세포외소포체(EVP)**: miRNA와 단백질을 담은 엑소좀을 통해 원거리 paracrine 신호 전달

SASP의 전사적 조절에서 핵심 조절자는 **NF-kappaB**다. 지속적 DDR 신호가 NF-kappaB를 활성화하고, 활성화된 NF-kappaB는 IL-6, IL-8 등 SASP 인자들의 전사를 직접 구동한다. 이에 더해, **C/EBPbeta** 전사인자와 **mTOR** 경로도 SASP 조절에 관여하며, mTOR는 SASP mRNA의 번역 효율을 조절하는 것으로 알려져 있다. 이러한 mTOR-SASP 연결이 라파마이신의 세노모르픽(senomorphic) 효과의 분자적 기반을 제공한다.

### 2.3 부분 리프로그래밍 (Partial Reprogramming / OSKM)

#### 2.3.1 야마나카 인자와 세포 운명 역전

2006년 야마나카 신야(Shinya Yamanaka)가 발견한 4개의 전사인자 — **Oct4 (O), Sox2 (S), Klf4 (K), c-Myc (M)** — 는 분화된 체세포를 만능줄기세포(iPSC)로 역분화시키는 능력을 가진다. 부분 리프로그래밍은 이 OSKM 인자들을 **단기간, 제어된 발현**으로 사용하여, 세포 정체성(identity)을 유지하면서 후성유전적 나이만 되돌리는 전략이다.

#### 2.3.2 부분 리프로그래밍의 분자 기전

전체 리프로그래밍과 부분 리프로그래밍의 차이는 **발현 기간과 강도**에 있다:

- **전체 리프로그래밍** (수주간 지속 발현): 체세포 정체성 완전 소실 → 다능성(pluripotency) 획득 → iPSC 형성. 체내에서는 테라토마(teratoma) 형성 위험.
- **부분 리프로그래밍** (수일간 단기 발현): DNA 메틸화 패턴의 부분적 리셋 → 후성유전적 나이 감소, 세포 정체성 유지. OSKM의 단기 발현은 히스톤 변형(H3K9me3, H3K27me3)과 DNA 메틸화를 노화 이전 상태로 부분 복원한다.

Browder 등(2022)은 장기간 주기적 부분 리프로그래밍(doxycycline 유도 OSKM, 2일 ON/5일 OFF, 7개월)이 마우스의 피부, 신장, 혈액 후성유전적 시계를 젊게 되돌렸음을 보고했다. 중요하게도 c-Myc의 종양유전자적 성격 때문에 최근 연구는 **OSK (c-Myc 제외) 3인자 조합**에 집중하고 있다. Sinclair 그룹(2023)은 AAV 전달 유도성 OSK 시스템을 124주령 노화 마우스에 전신 투여하여 **중앙 잔여 수명을 109% 연장**하고 다수의 건강 매개변수를 개선했으며, c-Myc 없이도 충분한 회춘 효과가 달성됨을 입증했다.

#### 2.3.3 안전성 고려사항

단 하나의 만능 세포도 종양을 형성하기에 충분하다는 점에서, **발현량과 타이밍의 정밀 제어**가 핵심 안전 과제다. 현재 접근법들은 다음과 같은 안전장치를 채택한다:

- **유도성 프로모터** (Tet-On/Off): 약물(doxycycline)로 발현을 켜고 끌 수 있음
- **조직 특이적 프로모터**: 목표 조직에서만 인자 발현
- **OSK 3인자 조합**: 종양유전자 c-Myc 제외
- **화학적 리프로그래밍**: Yamanaka 인자 대신 소분자 칵테일로 대체 (Yang 등, 2023, *Aging*)

### 2.4 라파마이신과 mTOR 경로

#### 2.4.1 mTOR 신호전달의 구조

**mTOR (mechanistic Target of Rapamycin)**는 세포 성장, 대사, 오토파지를 통합 조절하는 serine/threonine 키나제로, 두 가지 기능적으로 구별되는 복합체를 형성한다:

- **mTORC1** (mTOR-Raptor-mLST8-PRAS40-DEPTOR): 영양소, 성장인자, 에너지 상태를 감지하여 단백질 합성(S6K1, 4E-BP1 인산화), 지질 합성, 뉴클레오티드 합성을 촉진하고 오토파지를 억제한다.
- **mTORC2** (mTOR-Rictor-mLST8-mSIN1-Protor): Akt/PKB를 인산화하여 세포 생존, 대사, 세포골격 조직을 조절한다.

노화에서 mTORC1의 과활성화는 핵심 문제다: (1) 오토파지 억제로 손상된 단백질/미토콘드리아 축적, (2) SASP 구성 요소의 번역 증가, (3) 줄기세포 고갈 가속화.

#### 2.4.2 라파마이신의 작용 기전

라파마이신(sirolimus)은 세포 내 수용체 **FKBP12**에 결합하고, FKBP12-라파마이신 복합체가 mTORC1의 FRB 도메인에 결합하여 **mTORC1를 알로스테릭하게 억제**한다. 이 억제의 하류 효과는 다음과 같다:

1. **오토파지 활성화**: ULK1 복합체의 탈억제 → 자가포식소체(autophagosome) 형성 촉진 → 손상된 미토콘드리아(미토파지) 및 단백질 응집체 제거
2. **SASP 감소**: 4E-BP1 탈인산화 → SASP 구성 요소(IL-6, IL-8 등) mRNA의 cap-dependent 번역 억제
3. **줄기세포 기능 보존**: 조혈줄기세포 및 장관줄기세포의 자기복제(self-renewal) 능력 유지
4. **면역 조절**: 저용량에서 면역기능 개선 (paradoxical immunostimulation) — Mannick 등(2014)이 건강한 노인에서 인플루엔자 백신 반응 개선을 보고

라파마이신은 모델 생물에서 가장 일관된 수명 연장 효과를 보여준 약물이다: 효모, 선충, 초파리, 마우스에서 모두 수명 연장이 확인되었으며, 특히 NIA Interventions Testing Program에서 마우스 수명을 **9-14%** 연장했다.

### 2.5 NAD+ 구제 경로 (NAD+ Salvage Pathway)

#### 2.5.1 NAD+ 대사의 분자 생화학

**NAD+ (Nicotinamide Adenine Dinucleotide)**는 세포 에너지 대사, DNA 수복, 유전자 발현 조절에 관여하는 필수 조효소다. 나이가 들면서 NAD+ 수준이 현저하게 감소하며(40-60대에서 약 50% 감소), 이는 미토콘드리아 기능 저하의 핵심 원인으로 지목된다.

NAD+ 생합성에는 세 가지 경로가 존재한다:

1. **De novo 합성** (kynurenine pathway): 트립토판에서 출발하여 quinolinate → nicotinic acid mononucleotide 경로로 NAD+ 합성
2. **Preiss-Handler 경로**: 니코틴산(NA) → NAMN → NAAD → NAD+ 경로
3. **구제 경로 (Salvage pathway)**: 포유류 세포에서 가장 중요한 NAD+ 재생 경로로, **NAMPT (Nicotinamide Phosphoribosyltransferase)**가 속도결정효소다.

구제 경로의 핵심 반응:
```
Nicotinamide (NAM) → [NAMPT] → NMN → [NMNAT1/2/3] → NAD+
```

**NMN (Nicotinamide Mononucleotide)**과 **NR (Nicotinamide Riboside)**은 모두 NAD+ 전구체(precursor)로 작용한다:
- NR은 **NRK1/NRK2 (Nicotinamide Riboside Kinase)**에 의해 NMN으로 전환된 후 NAD+로 합성된다.
- NMN은 NMNAT에 의해 직접 NAD+로 전환된다.

#### 2.5.2 NAD+와 시르투인 의존적 방어 기전

NAD+의 노화 방지 효과는 주로 **시르투인(SIRT1-7)** 패밀리를 통해 매개된다:

- **SIRT1**: 핵에서 히스톤/비히스톤 단백질의 탈아세틸화 → PGC-1alpha 활성화 → 미토콘드리아 생합성 촉진; p53 탈아세틸화 → 세포자멸사 억제
- **SIRT3**: 미토콘드리아 기질에서 SOD2 탈아세틸화 → 산화적 스트레스 방어; 전자전달계 복합체 탈아세틸화 → 대사 효율 향상
- **SIRT6**: 텔로미어 유지, 이중쇄 절단(DSB) 수복, 당 분해 억제

NAD+가 감소하면 이 시르투인 의존적 방어 기전이 약화되어 게놈 불안정성, 미토콘드리아 기능 장애, 만성 염증이 가속화된다. 또한 NAD+를 소비하는 효소인 **CD38** (NAD+ glycohydrolase)의 노화 관련 과발현과 **PARP1** (DNA 수복 효소)의 과활성화가 NAD+ 고갈을 심화시킨다.

### 2.6 후성유전적 시계 (Horvath Epigenetic Clock)

#### 2.6.1 DNA 메틸화 기반 노화 측정

2013년 Steve Horvath가 개발한 **후성유전적 시계(epigenetic clock)**는 DNA 메틸화(CpG 사이트의 5-methylcytosine) 패턴을 기반으로 생물학적 나이를 추정하는 수학적 모델이다. 원래 Horvath 시계는 **353개 CpG 사이트**의 메틸화 수준을 Illumina 450K 또는 EPIC 어레이로 측정하여, 다양한 조직(51개 조직/세포 유형)에 걸쳐 r > 0.96의 정확도로 연대기적 나이를 예측한다.

후속 시계들이 개발되었다:

- **Hannum Clock** (2013): 혈액 DNA 메틸화 기반, 71개 CpG 마커
- **PhenoAge/GrimAge** (Levine, 2018; Lu, 2019): 사망률과 질병 위험을 더 정확히 반영하는 "2세대" 시계
- **DunedinPACE** (Belsky, 2022): DNA 메틸화로 노화 **속도(pace)**를 측정하는 시계
- **범포유류 시계** (Horvath, 2023): Mammalian Methylation Consortium의 11,754개 어레이 데이터, 185종에 걸친 범종(pan-mammalian) 노화 시계 (r > 0.96)

#### 2.6.2 후성유전적 시계의 기전적 의미

후성유전적 시계가 측정하는 CpG 메틸화 변화는 **Polycomb Repressive Complex 2 (PRC2)** 결합 부위에 고도로 집중되어 있다. PRC2는 H3K27me3 히스톤 마크를 통해 발생 유전자를 억제하는 복합체로, 노화에 따른 PRC2 결합 부위의 메틸화 표류(drift)가 유전자 발현 프로그램의 탈조절을 반영한다는 가설이 유력하다.

후성유전적 나이 가속(epigenetic age acceleration, 생물학적 나이 > 연대기적 나이)은 **전체 사망률, 심혈관 질환, 암, 알츠하이머병**과 유의한 상관관계를 보이며, 이는 후성유전적 시계가 단순한 바이오마커가 아닌 노화의 **기전적 매개자**일 수 있음을 시사한다. 실제로 부분 리프로그래밍(OSKM/OSK)이 후성유전적 시계를 되돌린다는 결과는 이 시계가 **치료적 중재의 표적**이 될 수 있음을 보여준다.

---

## 3. 임상 데이터

### 3.1 세노리틱스 (Senolytics) 임상시험

#### 3.1.1 Dasatinib + Quercetin (D+Q)

D+Q 조합은 BCL-2 패밀리(노화 세포의 생존에 필수적인 항아포토시스 단백질)와 p53 경로를 표적으로 하는 최초의 세노리틱 조합 요법이다.

**STAMINA 연구 (2025)**: eBioMedicine에 발표된 이 pilot study는 65세 이상의 보행 속도 저하 + 경도인지장애 환자 12명을 대상으로, Dasatinib 100 mg + Quercetin 1250 mg을 2주 간격으로 2일간 투여하는 간헐적 프로토콜을 12주간 수행했다. 인지 기능(MoCA) 및 보행 기능의 개선 경향이 관찰되었으나, 소규모 오픈 라벨 특성상 확정적 결론은 유보된다.

**골밀도 Phase 2 RCT (2024)**: Nature Medicine에 발표된 이 무작위 대조 시험은 폐경 후 여성 60명을 D+Q군 30명 + 대조군 30명으로 20주간 추적했다. 골흡수 마커에는 군 간 차이가 없었으나, D+Q군에서 초기(2-4주) 골형성 마커의 유의한 증가가 관찰되었다. 20주 시점에서는 군 간 차이가 소실되어, 간헐적 투여의 **효과 지속성(durability)**이 핵심 과제로 남았다.

#### 3.1.2 Unity Biotechnology: UBX0101 / UBX1325

Unity Biotechnology는 세노리틱스 상업화의 선구자였으나, 연속적 임상 실패를 경험했다:

- **UBX0101 (BCL-xL 억제제, 관절 내 주사)**: 무릎 골관절염 대상 Phase 2에서 12주 시점 통증 감소가 위약과 유의한 차이를 보이지 못함 (2020).
- **UBX1325 (BCL-xL 억제제, 유리체강 내 주사)**: 당뇨성 황반부종 대상 Phase 2b에서 24주 시점 표준치료(anti-VEGF) 대비 비열등성(non-inferiority) 달성 실패 (2024).

2025년 9월 Unity Biotechnology 주주들은 회사 청산을 승인했다. 이 실패의 교훈은 다음과 같다: (1) 국소 세노리틱 전달만으로는 전신적 노화 세포 부담(senescent cell burden)을 충분히 해결하지 못할 수 있다; (2) 노화 세포 제거가 실제로 이루어졌는지에 대한 PD 바이오마커 확인이 부재했다; (3) 노화 세포의 일부 유익한 기능(조직 수복 시 일시적 노화)을 고려해야 한다.

### 3.2 라파마이신 임상시험

#### 3.2.1 PEARL 시험 (2024-2025)

**PEARL (Participatory Evaluation of Aging with Rapamycin for Longevity)**은 라파마이신 장기 인체 투여의 첫 번째 대규모 RCT다. 48주, 이중맹검, 위약 대조 설계로 114명의 건강한 성인(평균 60세)이 완료했다: 10 mg군 35명, 5 mg군 40명, 위약군 39명.

주요 결과 (Aging 저널, 2025):
- **1차 종료점 (내장 지방)**: 군 간 유의한 차이 없음
- **안전성**: 이상반응 및 심각한 이상반응 빈도가 전 군에서 유사
- **2차 탐색적 종료점**: 10 mg 라파마이신 투여 여성에서 제지방량(lean tissue mass) 유의한 증가 및 자기보고 통증 개선; 5 mg군에서 정서적 안녕감과 전반적 건강 개선
- **제한점**: 자기보고 의존, 혈액 바이오마커 변화가 정상 범위 내, 라파마이신이 인간 수명/건강수명을 연장한다는 직접적 증거 미제공

#### 3.2.2 RAPA-501-ALLO 등 기타 시험

저용량 라파마이신은 면역 노화(immunosenescence) 개선, 염증 바이오마커 감소에 대한 소규모 시험이 진행 중이며, 피부 노화(국소 라파마이신)에 대한 Phase 2 결과도 보고되고 있다.

### 3.3 NAD+ 전구체 임상시험

**NR (Nicotinamide Riboside)**:
- MCI 환자 대상 위약 대조 파일럿 (2024, PMC): 20명을 대상으로 NR 1 g/day, 10주 투여. 혈중 NAD+ 수준 유의 상승, 인지 기능에 대한 탐색적 양성 신호.
- Long-COVID 환자 대상 24주 RCT (2025, eClinicalMedicine): 58명 등록, NR 20주 투여. NAD+ 수준 회복 확인, 인지 및 증상 회복에 대한 제한적 효과.

**NMN (Nicotinamide Mononucleotide)**:
- 건강한 고령자(65-75세) 대상 12주 RCT: NMN 250 mg/day 투여군에서 4m 보행 시간 유의 단축 및 수면의 질 개선.
- 메타분석 (2024, PMC): 9개 연구, 412명. NMN은 보행 속도 기반 근육 기능 개선, 인슐린 저항성 감소, 아미노트랜스퍼라제 감소 효과. 그러나 대퇴 근육량에 대한 효과는 임상적으로 미미.

### 3.4 부분 리프로그래밍

2026년 현재 인체 임상시험에 진입한 부분 리프로그래밍 프로그램은 없다. Altos Labs, NewLimit, Retro Biosciences 등이 전임상 단계에서 활발히 연구 중이며, 2027-2028년 첫 IND 신청이 기대된다.

---

## 4. 시장 분석

### 4.1 시장 규모와 세분화

| 세그먼트 | 2025 추정 | 2030 전망 | CAGR |
|---------|----------|----------|------|
| 노화 방지 전체 시장 (화장품 + 보충제 + 치료제) | $85B+ | $120B+ | ~7% |
| 장수 바이오텍 치료제 | <$1B | $5-10B (승인 시) | >30% |
| NAD+ 보충제 | $500M+ | $1B+ | ~15% |
| 후성유전적 진단/바이오마커 | $200M | $1B+ | ~25% |

### 4.2 주요 기업 벨류에이션과 투자 현황

| 기업 | 상태 | 접근법 | 투자/시가총액 |
|------|------|--------|-------------|
| Altos Labs | 비상장 | 부분 리프로그래밍 | $3B+ (Bezos, Milner) |
| Retro Biosciences | 비상장 | 리프로그래밍, 혈장교환, 오토파지 | Sam Altman 투자 |
| NewLimit | 비상장 | 후성유전 편집 + AI | Sam Altman 투자 |
| Calico (Alphabet) | 비상장 | ML 기반 노화 연구 | Alphabet 자회사 |
| BioAge Labs (BIOA) | 상장 | 노화 바이오마커 기반 약물 재목적화 | 소형주 |
| ChromaDex (CDXC) | 상장 | Tru Niagen (NR 보충제) | 소형주 |
| Hevolution Foundation | 재단 | 장수 연구 펀딩 | 사우디 $1B/yr |

### 4.3 투자 관점 핵심 테제

1. **10년+ 초장기 시계**: FDA 승인 노화 치료제가 없으며, 대부분 전임상~Phase 2 단계. "노화" 적응증 인정 전까지는 질환별 우회 필요.
2. **삽과 곡괭이 전략이 가장 안전**: 후성유전적 시계 측정 기업, 오믹스 분석 기업(Illumina, Thermo Fisher)이 분야 전체의 수혜자.
3. **후성유전 리프로그래밍 = 최대 보상/최대 리스크**: 성공 시 의학 역사의 전환점이지만, 안전성 문제로 상업화까지 가장 긴 경로.
4. **GLP-1 비만약 간접 수혜**: 체중 감량이 노화 관련 질환(당뇨, 심혈관) 개선 → 노화 바이오마커 개선의 간접 경로.
5. **규제 리스크**: FDA가 "노화"를 적응증으로 인정하면 시장 급팽창, 미인정 시 질환별 시장으로 분산.

---

## 5. AI 적용

### 5.1 후성유전적 시계와 ML

Horvath 시계 자체가 **엘라스틱넷 회귀(elastic net regression)** 기반 ML 모델이다. 이후 딥러닝 기반 시계(DeepMAge, AltumAge)가 개발되어 예측 정확도와 노이즈 내성이 향상되었다. 2023년 Horvath의 범포유류 시계는 11,754개 메틸화 어레이와 185종 데이터를 학습하여, 종 간 보편적 노화 시그니처를 추출했다.

### 5.2 약물 재목적화 (Drug Repurposing)

BioAge Labs(BIOA)의 플랫폼은 대규모 종단적 바이오마커 데이터(UK Biobank 등)에 ML을 적용하여, 기존 약물 중 노화 경로에 영향을 미치는 후보를 식별한다. 이 접근법은 이미 Phase 2 까지 진입한 후보들을 보유하고 있으며, 전통적 신약 개발 대비 시간과 비용을 대폭 절감한다.

### 5.3 노화 바이오마커 발굴

멀티오믹스(유전체 + 전사체 + 단백체 + 대사체 + 마이크로바이옴) 데이터를 통합 분석하는 **그래프 신경망(GNN)**과 **트랜스포머 모델**이 노화 진행도를 다차원적으로 측정하는 복합 바이오마커 패널 개발에 활용된다.

### 5.4 표적 발견

AI 기반 지식 그래프(knowledge graph)가 문헌, 데이터베이스, 오믹스 데이터를 통합하여 노화 관련 새로운 약물 표적을 식별한다. BenevolentAI의 플랫폼이 이 접근법을 대표하며, Calico는 Alphabet의 데이터 인프라와 ML 역량을 활용하여 노화의 근본 기전 해명에 집중하고 있다.

### 5.5 임상시험 설계 최적화

"노화"의 임상적 종료점(endpoint) 정의가 어렵다는 문제에 대해, AI는 다음 방식으로 기여한다:
- **후성유전적 나이 가속**을 대리 바이오마커로 사용하는 적응적 시험 설계
- 환자 층화(stratification): 생물학적 나이 기반 그룹화로 치료 효과 신호 증폭
- 디지털 바이오마커: 웨어러블 데이터의 ML 분석으로 실시간 노화 진행 모니터링

---

## 6. 참고문헌

1. Lopez-Otin, C., Blasco, M.A., Partridge, L., Serrano, M. & Kroemer, G. "Hallmarks of aging: An expanding universe." *Cell* 186(2), 243-278 (2023). https://doi.org/10.1016/j.cell.2022.11.001

2. Horvath, S. "DNA methylation age of human tissues and cell types." *Genome Biology* 14, R115 (2013). https://doi.org/10.1186/gb-2013-14-10-r115

3. Horvath, S., Haghani, A., et al. "Universal DNA methylation age across mammalian tissues." *Nature Aging* 3, 1144-1166 (2023). https://www.nature.com/articles/s43587-023-00462-6

4. Browder, K.C., et al. "In vivo partial reprogramming alters age-associated molecular changes during physiological aging in mice." *Nature Aging* 2, 243-253 (2022). https://doi.org/10.1038/s43587-022-00183-2

5. Yang, J.-H., et al. "Gene therapy-mediated partial reprogramming extends lifespan and reverses age-related changes in aged mice." *Cellular Reprogramming* 26(1), 24-32 (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC10909732/

6. Mannick, J.B., et al. "TORC1 inhibition enhances immune function and reduces infections in the elderly." *Science Translational Medicine* 10(449), eaaq1564 (2018). https://doi.org/10.1126/scitranslmed.aaq1564

7. Georgila, K., Vyrla, D. & Drakos, E. "Apolipoprotein E in health and disease: PEARL trial results — Influence of rapamycin on safety and healthspan metrics after one year." *Aging* (2025). https://pmc.ncbi.nlm.nih.gov/articles/PMC12074816/

8. Hickson, L.J., et al. "Senolytics decrease senescent cells in humans: Preliminary report from a clinical trial of Dasatinib plus Quercetin in individuals with diabetic kidney disease." *eBioMedicine* 47, 446-456 (2019). https://doi.org/10.1016/j.ebiom.2019.08.069

9. Gonzales, M.M., et al. "A pilot study of senolytics to improve cognition and mobility in older adults at risk for Alzheimer's disease." *eBioMedicine* 113, 105571 (2025). https://www.thelancet.com/journals/ebiom/article/PIIS2352-3964(25)00056-8/fulltext

10. Gorgoulis, V., Adams, P.D., et al. "Cellular senescence: Defining a path forward." *Cell* 179(4), 813-827 (2019). https://doi.org/10.1016/j.cell.2019.10.005

11. Herranz, N. & Gil, J. "The senescence-associated secretory phenotype and its physiological and pathological implications." *Nature Reviews Molecular Cell Biology* 25, 958-978 (2024). https://www.nature.com/articles/s41580-024-00727-x

12. Rajman, L., Chwalek, K. & Bhupinder, S. "Therapeutic potential of NAD-boosting molecules: the in vivo evidence." *Cell Metabolism* 27(3), 529-547 (2018). https://doi.org/10.1016/j.cmet.2018.02.011

13. Freitas-Rodriguez, S., et al. "The relationship between telomere length and aging-related diseases." *Clinical and Experimental Medicine* 25, 56 (2025). https://link.springer.com/article/10.1007/s10238-025-01608-z

14. Rossiello, F., Jurk, D., Passos, J.F. & d'Adda di Fagagna, F. "Telomere dysfunction in ageing and age-related diseases." *Nature Cell Biology* 24, 135-147 (2022). https://www.nature.com/articles/s41556-022-00842-x

---

*본 리뷰는 투자 권유를 목적으로 하지 않으며, 면책조항이 적용됩니다. 모든 투자 판단은 개인의 책임하에 이루어져야 합니다.*
