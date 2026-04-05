# 바이오 기술 리뷰 #2: 유도 미사일 (Targeted Therapy) — 기전, 임상 데이터, 투자 분석

> **Review Article** | 2026-04-05
> 키워드: ADC, PROTAC, molecular glue, 단클론항체, 링커 화학, DAR, E3 리가제, ubiquitin-proteasome

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

### 1.1 표적치료의 분자생물학적 기반

표적치료(targeted therapy)는 암세포의 특이적 분자 표적을 선택적으로 공격하여 정상 조직 손상을 최소화하는 치료 전략이다. 이 접근법의 이론적 토대는 Paul Ehrlich의 "magic bullet" 개념(1900년대 초)에서 출발하며, 분자생물학과 면역학의 발전으로 실현되었다.

표적치료의 핵심 모달리티(modality)는 네 가지로 분류된다:

| 모달리티 | 작용 기전 | 분자량 | 대표 예 |
|---------|---------|--------|---------|
| 소분자 억제제 | 세포 내 키나제 활성 부위 차단 | <1 kDa | Osimertinib (EGFR) |
| 단클론항체 (mAb) | 세포 외 표적 결합 + 면역 활성화 | ~150 kDa | Trastuzumab (HER2) |
| 항체-약물 접합체 (ADC) | 항체 유도 + 세포독성 약물 전달 | ~150-160 kDa | Enhertu (HER2) |
| 표적 단백질 분해제 | 단백질 분해 기전 활용 | ~1 kDa (PROTAC), <0.5 kDa (글루) | ARV-471 (ER) |

### 1.2 종양학의 패러다임 전환: "억제"에서 "분해"로

전통적 표적치료는 표적 단백질의 **기능 억제(inhibition)**에 의존했다. 그러나 이 접근법의 근본적 한계가 있다:

- **활성 부위 의존성**: 약물 결합을 위한 깊은 소수성 포켓이 필요 → "undruggable" 표적 ~80%
- **점 돌연변이 내성**: 게이트키퍼 돌연변이로 약물 결합 소실 (예: EGFR T790M)
- **화학양론적 억제**: 약물 농도가 표적 농도를 초과해야 함 → 높은 투여 용량

표적 단백질 분해(TPD, Targeted Protein Degradation)는 이 패러다임을 전복한다. 세포 자체의 유비퀴틴-프로테아좀 시스템(UPS)을 활용하여 표적 단백질을 물리적으로 제거하므로:

- **표면 결합만으로 충분**: 활성 부위가 필요 없음
- **촉매적 작용**: 하나의 PROTAC 분자가 여러 표적 단백질을 순차적으로 분해 → sub-stoichiometric 효능
- **내성 극복**: 단백질 자체를 제거하므로 점 돌연변이 내성 회피 가능

---

## 2. 핵심 기술 세부

### 2.1 ADC 링커 화학 (Cleavable vs. Non-cleavable)

ADC의 세 구성 요소 — 항체(antibody), 링커(linker), 페이로드(payload) — 중 링커 설계가 ADC의 치료 지수(therapeutic index)를 결정하는 핵심 변수다 [1, 2].

#### 2.1.1 절단형 링커 (Cleavable Linkers)

종양 미세환경 또는 세포 내부의 특정 조건에 반응하여 절단되는 링커:

**① 산 민감성 링커 (Acid-labile linkers)**
- **메커니즘**: 히드라존(hydrazone) 결합이 엔도솜/리소좀의 낮은 pH(4.5-5.5)에서 가수분해
- **예시**: Mylotarg(gemtuzumab ozogamicin)에 사용
- **한계**: 혈중 순환 시 조기 방출(premature release) 위험 → 독성 문제로 Mylotarg 초기 시장 철수의 원인

**② 디설파이드 링커 (Disulfide linkers)**
- **메커니즘**: 세포 내 글루타치온(GSH) 농도(1-10 mM) > 혈중(~5 μM) 차이를 이용. 세포질의 환원 환경에서 S-S 결합 절단
- **안정성 조절**: 디설파이드 결합 인접 메틸기 도입으로 입체 장애(steric hindrance) 증가 → 혈중 안정성 향상
- **예시**: Maytansinoid 기반 ADC에 적용

**③ 펩타이드 링커 (Peptide/enzyme-cleavable linkers)**
- **메커니즘**: 리소좀 protease인 Cathepsin B에 의해 인식/절단되는 디펩타이드 서열 사용
- **대표 서열**: Val-Cit(valine-citrulline) → 가장 널리 사용
- **작동**: Cathepsin B가 Cit의 C-말단 아미드 결합을 절단 → PABC(para-aminobenzylcarbamate) 자발적 분해 → 페이로드 방출
- **장점**: 혈중 안정성 우수 (혈장에 Cathepsin B 농도 극히 낮음)
- **예시**: Adcetris(brentuximab vedotin) — mc-Val-Cit-PABC-MMAE

**④ 글루쿠로나이드 링커**
- **메커니즘**: β-glucuronidase에 의해 절단 → 종양 괴사 부위에서 높은 효소 활성 이용
- **장점**: 소수성 페이로드의 수용성 개선

#### 2.1.2 비절단형 링커 (Non-cleavable Linkers)

- **메커니즘**: 항체가 세포 내 리소좀에서 완전히 분해된 후에만 페이로드-링커-아미노산 잔기가 방출
- **대표 구조**: Thioether(티오에테르) 링커 — SMCC(N-succinimidyl-4-(N-maleimidomethyl)cyclohexane-1-carboxylate)
- **예시**: Kadcyla(T-DM1) — thioether linker + DM1 maytansinoid
- **장점**: 극도의 혈중 안정성, 낮은 bystander effect
- **단점**: 페이로드가 아미노산 잔기 부착 상태로 방출 → 세포막 투과 불가 → bystander killing 제한적

| 특성 | 절단형 | 비절단형 |
|------|--------|---------|
| 혈중 안정성 | 중간~높음 | 매우 높음 |
| 페이로드 방출 | 종양 미세환경/세포내 | 리소좀 분해 후 |
| Bystander effect | 있음 (유리 페이로드 확산) | 제한적 |
| 이질 종양 치료 | 유리 | 불리 |
| 대표 약물 | Enhertu, Adcetris, Trodelvy | Kadcyla |

#### 2.1.3 최신 링커 혁신

- **바이오직교(bioorthogonal) 링커**: 클릭 화학 기반으로 체내에서 외부 자극(예: tetrazine-TCO 반응)에 의해 선택적 절단
- **종양 미세환경 반응형**: 저산소(hypoxia), 높은 MMP 활성, 산성 pH에 연쇄적으로 반응하는 다단계(multi-responsive) 링커
- **부위 특이적 접합(site-specific conjugation)**: THIOMAB, SMARTag, 미생물 transglutaminase, glycan remodeling 등으로 접합 위치를 정밀 제어 → 균일한 DAR 생성 [1, 2]

### 2.2 DAR(Drug-to-Antibody Ratio) 최적화

DAR은 하나의 항체에 결합된 페이로드 분자의 평균 수로, ADC의 효능과 안전성을 결정하는 핵심 파라미터다 [2].

#### 2.2.1 DAR과 약동학/약력학 관계

| DAR | 효능 | 소수성 | 혈중 클리어런스 | 치료 지수 |
|-----|------|--------|---------------|---------|
| 2 | 낮음 | 낮음 | 느림 | 중간 |
| **4** | **최적** | **중간** | **중간** | **최적** |
| 8 | 높음 | 높음 | 빠름 | 낮음 |

DAR > 6인 ADC는 소수성 증가로 인해:
- 혈장 단백질(특히 FcRn)과의 상호작용 변경 → 가속 클리어런스
- 응집(aggregation) 경향 증가
- 비특이적 세포 흡수 증가 → 독성 상승

#### 2.2.2 Enhertu의 DAR 8 패러다임 전복

Enhertu(trastuzumab deruxtecan, T-DXd)는 DAR~8이라는 이례적으로 높은 비율을 채택하면서도 우수한 치료 지수를 달성했다. 이것이 가능한 핵심 요인:

1. **DXd 페이로드의 높은 세포막 투과성**: topoisomerase I 억제제 DXd가 유리 형태로 방출 후 주변 세포로 확산 → **강력한 bystander effect**
2. **DXd의 짧은 혈중 반감기**: 유리 DXd는 혈중에서 t1/2 ~1.3시간으로 급속 소실 → 전신 독성 최소화
3. **GGFG tetrapeptide 링커**: Cathepsin 매개 절단으로 효율적 세포내 방출
4. **친수성 링커 설계**: DAR 8에도 소수성 증가 최소화 → 응집 방지, 정상 약동학 유지

### 2.3 PROTAC: E3 유비퀴틴 리가제 모집 메커니즘

PROTAC(Proteolysis-Targeting Chimera)은 이기능성(bifunctional) 소분자로, 한쪽은 표적 단백질(POI, Protein of Interest)에, 다른 한쪽은 E3 유비퀴틴 리가제에 결합하여 강제 근접(induced proximity)을 유도한다 [3, 4].

#### 2.3.1 유비퀴틴-프로테아좀 시스템(UPS) 작동 원리

정상적 UPS 캐스케이드:
1. **E1 활성화 효소**: ATP 의존적으로 유비퀴틴(Ub)의 C-말단 Gly76을 활성화 → E1~Ub 티오에스터 결합
2. **E2 접합 효소**: E1에서 Ub를 받아 E2~Ub 형성 (~40종의 E2)
3. **E3 리가제**: 기질 특이성 결정 → POI와 E2~Ub를 동시에 결합하여 POI의 Lys 잔기에 Ub 전이
4. **폴리유비퀴틴화**: K48-linked poly-Ub 사슬 (≥4개 Ub) 형성 → 프로테아좀 인식 신호
5. **26S 프로테아좀**: 19S 캡이 poly-Ub 사슬 인식 → 탈유비퀴틴화 + 언폴딩 → 20S 코어에서 펩타이드 단편으로 분해

#### 2.3.2 PROTAC이 활용하는 E3 리가제

인간 게놈에는 ~600종의 E3 리가제가 존재하지만, PROTAC에 활용되는 것은 극소수다:

| E3 리가제 | 리간드 | 장점 | 한계 | 대표 PROTAC |
|----------|--------|------|------|------------|
| **CRBN (Cereblon)** | Thalidomide 유도체 (pomalidomide, lenalidomide) | 풍부한 SAR 데이터, 구조 정보 | 조직 특이성 부족 | ARV-110, CC-885 |
| **VHL (von Hippel-Lindau)** | VH032 유도체 | 높은 선택성, 깨끗한 프로파일 | 분자량 증가 | ARV-471, MZ1 |
| **cIAP1 (cellular Inhibitor of Apoptosis 1)** | Bestatin 유도체 | 자가분해 동반 효과 | 제한적 SAR | SNIPER계열 |
| **MDM2** | Nutlin 유도체 | p53 경로 활용 가능 | 독성 우려 | MD-224 |

#### 2.3.3 삼원 복합체(Ternary Complex) 형성의 열역학

PROTAC 효능의 핵심은 POI-PROTAC-E3 삼원 복합체의 안정성이다:

- **협동성(cooperativity, α값)**: α > 1이면 양성 협동성 → 삼원 복합체 안정성이 이원 복합체 합보다 큼
- **PPI(Protein-Protein Interaction)**: POI 표면과 E3 리가제 표면 사이의 신규 접촉면이 형성되어야 함
- **링커 길이/구조**: POI-E3 간 최적 거리와 배향(orientation)을 결정 → 1-2 원자 차이로 활성 10-100배 변동

ARV-471(vepdegestrant)은 VHL E3 리가제를 모집하여 에스트로겐 수용체(ER)를 분해한다. ER-ARV-471-VHL 삼원 복합체에서 ER의 ligand-binding domain과 VHL의 β-도메인 사이에 새로운 단백질-단백질 접촉면이 형성되며, 이것이 높은 분해 효율의 구조적 기반이다 [4].

### 2.4 Molecular Glue: 네오기질 인식과 분해

Molecular glue 분해제는 PROTAC과 달리 이기능성 구조가 아닌 **단일 소분자**로, E3 리가제의 기질 인식면을 리모델링하여 원래 상호작용하지 않는 단백질(neosubstrate)의 분해를 유도한다 [5, 6].

#### 2.4.1 Cereblon-IMiD 패러다임

Thalidomide, lenalidomide, pomalidomide(통칭 IMiDs)의 작용 기전 해명은 molecular glue 분야의 기원이다:

1. **CRBN 결합**: 글루타리미드(glutarimide) 모이어티가 CRBN의 Trp380, His378이 형성하는 얕은 포켓에 결합
2. **표면 리모델링**: IMiD의 프탈리미드(phthalimide) 부분이 CRBN 표면에서 돌출 → 새로운 소수성 접면 형성
3. **네오기질 인식**: 변형된 CRBN 표면이 IKZF1(Ikaros)/IKZF3(Aiolos)의 Cys2-His2 zinc finger 도메인(ZnF2)을 인식
4. **유비퀴틴화**: CUL4-DDB1-RBX1-CRBN E3 리가제 복합체가 IKZF1/3를 K48-linked 폴리유비퀴틴화
5. **프로테아좀 분해**: 26S 프로테아좀에 의한 완전 분해

#### 2.4.2 IKZF1/3 분해의 생물학적 결과

IKZF1(Ikaros)과 IKZF3(Aiolos)는 림프구 발달의 핵심 전사인자다:

- **IRF4/c-MYC 하향조절**: IKZF1/3 분해 → IRF4, c-MYC 전사 억제 → 골수종 세포 증식 정지
- **IL-2/IFN-γ 상향조절**: T세포에서 IKZF1/3은 IL-2 프로모터의 억제자 → 분해 시 IL-2 생산 증가 → T세포 활성화
- **NK 세포 활성화**: IFN-γ 상향조절 → NK 세포 매개 종양 살해 촉진

#### 2.4.3 차세대 Molecular Glue

| 약물 | 기업 | 네오기질 | 적응증 | 상태 |
|------|------|---------|--------|------|
| CC-220 (iberdomide) | BMS | IKZF1/3 (고친화도) | 다발성 골수종 | Phase 3 |
| CC-92480 (mezigdomide) | BMS | IKZF1/3 (초고친화도) | 다발성 골수종 | Phase 3 |
| CC-99282 (golcadomide) | BMS | IKZF1/3 | DLBCL | Phase 3 |
| MRT-31619 | — | CRBN 자체 (homo-dimerization) | 연구단계 | 전임상 |

2025년 Science에 발표된 연구에서, CRBN 표적 공간의 체계적 마이닝(mining)을 통해 molecular glue의 네오기질 인식 규칙이 재정의되었다 [6]. 기존에 알려진 zinc finger 도메인 외에도 다양한 구조 모티프가 CRBN-glue 복합체에 의해 인식될 수 있음이 밝혀졌다.

---

## 3. 임상 데이터

### 3.1 Enhertu(Trastuzumab Deruxtecan) — ADC의 기준점

#### DESTINY-Breast03 (NCT03529110): HER2+ 전이성 유방암

T-DXd vs. T-DM1(Kadcyla) 직접 비교 [7]:

| 항목 | T-DXd | T-DM1 | 통계량 |
|------|-------|-------|--------|
| 피험자 수 | 261 | 263 | — |
| 중앙 PFS | **미도달** | 6.8개월 | HR 0.28 (95% CI 0.22-0.37; P<0.001) |
| ORR | **79.7%** | 34.2% | — |
| mOS | **미도달** | **미도달** | HR 0.64 (95% CI 0.47-0.87; P=0.0037) |
| 12개월 PFS율 | 75.8% | 34.1% | — |

#### DESTINY-Breast04 (NCT03734029): HER2-low 전이성 유방암

HER2-low라는 새로운 치료 카테고리를 창출한 획기적 시험 [7]:

| 항목 | T-DXd | 표준 화학요법 |
|------|-------|-------------|
| 중앙 PFS | **9.9개월** | 5.1개월 (HR 0.50) |
| 중앙 OS (32개월 추적) | **22.9개월** | 16.8개월 (HR 0.69; 95% CI 0.55-0.86) |
| ORR | 52.3% | 16.3% |

#### DESTINY-Breast05 (NCT04622319): HER2+ 조기 유방암

수술 전후 보조요법 비교 (2025년 데이터) [7]:

- T-DXd가 T-DM1 대비 **침습적 무병 생존(iDFS) 53% 개선** (HR 0.47; 95% CI 0.34-0.66; P<0.0001)

#### DESTINY-Breast09 (NCT04784715): HER2+ 전이성 유방암 1차 치료

| 항목 | T-DXd + Pertuzumab | Taxane + Trastuzumab + Pertuzumab |
|------|--------------------|---------------------------------|
| 중앙 PFS | **40.7개월** | 26.9개월 (HR 0.56; 95% CI 0.44-0.71) |

### 3.2 Padcev(Enfortumab Vedotin) — ADC 적응증 확대

#### EV-302/KEYNOTE-A39 (NCT04223856): 요로상피암 1차

Padcev + Pembrolizumab vs. Gemcitabine-Cisplatin [8]:

| 항목 | Padcev + Pembro | Gem-Cis |
|------|----------------|---------|
| 중앙 PFS | **12.5개월** | 6.3개월 (HR 0.45; P<0.001) |
| 중앙 OS | **31.5개월** | 16.1개월 (HR 0.47; P<0.001) |
| ORR | 67.7% | 44.4% |

### 3.3 ARV-471 (Vepdegestrant) — 최초의 PROTAC 승인 후보

#### VERITAC-2 (NCT05654623): ER+/HER2- ESR1-변이 전이성 유방암

2025년 3월 결과 발표 및 NDA 제출 완료 [4]:

- **1차 종료점**: 이전 내분비 치료 후 ESR1 변이 유방암 환자에서 PFS 유의한 개선
- Arvinas와 Pfizer는 2차 치료 단독요법으로 FDA 승인 신청 완료 (2025년 8월 수리)
- 일부 추가 Phase 3 시험(VERITAC-3, VERITAC-4)은 전략적 집중을 위해 취소

2026년 승인 시 **세계 최초 PROTAC 상용화**가 실현된다.

#### 기타 PROTAC Phase 3 파이프라인

| 약물 | 기업 | 표적 | 적응증 | 시험 |
|------|------|------|--------|------|
| BGB-16673 (catadegbrutinib) | BeiGene | BTK | CLL/SLL | Phase 3 |
| BMS-986365 (gridegalutamide) | BMS | AR | mCRPC | Phase 3 |

### 3.4 Molecular Glue 임상 데이터

#### Lenalidomide — DLBCL

AUGMENT 시험: R/R indolent NHL에서 lenalidomide + rituximab이 rituximab 단독 대비 PFS 39.4개월 vs. 14.1개월 (HR 0.46; P<0.001).

#### Mezigdomide (CC-92480) — 다발성 골수종

Phase 1/2 (CC-92480-MM-001): 중도 치료 내성 다발성 골수종 환자에서:
- **ORR**: 40% (dexamethasone 병용 시)
- **중앙 반응 기간**: 7.6개월
- CRBN에 대한 초고친화도 결합 → lenalidomide/pomalidomide 내성 환자에서도 IKZF1/3 분해 가능

---

## 4. 시장 분석

### 4.1 TAM

| 모달리티 | 2025 시장 | 2030 전망 | 2035 전망 | CAGR |
|---------|----------|----------|----------|------|
| ADC | $13.5B | $20.1B | $32.7B | 9.2% |
| mAb (전체) | ~$250B | ~$330B | ~$450B | ~5% |
| mAb 바이오시밀러 | $17.4B | ~$35B | $58.1B | 16.3% |
| PROTAC/TPD | $1.0B | ~$3.5B | $6.9-9.85B | 21-35% |

### 4.2 ADC 경쟁 구도

#### 승인 ADC (2026년 4월 기준)

15개 이상의 ADC가 FDA 승인을 받았으며, 핵심 상용화 제품:

| 약물 | 항원 | 페이로드 | 링커 | DAR | 연 매출 |
|------|------|---------|------|-----|---------|
| Enhertu | HER2 | DXd (Topo I) | GGFG peptide | ~8 | ~$8B |
| Padcev | Nectin-4 | MMAE | mc-Val-Cit-PABC | ~4 | ~$4B |
| Trodelvy | Trop-2 | SN-38 (Topo I) | CL2A | ~7.6 | ~$2B |
| Adcetris | CD30 | MMAE | mc-Val-Cit-PABC | ~4 | ~$1.3B |
| Kadcyla | HER2 | DM1 | SMCC (non-cleavable) | ~3.5 | ~$2B |

#### 주요 딜

- **BioNTech + BMS**: BNT327 공동개발 — upfront $1.5B, 마일스톤 최대 $7.6B (2025)
- **Eli Lilly**: ADC 생산시설 $5B 투자 (2025)
- **Pfizer의 Seagen 인수**: $43B (2023) → ADC 파이프라인 대폭 확보

### 4.3 특허 절벽과 바이오시밀러

**Keytruda(pembrolizumab) 특허 만료**: 2028년 예상
- 연 매출 ~$30B → 바이오시밀러 진입 시 $10B+ 시밀러 시장 형성
- Merck는 피하주사 Keytruda(특허 연장), Keytruda 기반 ADC(MK-2140) 등으로 생명주기 관리

**Humira(adalimumab)**: 이미 바이오시밀러 진입 → AbbVie 매출 급락이 시밀러 시장의 선례

### 4.4 차세대 ADC 플랫폼

| 플랫폼 | 설명 | 잠재력 |
|--------|------|--------|
| 이중 페이로드 ADC | 한 항체에 2종류 약물 탑재 | 내성 극복, 시너지 |
| 바이스페시픽 ADC | 이중특이성 항체 + 약물 | 다중 항원 표적 |
| 조건부 활성화 ADC | TME에서만 항체 활성화 | 안전성 극대화 |
| **DAC (Degrader-Antibody Conjugate)** | ADC + PROTAC 하이브리드 | "undruggable" 표적 도달 |
| XDC (비항체 접합체) | 나노바디, 펩타이드 등 활용 | 낮은 제조 비용, 조직 침투 |

DAC는 ADC의 세포 유도 능력과 PROTAC의 촉매적 단백질 분해 능력을 결합한 차세대 플랫폼으로, 2025년 이후 다수의 전임상/초기 임상 프로그램이 진행 중이다 [9].

---

## 5. AI 적용

### 5.1 AI de novo 항체 설계

- **Absci (ABSI)**: AI 생성 모델로 표적 항원에 대한 항체를 처음부터(de novo) 설계. 동물 면역화 없이 수일 내 후보 항체 도출. Twist Bioscience와 파트너십.
- **Generate Biomedicines**: 생성 AI로 신규 치료 항체 생성. 서열 공간의 체계적 탐색.
- **LabGenius (→ Sanofi)**: AI 설계 T-cell engager, 2026 IND 예정.

### 5.2 AlphaFold 기반 구조 예측

AlphaFold3는 항체-항원 결합 구조를 원자 수준에서 예측할 수 있으며 [10]:
- **CDR 루프 최적화**: 상보성 결정 영역(CDR)의 구조를 예측하여 결합력 최적화
- **에피토프 맵핑**: 항원의 3D 구조에서 최적 결합 부위 식별
- **PROTAC 삼원 복합체 모델링**: POI-PROTAC-E3 삼원 복합체의 구조 예측 → 최적 링커 길이/배향 결정

### 5.3 ADC 최적화

- **링커-페이로드 조합 탐색**: ML 모델이 수천 가지 링커-페이로드 조합의 안정성, 방출 속도, 세포 투과성을 동시 예측
- **DAR 최적화**: AI가 항체 표면의 최적 접합 부위를 예측하여 균일한 DAR 달성
- **ADMET 예측**: ADC의 흡수-분포-대사-배설-독성을 사전 스크리닝 → 독성 프로파일 예측 정확도 향상

### 5.4 PROTAC/Molecular Glue AI 설계

- **E3 리가제 매칭**: AI가 표적 단백질의 표면 특성을 분석하여 최적 E3 리가제-표적 조합 예측
- **협동성(cooperativity) 예측**: ML 모델이 삼원 복합체의 결합 자유에너지를 계산하여 양성 협동성 후보 사전 선별 [5]
- **Molecular Glue 발굴**: AI가 E3 리가제-단백질 접면을 스캔하여 새로운 네오기질/글루 후보 체계적 탐색
- **MolGlueDB**: 2025년 출시된 온라인 molecular glue 데이터베이스 → AI 학습 데이터 체계화

---

## 6. 참고문헌

[1] Matsuda Y, et al. "Advanced Antibody-Drug Conjugates Design: Innovation in Linker Chemistry and Site-Specific Conjugation Technologies." *ChemBioChem*. 2025;e202500305. https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/cbic.202500305

[2] Lei M, et al. "Linker Design for the Antibody Drug Conjugates: A Comprehensive Review." *ChemMedChem*. 2025;e202500262. https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/cmdc.202500262

[3] Anaya J, et al. "Proteolysis-targeting chimeras in cancer therapy: Targeted protein degradation for next-generation treatment." *Cancer*. 2025. https://acsjournals.onlinelibrary.wiley.com/doi/full/10.1002/cncr.70132

[4] Arvinas/Pfizer. "NDA Submission of Vepdegestrant (ARV-471) to U.S. FDA." *J Med Chem*. 2025. https://pubs.acs.org/doi/pdf/10.1021/acs.jmedchem.5c01818

[5] Shen C, et al. "Recent Advances in Targeted Protein Degradation Molecular Glues as Anticancer Drugs." *Clin Exp Pharmacol Physiol*. 2025;70064. https://onlinelibrary.wiley.com/doi/10.1111/1440-1681.70064

[6] Donovan KA, et al. "Mining the CRBN target space redefines rules for molecular glue-induced neosubstrate recognition." *Science*. 2025. https://www.science.org/doi/10.1126/science.adt6736

[7] Modi S, et al. "Trastuzumab deruxtecan versus trastuzumab emtansine in HER2-positive metastatic breast cancer: long-term survival analysis of the DESTINY-Breast03 trial." *Nature Medicine*. 2024. https://www.nature.com/articles/s41591-024-03021-7 / AstraZeneca. "DESTINY-Breast05 results." 2025. https://www.astrazeneca.com/media-centre/press-releases/2025/enhertu-reduced-the-risk-of-disease-recurrence-or-death-by-53-vs-t-dm1-in-patients-with-high-risk-her2-positive-early-breast-cancer.html

[8] Powles T, et al. "Enfortumab vedotin plus pembrolizumab versus chemotherapy in advanced urothelial carcinoma (EV-302/KEYNOTE-A39)." *N Engl J Med*. 2024. NCT04223856.

[9] BiochemPEG. "DAC: Next Evolution of ADC." 2025. https://www.biochempeg.com/article/443.html

[10] Abramson J, et al. "Accurate structure prediction of biomolecular interactions with AlphaFold 3." *Nature*. 2024;630:493-500. https://blog.google/innovation-and-ai/products/google-deepmind-isomorphic-alphafold-3-ai-model/

[11] Fu Z, et al. "Antibody-Drug Conjugates (ADCs): current and future biopharmaceuticals." *J Hematol Oncol*. 2025;18:1704. https://link.springer.com/article/10.1186/s13045-025-01704-3

[12] Liu X, et al. "Antibody-drug conjugates in cancer therapy: current landscape, challenges, and future directions." *Mol Cancer*. 2025;24:2489. https://link.springer.com/article/10.1186/s12943-025-02489-2

[13] Zhou L, et al. "PROTAC Technology as a New Tool for Modern Pharmacotherapy." *Int J Mol Sci*. 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12114078/

[14] BiochemPEG. "PROTAC Degraders in Clinical Trials: 2025 Update." https://www.biochempeg.com/article/434.html

[15] Nature Communications. "A degron-mimicking molecular glue drives CRBN homo-dimerization and degradation." 2025. https://www.nature.com/articles/s41467-025-65094-3

---

> **면책조항**: 본 리뷰는 기술적 분석 목적으로 작성되었으며, 특정 종목의 매수/매도를 권유하지 않습니다. 투자 결정은 전문가 자문을 통해 독립적으로 이루어져야 합니다.
