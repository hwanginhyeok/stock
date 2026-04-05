# 바이오 기술 리뷰 #9: 재생의학 & 조직공학 — 기전, 임상 데이터, 투자 분석

> **Technical Review Series** | 2026-04-05
> 재생의학(Regenerative Medicine)과 조직공학(Tissue Engineering)의 분자적 기전, 핵심 기술 플랫폼,
> 임상 시험 데이터, 시장 전망, 그리고 AI 적용 현황을 학술적 수준에서 종합 분석한다.

---

## 1. 기술 개요: 재생의학의 분자적 기전

재생의학은 손상되거나 퇴행한 조직 및 장기를 세포 수준에서 복원하는 기술 영역이다. 전통적인 의학이 증상 완화와 기능 보존에 집중하는 반면, 재생의학은 조직의 **구조적·기능적 원상 복구(restitutio ad integrum)**를 목표로 한다.

### 1.1 세포 리프로그래밍의 분자적 기반

재생의학의 핵심 패러다임은 Takahashi와 Yamanaka가 2006년 *Cell*에 보고한 유도만능줄기세포(induced pluripotent stem cell, iPSC) 기술이다[1]. 네 개의 전사인자 — **Oct4 (POU5F1), Sox2, Klf4, c-Myc** (OSKM 인자) — 를 체세포에 도입하면, 후성유전적 리모델링을 거쳐 배아줄기세포(ESC)와 유사한 만능성(pluripotency)을 획득한다.

#### OSKM 인자의 분자적 역할

- **Oct4 (POU5F1)**: POU 도메인 전사인자로, 만능성 유전자 네트워크의 마스터 레귤레이터. Oct4는 Sox2와 협력하여 *Nanog*, *Fgf4* 등 만능성 유전자의 sox-oct 복합 모티프에 결합한다. 자가조절 양성 피드백 루프를 형성하여 만능성 상태를 강화하며[2], 발현 수준이 리프로그래밍 효율에 결정적이다. 과발현 시 내배엽/중배엽 분화가 유도되고, 저발현 시 영양외배엽으로 분화한다.

- **Sox2**: HMG-box 전사인자로, Oct4와 이종이합체(heterodimer)를 형성하여 만능성 인핸서에 결합한다. Sox2는 Oct4의 안정적 발현을 유지하는 데 필수적이며, 신경외배엽 분화에서도 핵심 역할을 수행한다.

- **Klf4**: Kruppel-like 인자 계열로, Oct4 및 Sox2와 직접 상호작용하여 리프로그래밍을 촉진한다[3]. p21 활성화를 통해 세포주기 정지를 유도하며, 이는 리프로그래밍 초기의 mesenchymal-to-epithelial transition (MET)에 기여한다. E-cadherin 발현을 활성화하여 상피성 형태로의 전환을 유도한다.

- **c-Myc**: 원종양유전자(proto-oncogene)로, 리프로그래밍 초기에 활성 크로마틴 환경을 조성한다. 전사 개시에서 신장(elongation)으로의 전환을 촉진하며[1], 히스톤 아세틸트랜스퍼라제를 동원하여 크로마틴 접근성을 증가시킨다. 그러나 c-Myc의 종양유전자적 특성 때문에 종양 발생 위험이 존재하며, 이를 대체하는 소분자(small molecule) 전략이 활발히 연구되고 있다.

#### 리프로그래밍의 확률론적 모델

iPSC 리프로그래밍은 본질적으로 **확률론적(stochastic)이고 비효율적**인 과정이다. OSKM 발현 세포 중 극히 일부만이 형태학적·전사체적·후성유전적 변화를 모두 통과하여 진정한 iPSC가 된다[4]. 리프로그래밍 효율은 일반적으로 0.01-1% 수준이며, 이를 개선하기 위한 소분자 칵테일(VPA, CHIR99021, RepSox 등)이 개발되고 있다.

### 1.2 세포외기질 기반 조직공학

탈세포화(decellularization) 스캐폴드는 원래 조직의 세포를 제거하고 세포외기질(ECM) 구조와 생화학적 신호를 보존하는 접근법이다. SDS, Triton X-100 등 계면활성제 기반 프로토콜과 효소적(트립신, DNase/RNase) 프로토콜이 사용된다.

탈세포화 ECM(dECM) 스캐폴드는 네이티브 조직 구조와 성장인자를 보존하면서 면역 반응을 최소화하는 생체모방 템플릿을 생성한다[5]. 피부 및 혈관 이식재와 같은 단순 구조물은 이미 임상적 성공을 거두었으나, 전체 장기 수준의 복합 이식은 여전히 도전 과제이다.

### 1.3 엑소좀 생합성: MVB 경로

엑소좀(exosome)은 세포가 분비하는 30-150nm 크기의 나노소포체로, **다소포체(multivesicular body, MVB)** 경로를 통해 생성된다[6]. MVB는 후기 엔도솜(late endosome)의 한 형태로, 내강내 소포(intraluminal vesicle, ILV)를 포함한다.

#### ESCRT 의존적 경로

ILV 형성의 전형적 기전은 **ESCRT(Endosomal Sorting Complex Required for Transport)** 복합체에 의해 매개된다:

1. **ESCRT-0** (HRS/STAM 복합체): 유비퀴틴화된 화물 단백질(cargo)을 엔도솜 막에 클러스터링
2. **ESCRT-I** (TSG101, VPS28, VPS37, MVB12): ESCRT-0으로부터 화물을 인수하고, 막 변형 개시
3. **ESCRT-II** (EAP20, EAP30, EAP45): ESCRT-I과 협력하여 막을 내강 방향으로 출아(budding). ESCRT-I과 ESCRT-II의 조합만으로도 화물이 격리된 막 돌출(bud)을 형성할 수 있다[7]
4. **ESCRT-III** (CHMP2, CHMP3, CHMP4, CHMP6): 출아 경부(neck)에 위치하여 막 절단(scission) 수행
5. **VPS4 ATPase**: ESCRT-III 복합체를 분해하여 재활용

이렇게 형성된 ILV를 포함한 MVB가 원형질막과 융합하면, ILV가 세포외 공간으로 방출되어 엑소좀이 된다.

#### ESCRT 비의존적 경로

세라마이드(ceramide)/스핑고미엘리나제 경로, 테트라스파닌(CD9, CD63, CD81) 의존적 경로, 그리고 syntenin-ALIX 경로가 존재한다[8]. ARF6과 PLD2는 syntenin-ALIX 엑소좀 생합성과 MVB로의 출아를 조절한다.

---

## 2. 핵심 기술 세부

### 2.1 iPSC 리프로그래밍 기술

#### 현재 리프로그래밍 전략

| 전략 | 효율 | 안전성 | 임상 적용성 |
|------|------|--------|------------|
| 레트로바이러스 OSKM | 0.01-0.1% | 낮음 (게놈 삽입) | 연구용 |
| 센다이바이러스 | 0.1-1% | 중간 (비삽입) | GMP 생산 가능 |
| mRNA 형질주입 | 1-4% | 높음 (비삽입) | FDA 선호 |
| 소분자 화학적 리프로그래밍 | 0.1-0.5% | 높음 | 차세대 전략 |
| Episomal 벡터 | 0.01-0.1% | 높음 (비삽입) | GMP 표준 |

OSKM 인자의 화학량론적 비율은 효율에 결정적이다. Carey 등은 Oct4 고발현, Sox2/Klf4 중간 발현, c-Myc 저발현의 조합이 최적임을 보고하였다[9].

#### iPSC 유래 세포 치료 임상 현황

- **RIKEN (일본)**: iPSC 유래 망막색소상피(RPE) 세포를 이용한 가령황반변성 치료 — 세계 최초 iPSC 임상 시험 (2014)
- **Heartseed (일본)**: iPSC 유래 심근세포를 이용한 심부전 치료 — Phase 1/2 (NCT04945018)
- **Cynata Therapeutics**: iPSC 유래 MSC (Cymerus) — GvHD Phase 3 진행 중

### 2.2 탈세포화 프로토콜

탈세포화의 핵심 과제는 **세포 완전 제거**와 **ECM 보존** 사이의 균형이다.

#### 주요 탈세포화 프로토콜 비교

| 방법 | 메커니즘 | ECM 보존도 | DNA 잔류 | 적용 조직 |
|------|---------|-----------|---------|----------|
| SDS (0.1-1%) | 이온성 계면활성제 | 중간 | 낮음 | 심장, 폐, 간 |
| Triton X-100 | 비이온성 계면활성제 | 높음 | 중간 | 혈관, 연골 |
| 동결-해동 사이클 | 물리적 세포 파괴 | 높음 | 높음 | 근육, 건 |
| 효소적 (트립신) | 단백분해 | 낮음 | 낮음 | 보조 처리 |
| 초임계 CO₂ | 용매 추출 | 높음 | 낮음 | 연구 단계 |

FDA 승인 dECM 제품: AlloDerm (피부, LifeCell), Surgisis (소장점막하, Cook Medical), CorMatrix (심장 ECM) 등이 상용화되어 있다.

임상에서 탈세포화된 인간 대동맥을 기관(trachea) 대체물로 사용한 사례가 보고되었으며, 이식된 대동맥 이식재의 내면에 섬모세포, 외면에 연골이 성장하는 것이 확인되었다[5].

### 2.3 바이오잉크 레올로지

3D 바이오프린팅의 성패는 바이오잉크의 유변학적(rheological) 특성에 좌우된다.

#### GelMA (Gelatin Methacryloyl) 바이오잉크

GelMA는 젤라틴에 메타크릴로일기를 도입한 광가교성 하이드로겔로, 생체적합성, 세포 부착성(RGD 모티프 보존), 그리고 조절 가능한 기계적 물성을 겸비한다[10].

**핵심 레올로지 파라미터:**
- **점도(Viscosity)**: 최적 바이오프린팅 점도 범위 100-1,000 Pa·s
- **전단 박화(Shear thinning)**: 전단 속도 증가 시 점도 감소 — 노즐 통과 시 유동성 확보, 압출 후 형상 유지
- **항복 응력(Yield stress)**: 중력에 의한 변형 없이 형태를 유지하는 임계값
- **탄성 복원(Elastic recovery)**: 전단 제거 후 겔 상태로 빠른 복귀

GelMA의 메타크릴화 치환도(degree of substitution, DS)에 따라 가교 밀도와 기계적 강도가 조절된다. DS 60-80%가 인쇄 적성과 세포 생존율의 최적 균형을 제공한다.

**복합 바이오잉크 전략**: 순수 GelMA의 한계(과도한 점도 시 노즐 막힘, 낮은 점도 시 구조 붕괴)를 극복하기 위해 알기네이트(alginate), 히알루론산(HA), 메틸셀룰로스(MC) 등과의 블렌딩 전략이 활발히 연구되고 있다[10].

#### FRESH 바이오프린팅

Carnegie Mellon 대학의 Feinberg 연구팀이 개발한 **FRESH(Freeform Reversible Embedding of Suspended Hydrogels)** 기술은 500 kPa 미만의 탄성 계수를 가진 연성 하이드로겔의 정밀 인쇄를 가능하게 한다[11]. 젤라틴 미세입자로 구성된 지지 배스(support bath) 내에서 인쇄 후, 37도C 가열로 지지체를 녹여 구조물을 회수한다. 이 기술로 배아 심장 및 뇌의 복잡한 내·외부 구조를 인쇄하는 데 성공하였으며, 최근에는 혈관화된 조직 인쇄로 확장되었다.

### 2.4 엑소좀 치료제 엔지니어링

엑소좀은 약물/유전자 전달체로서 **면역원성이 낮고 혈뇌장벽(BBB)을 통과**할 수 있다는 점에서 리포좀 및 합성 나노입자 대비 우위를 가진다.

#### 엔지니어링 전략

| 전략 | 방법 | 목적 |
|------|------|------|
| 표면 디스플레이 | Lamp2b-RVG 융합 | 뇌 표적 전달 |
| 화물 로딩 | 전기천공, 소닉케이션 | siRNA, mRNA 전달 |
| 생산 세포 최적화 | HEK293T 과발현 시스템 | 수율 향상 |
| 화학적 표면 변형 | PEG, 항체 접합 | 반감기 연장, 표적화 |

---

## 3. 임상 데이터

### 3.1 줄기세포 치료: Mesoblast Remestemcel-L

Mesoblast의 remestemcel-L (Ryoncil)은 FDA 승인을 받은 최초의 동종 MSC 세포 치료제이다(2024년 12월).

**Phase 3 임상 시험 (NCT02336230)**[12]:
- **대상**: 스테로이드 불응성 급성 이식편대숙주병(SR-aGvHD) 소아 환자 54명
- **투여**: 2 x 10⁶ cells/kg, 주 2회, 4주간
- **1차 평가변수**: Day 28 전체 반응률(OR) = **70.4%** vs 사전 설정 대조값 45% (P = 0.0003)
- **완전 반응률**: Day 28 29.6% → Day 100 44.4%로 증가
- **생존율**: Day 100 **74.1%**, Day 180 **68.5%**
- **반응자 vs 비반응자 생존율**: Day 100 86.8% vs 47.1% (P = 0.0001)
- **안전성**: 주입 관련 독성 미확인, 주요 이상 반응은 감염, 발열, 출혈

### 3.2 3D 바이오프린팅 전임상 진전

- **Organovo**: 바이오프린팅 간 조직(exVive3D)을 이용한 NASH 모델 — 약물 독성 스크리닝에서 기존 2D 배양 대비 예측력 10배 향상
- **Aspect Biosystems**: 바이오프린팅 췌장 조직을 이용한 1형 당뇨 치료 — 전임상 단계에서 인슐린 분비 기능 확인
- **Fraunhofer Institute**: EUR 4,000만 투자로 GMP급 바이오프린팅 센터 개소(2025년) — 임상용 조직 생산 인프라 구축

### 3.3 엑소좀 치료제

| 기업 | 파이프라인 | 단계 | 핵심 데이터 |
|------|-----------|------|------------|
| Evox Therapeutics | ATXN2 표적 CNS (SCA2/ALS) | CTA-enabling (2026) | Eli Lilly 협력, BBB 통과 확인[13] |
| Coya Therapeutics | COYA 302 (ALS) | Phase 2 | 조절 T세포 유래 엑소좀 |
| ExoCoBio | ASCE+ (피부 재생) | Phase 2 | 아토피 피부염 개선 |
| PrimeGen US | 세포/엑소좀 복합 치료 | 전임상 | $1.5B SPAC 합병 (2026.02) |

### 3.4 iPSC 유래 임상

- **Heartseed (HS-001)**: iPSC 유래 심근구(cardiac spheroid) — Phase 1/2에서 심부전 환자의 좌심실 박출률 개선 확인 (일본 PMDA)
- **Cynata (CYP-001)**: iPSC-MSC — SR-aGvHD Phase 3 진행 중, Phase 2에서 CR 50% 달성

---

## 4. 시장 분석

### 4.1 시장 규모 및 성장률

| 세그먼트 | 2024-2025 | 2030 | 2035 | CAGR |
|---------|-----------|------|------|------|
| 조직공학 전체 | $19.7B | — | $56.7B | 10.1% |
| 재생의학 전체 | $9.8B (2025) | — | $22.1B | 8.4% |
| 3D 바이오프린팅 | $2.2-4.6B | — | $23.1B | 12.7-17.7% |
| 엑소좀 | $710M | $2.2B | — | 25.5% |
| 조직 재생 기술 | $17.9B | — | $73.5B | 15.2% |

**총 TAM (2035 기준)**: $70-150B 이상. 장기 이식 대기자 문제 해결 시 상한선은 사실상 무한.

### 4.2 경쟁 환경

**Tier 1: 상용 제품 보유**
- Integra LifeSciences — dECM 피부/신경 이식재
- Organogenesis — 피부 대체물 (Apligraf, Dermagraft)
- Smith & Nephew — 조직 재생 매트릭스
- Mesoblast (MESO) — Ryoncil FDA 승인 (2024)

**Tier 2: 파이프라인 리더**
- CELLINK/BICO — 바이오잉크 + 자동 바이오프린터 플랫폼
- Evox Therapeutics — 엔지니어드 엑소좀
- Aspect Biosystems — 바이오프린팅 세포 치료
- CollPlant (CLGN) — 식물 유래 rhCollagen

**Tier 3: 플랫폼/인프라**
- Thermo Fisher (TMO) — 줄기세포 배양 미디어, 시약
- Lonza — 세포 치료 CDMO
- Fujifilm — iPSC 대량 생산

### 4.3 핵심 리스크 요인

1. **규제 불확실성**: 복합 생물학적 제품(combination product)의 FDA 분류 모호
2. **대량 생산(scale-up)**: iPSC/엑소좀의 GMP 대량 생산 비용 고가
3. **장기 안전성**: iPSC 유래 세포의 종양 형성 위험 (c-Myc)
4. **상업화 시간**: 대부분 전임상~초기 임상 단계, 5-10년 시계

---

## 5. AI 적용

### 5.1 바이오프린팅 최적화

- **인쇄 파라미터 실시간 조정**: 컴퓨터 비전 + ML 모델이 인쇄 중 온도, 속도, 압력을 실시간 조정하여 세포 생존율 최적화
- **결함 감지**: CNN 기반 이미지 분석으로 인쇄 결함을 실시간 식별하고 보정
- **바이오잉크 설계**: GAN/VAE 생성 모델로 새로운 바이오잉크 조성을 in silico 예측 — 기계적 강도와 생체적합성의 파레토 최적 탐색

### 5.2 엑소좀 엔지니어링

- **표면 단백질 최적화**: 딥러닝으로 표적 조직 도달률을 극대화하는 표면 리간드 조합 탐색
- **화물 로딩 예측**: ML 모델이 RNA/단백질 화물의 엑소좀 내 봉입 효율 예측
- **배치 품질 관리**: 나노입자 추적 분석(NTA) 데이터의 AI 해석으로 배치 간 일관성 보장

### 5.3 조직 성숙 시뮬레이션

- **디지털 트윈**: 바이오프린팅된 조직의 성숙 과정을 물리 기반 시뮬레이션 + ML 서로게이트 모델로 예측
- **성장인자 방출 최적화**: 강화학습으로 스캐폴드 내 성장인자 방출 프로파일 최적화

### 5.4 iPSC 품질 관리

- **형태 기반 스크리닝**: 현미경 이미지의 딥러닝 분석으로 iPSC 콜로니 품질 자동 평가. 정상 iPSC 콜로니의 compact 경계, 높은 핵/세포질 비율 등 형태학적 특성을 CNN이 정량화하여 분화 시작 또는 품질 저하를 조기 감지
- **게놈 안정성 예측**: 전사체/후성유전체 데이터를 통합한 ML 모델로 분화 잠재력과 종양 위험 예측. 특히 iPSC 장기 배양 시 발생하는 chr1q, chr20q11.21 gain 등 반복적 CNV 패턴을 조기 탐지
- **분화 프로토콜 최적화**: 성장인자/소분자의 농도, 투여 시점, 기간의 다차원 공간에서 베이지안 최적화를 통해 목표 세포 수율 극대화

### 5.5 엑소좀 생산 공정 AI 최적화

- **배양 조건 최적화**: 세포 컨플루언시, 배지 조성, 저산소 조건 등의 파라미터를 ML로 최적화하여 엑소좀 수율(particles/cell) 극대화
- **순도 예측**: NTA(Nanoparticle Tracking Analysis), ExoView, 단일 소포 분석 데이터의 AI 해석으로 배치 순도와 크기 분포를 실시간 모니터링
- **표적 전달 시뮬레이션**: 분자 동역학 + ML 서로게이트 모델로 엔지니어드 엑소좀의 체내 분포와 표적 조직 축적을 in silico 예측

---

## 6. 투자 시사점

### 6.1 핵심 투자 테제

1. **장기 부족은 구조적 문제**: 미국에서만 연간 100,000명 이상이 장기 이식 대기, 전 세계적으로는 연간 200만 건 이상의 미충족 수요 — 성공 시 TAM 무한
2. **엑소좀이 가장 빠른 상업화 경로**: 진단(cfDNA 기반 액체생검) 시장은 이미 형성, 치료제는 2026-2028 첫 승인 예상. 2025년 초 $50M+ 투자 라운드 다수 체결로 투자자 신뢰 상승
3. **MSC 세포 치료는 PoC 완료**: Ryoncil FDA 승인(2024.12)으로 동종 MSC 치료의 상업적 검증 시작. SR-aGvHD에서 70.4% 반응률은 기존 표준 치료 대비 명확한 우위
4. **3D 바이오프린팅은 연구 도구 단계**: 상업적 장기/조직 제품은 5-10년 후, 현재는 바이오잉크/장비 인프라 투자가 합리적. GMP급 바이오프린팅 센터(Fraunhofer EUR 4,000만)가 임상 전환의 병목 해소에 기여
5. **이종장기(축 4)가 재생의학보다 먼저 올 수 있음**: 돼지 신장 임상 시험 진행 중 — 재생의학과의 타임라인 경쟁. 두 기술은 대체적이 아닌 보완적 관계

### 6.2 기술 성숙도 평가 (TRL 기반)

| 기술 | TRL | 상태 | 상업화 예상 |
|------|-----|------|------------|
| dECM 피부/연골 이식재 | 9 | FDA 승인, 상용 | 현재 |
| MSC 세포 치료 (GvHD) | 9 | FDA 승인 (Ryoncil) | 현재 |
| 엑소좀 진단 | 7-8 | 후기 임상 / 초기 상용 | 2025-2027 |
| 엑소좀 치료제 | 4-5 | 전임상-Phase 1 | 2028-2030 |
| iPSC 유래 세포 치료 | 5-6 | Phase 1-2 | 2027-2030 |
| 3D 바이오프린팅 조직 | 3-4 | 전임상 | 2030-2035 |
| 바이오프린팅 장기 | 2-3 | 연구 | 2035+ |

### 6.3 투자 전략 매트릭스

| 시계 | 전략 | 대표 종목 |
|------|------|----------|
| 단기 (1-3년) | 상용 제품 보유 기업 | Mesoblast (MESO), Integra (IART) |
| 중기 (3-5년) | 엑소좀 + 플랫폼 | BICO, CollPlant (CLGN) |
| 장기 (5-10년) | iPSC + 바이오프린팅 | Organovo, Aspect Biosystems |
| 인프라 | 삽과 곡괭이 | Thermo Fisher (TMO), Lonza |

### 6.4 모니터링 이벤트

| 시기 | 이벤트 | 영향 |
|------|--------|------|
| 2026 H1 | Evox Therapeutics CTA-enabling 연구 완료 | 엑소좀 치료제 임상 진입 첫 사례 |
| 2026-2027 | Heartseed HS-001 Phase 1/2 데이터 | iPSC 심근세포 치료 PoC |
| 2027 | Cynata CYP-001 Phase 3 결과 | iPSC-MSC 대규모 임상 검증 |
| 2025-2027 | Fraunhofer GMP 바이오프린팅 센터 가동 | 바이오프린팅 임상 물질 생산 인프라 |
| 연속 | PrimeGen SPAC 합병 후 파이프라인 | 엑소좀 + 세포 복합 치료 경로 |

---

## 참고문헌

[1] Takahashi K, Yamanaka S. "Induction of Pluripotent Stem Cells from Mouse Embryonic and Adult Fibroblast Cultures by Defined Factors." *Cell*. 2006;126(4):663-676. doi:10.1016/j.cell.2006.07.024. https://pubmed.ncbi.nlm.nih.gov/16904174/

[2] Shi G, Jin Y. "The roles of the reprogramming factors Oct4, Sox2 and Klf4 in resetting the somatic cell epigenome during induced pluripotent stem cell generation." *Genome Biology*. 2012;13(10):251. doi:10.1186/gb-2012-13-10-251. https://pmc.ncbi.nlm.nih.gov/articles/PMC3491406/

[3] Wei Z, et al. "Klf4 Interacts Directly with Oct4 and Sox2 to Promote Reprogramming." *Stem Cells*. 2009;27(12):2969-2978. doi:10.1002/stem.231. https://stemcellsjournals.onlinelibrary.wiley.com/doi/pdf/10.1002/stem.231

[4] Carey BW, et al. "Stoichiometric and temporal requirements of Oct4, Sox2, Klf4, and c-Myc expression for efficient human iPSC induction and differentiation." *PNAS*. 2011;108(47):18876-18881. doi:10.1073/pnas.0904825106. https://www.pnas.org/doi/10.1073/pnas.0904825106

[5] Liu Y, et al. "Bioactive scaffolds for tissue engineering: A review of decellularized extracellular matrix applications and innovations." *Exploration*. 2025. doi:10.1002/EXP.20230078. https://pmc.ncbi.nlm.nih.gov/articles/PMC11875452/

[6] Xu M, et al. "Exosome biogenesis: machinery, regulation, and therapeutic implications in cancer." *Molecular Cancer*. 2022;21:207. doi:10.1186/s12943-022-01671-0. https://link.springer.com/article/10.1186/s12943-022-01671-0

[7] Wollert T, Hurley JH. "Molecular mechanism of multivesicular body biogenesis by ESCRT complexes." *Nature*. 2010;464:864-869. doi:10.1038/nature08849. https://www.nature.com/articles/nature08849

[8] Ghossoub R, et al. "Syntenin-ALIX exosome biogenesis and budding into multivesicular bodies are controlled by ARF6 and PLD2." *Nature Communications*. 2014;5:3477. doi:10.1038/ncomms4477. https://www.nature.com/articles/ncomms4477

[9] Raab S, et al. "Application of the Yamanaka Transcription Factors Oct4, Sox2, Klf4, and c-Myc from the Laboratory to the Clinic." *Genes*. 2023;14(9):1697. doi:10.3390/genes14091697. https://pmc.ncbi.nlm.nih.gov/articles/PMC10531188/

[10] Pal A, et al. "An insight into synthesis, properties and applications of gelatin methacryloyl hydrogel for 3D bioprinting." *Materials Advances*. 2023. doi:10.1039/D3MA00715D. https://pubs.rsc.org/en/content/articlehtml/2023/ma/d3ma00715d

[11] Hinton TJ, et al. "Three-dimensional printing of complex biological structures by freeform reversible embedding of suspended hydrogels." *Science Advances*. 2015;1(9):e1500758. doi:10.1126/sciadv.1500758. https://www.science.org/doi/10.1126/sciadv.1500758

[12] Kurtzberg J, et al. "A Phase 3, Single-Arm, Prospective Study of Remestemcel-L for the Treatment of Pediatric Patients Who Failed to Respond to Steroid Treatment for Acute Graft-versus-Host Disease." *Biology of Blood and Marrow Transplantation*. 2020;26(5):845-854. doi:10.1016/j.bbmt.2020.01.018. https://pubmed.ncbi.nlm.nih.gov/32018062/

[13] Evox Therapeutics. "DeliverEX Exosome Therapeutics Platform — Exosome-Mediated Delivery of Genetic Medicines." 2023. https://www.evoxtherapeutics.com/technology/science/

[14] Colombo M, et al. "Biogenesis, Secretion, and Intercellular Interactions of Exosomes and Other Extracellular Vesicles." *Annual Review of Cell and Developmental Biology*. 2014;30:255-289. https://www.gene-quantification.de/colombo-et-al-exosome-biogenesis-2014.pdf

---

*본 리뷰는 투자 권유가 아닌 기술 분석 목적으로 작성되었습니다. 투자 결정은 개인의 판단과 책임 하에 이루어져야 합니다.*
