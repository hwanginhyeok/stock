# 바이오 기술 리뷰 #6: 방사성의약품 — 기전, 임상 데이터, 투자 분석

> 베타 입자에서 알파 입자까지: 방사성 동위원소 치료의 핵물리학, 킬레이터 화학, 테라노스틱스 패러다임

---

## 1. 기술 개요: 방사성의약품의 물리학적·생물학적 기반

### 1.1 방사성 동위원소 붕괴와 치료 원리

방사성의약품(radiopharmaceuticals)은 방사성 동위원소를 종양 표적 리간드에 결합시켜, 방사선을 종양 세포에 국소적으로 전달하는 표적 치료 전략이다. 이 접근의 핵심 원리는 "see what you treat, treat what you see" — 동일한 분자 표적에 진단용 동위원소와 치료용 동위원소를 각각 결합하여 영상 진단과 치료를 통합하는 테라노스틱스(theranostics)이다.

방사성 동위원소의 붕괴 과정에서 방출되는 입자(알파, 베타)와 감마선이 세포의 DNA에 손상을 가하여 세포 사멸을 유도한다. 핵심적 차이는 입자의 유형에 따른 선형 에너지 전달(Linear Energy Transfer, LET)과 조직 침투 깊이에 있다:

- **베타 입자(β-)**: 전자, LET ~0.2 keV/μm, 조직 침투 깊이 0.5-12 mm
- **알파 입자(α)**: 헬륨-4 핵, LET ~80 keV/μm, 조직 침투 깊이 50-100 μm (세포 수 개 직경)
- **오제 전자(Auger electron)**: 극저 에너지, LET ~4-26 keV/μm, 침투 깊이 <1 μm (세포핵 내부)

### 1.2 DNA 손상 메커니즘의 차이

방사선에 의한 DNA 손상은 직접 효과(방사선이 DNA에 직접 작용)와 간접 효과(물의 방사분해로 생성된 자유 라디칼이 DNA를 손상)로 구분된다.

**베타 입자의 DNA 손상**: 낮은 LET로 인해 주로 단일가닥 절단(single-strand break, SSB)을 유발한다. 세포는 base excision repair(BER) 등의 DNA 수복 기전으로 SSB를 효율적으로 수복할 수 있으므로, 베타 입자 치료는 충분한 누적 선량이 필요하다. 그러나 mm 수준의 침투 깊이는 "crossfire effect"를 통해 방사성 리간드가 직접 결합하지 않은 인접 세포에도 방사선을 전달하여, 표적 발현이 불균일한 큰 종양에 유리하다.

**알파 입자의 DNA 손상**: 높은 LET(약 100 keV/μm)로 인해 DNA 이중가닥 절단(double-strand break, DSB)을 고밀도로 유발한다. DSB는 세포의 수복 능력을 초과하는 치명적 손상이며, 특히 clustered DSB(수 base pair 이내에 다수의 DSB가 밀집)는 비상동 말단 접합(NHEJ)이나 상동 재조합(HR)으로도 정확히 수복할 수 없다 [1]. 이 때문에 알파 입자는 세포당 1-5개의 적중(hit)만으로도 세포 사멸을 유도할 수 있어, 미세 전이(micrometastasis)와 잔존 병변 치료에 이론적으로 최적이다.

---

## 2. 핵심 기술 세부

### 2.1 Lutetium-177 베타 방출 물리학

#### 2.1.1 Lu-177의 핵물리학적 특성

Lutetium-177(¹⁷⁷Lu)은 방사성의약품 분야에서 가장 널리 사용되는 베타 방출 동위원소이다:

- **반감기**: 6.647일 — 치료적으로 충분한 방사선 전달과 합리적인 물류 관리의 균형점
- **베타 입자 에너지**: 최대 에너지 497 keV (Eβmax), 평균 에너지 ~134 keV
- **조직 침투**: 평균 범위 ~0.67 mm, 최대 범위 ~2 mm
- **감마선 방출**: 208 keV (11%) 및 113 keV (6.4%) 감마선 동시 방출 — 이것이 테라노스틱스의 핵심으로, SPECT 영상을 통한 치료 중 체내 분포 모니터링과 흡수선량 계산(dosimetry)이 가능

#### 2.1.2 Lu-177의 생산

Lu-177은 두 가지 경로로 생산된다:
- **직접 생산(carrier-added)**: 천연 Lu-176 표적에 중성자 포획 (¹⁷⁶Lu + n → ¹⁷⁷Lu). 비방사능(specific activity)이 상대적으로 낮음
- **간접 생산(no-carrier-added)**: Yb-176을 표적으로 중성자 조사 후 화학적 분리 (¹⁷⁶Yb + n → ¹⁷⁷Yb → ¹⁷⁷Lu). 높은 비방사능 달성 가능, 그러나 생산 효율과 Yb/Lu 분리의 화학적 난이도가 과제

높은 비방사능은 수용체 포화 없이 충분한 방사선량을 전달하기 위해 중요하다. 수용체 수가 제한된 종양에서 carrier(비방사성 Lu)가 수용체를 점유하면 치료 효과가 감소한다.

### 2.2 Actinium-225 알파 입자 캐스케이드

#### 2.2.1 Ac-225의 붕괴 사슬

Actinium-225(²²⁵Ac)는 방사성의약품에서 가장 주목받는 알파 방출 동위원소이다. 그 핵심적 특징은 하나의 ²²⁵Ac 붕괴에서 총 4개의 알파 입자가 순차적으로 방출되는 캐스케이드 붕괴(cascade decay)이다 [2]:

```
²²⁵Ac (t₁/₂ = 9.92일)
  → ²²¹Fr + α (5.83 MeV)         [t₁/₂ = 4.8분]
    → ²¹⁷At + α (6.34 MeV)       [t₁/₂ = 32.3 ms]
      → ²¹³Bi + α (7.07 MeV)     [t₁/₂ = 45.6분]
        → ²¹³Po + β⁻             [t₁/₂ = 4.2 μs]
          → ²⁰⁹Pb + α (8.38 MeV)
            → ²⁰⁹Bi + β⁻ (안정)
```

4개 알파 입자의 총 방출 에너지는 약 27.6 MeV이며, 이는 Lu-177 베타 입자 에너지의 약 50배에 달한다. 이 막대한 에너지가 극히 짧은 거리(50-100 μm)에 집중되어 높은 세포독성을 발휘한다.

#### 2.2.2 딸핵종 재분포 문제

Ac-225 캐스케이드 붕괴의 최대 난제는 **딸핵종(daughter nuclide) 재분포**이다. 알파 붕괴 시 반동(recoil) 에너지가 화학 결합 에너지의 10,000배 이상이므로, 첫 번째 알파 붕괴 직후 ²²¹Fr 딸핵종이 킬레이터로부터 이탈한다 [3]. 이탈한 딸핵종은:

- **²²¹Fr**: 반감기 4.8분으로 빠르게 붕괴하지만 체내 재분포 가능
- **²¹³Bi**: 반감기 45.6분으로 신장에 축적되어 신독성(nephrotoxicity)을 유발할 수 있음

전임상 및 임상 연구에서 ²¹³Bi의 신장 재분포에 의한 신독성이 보고되었으며 [3], 이는 Ac-225 기반 치료의 핵심 용량 제한 독성(dose-limiting toxicity)이다. 현재 연구 방향:
- 나노캐리어 내부에 Ac-225를 봉입하여 딸핵종 방출을 물리적으로 억제
- 신장 보호제 병용 투여
- 용량 분할 전략

### 2.3 킬레이터 화학: DOTA, PSMA, 차세대 킬레이터

#### 2.3.1 킬레이터의 역할

킬레이터(chelator)는 방사성 금속 이온을 안정적으로 결합(coordination)하여 생체 내 조건에서 이탈을 방지하는 이기능성(bifunctional) 분자이다. 이상적인 킬레이터는:
- 방사성 금속과 높은 열역학적 안정성(thermodynamic stability)과 동력학적 불활성(kinetic inertness)
- 생리적 pH에서 금속 이탈 최소화
- 온화한 방사표지 조건(항체 등 열 민감 분자와 호환)

#### 2.3.2 DOTA (1,4,7,10-tetraazacyclododecane-1,4,7,10-tetraacetic acid)

DOTA는 방사성의약품에서 가장 널리 사용되는 거대고리(macrocyclic) 킬레이터이다:

- **구조**: 12원 거대고리에 4개의 질소 원자와 4개의 카르복실산 팔(arm)을 가진 N4O4 배위 환경
- **금속 배위**: 최대 8좌 배위(coordination number 8)를 제공하여 Ga³⁺, Lu³⁺, Y⁹⁰, Ac³⁺ 등 다양한 방사성 금속과 결합
- **Lu-177과의 호환성**: Lu³⁺(이온 반경 0.861 Å)는 DOTA 공동에 잘 맞으며, 높은 열역학적 안정성(log K ~21)을 보여 체내에서 안정적
- **Ac-225와의 한계**: Ac³⁺(이온 반경 1.12 Å)는 DOTA 공동에 비해 크기가 커서 열역학적 안정성이 상대적으로 낮음 [4]. 또한 방사표지 시 50°C 이상 가열이 필요하여 항체와의 접합에 제약

**PSMA-617 구조**: Pluvicto의 전구체인 PSMA-617은 DOTA 킬레이터 + 링커 + glutamate-urea-lysine PSMA 결합 모이어티로 구성된 삼성분 구조이다. PSMA(prostate-specific membrane antigen)는 전립선암 세포 표면에 고발현(정상 전립선 대비 100-1000배)되는 type II 막관통 단백질로, 내재화 능력이 있어 방사성 리간드를 세포 내부로 운반한다.

#### 2.3.3 차세대 킬레이터

Ac-225의 대형 이온 반경 문제를 해결하기 위한 차세대 킬레이터:

- **Macropa**: 18원 거대고리로 DOTA보다 큰 공동을 제공. Ac³⁺와의 결합 안정성이 DOTA 대비 우수하며, 실온에서 방사표지 가능 [5]
- **H₂BZmacropa-NCS**: Macropa의 이기능성 유도체로 항체 접합이 가능한 NCS(isothiocyanate) 관능기 보유
- **DOTPA**: DOTA의 프로피온산 유도체, Ac³⁺와의 안정성 개선
- **Crown ether 기반 킬레이터**: Ac³⁺의 소프트 Lewis acid 특성에 맞춘 산소 배위 환경

### 2.4 테라노스틱스: 진단-치료 쌍(Theranostic Pair)

#### 2.4.1 영상 동위원소

**Ga-68 (⁶⁸Ga)**:
- 양전자(β⁺) 방출 → PET 영상
- 반감기 67.7분 — ⁶⁸Ge/⁶⁸Ga 발생기(generator)로 현장 생산 가능
- DOTA 킬레이터와 호환 → 치료용 Lu-177/Ac-225과 동일 리간드 사용 가능
- 대표 제제: ⁶⁸Ga-PSMA-11 (전립선암), ⁶⁸Ga-DOTATATE (신경내분비종양)

**F-18 (¹⁸F)**:
- 양전자 방출 → PET 영상
- 반감기 109.8분 — Ga-68보다 긴 영상 윈도우
- 공유결합으로 리간드에 부착 → 킬레이터 불필요
- 대표 제제: ¹⁸F-DCFPyL (Pylarify, PSMA PET), ¹⁸F-FDG

#### 2.4.2 "See and Treat" 워크플로우

테라노스틱스의 실제 임상 적용 흐름:

1. **영상 진단(See)**: ⁶⁸Ga-PSMA-11 PET/CT 촬영 → PSMA 발현 종양 병변의 위치, 크기, SUV(standardized uptake value) 정량
2. **환자 선별**: PSMA PET 양성(SUVmax ≥ 기준치) 환자만 치료 대상으로 선별 — 바이오마커 기반 환자 층화가 치료에 내장
3. **치료(Treat)**: ¹⁷⁷Lu-PSMA-617 정맥 투여 (7.4 GBq/회, 6주 간격, 4-6회)
4. **치료 반응 모니터링**: 치료 후 ⁶⁸Ga-PSMA PET 재촬영 또는 ¹⁷⁷Lu의 감마선을 이용한 SPECT 영상으로 치료 반응 평가

이 통합 패러다임은 "환자가 치료에 반응할 것인지를 치료 전에 영상으로 확인"한다는 점에서 정밀의학의 완성형에 해당한다.

---

## 3. 임상 데이터: 주요 시험 결과

### 3.1 VISION Trial — Lu-177-PSMA-617 (Pluvicto)

**설계**: Phase 3, 무작위 배정, 개방 표지, 국제 다기관 (NCT03511664)
- 대상: PSMA-PET 양성 전이성 거세 저항성 전립선암(mCRPC), AR 경로 억제제 1개 이상 + 택산 1-2개 사전 치료
- 무작위 배정: 2:1 (¹⁷⁷Lu-PSMA-617 + 표준 치료 vs. 표준 치료 단독)
- 치료: 7.4 GBq 정맥 투여, 6주 간격, 최대 6회

**주요 결과** [6]:
- **전체 생존(OS)**: 중앙값 15.3개월 vs. 11.3개월 (HR 0.62, 95% CI 0.52-0.74, p<0.001)
- **방사선학적 무진행 생존(rPFS)**: 중앙값 8.7개월 vs. 3.4개월 (HR 0.40, 99.2% CI 0.29-0.57, p<0.001)
- **PSA 반응률(≥50% 감소)**: 46% vs. 7.1%

**안전성**:
- Grade 3-4 이상반응: 피로(5.4%), 빈혈(12.9%), 혈소판감소증(7.6%)
- 구갈(dry mouth): 39% (대부분 Grade 1-2)
- 신독성: 경미 (GFR 유의한 감소 미관찰)

이 결과를 바탕으로 FDA는 2022년 3월 Pluvicto를 PSMA-PET 양성 mCRPC 치료제로 승인했으며, Pluvicto는 승인 첫 9개월 동안 $1.04B 매출을 달성하여 블록버스터 진입에 성공했다.

### 3.2 PSMAfore Trial — 택산 미치료 mCRPC로 확장

**설계**: Phase 3, 무작위 배정, 개방 표지 (NCT04689828)
- 대상: 이전 ARPI 1개에서 진행된 택산 미치료 PSMA-양성 mCRPC
- 무작위 배정: ¹⁷⁷Lu-PSMA-617 vs. ARPI 변경 (abiraterone 또는 enzalutamide)

**주요 결과** [7]:
- **방사선학적 무진행 생존(rPFS)**: HR 0.41 (95% CI 0.29-0.56) — Lu-PSMA-617이 ARPI 변경 대비 59% 진행 위험 감소
- **전체 생존(OS)**: 중앙값 24.48개월 vs. 23.13개월 (HR 0.91, 95% CI 0.72-1.14, p=0.20) — OS에서는 유의한 차이 미달, 교차(crossover)의 영향
- **안전성**: 구갈 59.5% (Grade ≥3: 0.9%), 빈혈 27.3% (Grade ≥3: 6.2%)

PSMAfore의 rPFS 성공은 FDA의 Pluvicto 적응증 확대 승인(2024년)으로 이어져, 택산 미경험 환자까지 치료 대상이 확장되었다.

### 3.3 PSMAddition Trial — 호르몬 감수성 전립선암으로 전진

**설계**: Phase 3, 무작위 배정 (NCT04720157)
- 대상: PSMA-양성 전이성 호르몬 감수성 전립선암(mHSPC) — 가장 이른 전립선암 단계에서의 Lu-PSMA 평가
- 치료: ADT + ARPI + ¹⁷⁷Lu-PSMA-617 vs. ADT + ARPI

**1차 결과 (2025)**:
- rPFS에서 유의한 개선이 보고되어, Pluvicto의 치료 영역이 말기(mCRPC)에서 초기(mHSPC)까지 확장될 가능성을 시사 [8]

### 3.4 Lutathera — 신경내분비종양(NET)

**NETTER-1 (Phase 3, NCT01578239)**:
- 적응증: 소마토스타틴 수용체 양성 진행성 위장관 신경내분비종양
- 결과: 중앙 PFS 미도달 vs. octreotide LAR 단독 8.4개월 (HR 0.21, p<0.0001)
- Lu-177-DOTATATE는 SSTR2를 표적으로 하며, PSMA와 다른 수용체계를 활용

### 3.5 RYZ101 — 차세대 Ac-225 알파 입자 치료제

**ACTIONET (Phase 3, NCT05595460)**:
- 적응증: SSTR-양성 위장관 신경내분비종양 (Lutathera 후 진행)
- 동위원소: Ac-225 — 알파 입자의 높은 LET로 Lu-177 저항성 극복 시도
- BMS가 RayzeBio를 $4.1B에 인수하여 확보한 핵심 파이프라인
- 진행 중, 결과 미보고

---

## 4. 시장 분석

### 4.1 시장 규모

| 세그먼트 | 2024 | 2033 전망 | CAGR |
|---------|------|----------|------|
| 방사성의약품 전체 | $6.8B | $13.4B | 7.8% |
| 테라노스틱스 | $2.4B | $6B+ | ~12% |
| Pluvicto 단독 매출 | ~$1.5B (연환산) | — | — |

### 4.2 빅파마의 대규모 M&A (2023-2024)

방사성의약품 분야에서 2023-2024년 $10B+ 규모의 M&A가 집중 발생했다:

| 년도 | 인수자 | 대상 | 금액 | 전략적 의미 |
|------|--------|------|------|------------|
| 2023 | Eli Lilly | Point Biopharma | $1.4B | Lu-177 전립선암 파이프라인 |
| 2024 | BMS | RayzeBio | $4.1B | Ac-225 알파 입자 기술 |
| 2024 | AstraZeneca | Fusion Pharma | $2.4B | 알파 입자 기술 |
| 2024 | Eli Lilly | Aktis Oncology | $1.1B+ | 차세대 방사성 치료제 |

이 M&A 물결은 빅파마가 방사성의약품을 면역항암제(IO) 이후의 차기 종양학 성장축으로 인식하고 있음을 시사한다.

### 4.3 핵심 투자 테제

1. **Novartis의 선점 우위**: Pluvicto + Lutathera로 시장을 선도하며, PSMAfore/PSMAddition 적응증 확대로 Pluvicto의 TAM이 연간 $5B+ 잠재력
2. **알파 입자(Ac-225)가 다음 프론티어**: Lu-177 베타 치료에 저항하는 미세 전이에 대한 이론적 우위. 그러나 Ac-225 공급 제한이 최대 병목 — 전 세계 연간 생산량이 수 Ci 수준으로 수천 환자 치료에도 부족
3. **CDMO 기회**: 방사성 물질 취급 시설(hot cell) 구축에 $수억 소요 → 위탁생산(CDMO) 수요 급증. Jubilant Radiopharma, PharmaLogic 등이 수혜
4. **가격과 접근성 과제**: Pluvicto ~$42K/회 x 4-6회 = 환자당 $200K+ — 보험 급여와 비용 효과 분석이 시장 확대의 관건
5. **반감기 관리 물류**: 방사성 동위원소는 생산 후 시간이 경과하면 효력이 상실 → "just-in-time" 제조·물류 체계가 필수, 이는 높은 진입 장벽

---

## 5. AI 적용: 방사성의약품 개발과 임상에서의 인공지능

### 5.1 AI 기반 선량 계산(Dosimetry)

전통적 방사성의약품 dosimetry는 MIRD(Medical Internal Radiation Dose) 방법론에 기반하여, 연속적 SPECT/CT 영상에서 장기별 시간-방사능 곡선을 구하고 S-factor를 적용하여 흡수선량을 계산한다. 이 과정은 노동 집약적이며 여러 시점의 영상이 필요하다.

AI의 혁신:
- **U-Net 기반 장기 분할**: 딥러닝이 SPECT/CT 영상에서 종양, 신장, 간, 골수 등을 자동 분할하여 dosimetry 워크플로우 가속 [9]
- **단일 시점 dosimetry**: CNN 모델이 치료 후 단일 SPECT 영상만으로 전체 시간-방사능 곡선을 예측하여 환자의 영상 검사 부담 경감
- **GAN 기반 영상 향상**: 저선량 SPECT 영상을 고선량 품질로 향상시켜 dosimetry 정확도 개선

### 5.2 PET 영상 AI 분석

- **자동 종양 부하(tumor burden) 정량**: AI가 ⁶⁸Ga-PSMA PET에서 전체 종양 부피와 총 PSMA 발현량을 자동 정량하여 치료 반응 예측 [10]
- **치료 전 반응 예측**: 기계학습 모델이 치료 전 PET 특징(radiomic features)으로 Lu-PSMA-617 치료 반응과 생존을 예측

### 5.3 표적 발굴과 신규 킬레이터 설계

- **대규모 프로테오믹스 데이터에서 종양 특이 수용체 식별**: AI가 종양과 정상 조직의 단백질 발현 프로파일을 비교하여 새로운 방사성의약품 표적 후보를 발굴
- **Generative AI를 이용한 킬레이터 분자 설계**: 동위원소-킬레이터 복합체의 열역학적 안정성, 동력학적 불활성, 방사표지 조건을 동시에 최적화하는 분자 생성 모델
- **환자별 맞춤 용량 최적화**: 환자의 종양 부하, 신기능(GFR), 체중, 골수 예비능을 통합하여 최적 투여 용량을 AI가 계산

---

## 6. 참고문헌

[1] Sgouros G, Bodei L, McDevitt MR, Nedrow JR. "Radiopharmaceutical therapy in cancer: clinical advances and challenges." *Nature Reviews Drug Discovery*. 2020;19(9):589-608.
https://www.nature.com/articles/s41573-020-0073-9

[2] Kratochwil C, Bruchertseifer F, Giesel FL, et al. "225Ac-PSMA-617 for PSMA-targeted α-radiation therapy of metastatic castration-resistant prostate cancer." *Journal of Nuclear Medicine*. 2016;57(12):1941-1944.
https://jnm.snmjournals.org/content/57/12/1941

[3] de Kruijff RM, Wolterbeek HT, Denkova AG. "A critical review of alpha radionuclide therapy — how to deal with recoiling daughters?" *Pharmaceuticals*. 2015;8(2):321-336. / Hooijman EL, et al. "Implementing Ac-225 labelled radiopharmaceuticals: practical considerations and (pre-)clinical perspectives." *EJNMMI Radiopharmacy and Chemistry*. 2024;9:9.
https://link.springer.com/article/10.1186/s41181-024-00239-1

[4] Thiele NA, Brown V, Kelly JM, et al. "Actinium-225 for Targeted α Therapy: Coordination Chemistry and Current Chelation Approaches." *Cancer Biotherapy and Radiopharmaceuticals*. 2018;33(8):336-348.
https://pmc.ncbi.nlm.nih.gov/articles/PMC6207149/

[5] Thiele NA, Wilson JJ. "H₂BZmacropa-NCS: A Bifunctional Chelator for Actinium-225 Targeted Alpha Therapy." *Bioconjugate Chemistry*. 2022;33(8):1489-1495.
https://pubs.acs.org/doi/10.1021/acs.bioconjchem.2c00190

[6] Sartor O, de Bono J, Chi KN, et al. "Lutetium-177-PSMA-617 for Metastatic Castration-Resistant Prostate Cancer." *New England Journal of Medicine*. 2021;385(12):1091-1103.
https://www.nejm.org/doi/full/10.1056/NEJMoa2107322

[7] Fizazi K, Herrmann K, Krber MI, et al. "177Lu-PSMA-617 versus a change of androgen receptor pathway inhibitor therapy for taxane-naive patients with progressive metastatic castration-resistant prostate cancer (PSMAfore): a phase 3, randomised, controlled trial." *The Lancet*. 2024.
https://pubmed.ncbi.nlm.nih.gov/39293462/

[8] Novartis. "PSMAddition data show Novartis Pluvicto delays progression to end-stage prostate cancer." Press release, 2025.
https://www.novartis.com/news/media-releases/psmaddition-data-show-novartis-pluvictotm-delays-progression-end-stage-prostate-cancer

[9] Kim C, et al. "The Role of Artificial Intelligence in Advancing Theranostics Dosimetry for Cancer Therapy: a Review." *Nuclear Medicine and Molecular Imaging*. 2025.
https://link.springer.com/article/10.1007/s13139-025-00939-9

[10] Gafita A, et al. "Quantitative 68Ga-PSMA-11 PET and Clinical Outcomes in Metastatic Castration-resistant Prostate Cancer Following 177Lu-PSMA-617 (VISION Trial)." *Radiology*. 2024.
https://pubmed.ncbi.nlm.nih.gov/39162634/

[11] Tao W, et al. "Embracing artificial intelligence design for better radiopharmaceuticals." *iRADIOLOGY*. 2024;2(3):245-261.
https://onlinelibrary.wiley.com/doi/full/10.1002/ird3.76

[12] Bodei L, et al. "Radiomics and Artificial Intelligence in Radiotheranostics: A Review of Applications for Radioligands Targeting Somatostatin Receptors and Prostate-Specific Membrane Antigens." *Cancers*. 2024;16(3):419.
https://pmc.ncbi.nlm.nih.gov/articles/PMC10814892/

---

*면책조항: 본 리뷰는 정보 제공 목적으로 작성되었으며, 특정 종목에 대한 투자 권유가 아닙니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.*
