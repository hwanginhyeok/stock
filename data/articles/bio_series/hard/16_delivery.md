# 바이오 기술 리뷰 #16: 약물 전달 시스템 — 기전, 임상 데이터, 투자 분석

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

### 1.1 약물 전달의 근본 문제

약물 전달 시스템(Drug Delivery Systems, DDS)은 바이오의학의 **"최종 마일(last mile) 문제"**를 해결하는 기술이다. 아무리 강력한 치료적 분자도, 목표 세포의 세포질(또는 핵)에 도달하지 못하면 무용지물이다. 이 문제는 특히 핵산 치료제(mRNA, siRNA, CRISPR 가이드 RNA)에서 극적으로 부각된다: 이들은 (1) 대형 음하전 분자로 세포막 투과 불가, (2) 혈중 뉴클레아제에 의한 급속 분해, (3) 신장에 의한 빠른 배설의 삼중 장벽에 직면한다.

약물 전달 시스템은 다음 기능을 수행한다:
- **보호(Protection)**: 생체 내 분해로부터 치료적 분자 보호
- **표적화(Targeting)**: 목표 조직/세포로의 선택적 축적
- **세포 내 전달(Intracellular delivery)**: 세포막 통과 및 엔도솜 탈출(endosomal escape)
- **제어 방출(Controlled release)**: 시간적/공간적 방출 제어

### 1.2 약물 전달 기술의 분류

| 기술 | 적용 화물(cargo) | 주요 표적 장기 | 성숙도 |
|------|----------------|--------------|--------|
| **LNP** (지질 나노입자) | mRNA, siRNA, CRISPR gRNA | 간 (기본) → 폐, 뇌 (연구 중) | 상용화 |
| **GalNAc 접합** | siRNA, ASO | 간 (전용) | 상용화 |
| **AAV** (아데노연관바이러스) | DNA (유전자) | 다양 (혈청형 의존) | 상용화 |
| **엑소좀** | 단백질, RNA, 소분자 | 연구 중 | 전임상-Phase 1 |
| **폴리머 나노입자** | 소분자, 단백질 | 다양 | 상용화 |
| **ADC** | 세포독성 소분자 | 종양 (항체 표적) | 상용화 |

### 1.3 COVID-19가 촉발한 패러다임 전환

Moderna (Spikevax)와 Pfizer/BioNTech (Comirnaty) COVID-19 mRNA 백신은 LNP 기술의 **대규모 인체 검증**을 달성했다. 수십억 회 투여(>13B doses globally)라는 전례 없는 규모에서 LNP-mRNA 시스템의 안전성과 유효성이 입증되었으며, 이는 LNP를 단순 백신 플랫폼을 넘어 **범용 핵산 전달 시스템**으로 확립하는 계기가 되었다.

---

## 2. 핵심 기술 세부

### 2.1 LNP 이온화 지질 화학 (LNP Ionizable Lipid Chemistry)

#### 2.1.1 LNP의 4성분 구조

LNP는 4가지 지질 성분의 정밀한 조합으로 구성된다:

1. **이온화 가능 지질 (Ionizable lipid)**: LNP의 핵심 구성 요소 (전체 지질의 30-50 mol%). 생리적 pH (7.4)에서 중성이나, 산성 pH (엔도솜 내 pH 5-6)에서 양전하를 띔. 이 pH 의존적 전하 전환이 LNP의 작동 원리의 핵심.
2. **헬퍼 지질 (Helper lipid)**: DSPC(1,2-distearoyl-sn-glycero-3-phosphocholine) — 이중층 안정화
3. **콜레스테롤**: 막 강성(rigidity) 및 안정성 부여, 혈중 지단백과의 상호작용 조절
4. **PEG-지질 (PEGylated lipid)**: DMG-PEG2000 등 — 스텔스 효과로 면역 회피, 입자 크기 제어 (80-100 nm)

#### 2.1.2 핵심 이온화 지질의 화학 구조와 특성

**DLin-MC3-DMA (MC3)**:
- Alnylam/Acuitas가 개발한 최초의 임상적으로 성공한 이온화 지질
- **Onpattro (patisiran)** — 최초의 FDA 승인 siRNA 치료제 (2018)에 사용
- 구조: 디메틸아미노 머리(head group) + 리놀레일(linoleyl) 이중 불포화 알킬 사슬 2개
- **pKa ~6.44**: 이 값이 엔도솜 pH와 혈중 pH 사이에 위치하여, 혈중에서는 중성(면역 회피), 엔도솜 내에서는 양전하(막 파괴)의 이중 기능을 수행
- **한계**: 에스테르 결합 부재로 생분해성 제한 → 간 축적 우려

**SM-102**:
- Moderna의 Spikevax COVID-19 백신에 사용
- 구조: 분지형(branched) 포화 알킬 사슬 + **에스테르 결합 2개** — MC3 대비 생분해성 대폭 향상
- pKa ~6.68
- 에스테르 결합이 체내 에스테라아제에 의해 가수분해되어 무독성 대사물로 분해
- In vitro에서 단백질 발현 유도 효율이 가장 우수

**ALC-0315**:
- Pfizer/BioNTech의 Comirnaty COVID-19 백신에 사용
- Acuitas Therapeutics에서 라이선스
- 구조: SM-102와 유사한 분지형 포화 사슬 + 에스테르 결합 2개
- pKa ~6.09
- MC3 대비 에스테르 결합의 생분해성 추가가 핵심 개선점

#### 2.1.3 이온화 지질의 작동 기전: pH 의존적 전하 전환

LNP의 세포 내 전달 과정을 분자 수준에서 추적하면:

**Step 1: 혈중 이동 (pH 7.4)**
이온화 지질의 3차 아민이 탈양성자화(deprotonated) 상태 → LNP 표면 전하 중성 → PEG 코팅과 함께 **면역계 회피(stealth effect)** 달성. 혈중 ApoE(Apolipoprotein E)가 LNP 표면에 자발적으로 흡착하여 **내인성 표적화 리간드**로 기능 (간세포 LDL 수용체 인식).

**Step 2: 세포 내재화 (Endocytosis)**
ApoE-코팅 LNP가 간세포 LDL 수용체에 결합 → 클라트린 매개 세포내이입(clathrin-mediated endocytosis) → 초기 엔도솜(early endosome)에 포획

**Step 3: 엔도솜 탈출 (Endosomal Escape) — 핵심 단계**
엔도솜 성숙 과정에서 H+-ATPase가 양성자를 펌핑하여 pH 감소 (7.4 → 6.0 → 5.0):
- pH 감소에 따라 이온화 지질의 3차 아민이 **양성자화(protonated)** → 양전하 획득
- 양전하 이온화 지질이 엔도솜 막의 음전하 인지질(phosphatidylserine)과 **이온 쌍(ion pair)**을 형성
- 이온 쌍 형성은 원추형(cone-shaped) 비이중층 지질 구조를 유도
- 이 비이중층 구조가 **역 헥사고날 상(inverted hexagonal phase, HII)** 전이를 촉발
- HII 상 전이가 엔도솜 막의 국소적 파괴(disruption)를 야기
- LNP 내용물(mRNA, siRNA)이 세포질로 방출

**Step 4: 세포질 방출 후**
- mRNA: 리보솜에서 번역 → 치료적 단백질 합성
- siRNA: RISC(RNA-Induced Silencing Complex) 로딩 → 표적 mRNA 분해

#### 2.1.4 LNP의 내부 구조: 역 미셀 모델

2024년 *Accounts of Chemical Research*에 발표된 연구에 따르면, LNP의 내부 구조는 단순한 리포좀이 아닌 **역 미셀(inverted micelle) 구조**다:
- 이온화 지질이 mRNA를 감싸는 역 미셀 코어
- 중성 pH에서 비정렬(non-ordered) 상태
- 산성 pH에서 정렬된 역 미셀 → 역 헥사고날 → 역 큐빅(cubic) 상으로 전이
- 이 메소페이즈(mesophase) 전이와 mRNA 형질전환 효율 간의 상관관계 확인

### 2.2 AAV 혈청형과 조직 향성 (AAV Serotype Tropism)

#### 2.2.1 AAV의 기본 생물학

아데노연관바이러스(Adeno-Associated Virus, AAV)는 약 25 nm 크기의 비외피(non-enveloped) 정20면체 바이러스로, ~4.7 kb의 단일가닥 DNA 게놈을 보유한다. 야생형 AAV는 비병원성이며, 분열하지 않는 세포에서 장기간 유전자 발현을 제공하여 **유전자 치료의 선호 벡터**가 되었다.

재조합 AAV(rAAV)에서 바이러스 유전자(rep, cap)는 치료적 유전자 카세트로 대체되고, 캡시드(capsid) 단백질(VP1, VP2, VP3)만 유지되어 비복제성이 된다.

#### 2.2.2 혈청형별 조직 향성

AAV 캡시드의 표면 구조가 세포 표면 수용체 인식을 결정하며, 이것이 조직 향성(tropism)의 분자적 기반이다:

**수용체 결합 메커니즘**:
- **1차 수용체**: 글리칸(glycan), 당접합체(glycoconjugate), 시알산(sialic acid) — 캡시드의 초기 세포 표면 부착
- **보조 수용체**: AAVR(AAV Receptor, KIAA0319L), HSPG(Heparan Sulfate Proteoglycan), LamR 등 — 세포내이입 매개

| 혈청형 | 1차 수용체 | 주요 향성 | FDA 승인 치료제 |
|--------|----------|----------|---------------|
| AAV1 | N-linked sialic acid | 골격근, 심장 | — |
| AAV2 | HSPG | 넓음 (간, 근육, CNS) | Luxturna (RPE65, 망막) |
| AAV5 | N-linked sialic acid | CNS, 간, 폐 | Hemgenix (Factor IX, 혈우병 B) |
| AAV8 | LamR | 간, 근육 | — |
| AAV9 | N-linked galactose | BBB 통과, CNS, 심장, 근육 | Zolgensma (SMN1, SMA) |
| AAVrh10 | — | CNS | — |
| AAV-PHP.eB | LY6A (마우스 특이적) | CNS (마우스에서 고효율) | 전임상 |

**AAV9의 독특한 BBB 통과 능력**: AAV9는 N-linked galactose를 1차 수용체로 사용하며, 뇌혈관 내피세포를 통한 **트랜스사이토시스(transcytosis)**로 혈뇌장벽을 통과한다. 이로 인해 전신 정맥 투여로 CNS 형질도입이 가능하며, Novartis의 Zolgensma(척수성 근위축증 유전자 치료제)의 기반 기술이다.

#### 2.2.3 차세대 AAV 엔지니어링

자연 혈청형의 한계(면역원성, 비특이적 분포, 낮은 형질도입 효율)를 극복하기 위한 엔지니어링 전략:

- **정방향 진화(Directed evolution)**: 캡시드 변이체 라이브러리 → 목표 조직 선별 반복
- **합리적 설계(Rational design)**: 캡시드 표면에 표적화 펩타이드/나노바디 삽입
- **AAV 캡시드 화학적 변형**: N-에틸말레이미드 등으로 캡시드 표면 시스테인 변형 → 향성 변경
- **나노바디 교체(Nanobody swapping)**: 캡시드 핫스팟에 표적 특이적 나노바디를 삽입하여 정밀 표적화 달성

2025년 *Cell: Molecular Therapy*에 발표된 마우스 종합 AAV 향성 아틀라스(atlas)는 다수의 AAV 혈청형과 엔지니어드 변이체의 전신 분포를 체계적으로 매핑하여, 향후 조직 특이적 AAV 설계의 참조 데이터를 제공했다.

### 2.3 GalNAc-ASGPR 수용체 메커니즘

#### 2.3.1 ASGPR의 생물학

**아시알로당단백질 수용체(Asialoglycoprotein Receptor, ASGPR)**는 간세포(hepatocyte) 표면에 **특이적으로, 고밀도로** 발현되는 C-type 렉틴(lectin) 수용체다:

- **발현 밀도**: 간세포 표면당 약 **500,000개** — 이 극단적 밀도가 GalNAc 전달 효율의 기반
- **구조**: ASGPR는 H1(주) 및 H2(보조) 서브유닛의 헤테로올리고머로, 삼량체(trimer) 또는 사량체(tetramer) 클러스터를 형성
- **생리적 기능**: 혈중 노화 당단백질(galactose-노출)의 제거 (간 청소 기능)
- **내재화 속도**: 클라트린 매개 세포내이입, 15분마다 재순환(recycling) — 하루에 수용체당 수십 회 내재화 사이클

#### 2.3.2 GalNAc 접합체의 설계 원리

**N-아세틸갈락토사민(GalNAc)** 접합체는 ASGPR의 생리적 리간드(galactose)를 모방하여 설계되었다:

**삼가(Trivalent) GalNAc 구조**:
- 3개의 GalNAc 당이 **삼분지(triantennary)** 링커에 부착된 구조
- 삼가 구조가 단가(monovalent) 대비 ASGPR 결합 친화도를 **~1,000배** 향상 (cluster glycoside effect)
- ASGPR의 삼량체 구조와 삼가 GalNAc의 기하학적 상보성이 고친화 결합의 분자적 기반

**Alnylam의 ESC (Enhanced Stabilization Chemistry) 플랫폼**:
- siRNA 센스 가닥의 3' 말단에 삼가 GalNAc 접합
- 2'-O-methyl, 2'-F, phosphorothioate 변형으로 뉴클레아제 저항성 부여
- 피하주사 투여 → 혈류 → ASGPR 매개 간세포 내재화

#### 2.3.3 세포 내 운명 (Intracellular Trafficking)

GalNAc-siRNA의 세포 내 경로:

1. **ASGPR 결합 및 내재화**: 삼가 GalNAc-ASGPR 고친화 결합 → 클라트린 피복 소포(clathrin-coated pit) 형성 → 세포내이입
2. **엔도솜 내 pH 감소**: 초기 엔도솜(pH 6.0) → 후기 엔도솜(pH 5.0)으로 성숙하면서 pH 감소
3. **GalNAc-ASGPR 해리**: 산성 pH에서 GalNAc가 ASGPR로부터 해리
4. **ASGPR 재순환**: 해리된 ASGPR은 세포 표면으로 재순환하여 다음 결합 사이클 준비
5. **GalNAc/링커 분해**: 엔도솜 내 글리코시다아제가 GalNAc 당 분해, 링커 절단으로 siRNA 유리
6. **엔도솜 탈출**: 전체 내재화된 siRNA 중 **<1%**만이 엔도솜 탈출에 성공 — 이것이 GalNAc 플랫폼의 핵심 병목
7. **RISC 로딩**: 세포질에 도달한 siRNA가 Argonaute 2(AGO2) 단백질에 로딩 → RISC 형성 → 표적 mRNA 상보적 결합 → mRNA 절단/분해

**약동학적 장점 (2024, Journal of Clinical Pharmacology)**:
LNP 기반 siRNA(Onpattro) 대비 GalNAc-siRNA의 우위:
- **안전성 프로파일 우수**: LNP의 면역 활성화(보체 활성화, 사이토카인 방출) 우려 감소
- **투여 편의성**: 피하주사 (LNP는 정맥주사 필요)
- **지속 시간 연장**: 단회 투여로 3-6개월 효과 지속 (Ago2에 결합된 siRNA의 세포 내 반감기)
- **합성 용이성**: 고체상 올리고뉴클레오티드 합성의 확립된 공정

### 2.4 엑소좀 적재 방법 (Exosome Loading Methods)

#### 2.4.1 엑소좀의 기본 생물학

엑소좀(exosome)은 **30-150 nm** 크기의 세포외소포체(extracellular vesicle, EV)로, 다소포체(multivesicular body, MVB)의 내향 출아(inward budding)로 형성되어 세포 밖으로 분비된다. 자연적으로 단백질, mRNA, miRNA, 지질을 세포 간에 전달하는 생리적 수송체이며, 이 특성이 약물 전달에서 다음 고유 장점을 제공한다:

- **낮은 면역원성**: 자가 세포(autologous cell) 유래 시 면역 반응 최소
- **BBB 통과 능력**: 특정 세포 유래 엑소좀의 내인적 BBB 통과 가능
- **자연적 표적화**: 모세포(parent cell)의 표면 단백질이 특정 수용체-리간드 상호작용을 통해 표적 세포 인식
- **엔도솜 탈출 효율**: 합성 나노입자 대비 우수한 세포 내 화물 전달

#### 2.4.2 적재(Loading) 방법론

엑소좀 약물 적재는 크게 두 범주로 분류된다:

**A. 내인적 적재 (Endogenous/Pre-loading)**

모세포(parent cell) 수준에서 화물을 엑소좀에 탑재하는 방법:

1. **공동 배양 (Co-incubation)**: 모세포를 약물과 함께 배양하여, 자연적 세포내이입 → MVB 경로 → 엑소좀 내 포함. 단순하지만 적재 효율 낮음.

2. **유전적 조작**: 모세포에 유전자를 도입하여, 엑소좀 내 자연적으로 분류되는 단백질(Lamp2b, CD63, CD9)과 치료적 단백질/RNA의 융합 단백질 발현. 특정 화물의 엑소좀 내 농축(enrichment)을 유도.

3. **조건 배양**: 스트레스 조건(저산소, 열 충격)으로 모세포의 엑소좀 생산 및 특정 화물 탑재 유도

**B. 외인적 적재 (Exogenous/Post-loading)**

분리된 엑소좀에 직접 화물을 적재하는 방법:

1. **전기천공 (Electroporation)**: 전기 펄스로 엑소좀 막에 일시적 기공(pore) 생성 → siRNA, DNA, 소분자 삽입. 높은 적재 효율, 엑소좀 응집 위험.

2. **초음파 처리 (Sonication)**: 초음파 에너지로 막 투과성 일시 증가 → 약물 삽입. 반복적 on/off 사이클로 막 손상 최소화.

3. **사포닌 투과화 (Saponin permeabilization)**: 사포닌이 엑소좀 막의 콜레스테롤과 상호작용하여 소공(small pore) 형성 → 막 투과성 증가. **높은 적재 효율과 최소 막 손상**의 균형이 장점.

4. **동결-융해 (Freeze-thaw)**: 반복적 동결(-80C)과 융해(RT)로 막 불안정화 → 화물 삽입. 단순하지만 적재 효율 불균일.

5. **압출 (Extrusion)**: 엑소좀 + 약물 혼합물을 폴리카보네이트 막 필터를 통해 강제 통과 → 균일한 크기의 적재 엑소좀 생성.

**C. 차세대 엔지니어링 (2025, *Nature Communications*)**

최근 엔지니어드 미니-인테인(mini-intein) 단백질의 자가 절단(self-cleavage) 활성을 이용한 능동적 화물 적재와, 퓨소제닉 VSV-G 단백질을 이용한 엔도솜 탈출 향상 전략이 보고되었다. 이 접근법은 Cre 재조합효소와 Cas9/sgRNA 화물의 고효율 세포 내 전달 및 재조합/게놈 편집을 달성했다.

#### 2.4.3 엑소좀 DDS의 현재 한계

| 과제 | 현황 |
|------|------|
| **대량 생산** | 세포 배양 기반 생산의 확장성 제한, CDMO 인프라 미비 |
| **품질 관리** | 크기/내용물의 이질성(heterogeneity), 표준화된 특성 분석 방법 부재 |
| **규제 경로** | FDA/EMA의 엑소좀 약물 분류 및 규제 가이드라인 미확립 |
| **적재 효율** | 외인적 적재의 불균일한 효율, 화물 유형별 최적 방법 상이 |
| **약동학** | 반감기 단축, 비특이적 세포 흡수, 체내 분포 예측 어려움 |

---

## 3. 임상 데이터

### 3.1 LNP-mRNA 치료제

#### 3.1.1 COVID-19 백신 (Phase 3/상용화)

| 백신 | 이온화 지질 | 용량 | 효능 (원형주) | 이상반응 |
|------|-----------|------|-------------|---------|
| Spikevax (Moderna) | SM-102 | 50-100 ug | 94.1% | 국소 반응, 발열, 근육통 |
| Comirnaty (Pfizer/BioNTech) | ALC-0315 | 30 ug | 95.0% | 유사 |

#### 3.1.2 비감염 적응증 LNP-mRNA 파이프라인

| 적응증 | 기업 | 단계 | 비고 |
|--------|------|------|------|
| 흑색종 개인화 암백신 | BioNTech/Genentech | Phase 2 | mRNA-4157 (V940) + 키트루다 병용 |
| 심근경색 후 심장 재생 | Moderna/AstraZeneca | Phase 1/2 | AZD8601 — VEGF-A mRNA |
| 낭포성 섬유증 | Translate Bio/Sanofi | Phase 1/2 | CFTR mRNA 폐 흡입 |
| 프로피온산혈증 | Moderna | Phase 1/2 | mRNA-3927 — PCCB mRNA 간 대체 |
| CMV 백신 | Moderna | Phase 3 | mRNA-1647 |

### 3.2 GalNAc-siRNA 치료제

#### 3.2.1 승인 약물

| 약물 | 표적 | 적응증 | 투여 | 승인 |
|------|------|--------|------|------|
| **Onpattro** (patisiran) | TTR | hATTR 다발신경병 | IV, Q3W (LNP) | 2018 |
| **Givlaari** (givosiran) | ALAS1 | 급성 간성 포르피린증 | SC, 월 1회 (GalNAc) | 2019 |
| **Oxlumo** (lumasiran) | HAO1 | 원발성 고옥살산뇨증 1형 | SC, 월→Q3M (GalNAc) | 2020 |
| **Leqvio** (inclisiran) | PCSK9 | 고콜레스테롤혈증 | SC, 6개월 1회 (GalNAc) | 2021 (EU), 2023 (US) |
| **Amvuttra** (vutrisiran) | TTR | hATTR 다발신경병 | SC, Q3M (GalNAc) | 2022 |
| **Wainua** (eplontersen) | TTR | hATTR 심근병증 | SC, 월 1회 (GalNAc-ASO) | 2023 |

Alnylam은 GalNAc-siRNA 플랫폼의 **체계적 상업화**에 가장 성공적인 기업으로, 6개 승인 약물이 모두 간 표적 핵산 치료제다. Leqvio (inclisiran)는 6개월 1회 피하주사로 PCSK9을 억제하는 "RNA 간섭 기반 고지혈증 치료제"로, 기존 PCSK9 항체(에볼로쿠맙, 알리로쿠맙) 대비 투여 편의성에서 획기적 차별화를 달성했다.

### 3.3 AAV 유전자 치료제

#### 3.3.1 승인 약물

| 약물 | AAV | 적응증 | 가격 | 승인 |
|------|-----|--------|------|------|
| **Luxturna** (voretigene) | AAV2 | RPE65 관련 유전성 망막이영양증 | $850K | 2017 |
| **Zolgensma** (onasemnogene) | AAV9 | 척수성 근위축증 (SMA) | $2.1M | 2019 |
| **Hemgenix** (etranacogene) | AAV5 | 혈우병 B | $3.5M | 2022 |
| **Elevidys** (delandistrogene) | AAVrh74 | 뒤시엔 근이영양증 | $3.2M | 2023 (가속승인) |
| **Roctavian** (valoctocogene) | AAV5 | 혈우병 A | $2.9M | 2023 (EU) |

### 3.4 비간 LNP 표적화: SORT 기술

#### 3.4.1 SORT (Selective Organ Targeting) 원리

텍사스 대학교 사우스웨스턴의 Daniel Siegwart 그룹이 개발한 **SORT** 기술은 기존 4성분 LNP에 5번째 성분("SORT 분자")을 추가하여 조직 향성을 제어한다:

- **간 표적 (기본)**: 추가 성분 없음, ApoE 매개
- **폐 표적**: 영구 양전하 지질(DOTAP) 추가 → LNP 표면 양전하 → 폐 모세혈관 내피세포에 흡착. LNP pKa > 9
- **비장 표적**: 음전하 지질(18PA) 추가 → LNP 표면 음전하 → 비장 대식세포 흡수

2024년 *Nature Communications*에 보고된 후속 연구에서, 콜레스테롤 제거가 간 축적을 방지하면서 폐/비장 표적화를 향상시키는 전략이 추가로 제시되었다.

#### 3.4.2 뇌 표적 LNP

2024년 *ACS Nano*에 보고된 AI-검증 뇌 표적 mRNA LNP는 BBB 수송체/수용체에 결합하는 소분자 PEG-지질 접합체를 LNP에 통합하여, 뉴런 향성(neuronal tropism)과 세포 유형별 정밀 표적화를 달성했다.

---

## 4. 시장 분석

### 4.1 시장 규모

| 세그먼트 | 2024/2025 | 2030 전망 | CAGR |
|---------|----------|----------|------|
| 약물 전달 시스템 전체 | $280B+ | $400B+ | ~6% |
| LNP 기반 치료제 | $20B+ (COVID 백신 포함) | $15-30B (비COVID) | ~15% |
| siRNA/ASO 치료제 | $5B+ | $15B+ | ~20% |
| AAV 유전자 치료제 | $3B+ | $10B+ | ~25% |
| 엑소좀 치료제 | <$100M | $1B+ | >50% |
| CDMO (LNP/AAV 제조) | $5B+ | $15B+ | ~20% |

### 4.2 핵심 기업 벨류에이션

| 기업 | 티커 | 핵심 | 시가총액/밸류에이션 |
|------|------|------|-----------------|
| Moderna | MRNA | LNP-mRNA 플랫폼 | ~$15B |
| BioNTech | BNTX | LNP-mRNA 플랫폼 | ~$25B |
| Alnylam | ALNY | GalNAc-siRNA 선두 | ~$35B |
| Arbutus Biopharma | ABUS | LNP 원천 특허 | 소형주 |
| Sarepta | SRPT | AAV 유전자 치료 | ~$10B |
| BioMarin | BMRN | AAV 유전자 치료 | ~$12B |
| Evox Therapeutics | 비상장 | 엔지니어드 엑소좀 | 비상장 |
| ILIAS Biologics | 비상장 | 엑소좀 DDS | 비상장 (한국) |

### 4.3 투자 핵심 테제

1. **약물 전달 = 바이오의 "삽과 곡괭이"**: mRNA, siRNA, CRISPR, 유전자치료 — 모든 핵산 의약품이 DDS에 의존. DDS 기업은 파이프라인 다각화의 수혜자.
2. **비간 LNP 표적화가 시장 10배 확장의 열쇠**: 현재 LNP의 기본 행선지는 간. 폐, 뇌, 근육, 종양 표적화 성공 시 적응증이 수십 배 확대.
3. **GalNAc 플랫폼의 확장성**: Alnylam이 간 표적 siRNA의 "플랫폼 기업"으로 확립. 6개월 1회 투여의 편의성이 만성 질환(고지혈증, ATTR) 시장에서 경쟁 우위.
4. **AAV 제조 병목**: AAV 대량 생산의 기술적 난이도와 비용이 유전자치료 확산의 최대 장벽. CDMO (삼성바이오, Lonza, Catalent) 수혜.
5. **엑소좀 = 장기 테마**: 현재 전임상 단계이나, 합성 나노입자의 면역원성/독성 한계를 극복할 잠재력. 2030년 이후 본격 성장 기대.
6. **특허 경쟁**: LNP 이온화 지질 특허(Arbutus/Acuitas/Moderna/Pfizer)의 라이선싱/소송 결과가 산업 구도에 영향.

---

## 5. AI 적용

### 5.1 LNP 조성 최적화

AI가 이온화 지질 구조, 지질 몰비, PEG-지질 비율, 공정 매개변수(미세유체 혼합 속도, pH, 유속)를 **동시 최적화**하여 목표 장기 도달률을 극대화한다:

- **베이지안 최적화**: 소수의 실험으로 고차원 매개변수 공간 탐색
- **그래프 신경망**: 이온화 지질의 분자 구조로부터 pKa, 형질전환 효율, 독성 예측
- **SORT 기술과의 결합**: AI가 SORT 분자 유형/비율과 조직 향성의 관계를 학습하여, 원하는 장기 표적화를 위한 최적 조성 예측

2024년 *ACS Nano*의 연구에서 AI 모델이 뇌 표적 LNP 조성을 검증한 사례는 이 접근법의 실현 가능성을 보여준다.

### 5.2 AAV 캡시드 엔지니어링

**ML 기반 캡시드 설계**:
- AAV 캡시드 서열-향성 관계를 대규모 크리닝 데이터에서 학습
- 원하는 향성(예: 특정 뇌 세포 유형)을 가진 캡시드 변이체를 생성적 모델(VAE, 확산 모델)로 de novo 설계
- Dyno Therapeutics: ML 기반 AAV 캡시드 최적화 플랫폼, Novartis/Sarepta 파트너십

### 5.3 엑소좀 표면 엔지니어링

AI가 엑소좀 표면 단백질(Lamp2b, CD63)에 삽입할 표적화 펩타이드를 설계하고, 표적 수용체와의 결합 친화도를 예측한다. AlphaFold 3를 이용한 표적화 펩타이드-수용체 복합체 구조 예측이 이 과정을 가속화한다.

### 5.4 GalNAc 링커 최적화

AI 기반 분자 역학 시뮬레이션과 QSAR 모델링이 GalNAc 링커 구조와 안정성, ASGPR 결합 친화도, 엔도솜 내 글리코시다아제 저항성의 관계를 예측하여, 차세대 대사적으로 안정한(metabolically stable) GalNAc 접합체 설계를 지원한다 (Alnylam, 2023, *Journal of Medicinal Chemistry*).

### 5.5 약동학 시뮬레이션

PBPK(Physiologically Based Pharmacokinetic) 모델에 ML을 통합한 하이브리드 모델이 나노입자 약물의 체내 분포, 세포 내 전달, 치료 효과를 시뮬레이션한다. 이는 동물 실험을 줄이면서(3R 원칙) 최적 투여량/투여 간격을 예측하는 데 기여한다.

---

## 6. 참고문헌

1. Hou, X., Zaks, T., Langer, R. & Bhatt, D.G. "Lipid nanoparticles for mRNA delivery." *Nature Reviews Materials* 6, 1078-1094 (2021). https://doi.org/10.1038/s41578-021-00358-0

2. Wang, D., Tai, P.W.L. & Gao, G. "Adeno-associated virus as a delivery vector for gene therapy of human diseases." *Signal Transduction and Targeted Therapy* 9, 78 (2024). https://www.nature.com/articles/s41392-024-01780-w

3. Akinc, A., Maier, M.A., Manoharan, M., et al. "The Onpattro story and the clinical translation of nanomedicines containing nucleic acid-based drugs." *Nature Nanotechnology* 14, 1084-1087 (2019). https://doi.org/10.1038/s41565-019-0591-y

4. Cheng, Q., Wei, T., Farbiak, L., et al. "Selective organ targeting (SORT) nanoparticles for tissue-specific mRNA delivery and CRISPR-Cas gene editing." *Nature Nanotechnology* 15, 313-320 (2020). https://doi.org/10.1038/s41565-020-0669-6

5. Kulkarni, J.A., Witzigmann, D., Thomson, S.B., et al. "The current landscape of nucleic acid therapeutics." *Nature Nanotechnology* 16, 630-643 (2021). https://doi.org/10.1038/s41565-021-00898-0

6. Foster, D.J., Brown, C.R., Shaikh, S., et al. "Advanced siRNA designs further improve in vivo performance of GalNAc-siRNA conjugates." *Molecular Therapy* 26(3), 708-717 (2018). https://doi.org/10.1016/j.ymthe.2017.12.021

7. Habtemariam, B.A., Karber, P.A., Engleton, K.N., et al. "Metabolically stable anomeric linkages containing GalNAc-siRNA conjugates." *Journal of Medicinal Chemistry* 66(6), 4063-4078 (2023). https://pubs.acs.org/doi/10.1021/acs.jmedchem.2c01337

8. Liang, X., et al. "Ionizable lipid nanoparticles for mRNA delivery: internal self-assembled inverse mesophase structure and endosomal escape." *Accounts of Chemical Research* (2025). https://pubs.acs.org/doi/abs/10.1021/acs.accounts.5c00522

9. An, J.H. "Pharmacokinetics and pharmacodynamics of GalNAc-conjugated siRNAs." *Journal of Clinical Pharmacology* 64(4), 422-434 (2024). https://accp1.onlinelibrary.wiley.com/doi/10.1002/jcph.2337

10. Herrmann, I.K., Wood, M.J.A. & Fuhrmann, G. "Extracellular vesicles as a next-generation drug delivery platform." *Nature Nanotechnology* 16, 748-759 (2021). https://www.nature.com/articles/s41565-021-00931-2

11. Zhu, Y., et al. "Recent advances in extracellular vesicles for therapeutic cargo delivery." *Experimental & Molecular Medicine* 56, 836-849 (2024). https://www.nature.com/articles/s12276-024-01201-6

12. Raguram, A., Banskota, S. & Liu, D.R. "Engineering of extracellular vesicles for efficient intracellular delivery of multimodal therapeutics including genome editors." *Nature Communications* 16, 4483 (2025). https://www.nature.com/articles/s41467-025-59377-y

13. Chen, L., et al. "A comprehensive atlas of AAV tropism in the mouse." *Molecular Therapy* 33(2), 379-395 (2025). https://www.cell.com/molecular-therapy-family/molecular-therapy/fulltext/S1525-0016(25)00043-7

14. Reformatting Lipid Nanoparticles Team. "Reformulating lipid nanoparticles for organ-targeted mRNA accumulation and translation." *Nature Communications* 15, 5659 (2024). https://www.nature.com/articles/s41467-024-50093-7

---

*본 리뷰는 투자 권유를 목적으로 하지 않으며, 면책조항이 적용됩니다. 모든 투자 판단은 개인의 책임하에 이루어져야 합니다.*
