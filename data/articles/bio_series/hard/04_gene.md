# 바이오 기술 리뷰 #4: 유전자 편집 & 세포/유전자 치료 (Gene Editing & Cell/Gene Therapy) — 기전, 임상 데이터, 투자 분석

> **Review Article** | 2026-04-05
> 키워드: CRISPR, Cas9, base editing, prime editing, AAV, LNP, iPSC, 이종장기, 유전자 치료

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

### 1.1 유전자 치료의 패러다임: 증상 관리에서 근본 교정으로

전통 약물은 질병의 증상이나 하위 분자 경로를 억제/활성화하지만, 유전자 치료(gene therapy)는 질병의 근본 원인인 **유전자 자체**를 수정한다. 이 접근법의 핵심 전제는:

1. **단일유전자 질환(monogenic disorders)**: 하나의 유전자 변이가 질병을 유발 → 해당 유전자의 교정 또는 보충으로 완치 가능
2. **다유전자/복합 질환**: 핵심 유전자 경로의 조절을 통해 질병 진행 억제 또는 역전

현재 유전자 치료의 세 축:

| 접근법 | 메커니즘 | 대표 기술 | 장점 | 한계 |
|--------|---------|----------|------|------|
| **유전자 보충** | 정상 유전자 복사본 전달 | AAV 벡터 | 검증된 플랫폼, 다수 승인 | 삽입 돌연변이, 면역 반응 |
| **유전자 편집** | 내인성 DNA 직접 교정 | CRISPR-Cas9 | 영구적 교정, 정밀성 | Off-target, 전달 과제 |
| **세포 치료** | 유전적으로 교정/설계된 세포 투여 | iPSC, CAR-T | 세포 수준 맞춤 | 제조 비용/시간, 거부반응 |

### 1.2 유전자 편집의 역사적 맥락

| 기술 | 발견 | 특징 | 한계 |
|------|------|------|------|
| ZFN (Zinc Finger Nuclease) | 1996 | 단백질 공학 기반 DNA 인식 | 설계 복잡, 고비용, 오프타겟 |
| TALEN | 2010 | 모듈 단백질 기반, ZFN보다 설계 용이 | 크기 문제, 전달 어려움 |
| **CRISPR-Cas9** | **2012** | RNA 기반 유도 → 설계 극도로 간편 | 이중 절단 → indel, 큰 결실 |
| Base Editing | 2016 | 단일 염기 전환, 절단 없음 | 제한적 전환(C→T, A→G) |
| Prime Editing | 2019 | "검색-교체" 수준 편집, 절단 없음 | 낮은 효율, 큰 삽입 제한 |
| Epigenome Editing | 2021+ | DNA 서열 변경 없이 발현 조절 | 초기 연구 단계 |

---

## 2. 핵심 기술 세부

### 2.1 Cas9 vs. Cas12/Cas13: 편집 도구의 비교

#### 2.1.1 CRISPR-Cas9의 분자 기전

Cas9(CRISPR-associated protein 9)은 Streptococcus pyogenes 유래 RNA 유도 엔도뉴클레이즈로, 1,368개 아미노산(SpCas9), ~160 kDa의 이엽(bilobed) 구조를 갖는다 [1, 2].

**작동 단계:**

1. **sgRNA 로딩**: Single-guide RNA(sgRNA = crRNA + tracrRNA 융합체)가 Cas9의 REC(recognition) 로브에 결합하여 ribonucleoprotein(RNP) 복합체 형성
2. **PAM 인식**: Cas9-sgRNA 복합체가 표적 DNA를 스캐닝하며 PAM(Protospacer Adjacent Motif) 서열(SpCas9: 5'-NGG-3') 인식 → DNA 풀림(unwinding) 개시
3. **R-loop 형성**: sgRNA의 20nt 스페이서 서열이 표적 DNA의 비주형 가닥(non-template strand)과 Watson-Crick 염기쌍 형성 → R-loop 구조
4. **이중가닥 절단(DSB)**: 두 개의 뉴클레이즈 도메인이 각각 한 가닥을 절단:
   - **RuvC 도메인**: 비주형 가닥(non-template strand) 절단 (PAM으로부터 3nt 상류)
   - **HNH 도메인**: 주형 가닥(template strand) 절단 (PAM으로부터 3nt 상류)
   - 결과: blunt-end DSB, PAM으로부터 3bp 상류
5. **DNA 복구**: 세포 내 복구 경로가 DSB를 처리:
   - **NHEJ(Non-Homologous End Joining)**: 오류 동반 → indel 생성 → 유전자 녹아웃(KO)
   - **HDR(Homology-Directed Repair)**: 외부 DNA 주형 존재 시 → 정밀 삽입/교정 (분열 세포에서만, 효율 낮음)

#### 2.1.2 Cas12(Cpf1)의 차별적 특성

| 특성 | Cas9 (SpCas9) | Cas12a (AsCpf1) | Cas12b |
|------|-------------|----------------|--------|
| 유래 | S. pyogenes | Acidaminococcus sp. | Alicyclobacillus |
| 크기 | 1,368 aa (~160 kDa) | 1,307 aa (~151 kDa) | ~130 kDa |
| 가이드 RNA | sgRNA (crRNA+tracrRNA) | crRNA만 (tracrRNA 불필요) | sgRNA |
| PAM 위치 | 3' (5'-NGG-3') | 5' (5'-TTTV-3') | 5' (다양) |
| 절단 유형 | Blunt-end DSB | **5' 오버행(staggered) DSB** | Staggered |
| 뉴클레이즈 도메인 | RuvC + HNH | RuvC (1개 도메인으로 양 가닥 순차 절단) | RuvC |
| AT-rich 서열 접근 | 제한적 (GG PAM) | 용이 (TTT PAM) | 다양 |
| Collateral activity | 없음 | ssDNA 비특이적 절단 (DETECTR 진단용) | 있음 |

Cas12a의 5' 오버행 DSB는 HDR 효율을 높일 수 있어 정밀 유전자 삽입에 유리하다.

#### 2.1.3 Cas13: RNA 표적 편집

Cas13은 DNA가 아닌 **RNA를 표적**으로 하는 유일한 CRISPR 도구:

- **기전**: crRNA가 표적 mRNA에 결합 → Cas13의 HEPN(Higher Eukaryotes and Prokaryotes Nucleotide-binding) 도메인이 RNA 절단
- **특징**: DNA 변형 없이 RNA 수준에서 유전자 발현 조절 → **가역적 편집**
- **응용**: RNA 바이러스 감염 치료, 일시적 유전자 침묵
- **한계**: Collateral activity(비표적 RNA 절단) → in vivo 적용 시 안전성 우려

### 2.2 Base Editing: 단일 염기 전환의 화학

Base editing은 2016년 David Liu 연구팀(Harvard/Broad Institute)이 개발한 기술로, DSB 없이 단일 염기를 정밀 전환한다 [1, 3].

#### 2.2.1 CBE (Cytosine Base Editor)

구조: **nickase Cas9(nCas9, D10A)** + **시토신 탈아미네이즈(cytosine deaminase, APOBEC1/rAPOBEC1)** + **UGI(Uracil Glycosylase Inhibitor)**

작동 기전:
1. sgRNA 유도로 nCas9가 표적 부위에 결합 → R-loop 형성
2. 비주형 가닥의 노출된 ssDNA에서 APOBEC1이 시토신(C)의 4번 아미노기를 탈아미노화 → **우라실(U)**로 전환
3. UGI가 BER(Base Excision Repair) 경로의 UDG(Uracil DNA Glycosylase)를 억제 → U가 제거되지 않도록 보호
4. nCas9가 주형 가닥만 절단(nick) → 세포가 비주형 가닥(U 포함)을 주형으로 사용하여 주형 가닥 복구
5. DNA 복제 시 U가 T로 읽힘 → 최종 결과: **C·G → T·A** 전환

편집 윈도우: PAM으로부터 대략 4-8번 위치(활성 영역)

#### 2.2.2 ABE (Adenine Base Editor)

구조: **nCas9(D10A)** + **진화된 아데노신 탈아미네이즈(TadA/TadA*)**

작동 기전:
1. TadA*가 비주형 가닥 ssDNA의 아데닌(A)을 탈아미노화 → **이노신(I)**으로 전환
2. 이노신은 세포의 복제/복구 기구에 의해 구아닌(G)으로 읽힘
3. DNA 복제 시 I → G → 최종 결과: **A·T → G·C** 전환

TadA*는 자연계 E. coli tRNA 아데노신 탈아미네이즈(TadA)를 7세대 이상의 directed evolution으로 dsDNA 작용 가능하도록 진화시킨 효소다.

#### 2.2.3 Base Editing의 임상적 의의

인간 병원성 단일 뉴클레오티드 변이(pathogenic SNV)의 ~60%가 전이(transition) 변이(C→T, G→A, A→G, T→C)이므로, CBE + ABE만으로 이론적으로 **모든 전이 변이를 교정** 가능하다 [3].

### 2.3 Prime Editing: "검색-교체" 수준의 정밀 편집

2019년 David Liu 연구팀이 발표한 prime editing은 DSB도 외부 DNA 주형도 필요 없는 가장 정밀한 편집 도구다 [1, 4].

#### 2.3.1 구조

**Prime Editor = nCas9(H840A) + M-MLV 역전사효소(RT)** 융합 단백질
- H840A 변이: HNH 도메인 비활성화 → 비주형 가닥만 절단(nick)
- M-MLV RT: Moloney Murine Leukemia Virus 역전사효소의 열안정 변이체

**pegRNA (Prime Editing Guide RNA)**:
- sgRNA 부분: 표적 부위로 유도
- PBS (Primer Binding Site): 절단된 비주형 가닥의 3' 말단에 결합 → RT 프라이밍
- RTT (RT Template): 원하는 편집을 포함하는 역전사 주형

#### 2.3.2 작동 기전

1. **표적 결합**: nCas9-RT가 pegRNA에 의해 표적 DNA로 유도
2. **Nick**: nCas9(H840A)가 PAM 가닥(비주형 가닥)만 절단
3. **프라이밍**: PBS가 절단된 3' 말단 비주형 가닥에 혼성화 → 역전사 개시점 제공
4. **역전사**: M-MLV RT가 RTT를 주형으로 새로운 DNA 가닥 합성 → 원하는 편집 서열 포함
5. **3' 플랩 경쟁**: 새로 합성된 3' 플랩과 기존 5' 플랩이 경쟁 → 5' 플랩은 FEN1 뉴클레이즈에 의해 제거
6. **라이게이션**: 새 가닥이 기존 DNA에 통합
7. **이질이합체(heteroduplex) 해소**: 편집된 가닥과 비편집 가닥 사이의 불일치 → MMR(Mismatch Repair)이 해소 → 편집 영구 고정

**PE3 전략**: 비편집 가닥에 추가 sgRNA로 nick을 도입 → MMR이 편집된 가닥을 주형으로 비편집 가닥 교정 → 편집 효율 2-5배 증가

#### 2.3.3 Prime Editing의 능력과 한계

| 편집 유형 | 가능 여부 | 효율 |
|----------|----------|------|
| 모든 12종 점 변이(SNV) | 가능 | 중간-높음 |
| 소규모 삽입 (≤44bp) | 가능 | 중간 |
| 소규모 결실 (≤80bp) | 가능 | 중간 |
| 조합 편집 (SNV + indel) | 가능 | 낮음-중간 |
| 대규모 삽입 (>100bp) | 제한적 | 매우 낮음 |

2025년 MIT 연구팀의 **proPE(processive prime editing)** 기술: 편집 오류율을 1/7에서 1/101로 감소, 편집 거리를 확장하고 효율을 6.2배 향상 [4].

### 2.4 전달 벡터: AAV 혈청형과 LNP

유전자 편집/치료의 임상 성공은 **전달(delivery)**에 의해 결정된다 [5, 6].

#### 2.4.1 AAV(Adeno-Associated Virus) 혈청형

AAV는 비병원성 파보바이러스로, ~4.7kb 단일가닥 DNA 게놈을 가진다. 캡시드 단백질(VP1/VP2/VP3)의 아미노산 서열 차이로 혈청형이 결정되며, 각 혈청형은 고유한 조직 향성(tropism)을 보인다:

| 혈청형 | 주요 수용체 | 조직 향성 | 승인 약물 |
|--------|-----------|----------|----------|
| AAV1 | Sialic acid (N-linked) | 골격근, 심장 | Glybera (유럽, 현재 철회) |
| AAV2 | HSPG + FGFR1/AAVR | 간, 눈, CNS | Luxturna (망막) |
| AAV5 | Sialic acid (N-linked) | 간, CNS | Hemgenix (간) |
| **AAV8** | LamR (laminin receptor) | **간** (최고 효율) | — |
| **AAV9** | Galactose (N-linked) | **CNS** (BBB 통과), 심장, 간 | Zolgensma (SMA) |
| AAVrh10 | LamR variant | CNS, 심장 | — |
| AAV-PHP.eB* | LY6A(마우스 특이적) | 마우스 CNS (인간 미적용) | — |

*AAV-PHP.eB는 마우스에서 AAV9 대비 40배 이상의 CNS 형질도입을 보이나, LY6A 수용체가 인간에 없어 직접 전환 불가.

**AAV의 한계:**
- **페이로드 제한**: ~4.7kb → 대형 유전자(예: Dystrophin 14kb) 전달 불가 → 듀얼/트리플 AAV 전략
- **면역원성**: 기존 항AAV 항체(인구의 30-70%) → 치료 불가
- **간 향성 편향**: IV 투여 시 대부분 간에 축적 → 비간 표적 조직 도달 어려움
- **재투여 불가**: 1차 투여 후 중화항체 형성 → 2회째 투여 효능 상실

**차세대 캡시드 공학:**
- **VCAP-102**: 영장류에서 AAV9 대비 20-400배 높은 CNS 형질도입 달성
- **AAV2.5**: AAV2 캡시드에 AAV1의 5개 변이 도입 → 근육 표적 + 수용체 결합 유지
- **Directed evolution**: 수백만 캡시드 변이체 라이브러리에서 원하는 향성을 가진 변이체 선별

#### 2.4.2 LNP(Lipid Nanoparticle) 전달 시스템

LNP는 mRNA 백신(COVID-19)으로 검증된 비바이러스 전달 플랫폼으로, CRISPR 구성 요소(sgRNA + Cas9 mRNA 또는 RNP)의 in vivo 전달에 적용되고 있다 [6].

**LNP 4대 구성 요소:**

| 성분 | 기능 | 비율 |
|------|------|------|
| **이온화 지질(ionizable lipid)** | 핵산 캡슐화, 엔도솜 탈출 | ~50 mol% |
| 인지질(helper lipid, 예: DSPC) | 이중층 안정성 | ~10 mol% |
| 콜레스테롤 | 구조 안정성, 막 유동성 | ~38 mol% |
| PEG-지질 | 입자 안정성, 면역 회피, 크기 조절 | ~1.5 mol% |

**이온화 지질의 핵심 메커니즘:**
1. **pH 의존적 하전**: pKa ~6.2-6.5 → 중성 pH(혈중)에서 비하전 → 안전한 순환
2. **핵산 로딩**: 산성 pH 제형 조건(pH 4)에서 양전하 → 음전하 핵산과 정전기 결합 → N/P 비 최적화
3. **엔도솜 탈출**: 세포 내재화 후 엔도솜(pH 5-6)에서 양성화 → 엔도솜 막의 음전하 인지질과 이온쌍 형성 → 막 불안정화 → 핵산 세포질 방출

**LNP의 임상적 이점 (vs. AAV):**
- **페이로드 무제한**: mRNA/RNP 크기 제약 거의 없음
- **일시적 발현**: Cas9 mRNA → 번역 후 분해 → 지속적 편집 효소 존재 없음 → 안전성
- **재투여 가능**: 항체 형성 최소 (vs. AAV)
- **제조 확장성**: mRNA + LNP = 화학적 제조 → 바이러스 생산 대비 확장 용이

**LNP의 한계:**
- **간 향성**: IV 투여 시 ApoE 코팅 → LDL 수용체 경유 간 흡수 → 비간 표적 어려움
- **비간 전달 전략**: 표면 리간드 접합, 이온화 지질 구조 변형, 경로 변경(흡입, 근육 주사 등)

2025년 Children's Hospital of Philadelphia: 최초의 개인 맞춤 CRISPR-LNP 치료 — 카바모일인산합성효소 1 결핍증(CPS1 deficiency) 영아에게 3회 LNP 투여, 중대 부작용 없음 [6].

---

## 3. 임상 데이터

### 3.1 Casgevy(Exa-cel) — 최초의 CRISPR 승인 치료제

Casgevy는 CRISPR Therapeutics와 Vertex Pharmaceuticals가 공동 개발한 ex vivo CRISPR-Cas9 유전자 편집 치료제로, 2023년 12월 세계 최초로 규제 승인(UK MHRA → FDA)을 획득했다 [7, 8].

**편집 전략:**
- 표적: BCL11A 유전자의 적혈구 특이적 인핸서
- BCL11A 녹다운 → 태아 헤모글로빈(HbF) 발현 재활성화 → 성인 겸상 헤모글로빈(HbS)의 중합 방지
- 환자의 조혈줄기세포(HSC)를 채취 → ex vivo CRISPR 편집 → 골수이식(busulfan 전처치 후 자가이식)

#### 겸상적혈구병(SCD) 데이터

| 항목 | 수치 |
|------|------|
| 피험자 수 (유효성 평가 대상) | 45명 |
| VOC(혈관폐쇄위기) 무발생률 | **100% (45/45)** |
| VOC 무발생 평균 기간 | **35.3개월** |
| HbF 수준 | 치료 전 ~1% → 치료 후 **>40%** |

#### 베타탈라세미아(TDT) 데이터

| 항목 | 수치 |
|------|------|
| 피험자 수 (유효성 평가 대상) | 56명 |
| 수혈 독립 달성률 | **98.2% (55/56)** |
| 수혈 독립 평균 기간 | **41.4개월** |
| 총 Hb 수준 | **>11 g/dL** (정상 범위) |

#### 소아(5-11세) 확장 데이터 (2025)

2025년 ASH에서 발표된 5-11세 소아 데이터 — 12세 이상 성인과 일치하는 효능 및 안전성 프로파일. Vertex는 2026년 상반기 전 세계 소아 적응증 규제 제출 계획 발표 [8].

### 3.2 NTLA-2001(Nexiguran Ziclumeran, nex-z) — 최초의 in vivo CRISPR 치료

Intellia Therapeutics가 개발한 체내(in vivo) CRISPR-Cas9 치료제로, LNP로 캡슐화된 Cas9 mRNA + sgRNA를 정맥주사하여 간세포의 TTR(transthyretin) 유전자를 직접 편집한다 [9].

#### Phase 1 데이터 — ATTR 심근병증(ATTR-CM)

AHA 2025에서 발표 [9]:

| 항목 | nex-z (단회 투여) |
|------|-----------------|
| 혈청 TTR 감소율 (36개월, n=9) | **87%** |
| 심근병증 마커 | 안정 또는 개선 |
| NT-proBNP | 안정 유지 |

#### Phase 1 데이터 — 유전성 ATTR 다발신경병증(ATTRv-PN)

NEJM에 발표 [9]:

| 항목 | nex-z (단회 투여) |
|------|-----------------|
| 혈청 TTR 감소율 | 최고 용량에서 **93%** |
| 반응 지속성 | 투여 후 **2년 이상** 지속 |
| 다발신경병증 악화 | **없음** (안정 또는 개선) |

#### 안전성 우려 사항

2025년 10월: MAGNITUDE Phase 3 시험에서 Grade 4 간효소 상승 + 빌리루빈 증가 사례 발생 → 환자 1명 사망 → 시험 일시 중단 [9]. 이 사건은 in vivo CRISPR의 간독성 위험을 부각시켰으며, LNP 전달의 면역원성 및 Cas9의 off-target 편집 가능성에 대한 심층 조사가 진행 중이다.

### 3.3 Base Editing 임상

#### BEAM-101: 겸상적혈구병

Beam Therapeutics의 base editing 치료제 [3]:
- 기전: ABE로 BCL11A 인핸서의 특정 위치를 A→G 전환 → HbF 재활성화
- Casgevy와 동일한 생물학적 전략이지만, DSB 없이 단일 염기 교정으로 안전성 프로파일 개선 목표
- Phase 1/2: 12명 대상, 2025년 6월 첫 투여 시작

#### VERVE-101: 가족성 고콜레스테롤혈증 (→ Eli Lilly 인수)

- Verve Therapeutics(Eli Lilly $1.3B 인수) [3]
- 기전: In vivo ABE로 간세포의 PCSK9 유전자를 영구 비활성화 → LDL-C 영구 저하
- Phase 1b: 단회 주입으로 PCSK9 48% 감소, LDL-C 39-55% 감소 데이터
- 빅파마(Lilly)의 CRISPR 베팅 시그널

### 3.4 유전자 치료 (AAV 벡터)

#### 주요 승인 제품 임상 데이터

| 약물 | 적응증 | 핵심 데이터 | 가격 |
|------|--------|-----------|------|
| **Zolgensma** (AAV9) | SMA Type 1 | 5년 추적: 100% 생존, 운동기능 유지 | **$2.1M/회** |
| **Hemgenix** (AAV5) | 혈우병 B | 3년 추적: FIX 활성 36.2% → 연간 출혈 0회, 인자 사용 97% 감소 | **$3.5M/회** |
| **Elevidys** (AAVrh74) | DMD | micro-dystrophin 발현 확인, 기능적 개선 | **$3.2M/회** |
| **Roctavian** (AAV5) | 혈우병 A | 2년: FVIII 활성 평균 39.4 IU/dL, 인자 사용 97% 감소 | **$2.9M/회** |

### 3.5 이종장기 이식(Xenotransplantation)

#### eGenesis — CRISPR 편집 돼지 신장

| 항목 | 수치 |
|------|------|
| 편집 유전자 수 | **69개** |
| 편집 내용 | 3개 면역 관련 돼지 유전자 KO + 7개 인간 유전자 삽입 + PERV(돼지 내인성 레트로바이러스) 59개 비활성화 |
| FDA IND 승인 | **2025년** |
| MGH 이식 성공 | 2건 (brain-dead 환자, 2025) |

#### United Therapeutics (UTHR) — UKidney

| 항목 | 수치 |
|------|------|
| 편집 유전자 수 | **10개** |
| FDA IND 승인 | **2025년** |
| 계획 임상 규모 | **50명** (생체 임상) |

2025-2026년은 이종장기 이식의 **인간 임상 데이터가 처음으로 축적되는 해**로, 성공 시 $10B+ 규모의 완전히 새로운 산업이 탄생할 수 있다.

---

## 4. 시장 분석

### 4.1 TAM

| 분야 | 2025 시장 | 2030 전망 | 2035 전망 | CAGR |
|------|----------|----------|----------|------|
| CRISPR/유전자 편집 | $4.76B | ~$10B | $18.89B | 14.77% |
| 유전자 치료 (AAV 등) | ~$7B | $30B+ | — | >20% |
| iPSC/줄기세포 치료 | $10.4B | ~$18B | $30.9B | 11.5% |
| 이종장기 | ~0 | ~$1B | $10B+ | — |

### 4.2 경쟁 구도

#### CRISPR 편집 기업

| 기업 | 티커 | 핵심 기술 | 파이프라인 단계 | 시가총액 |
|------|------|---------|-------------|---------|
| CRISPR Therapeutics | CRSP | Cas9 (ex vivo) | 상용화 (Casgevy) | ~$3B |
| Intellia Therapeutics | NTLA | Cas9 + LNP (in vivo) | Phase 3 (ATTR) | ~$2B |
| Beam Therapeutics | BEAM | Base editing | Phase 1/2 | ~$1.5B |
| Prime Medicine | PRME | Prime editing | 전임상→Phase 1 | ~$0.5B |
| Editas Medicine | EDIT | Cas9/Cas12 | Phase 1/2 | ~$0.3B |
| Verve → Eli Lilly | — | In vivo ABE (심혈관) | Phase 1b ($1.3B 인수) | — |

#### 유전자 치료 기업

| 기업 | 티커 | 강점 |
|------|------|------|
| Vertex (VRTX) | VRTX | Casgevy + iPSC(1형 당뇨) + 다중 파이프라인 |
| Sarepta (SRPT) | SRPT | DMD 유전자 치료 선도 |
| BioMarin (BMRN) | BMRN | 혈우병 A 유전자 치료 |

### 4.3 핵심 투자 리스크와 기회

**리스크:**
1. **가격 문제**: $2-3.5M/환자 → 보험 수재 및 지불 시스템 미정립
2. **안전성 우려**: NTLA-2001 환자 사망 사례 → in vivo CRISPR에 대한 규제 강화 가능
3. **제조 확장성**: ex vivo 세포 치료의 환자당 맞춤 제조 → 대량 생산 어려움
4. **장기 안전성 미지수**: off-target 편집의 장기적 결과(발암 등) → 10년+ 추적 필요

**기회:**
1. **In vivo 편집의 폭발적 TAM**: ex vivo(환자 세포 채취 필요) → in vivo(주사 1회)로 전환 시 치료 접근성 기하급수적 확대
2. **빅파마 진입 가속**: Eli Lilly(Verve $1.3B), Roche, Novartis → CRISPR 기업 인수 경쟁
3. **적응증 확장**: 단일유전자 질환 → 심혈관, 대사질환, 감염질환으로 확대
4. **이종장기**: 성공 시 장기 부족 위기의 근본적 해결 → 완전히 새로운 시장 창출

---

## 5. AI 적용

### 5.1 가이드 RNA 설계 최적화

- **Off-target 예측**: ML 모델(Elevation, CIRCLE-seq 데이터 학습)이 수십억 개 잠재적 off-target 사이트를 사전 스캔 → 안전한 가이드 선별
- **On-target 효율 예측**: DeepCRISPR, CRISPR-ML 등이 sgRNA 서열로부터 편집 효율 예측 (R² ~0.7-0.8)
- **크로마틴 접근성 통합**: ATAC-seq 데이터와 연동하여 실제 세포 환경에서의 편집 가능성 예측

### 5.2 AAV 캡시드 AI 설계

2025년 Advanced Science에 발표된 AI 기반 AAV 캡시드 공학 리뷰 [10]:
- **ML 기반 Directed Evolution**: 캡시드 서열-기능 관계를 학습하여 라이브러리 설계 최적화
- **De novo 캡시드 생성**: 생성 AI(VAE, GAN)가 자연계에 없는 완전 새로운 캡시드 변이체 설계
- **향성 예측**: 캡시드 서열로부터 조직 향성(간, CNS, 근육 등) 예측 모델
- **면역 회피 설계**: 항AAV 항체 에피토프를 회피하는 변이체의 합리적 설계

### 5.3 LNP 제형 AI 최적화

- **고처리량 스크리닝 + ML**: 수천 가지 이온화 지질 변이체의 캡슐화 효율, 세포 흡수, 엔도솜 탈출 효율을 AI가 예측
- **조직 표적화**: LNP 조성(이온화 지질 구조, PEG 비율, helper lipid 종류)과 생체 분포(biodistribution) 관계를 ML로 학습 → 비간 조직(폐, 비장, 뇌) 표적 LNP 설계
- **mRNA 서열 최적화**: 코돈 사용(codon usage), UTR 구조, polyA 길이를 AI가 최적화하여 발현 수준/지속 시간 극대화

### 5.4 세포 제조 자동화

- **iPSC 분화 프로토콜**: AI가 성장인자 농도, 배양 조건, 타이밍을 최적화하여 분화 효율/순도 향상
- **품질 관리(QC)**: 컴퓨터 비전이 세포 형태를 실시간 모니터링 → 비정상 클론 조기 검출
- **CRISPR 편집 효율**: 배양 조건(electroporation 조건, RNP 농도, cell density)과 편집 효율 관계를 ML로 최적화

### 5.5 AlphaFold와 유전자 치료

AlphaFold3의 단백질 구조 예측이 유전자 치료에 미치는 영향 [10]:
- **Cas 변이체 설계**: PAM 인식 도메인의 합리적 변형으로 PAM 범위 확장
- **AAV 캡시드-수용체 상호작용**: 캡시드 표면 루프의 3D 구조 예측 → 수용체 결합 최적화
- **PROTAC과의 융합**: 유전자 편집으로 만든 세포에서 표적 단백질 분해를 유도하는 복합 전략

---

## 6. 참고문헌

[1] Hossain MA, et al. "Advancing CRISPR genome editing into gene therapy clinical trials: progress and future prospects." *J Biomed Sci*. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12094669/

[2] Innovative Genomics Institute. "CRISPR Clinical Trials: A 2025 Update." https://innovativegenomics.org/news/crispr-clinical-trials-2025/

[3] Chen L, et al. "Research progress of base editing and prime editing tools based on the CRISPR/Cas system." *Mol Ther Nucleic Acids*. 2025. https://www.cell.com/molecular-therapy-family/nucleic-acids/fulltext/S2162-2531(25)00325-7

[4] Kim S, et al. "Emerging trends in prime editing for precision genome editing." *Exp Mol Med*. 2025. https://www.nature.com/articles/s12276-025-01463-8

[5] Zhang Y, et al. "Adeno-associated virus as a delivery vector for gene therapy of human diseases." *Signal Transduct Target Ther*. 2024;9:1780. https://www.nature.com/articles/s41392-024-01780-w

[6] Wu L, et al. "Lipid Nanoparticles for Delivery of CRISPR Gene Editing Components." *Small Methods*. 2026. https://onlinelibrary.wiley.com/doi/full/10.1002/smtd.202401632

[7] FDA. "FDA Approves First Gene Therapies to Treat Patients with Sickle Cell Disease." December 2023. https://www.fda.gov/news-events/press-announcements/fda-approves-first-gene-therapies-treat-patients-sickle-cell-disease

[8] Vertex Pharmaceuticals. "New Data on CASGEVY, Including First-Ever Data in Children Ages 5-11 Years." ASH 2025. https://news.vrtx.com/news-releases/news-release-details/vertex-presents-new-data-casgevyr-including-first-ever-data

[9] Gillmore JD, et al. "Nexiguran Ziclumeran Gene Editing in Hereditary ATTR with Polyneuropathy." *N Engl J Med*. 2025. NCT04601051. https://www.nejm.org/doi/full/10.1056/NEJMoa2510209 / Intellia IR. "MAGNITUDE Clinical Trials Update." October 2025. https://ir.intelliatx.com/news-releases/news-release-details/intellia-therapeutics-provides-update-magnitude-clinical-trials

[10] Tan J, et al. "Artificial Intelligence-Based Approaches for AAV Vector Engineering." *Adv Sci*. 2025. https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.202411062

[11] Agbim C, et al. "AAV Gene Therapy Drug Development and Translation of Engineered Ocular and Neurotropic Capsids: A Systematic Review Using Natural Language Processing." *Clin Transl Sci*. 2025. https://ascpt.onlinelibrary.wiley.com/doi/full/10.1111/cts.70428

[12] Bravo JPK, et al. "Advancing AAV technology: From capsid design to scalable manufacturing." *Mol Ther Methods Clin Dev*. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12134569/

[13] CRISPR Therapeutics IR. "Strategic Priorities and 2026 Milestones." https://ir.crisprtx.com/news-releases/news-release-details/crispr-therapeutics-highlights-strategic-priorities-and-0/

[14] Kidney Fund. "FDA Greenlights First Clinical Trials of Genetically Modified Pig Kidney Transplants in Humans." 2025. https://www.kidneyfund.org/article/fda-greenlights-first-clinical-trials-genetically-modified-pig-kidney-transplants-humans

[15] Gray Group. "Gene Editing and CRISPR in 2026: The Technology Reshaping Human Health." https://www.graygroupintl.com/blog/gene-editing-crispr-2026/

---

> **면책조항**: 본 리뷰는 기술적 분석 목적으로 작성되었으며, 특정 종목의 매수/매도를 권유하지 않습니다. 투자 결정은 전문가 자문을 통해 독립적으로 이루어져야 합니다.
