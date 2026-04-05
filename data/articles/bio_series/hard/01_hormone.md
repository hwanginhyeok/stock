# 바이오 기술 리뷰 #1: 호르몬 흉내 (Hormone Mimicry) — 기전, 임상 데이터, 투자 분석

> **Review Article** | 2026-04-05
> 키워드: GLP-1, GIP, amylin, incretin, semaglutide, tirzepatide, orforglipron, 비만약, 대사질환

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

### 1.1 인크레틴 시스템의 분자생물학적 기반

인크레틴(incretin) 호르몬은 식후 장내분비세포(enteroendocrine cells)에서 분비되는 펩타이드 호르몬으로, 포도당 의존적(glucose-dependent) 인슐린 분비 촉진이라는 독특한 약리학적 특성을 보유한다. 핵심 인크레틴 호르몬은 두 가지다:

- **GLP-1 (Glucagon-Like Peptide-1)**: 소장 원위부 L세포에서 프로글루카곤(proglucagon) 유전자의 조직 특이적 번역 후 가공(post-translational processing)을 통해 생성된다. 프로호르몬 전환효소 1/3(PC1/3)이 프로글루카곤을 절단하여 GLP-1(7-36)amide와 GLP-1(7-37) 활성형을 생산한다.
- **GIP (Glucose-dependent Insulinotropic Polypeptide)**: 십이지장 및 공장 상부 K세포에서 분비되는 42개 아미노산 펩타이드로, 인슐린 분비 촉진 외에 지방 조직 대사 조절에도 관여한다.

두 호르몬 모두 dipeptidyl peptidase-4(DPP-4)에 의해 수분 내 급속 분해(반감기 ~2분)되므로, 치료제 개발의 핵심 과제는 **DPP-4 내성 확보**와 **알부민 결합을 통한 반감기 연장**이다.

### 1.2 인크레틴 효과의 감소(Incretin Effect Deficiency)

건강한 성인에서 경구 포도당 섭취 시 인슐린 분비량은 동일 혈당을 유발하는 정맥 포도당 투여 시보다 약 50-70% 높다. 이 차이가 인크레틴 효과(incretin effect)이며, 2형 당뇨 환자에서는 이 효과가 현저히 감소해 있다. GLP-1 수용체 작용제(GLP-1RA)는 이 결핍을 약리학적으로 보충하는 전략이다.

### 1.3 호르몬 흉내 약물의 분류 체계

| 세대 | 메커니즘 | 대표 약물 | 투여 경로 |
|------|----------|----------|----------|
| 1세대 | GLP-1R 단독 작용 | Exenatide, Liraglutide | 주사 |
| 2세대 | GLP-1R 장시간 작용 | Semaglutide (Ozempic/Wegovy) | 주사/경구 |
| 3세대 | GLP-1R + GIPR 이중작용 | Tirzepatide (Mounjaro/Zepbound) | 주사 |
| 4세대 | GLP-1R + Amylin 이중작용 | Amycretin, CagriSema | 주사/경구 |
| 5세대 | 소분자 비펩타이드 | Orforglipron (Foundayo) | 경구 |
| 차세대 | Triple agonist (GLP-1/GIP/Glucagon) | Retatrutide | 주사 |

---

## 2. 핵심 기술 세부

### 2.1 GLP-1 수용체 신호전달 캐스케이드

GLP-1 수용체(GLP-1R)는 Class B1 G단백질결합수용체(GPCR) superfamily에 속하는 7회 막관통 수용체로, 463개 아미노산으로 구성된다 [1, 2].

#### 2.1.1 Gs-cAMP-PKA 축 (Canonical Pathway)

1. **리간드 결합**: GLP-1(7-36)amide가 GLP-1R의 N-말단 세포외 도메인(ECD)과 막관통 도메인(TMD) 사이 결합 포켓에 결합
2. **Gs 단백질 활성화**: 수용체 구조 변환 → Gsα 서브유닛이 GDP를 GTP로 교환
3. **아데닐산 시클라제(AC) 활성화**: Gsα-GTP가 AC를 자극 → ATP에서 cAMP 생성
4. **PKA 활성화**: cAMP가 PKA의 조절 서브유닛(RIIβ)에 결합 → 촉매 서브유닛(Cα) 해리 및 활성화
5. **CREB 인산화**: 활성 PKA가 핵 내 CREB(cAMP Response Element-Binding protein) 전사인자를 Ser133에서 인산화 → 인슐린 유전자(INS) 전사 촉진
6. **KATP 채널 폐쇄**: PKA가 SUR1/Kir6.2 복합체를 인산화 → K+ 유출 감소 → 막 탈분극
7. **Ca2+ 유입**: 전압 의존성 L-형 Ca2+ 채널(VDCC) 개방 → 세포내 Ca2+ 농도 상승
8. **인슐린 과립 분비**: Ca2+ 의존적 SNARE 복합체(syntaxin-1A, SNAP-25, VAMP2) 매개 과립 세포외유출(exocytosis)

#### 2.1.2 Epac2-Rap1 축 (Non-canonical Pathway)

cAMP는 PKA 외에도 Epac2(Exchange protein directly activated by cAMP 2)를 활성화한다:

1. **Epac2 활성화**: cAMP가 Epac2의 CNB(cyclic nucleotide-binding) 도메인에 결합 → 자가억제 해제
2. **Rap1 GTPase 활성화**: Epac2가 Rap1의 GDP→GTP 교환 촉진(GEF 활성)
3. **PLC-ε 활성화**: Rap1-GTP가 PLCε를 활성화 → PIP2 → IP3 + DAG
4. **ER Ca2+ 방출**: IP3가 소포체(ER) IP3 수용체에 결합 → Ca2+ 저장소 방출
5. **과립 프라이밍**: 분비 과립의 도킹(docking) 및 프라이밍(priming) 촉진 → 분비 가능 과립 풀(readily releasable pool) 확대

이 이중 경로(PKA + Epac2)의 동시 활성화가 GLP-1의 강력하고 포도당 의존적인 인슐린 분비 촉진 효과의 분자적 기반이다 [1].

#### 2.1.3 β-arrestin 및 수용체 내재화

GLP-1R 활성화 후 G단백질 결합 수용체 키나제(GRK)가 수용체의 C-말단 꼬리를 인산화하면, β-arrestin-1/2가 모집되어:
- 수용체를 clathrin-coated pit으로 유도하여 내재화(internalization)
- 엔도솜 내에서도 지속적 신호전달(sustained signaling) 가능
- MEK/ERK1/2 경로 활성화 → 베타세포 증식 및 항아포토시스

이 β-arrestin 매개 신호전달의 편향성(biased agonism)은 차세대 GLP-1RA 설계에서 핵심적 고려사항이다. 일부 약물은 G단백질 편향적(G-protein biased)으로 설계하여 내재화를 최소화하고 지속적 신호전달을 극대화하는 전략을 취한다 [2].

### 2.2 GIP 수용체 크로스토크

GIP 수용체(GIPR)도 Class B1 GPCR이며, GLP-1R과 유사한 Gs-cAMP 경로를 활성화하지만 하위 신호전달에서 중요한 차이를 보인다 [3]:

#### 2.2.1 GLP-1R과 GIPR의 신호전달 분기점

| 특성 | GLP-1R | GIPR |
|------|--------|------|
| 주요 G단백질 | Gs (높은 효율) | Gs (중간 효율) |
| β-arrestin 모집 | 강함 → 빠른 탈감작 | 약함 → 느린 탈감작 |
| 수용체 재순환 | 느림 (리소좀 분해 우세) | 빠름 (세포막 재순환) |
| cAMP 동역학 | 급격한 상승-하강 | 지속적 저수준 상승 |
| ERK 활성화 | β-arrestin 의존적 | G단백질 의존적 |

#### 2.2.2 이중작용의 시너지 메커니즘 (Tirzepatide)

Tirzepatide는 39개 아미노산 펩타이드로, GIP 서열 기반에 GLP-1R 활성을 부여하는 변형을 가한 구조다:

1. **GIPR에 대한 동등 친화도**: 네이티브 GIP와 동등한 GIPR 결합력
2. **GLP-1R에 대한 약 5배 낮은 친화도**: 네이티브 GLP-1 대비 GLP-1R에 대한 친화도는 낮지만, 이 불균형이 임상적으로 유리한 효능 프로파일을 생성
3. **C20 지방산 사슬**: Lys20에 부착된 C20 이산(diacid) 지방산이 알부민에 결합하여 반감기를 ~5일로 연장
4. **Aib (α-aminoisobutyric acid) 치환**: 2번 위치 Aib가 DPP-4 절단 내성 부여

GIPR과 GLP-1R의 동시 활성화는 β세포에서 additive가 아닌 **synergistic** cAMP 증가를 유발하며, 이는 두 수용체의 세포 내 미세구획화(microcompartmentalization) 차이에 기인한다 [3]. GIPR은 GLP-1R과 다른 엔도솜 구획에서 신호를 전달하여, 세포 내 cAMP의 시공간적(spatiotemporal) 프로파일을 다각화한다.

### 2.3 Amylin 신호전달과 POMC 경로

Amylin(Islet Amyloid Polypeptide, IAPP)은 37개 아미노산 펩타이드로, 췌장 β세포에서 인슐린과 1:100 비율로 공동 분비된다 [4].

#### 2.3.1 Amylin 수용체 복합체

Amylin은 단독 수용체가 아닌 **수용체 활성 변형 단백질(RAMP)**과의 복합체를 통해 신호를 전달한다:

- **AMY1 수용체**: CTR(Calcitonin Receptor) + RAMP1
- **AMY2 수용체**: CTR + RAMP2
- **AMY3 수용체**: CTR + RAMP3

이 복합체들은 모두 Gs-cAMP 경로를 활성화하지만, RAMP 서브타입에 따라 조직 분포와 리간드 선택성이 달라진다.

#### 2.3.2 시상하부 POMC 뉴런 경로

Amylin의 체중 감소 효과는 주로 **뇌간 area postrema(AP)** 및 **시상하부 궁상핵(arcuate nucleus)**에서의 신호전달에 의해 매개된다:

1. **Area Postrema 활성화**: 혈액-뇌 장벽(BBB)이 없는 AP의 AMY 수용체 활성화
2. **NTS(Nucleus Tractus Solitarius) 중계**: AP에서 NTS로 glutamatergic 신호 전달
3. **POMC 뉴런 활성화**: 궁상핵의 POMC(Pro-opiomelanocortin) 뉴런 탈분극 → cFos 발현 증가
4. **α-MSH 방출**: POMC가 PC1/3, PC2에 의해 절단되어 α-melanocyte-stimulating hormone(α-MSH) 생성
5. **MC4R 활성화**: α-MSH가 시상하부 실방핵(PVN) 및 외측 시상하부의 MC4R(Melanocortin-4 Receptor) 활성화
6. **식욕 억제**: MC4R-Gs-cAMP 신호가 BDNF, TRH 등 포만 신호를 상향조절
7. **NPY/AgRP 억제**: 동시에 궁상핵의 NPY/AgRP(식욕 촉진) 뉴런을 GABA성으로 억제

GLP-1과 amylin의 체중 감소 시너지는, 두 호르몬이 **서로 다른 뇌 영역의 상보적 식욕 조절 회로**를 활성화하기 때문이다. GLP-1은 주로 NTS의 GLP-1R+ 뉴런과 시상하부를 직접 활성화하는 반면, amylin은 AP를 경유하여 POMC 경로를 간접 활성화한다.

#### 2.3.3 Cagrilintide와 Amycretin

- **Cagrilintide**: 네이티브 amylin 유사체. 아실화(acylation)를 통해 반감기를 수일로 연장. AMY1/AMY3 수용체에 대한 선택적 작용.
- **Amycretin**: 단일 분자에 GLP-1R 작용과 AMY 수용체 작용을 통합한 최초의 이중작용 펩타이드. GLP-1, amylin, calcitonin 수용체 모두를 활성화한다 [4].

### 2.4 소분자 GLP-1RA의 구조약리학

#### 2.4.1 Orforglipron의 혁신

Orforglipron(상품명 Foundayo)은 비펩타이드(non-peptide) 소분자 GLP-1RA로, 2026년 4월 FDA 승인을 획득했다 [5]. 기존 펩타이드 GLP-1RA와의 근본적 차이:

| 특성 | 펩타이드 GLP-1RA | Orforglipron |
|------|-----------------|-------------|
| 분자량 | ~4,000-5,000 Da | <500 Da |
| 투여 경로 | 주사/경구(특수 제형) | 경구(일반 정제) |
| 식사/물 제한 | Rybelsus: 공복, 물 120mL 이하 | **제한 없음** |
| 생체이용률 | Rybelsus: ~1% | 높음 (정확한 수치 미공개) |
| 제조 원가 | 높음 (펩타이드 합성) | 낮음 (화학 합성) |
| 보관 | 냉장 (일부) | 실온 |

Orforglipron은 GLP-1R의 TMD(transmembrane domain) 내부, 즉 펩타이드 리간드 결합 부위와 다른 **알로스테릭 부위**에 결합하여 수용체를 활성화한다. 이 결합 양식은 양성 알로스테릭 조절자(positive allosteric modulator)이자 부분 작용제(partial agonist)로 기능하며, 펩타이드와의 구조적 차이에도 불구하고 유사한 하위 신호전달을 유발한다.

---

## 3. 임상 데이터

### 3.1 Semaglutide 핵심 임상시험

#### SELECT 시험 (NCT03574597)

심혈관 안전성 + 효능을 검증한 대규모 무작위 대조 시험 [6]:

| 항목 | 수치 |
|------|------|
| 피험자 수 | 17,604명 (BMI ≥27, 심혈관 질환 동반, 당뇨 없음) |
| 참여국 | 41개국 |
| 1차 종료점 | 3-point MACE (심혈관 사망, 비치명적 MI, 비치명적 뇌졸중) |
| MACE 감소 | **20% 감소** (HR 0.80; 95% CI 0.72-0.90; P<0.001) |
| Semaglutide군 MACE 발생 | 569/8,803 (6.5%) |
| Placebo군 MACE 발생 | 701/8,801 (8.0%) |
| 체중 감소 | 평균 -9.4% (vs. placebo -0.9%) |
| 허리둘레 경유 매개 효과 | MACE 혜택의 ~33%가 허리둘레 감소에 의해 매개 |

2025년 추가 분석에서, 심혈관 보호 효과의 상당 부분이 체중 감소와 독립적인 메커니즘에 의한 것으로 확인되었다 [6].

#### STEP 시험 시리즈 (비만)

| 시험 | NCT | 피험자 | 용량 | 체중 변화 | 주요 결과 |
|------|-----|--------|------|----------|----------|
| STEP 1 | NCT03548935 | 1,961명 (비만, 비당뇨) | 2.4mg QW | **-14.9%** vs. -2.4% | P<0.001 |
| STEP 2 | NCT03552757 | 1,210명 (비만 + T2DM) | 2.4mg QW | **-9.6%** vs. -3.4% | P<0.001 |
| STEP 5 | NCT03693430 | 304명 | 2.4mg QW | -15.2% (104주) | 지속적 감량 유지 |

### 3.2 Tirzepatide 핵심 임상시험

#### SURMOUNT-5 (NCT05822830)

Tirzepatide vs. semaglutide 직접 비교(head-to-head) 시험 [7]:

| 항목 | Tirzepatide | Semaglutide | P값 |
|------|------------|------------|------|
| 피험자 수 | 375명 | 376명 | — |
| 대상 | 비만 (BMI ≥30), 비당뇨 | 동일 | — |
| 72주 체중 변화 | **-20.2%** (95% CI: -21.4 ~ -19.1) | **-13.7%** (95% CI: -14.9 ~ -12.6) | P<0.001 |
| 절대 체중 감소 | 22.8 kg | 15.0 kg | — |
| ≥25% 감량 달성률 | **31.6%** | **16.1%** | — |
| GI 부작용으로 중단 | 2.7% | 5.6% | — |

SURMOUNT-5 post-hoc 분석에서, 10년 심혈관 위험도(ASCVD risk) 감소가 12주차에 이미 유의하게 관찰되어, 체중 감소 이전에 독립적 심혈관 보호 효과가 존재함을 시사했다 [7].

#### SURPASS-5 (T2DM)

| 항목 | Tirzepatide 15mg | Placebo |
|------|-----------------|---------|
| HbA1c 변화 | -2.59% | -0.93% |
| 체중 변화 | -10.9 kg | -1.6 kg |

### 3.3 CagriSema (Cagrilintide + Semaglutide)

2025년 NEJM에 발표된 Phase 3 결과 [8]:

| 항목 | CagriSema | Placebo |
|------|----------|---------|
| 68주 체중 변화 (비만, 비당뇨) | **-20.4%** | -3.0% |
| 68주 체중 변화 (T2DM) | **-13.7%** | -3.4% |

Novo Nordisk는 2026년 6월 CagriSema의 FDA 승인 신청을 완료했다 [8].

### 3.4 Amycretin (GLP-1/Amylin 이중작용 단일분자)

Phase 1b/2a 결과 (Lancet, 2025) [9]:

| 항목 | Amycretin 20mg (SC) | Placebo |
|------|---------------------|---------|
| 피험자 수 | 125명 (과체중/비만) | — |
| 36주 체중 변화 | **-22%** | +2% |
| 부작용 | GI 관련 (구역, 구토) 81% | — |
| 중증 부작용 | 없음 (전부 경증-중등도) | — |

36주 만에 22% 체중 감소는 기존 모든 비만약 중 최고 수치이며, Phase 3 진입이 2026년 확인되었다 [9].

### 3.5 Orforglipron (경구 소분자)

#### ATTAIN 시험 (비만)

FDA 승인 근거 시험 (2026) [5]:

| 용량 | 72주 체중 변화 | ≥10% 감량 달성 | ≥15% 감량 달성 | ≥20% 감량 달성 |
|------|-------------|-------------|-------------|-------------|
| 6 mg | -7.5% | — | — | — |
| 12 mg | -8.4% | — | — | — |
| 36 mg | **-11.2%** | **54.6%** | **36.0%** | **18.4%** |
| Placebo | -2.1% | 12.9% | 5.9% | 2.8% |

#### ACHIEVE-3 (T2DM, head-to-head vs. oral semaglutide)

Orforglipron 12mg 및 36mg이 경구 semaglutide 7mg 및 14mg 대비 HbA1c 감소 및 체중 감소에서 **모두 우월성(superiority)**을 입증 [5].

### 3.6 적응증 확장 임상

| 적응증 | 약물 | 시험 | 결과 |
|--------|------|------|------|
| MASH/NAFLD | Semaglutide | Phase 3 | FDA 승인 획득 (2025) |
| CKD | Semaglutide | FLOW (NCT03819153) | 신장 복합 종료점 24% 감소 → 조기 종료 |
| 수면무호흡증 | Tirzepatide | Phase 3 | FDA 승인 획득 (2025) |
| 심부전(HFpEF) | Semaglutide | STEP-HFpEF | 증상 개선 + 체중 감소 유의 |
| 알코올 사용 장애 | Semaglutide | Phase 2 | 2025 착수 |

---

## 4. 시장 분석

### 4.1 TAM (Total Addressable Market)

| 시점 | GLP-1 비만약 시장 | 전체 비만약 시장 | 인슐린 시장 |
|------|------------------|----------------|------------|
| 2025 | $70B | ~$80B | $30B |
| 2030 | $137.4B (GBN), $95B (Goldman Sachs) | $150B (Morgan Stanley) | $36B |
| 2035 | $315B | — | $46B |

Goldman Sachs는 2025년 보고서에서 비만약 시장이 기대보다 작을 수 있다고 경고했으나, Morgan Stanley는 2035년까지 $150B 전망을 유지하고 있다 [10].

미국 내 GLP-1 치료 환자 수: 2025년 ~1,000만 명 → 2030년 ~2,500만 명 → 2035년 ~3,000만 명 (비만 인구의 20-25%).

### 4.2 경쟁 구도

#### Tier 1: 현재 시장 지배자
| 기업 | 티커 | 주요 제품 | 강점 |
|------|------|----------|------|
| Novo Nordisk | NVO | Ozempic, Wegovy, CagriSema | GLP-1 개척자, 생산 인프라, amylin 파이프라인 |
| Eli Lilly | LLY | Mounjaro, Zepbound, Foundayo | 이중/삼중 작용제, 경구화 선점 |

#### Tier 2: 차별화된 도전자
| 기업 | 티커 | 파이프라인 | 차별점 |
|------|------|----------|--------|
| Amgen | AMGN | MariTide | 월 1회 주사 (항체-펩타이드 접합체) |
| Viking Therapeutics | VKTX | VK2735 | 경구/주사 GLP-1+GIP |
| Structure Therapeutics | GPCR | 소분자 GLP-1, 소분자 amylin | 순수 소분자 플레이어 |
| Regeneron | REGN | Trevogrumab + semaglutide | 근육보존형 (myostatin 억제) |

#### Tier 3: 특허 절벽 이후 준비
Semaglutide 물질 특허 만료: 2032년 전후. 바이오시밀러 진입 시 시장 재편 예상.

### 4.3 소분자 경구화의 경제적 임팩트

주사제에서 경구제로의 전환은 단순한 편의성 개선이 아닌 **시장 규모의 구조적 확대**를 의미한다:

1. **환자 접근성**: 주사 거부 환자층(전체 비만 환자의 ~60%) 흡수
2. **제조 원가**: 펩타이드 합성 대비 화학 합성 원가 1/10 수준
3. **유통**: 냉장 물류(cold chain) 불필요
4. **보험 수재**: 낮은 단가 → 보험사 수재 확대 가능성

Goldman Sachs 추정: 경구화가 TAM을 주사제 대비 **3-5배** 확대할 잠재력.

---

## 5. AI 적용

### 5.1 펩타이드 신약 설계

- **ImmunoPrecise Antibodies (IPA)**: 2025년 6월, AI 설계 GLP-1 펩타이드 시퀀스가 semaglutide와 동등 이상의 GLP-1R 활성화를 달성했다고 발표. AI가 수백만 개 서열 공간에서 최적 변이체를 탐색.
- **De novo 펩타이드 설계**: 생성 AI(generative AI) 모델이 자연계에 존재하지 않는 완전 새로운 GLP-1 유사체를 설계. 부작용(구역, 구토) 유발 구조 모티프를 회피하면서 효능을 유지하는 서열 최적화.

### 5.2 디지털 헬스 통합

- **CGM + AI 용량 최적화**: Dexcom(DXCM) 연속혈당모니터 + Novo Nordisk 스마트 인슐린 펜 연동 (2025) → AI가 실시간 혈당 패턴을 분석하여 개인 맞춤 GLP-1RA 용량 조절
- **Omnipod 5**: Insulet(PODD)의 AI 기반 자동 인슐린 전달 시스템 → 폐쇄 루프(closed-loop) 자동 투약
- **디지털 동반 진단(CDx)**: AI가 환자의 유전체, 대사체, 마이크로바이옴 데이터를 통합 분석하여 최적 GLP-1RA 선택 및 반응 예측

### 5.3 적응증 재창출(Drug Repurposing)

AI 기반 빅데이터 분석으로 GLP-1RA의 새로운 적응증 발굴이 가속화:
- **전자의무기록(EHR) 마이닝**: 수백만 건의 처방 데이터에서 GLP-1RA 사용 환자의 비의도적 치료 효과 탐지 → 알츠하이머, 파킨슨, 중독성 질환 등에서의 보호 효과 시그널 발견
- **다중오믹스(multi-omics)**: 유전체-단백체-대사체 통합 분석으로 GLP-1R 발현 조직 맵핑 → 뇌, 신장, 간에서의 새로운 약리 기전 규명

### 5.4 AlphaFold와 수용체 구조 기반 설계

AlphaFold3가 GLP-1R-리간드 복합체의 3D 구조를 원자 수준에서 예측할 수 있게 되면서 [11]:
- 소분자 GLP-1RA의 **결합 모드(binding mode)** 사전 예측
- 수용체 알로스테릭 부위의 체계적 탐색
- 리간드-수용체 상호작용의 자유에너지(binding free energy) 계산 → in silico 스크리닝 정확도 50% 이상 향상

---

## 6. 참고문헌

[1] Holst JJ, Gasbjerg LS, Rosenkilde MM. "GLP-1 and GIP receptor signaling in beta cells – A review of receptor interactions and co-stimulation." *Peptides*. 2022;151:170749. https://www.sciencedirect.com/science/article/pii/S0196978122000158

[2] Wootten D, Reynolds CA, Smith KJ, et al. "The GLP-1R as a model for understanding and exploiting biased agonism." *J Endocrinol*. 2024;261(2):JOE-23-0226. https://joe.bioscientifica.com/view/journals/joe/261/2/JOE-23-0226.xml

[3] Samms RJ, Coghlan MP, Sloop KW. "GLP-1 and GIP receptors signal through distinct β-arrestin pathways." *Cell Reports*. 2023;42(11):113384. https://www.cell.com/cell-reports/pdf/S2211-1247(23)01338-4.pdf

[4] Hay DL, Chen S, Lutz TA, et al. "Amycretin, a novel, unimolecular GLP-1 and amylin receptor agonist administered subcutaneously: results from a phase 1b/2a randomised controlled study." *The Lancet*. 2025;S0140-6736(25)01185-7. https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)01185-7/abstract

[5] Eli Lilly. "Orforglipron, an oral small-molecule GLP-1 receptor agonist, for the treatment of obesity in people with type 2 diabetes (ATTAIN-2): a phase 3, double-blind, randomised, multicentre, placebo-controlled trial." *The Lancet*. 2025. https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)02165-8/abstract

[6] Lincoff AM, Brown-Frandsen K, Colhoun HM, et al. "Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes." *N Engl J Med*. 2023;389:2221-2232. NCT03574597. https://pubmed.ncbi.nlm.nih.gov/37952131/

[7] Rodriguez PJ, Goodwin BJ, Engel SS, et al. "Tirzepatide as Compared with Semaglutide for the Treatment of Obesity." *N Engl J Med*. 2025. NCT05822830. https://www.nejm.org/doi/full/10.1056/NEJMoa2416394

[8] Wilding JPH, et al. "Coadministered Cagrilintide and Semaglutide in Adults with Overweight or Obesity." *N Engl J Med*. 2025. NCT05394519. https://www.nejm.org/doi/full/10.1056/NEJMoa2502081

[9] Enebo LB, et al. "Safety, tolerability, pharmacokinetics, and pharmacodynamics of the first-in-class GLP-1 and amylin receptor agonist, amycretin: a first-in-human, phase 1, double-blind, randomised, placebo-controlled trial." *The Lancet*. 2025. https://pubmed.ncbi.nlm.nih.gov/40550229/

[10] Goldman Sachs Research. "The anti-obesity drug market may prove smaller than expected." 2025. https://www.goldmansachs.com/insights/articles/the-anti-obesity-drug-market-may-prove-smaller-than-expected / Morgan Stanley. "Weight Loss Drug Market Could Reach $150 Billion Globally." https://www.morganstanley.com/insights/articles/weight-loss-medication-market-unstoppable-growth

[11] Abramson J, et al. "Accurate structure prediction of biomolecular interactions with AlphaFold 3." *Nature*. 2024;630:493-500. https://blog.google/innovation-and-ai/products/google-deepmind-isomorphic-alphafold-3-ai-model/

[12] Drucker DJ. "The expanding landscape of GLP-1 medicines." *Nature Medicine*. 2025. https://www.nature.com/articles/s41591-025-04124-5

[13] Li Y, et al. "Comprehensive evaluation of GLP-1 receptor agonists: an umbrella review of clinical outcomes across multiple diseases." *Nature Communications*. 2025;16:67701. https://www.nature.com/articles/s41467-025-67701-9

[14] Sattar N, et al. "GLP-1 receptor agonists and next-generation incretin-based medications: metabolic, cardiovascular, and renal benefits." *The Lancet*. 2025;S0140-6736(25)02105-1. https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)02105-1/fulltext

[15] Nature. "FDA approves GLP-1 pill for obesity." *Nat Rev Drug Discov*. 2026. https://www.nature.com/articles/d41573-026-00059-9

---

> **면책조항**: 본 리뷰는 기술적 분석 목적으로 작성되었으며, 특정 종목의 매수/매도를 권유하지 않습니다. 투자 결정은 전문가 자문을 통해 독립적으로 이루어져야 합니다.
