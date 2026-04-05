# 바이오 기술 리뷰 #12: 디지털 치료제 — 기전, 임상 데이터, 투자 분석

> **Technical Review Series** | 2026-04-05
> 디지털 치료제(Digital Therapeutics, DTx)의 기술적 프레임워크 — CBT-i 디지털 프로토콜,
> 게이미피케이션 신경과학(EndeavorRx), 바이오마커 통합, AI 개인화 치료 —
> 를 분석하고, FDA 승인 제품의 임상 데이터, 상환 환경, 시장 전망을 종합 리뷰한다.

---

## 1. 기술 개요: 디지털 치료제의 과학적 기반

디지털 치료제(DTx)는 소프트웨어 기반의 치료적 중재(intervention)로, 질병을 예방, 관리, 또는 치료하기 위해 설계된 **의학적 근거(evidence-based)**를 가진 프로그램이다. 전통적 약물이 분자 수준의 생화학적 경로를 표적하는 반면, DTx는 **행동 변화(behavioral modification)**, **인지 훈련(cognitive training)**, **신경가소성(neuroplasticity)** 경로를 표적한다.

### 1.1 DTx의 분류 체계

| 범주 | 정의 | 규제 | 예시 |
|------|------|------|------|
| 처방 DTx (PDTx) | FDA/EMA 승인, 의사 처방 필요 | 의료기기 (Class II) | EndeavorRx, Somryst |
| OTC DTx | FDA 승인, 처방 없이 사용 | 의료기기 (Class II) | EndeavorOTC |
| 디지털 동반자 | 기존 약물 치료 보완 | 웰니스/SaMD | BlueStar |
| 디지털 건강 앱 | 치료적 주장 없음 | 비규제 | Calm, Headspace |

DTx의 핵심 차별점은 **무작위 대조 시험(RCT)**을 통한 임상적 효과 입증이다. 이것이 일반 웰니스 앱과의 경계를 설정한다.

### 1.2 치료적 중재의 신경과학적 기반

DTx의 치료 효과는 세 가지 신경과학적 메커니즘에 기반한다:

1. **인지행동치료(CBT)의 신경 기반**: CBT는 전전두엽 피질(PFC)의 하향식(top-down) 인지 조절을 강화하여 편도체(amygdala)의 과활성화를 억제한다. fMRI 연구에서 CBT 후 배외측 전전두엽(dlPFC) 활성 증가와 편도체 반응성 감소가 확인되었다.

2. **주의력 네트워크 훈련**: 주의력(attention)은 경각(alerting), 방향(orienting), 집행(executive) 네트워크의 상호작용으로 구성된다. 반복적 인지 자극을 통해 전두-두정 주의 네트워크(frontoparietal attention network)의 기능적 연결성을 강화할 수 있다.

3. **보상 회로 조절**: 게이미피케이션은 선조체(striatum)의 도파민성 보상 경로를 활용하여 치료 순응도를 높이고, 동기화 학습(motivated learning)을 촉진한다.

---

## 2. 핵심 기술 세부

### 2.1 CBT-i 디지털 프로토콜 (Somryst/SHUTi)

인지행동치료-불면증(CBT-i)은 만성 불면증의 1차 치료로 권고되는 근거 기반 심리 치료이다[1]. 디지털 CBT-i (dCBT-i)는 이를 소프트웨어로 구현하여 치료사 접근성 문제를 해결한다.

#### CBT-i의 5대 구성 요소

| 구성 요소 | 메커니즘 | 신경과학적 기반 |
|----------|---------|----------------|
| **수면 제한(Sleep Restriction)** | 침대 시간을 실제 수면 시간으로 제한 → 수면 압력(sleep pressure) 증가 | 아데노신 축적 → 배외측 전시상(VLPO) 활성화 |
| **자극 통제(Stimulus Control)** | 침대 = 수면 연합 강화, 각성 자극 제거 | 조건 반사(classical conditioning) 소거 — 편도체/해마 연합 학습 재설정 |
| **인지 재구조화(Cognitive Restructuring)** | 수면에 대한 역기능적 신념 교정 | PFC 하향식 조절 → 과각성(hyperarousal) 감소 |
| **수면 위생(Sleep Hygiene)** | 카페인, 알코올, 스크린 노출 제한 | 멜라토닌 분비 리듬 정상화, HPA 축 안정화 |
| **이완 훈련(Relaxation Training)** | 점진적 근이완, 호흡법, 마음챙김 | 부교감신경 활성화 → 교감신경 톤 감소 |

#### Somryst (Pear → Mahana) 디지털 구현

Somryst는 Sleep Healthy Using the Internet (SHUTi)의 모바일 네이티브 적응으로, FDA De Novo 510(k) 승인을 받은 최초의 처방 디지털 CBT-i이다[1].

**디지털 프로토콜 아키텍처**:
1. **6-9 주 세션 구조**: 주 1-2회 대화형 콘텐츠 + 일일 수면 일기
2. **적응형 알고리즘**: 수면 일기 데이터 기반으로 수면 제한 목표 시간 자동 조정
3. **개인화 피드백**: 수면 효율(SE), 수면 잠복기(SOL), 수면 중 각성(WASO) 추이 시각화
4. **자동 단계 진행**: 이전 세션 완료 + 데이터 입력 기준 충족 시 다음 세션 해금

**불면증 심각도 지수(ISI) 기반 디지털 적응**:
- ISI 점수 > 15 → 집중적 수면 제한 시행
- ISI 점수 8-15 → 유지 프로토콜
- ISI 점수 < 8 → 관해(remission) 진입

### 2.2 게이미피케이션 신경과학: EndeavorRx의 주의력 메커니즘

EndeavorRx는 Akili Interactive가 개발한 세계 최초의 FDA 승인 게임형 디지털 치료제(2020년)로, 8-17세 ADHD 아동·청소년을 대상으로 한다[2].

#### SSME (Selective Stimulus Management Engine) 기술

EndeavorRx의 핵심은 Akili의 독점 기술인 **SSME(Selective Stimulus Management Engine)**이다[2]:

1. **이중 과제(Dual-Task) 패러다임**:
   - **감각 자극(Sensory stimuli)**: 시각적 표적/방해 자극이 게임 환경에서 제시
   - **운동 과제(Motor challenge)**: 기기 기울임(tilting)을 통한 캐릭터 조종
   - 동시에 두 과제를 수행함으로써 **간섭 처리(interference processing)** 훈련

2. **표적 신경 시스템**:
   - **전전두엽 피질(PFC)**: 집행 기능, 작업 기억
   - **전대상회(ACC)**: 갈등 모니터링, 오류 감지
   - **전두-두정 네트워크**: 주의력 할당, 과제 전환

3. **적응형 알고리즘**:
   - 개별 환자의 수행 수준에 따라 난이도 실시간 조정
   - 너무 쉬우면 → 집행 기능 훈련 불충분
   - 너무 어려우면 → 좌절감, 이탈
   - **최적 도전 지점(Zone of Proximal Development)** 유지가 핵심

4. **신경가소성 유도**:
   - 반복적 주의력 훈련이 PFC-ACC 연결의 시냅스 강도를 증가
   - Hebb의 법칙: "함께 발화하는 뉴런은 함께 결합한다"
   - 4주간 일 25분 x 5일/주 프로토콜로 측정 가능한 주의력 개선 유도

#### 게이미피케이션의 신경과학적 원리

| 게임 메커니즘 | 신경 기반 | 치료적 효과 |
|-------------|----------|------------|
| 즉각적 피드백 | VTA → NAc 도파민 방출 | 보상 예측 오류 학습 강화 |
| 진행 시스템 (레벨업) | 선조체 도파민 경로 | 내재적 동기 유지, 순응도 향상 |
| 적응형 난이도 | PFC 부하 최적화 | 최적 인지 훈련 강도 유지 |
| 몰입(Flow) 상태 | 전두-두정 네트워크 동기화 | 지속적 주의 집중 훈련 |
| 사회적 비교 | 측두-두정 접합부(TPJ) | 외재적 동기 보충 |

### 2.3 바이오마커 통합

차세대 DTx의 핵심 차별점은 **웨어러블 센서 데이터**와의 실시간 통합이다[3].

#### 통합 가능한 디지털 바이오마커

| 바이오마커 | 센서 | DTx 활용 | 적응증 |
|----------|------|---------|--------|
| 심박변이도(HRV) | PPG (스마트워치) | 자율신경 균형 모니터링 → 이완 훈련 트리거 | 불안, PTSD |
| 수면 단계 | 가속도계 + PPG | 수면 구조 분석 → CBT-i 프로토콜 조정 | 불면증 |
| 활동량/보행 패턴 | 가속도계 | 활동 수준 모니터링 → 행동 활성화 | 우울증 |
| 전기피부반응(EDA) | EDA 센서 | 스트레스 수준 실시간 추적 | 불안, PTSD |
| 혈당 연속 모니터링 | CGM | 실시간 혈당 → 행동/식이 피드백 | 당뇨 |
| 음성 바이오마커 | 마이크 | 음성 패턴 변화 → 기분 상태 추정 | 우울증 |
| 타이핑 패턴 | 터치스크린 | 인지/운동 기능 변화 감지 | ADHD, 파킨슨 |

#### 폐쇄 루프(Closed-Loop) DTx 아키텍처

```
[센서] → [데이터 수집] → [AI 분석] → [상태 추정] → [중재 결정] → [콘텐츠 전달]
   ↑                                                                      ↓
   └──────────────────── [반응 모니터링] ←────────────────────────────────┘
```

이 폐쇄 루프 구조는 전통적 약물의 "투여 → 대기 → 평가" 패러다임과 근본적으로 다르며, **실시간 적응적 치료(real-time adaptive therapy)**를 가능하게 한다.

### 2.4 AI 기반 개인화 치료 엔진

#### 치료 순응도 예측 모델

DTx의 최대 과제는 **사용 중단(dropout)**이다. 전통 약물 대비 DTx의 순응도가 낮은 것은 "앱 피로(app fatigue)"와 능동적 참여 요구에 기인한다.

**ML 기반 이탈 예측**:
- 입력 특성(features): 사용 빈도, 세션 완료율, 시간대별 패턴, 진도 속도, 인구학적 변수
- 모델: Gradient Boosting, LSTM (시계열 패턴)
- 출력: 7일 내 이탈 확률 → 임계값 초과 시 개입(알림, 보상, 난이도 조정)

#### 자연어처리(NLP) 기반 AI 치료사

AI 챗봇이 CBT의 인지 재구조화 세션을 자동화:
- 환자의 자연어 입력에서 **자동 사고(automatic thoughts)** 식별
- 인지 왜곡 유형 분류 (흑백논리, 과잉일반화, 파국화 등)
- 소크라테스식 질문 생성으로 대안적 사고 유도
- LLM(GPT-4, Claude) 기반 대화형 치료가 전통 스크립트형 대비 자연스러움 증가

---

## 3. 임상 데이터

### 3.1 Somryst (디지털 CBT-i)

**SHUTi RCT 메타분석** — 9개 무작위 시험, 3,000+ 환자[1]:

| 평가변수 | Somryst/SHUTi | 대조 | 차이 |
|---------|--------------|------|------|
| ISI (불면증 심각도) | -5.77점 감소 | — | 95% CrI [-8.53, -3.07] |
| ISI 관해(remission) | OR 12.33 | — | 95% CrI [2.28, 155.91] |
| 수면 잠복기(SOL) 감소 | **45%** | — | — |
| 수면 중 각성(WASO) 감소 | **52%** | — | — |
| 불면증 증상 심각도 감소 | **45%** | — | — |

**네트워크 메타분석**: 디지털 CBT-i의 효과 크기는 대면(face-to-face) CBT-i와 **동등**한 수준이며, 수면제(벤조디아제핀, z-drug) 대비 장기 효과가 우월하였다[4].

**DREAM 실세계 연구** (오픈 라벨)[5]:
- **대상**: 만성 불면증 성인 (처방 사용)
- **결과**: 치료 후 ISI 유의한 감소, 우울(PHQ-8) 및 불안(GAD-7) 동반 개선
- **실사용 순응도**: 6주 프로그램 완료율 약 70%

### 3.2 EndeavorRx (ADHD)

**STARS 피봇탈 시험** — Kollins 등, *Lancet Digital Health* 2020[2]:

| 평가변수 | EndeavorRx | 대조 (교육 게임) | 통계 |
|---------|-----------|-----------------|------|
| TOVA API 변화 | 유의한 개선 | — | **p = 0.006** |
| TOVA 개선 (>0.5 SD) | **47%** | 32% | — |
| 주의력 결핍 해소 (1+ 척도) | **33%** | — | — |
| 부모 보고 ADHD 증상 개선 | 68% | — | — |

**안전성 프로파일**[2]:
- 총 342명 투여 중 심각한 이상 반응(SAE): **0건**
- 치료 관련 AE: 17명 (4.97%)
- 좌절감 내성 감소: 2.34%
- 두통: 1.17%

**추가 데이터 (FDA 확장, 8-17세)**:
- 13-17세 청소년 대상 확장 시험에서 동일한 안전성 프로파일 확인
- 2024년 6월: EndeavorOTC — 최초의 OTC 디지털 ADHD 치료제로 성인 대상 FDA 승인

### 3.3 기타 DTx 임상 데이터

**Freespira (PTSD/공황장애)**:
- 바이오피드백 기반 호흡 훈련 장치
- PTSD 연구: 치료 후 **73%**가 PTSD 진단 기준 미충족
- 공황장애: **86%**가 공황 발작 소실
- FDA 510(k) 승인

**Click Therapeutics CT-152 (우울증, Otsuka 파트너십)**:
- Phase 3 진행 중 (NCT05350228)
- 디지털 CBT + 행동 활성화
- Otsuka와 $400M+ 딜

**Biofourmis (심부전)**:
- AI 기반 원격 모니터링 + 예측 알고리즘
- 심부전 재입원률 30일 내 38% 감소 보고
- FDA Breakthrough Device 지정

### 3.4 실패 사례: Pear Therapeutics

| 제품 | 적응증 | FDA 승인 | 결과 |
|------|--------|---------|------|
| reSET | 약물사용장애(SUD) | 2017 (최초 PDTx) | 파산 (2023.04) |
| reSET-O | 오피오이드 사용장애 | 2018 | 파산 |
| Somryst | 불면증 | 2020 | Mahana에 매각 |

**파산 원인 분석**:
1. **상환 실패**: 앱 가격 $1,000+/인 → 보험사 지불 거부
2. **의사 인식 부족**: DTx를 "진짜 약"으로 인식하지 않음
3. **순응도 문제**: 12주 프로그램 완료율 < 50%
4. **경쟁 심화**: 비규제 웰니스 앱과의 차별점 미흡

Pear의 실패는 **기술적 검증(clinical validation) ≠ 상업적 성공**이라는 DTx 산업의 핵심 교훈이다.

---

## 4. 시장 분석

### 4.1 시장 규모 및 성장률

| 연도 | 시장 규모 | CAGR | 출처 |
|------|----------|------|------|
| 2024 | $7.7B | — | Grand View Research |
| 2025 | $10.0-11.2B | — | 다수 |
| 2030 | $31.5-32.5B | 25.9-27.8% | Mordor/GVR |
| 2034 | $52.6-90.8B | 21-27.8% | Fortune BI/Towards Healthcare |

### 4.2 Medicare 상환: 게임 체인저

2025년은 DTx 산업의 변곡점이다. CMS가 정신건강 DTx에 대한 **3개 청구 코드**를 신설하여 Medicare 상환의 문을 열었다[6].

**Medicare DTx 파일럿 현황 (2025)**:
- Q1 2025: 99명 환자, 184회 청구
- Q3 2025: **446명 환자, 897회** 청구 (4.5배 성장)
- 대상 기기: 7개 정신건강 DTx 디바이스

**한계**: CMS가 전국 단일 요율을 설정하지 않고 지역 Medicare 계약자에 위임 → 요율 편차, 행정적 마찰

**상업 보험사 동향**:
- Cigna, Aetna, UnitedHealth 등이 선별적 DTx 커버리지 시작
- Employer-sponsored plan에서의 DTx 도입 증가 추세
- 그러나 전면적 커버리지까지는 2-3년 소요 전망

### 4.3 적응증별 시장 기회

| 적응증 | 시장 성숙도 | 상환 상태 | TAM (2030E) | 핵심 기업 |
|--------|-----------|----------|-------------|----------|
| 정신건강 (우울, 불안, PTSD) | 상용화/확장 | Medicare 시작 | $8-12B | Click, Happify |
| ADHD | 상용화 | 부분적 | $2-3B | Akili (→OTC) |
| 불면증 | 상용화 | 부분적 | $3-5B | Mahana (Somryst) |
| 당뇨 관리 | 상용화 | 상업 보험 | $3-5B | Welldoc (BlueStar) |
| 만성 통증 | 초기 | 미확립 | $5-8B | AppliedVR |
| 약물 중독 | 검증됨 (상업 실패) | 미확립 | $2-4B | PursueCare (reSET) |

### 4.4 경쟁 환경

**빅파마 + DTx 파트너십** (가장 안전한 투자 경로):
| 빅파마 | DTx 파트너 | 적응증 | 딜 규모 |
|--------|-----------|--------|---------|
| Otsuka | Click Therapeutics | 우울증, 금연 | $400M+ |
| Novartis | Pear (구 reSET) | 약물 중독 | (Pear 파산으로 종료) |
| Sanofi | Happify Health | 다발성경화증 | 비공개 |

**순수 DTx 기업의 도전**:
- Pear Therapeutics: 파산 (2023)
- Akili Interactive: OTC 전환 후 자산 매각 (2024) — 처방 모델 포기
- Better Therapeutics: 상장 후 저조한 매출

### 4.5 핵심 리스크 요인

1. **상환이 생명선**: Pear 파산이 증명 — 보험 적용 없으면 상업적 생존 불가
2. **순응도 과제**: DTx 12주 프로그램 완료율 40-70% — 약물의 refill rate 대비 낮음
3. **규제 마찰**: 앱 업데이트(버전 릴리즈)와 의료기기 승인 프로세스의 충돌
4. **효과 크기**: 일부 DTx의 효과 크기(effect size)가 약물 대비 작음 → 지불자 설득 어려움
5. **의사 인식 전환**: "앱은 약이 아니다"라는 문화적 저항

---

## 5. AI 적용

### 5.1 개인화 치료 알고리즘

AI는 DTx의 **실시간 개인화**를 가능하게 하는 핵심 인에이블러이다:

- **강화학습(RL) 기반 치료 최적화**: 환자 상태(state) → 중재 선택(action) → 결과(reward)의 MDP 프레임워크로 최적 치료 정책 학습
- **컨텍스추얼 밴딧(Contextual Bandit)**: 환자 특성에 따라 콘텐츠 유형(텍스트, 비디오, 게임, 명상)을 동적 배분
- **Just-In-Time Adaptive Intervention (JITAI)**: 센서 데이터가 특정 임계값 도달 시 즉각적 마이크로 중재 전달

### 5.2 바이오마커 기반 AI 시스템

웨어러블 센서 + AI의 통합으로 DTx가 **생체 신호 반응적(bioresponsive)** 치료로 진화한다[3]:

- **수면 분석**: PPG + 가속도계 데이터의 딥러닝 분석 → 수면 단계 분류(N1/N2/N3/REM) → CBT-i 프로토콜 실시간 조정
- **스트레스 감지**: HRV + EDA의 연속 모니터링 → LSTM 기반 스트레스 상태 예측 → 이완 훈련 자동 트리거
- **혈당 예측**: CGM 시계열 + 식이/활동 데이터 → Transformer 모델의 30분-2시간 혈당 예측 → 선제적 행동 변화 알림

### 5.3 NLP 기반 치료 챗봇

- **Woebot**: CBT 기반 AI 챗봇 — RCT에서 PHQ-9(우울 척도) 유의한 감소 확인
- **Tess (X2AI)**: 위기 상담 AI — 24/7 자연어 대화, 위기 감지 시 에스컬레이션
- **LLM 시대의 진화**: GPT-4/Claude 기반의 컨텍스트 인지 치료 대화 — 스크립트형 대비 자연스러움, 공감 표현 개선

### 5.4 효과 예측 모델

- **치료 반응 예측**: 베이스라인 환자 특성 + 초기 사용 패턴 → 치료 반응 확률 예측 → 비반응 예측 환자는 조기에 대안 치료로 전환
- **최적 치료 매칭**: 환자 프로파일 → DTx vs 약물 vs 대면 CBT 중 최적 치료 추천
- **임상 시험 설계 최적화**: 시뮬레이션 기반 표본 크기/평가변수 최적화

---

## 6. 투자 시사점

### 6.1 핵심 투자 테제

1. **Medicare 상환 = 게임 체인저**: 2025년 3개 청구 코드 신설로 상업적 생존성의 최대 장벽이 낮아짐. 그러나 전면 확대까지 2-3년 소요
2. **정신건강이 가장 유력한 적응증**: 치료사 부족 (미국 1.5억명 정신건강 전문가 부족 지역 거주) + 스티그마 감소 + 원격의료 수용도 증가
3. **순수 DTx보다 빅파마 파트너십이 안전**: Otsuka + Click ($400M+) 모델 — 빅파마의 상환 협상력 + DTx의 혁신 결합
4. **OTC 전환이 대안 비즈니스 모델**: Akili의 EndeavorOTC — 처방 모델의 상환 장벽 우회, 소비자 직접 판매
5. **AI + DTx = 자연스러운 수렴**: 디지털 매체의 특성상 AI 개인화가 가장 효과적으로 적용되는 치료 형태

### 6.2 Pear 파산의 교훈

| 교훈 | 시사점 |
|------|--------|
| FDA 승인 ≠ 상환 | 규제 승인과 지불자 수용은 별개 과정 |
| 높은 가격 ($1,000+) = 위험 | DTx의 가격 모델은 약물과 다름 — 구독/번들이 합리적 |
| 의사 채널 의존 = 느린 채택 | D2C(소비자 직접) 또는 고용주 채널이 보완 필요 |
| 순응도 = 효능의 함수 | 사용하지 않는 앱은 치료 효과 0 |

### 6.3 투자 전략 매트릭스

| 시계 | 전략 | 대표 종목/기업 |
|------|------|---------------|
| 단기 (1-3년) | 빅파마 파트너십 | Otsuka (4578.T), Click Therapeutics (비상장) |
| 중기 (3-5년) | Medicare 수혜 | Biofourmis (비상장), Welldoc (비상장) |
| 장기 (5-10년) | AI + 바이오마커 통합 | 차세대 폐쇄루프 DTx 기업 |
| 인프라 | 디지털 헬스 플랫폼 | Teladoc (TDOC), Veeva Systems (VEEV) |

---

## 참고문헌

[1] Ritterband LM, et al. "Profile of Somryst Prescription Digital Therapeutic for Chronic Insomnia: Overview of Safety and Efficacy." *Expert Review of Medical Devices*. 2021;18(sup1):45-55. doi:10.1080/17434440.2020.1852929. https://www.tandfonline.com/doi/full/10.1080/17434440.2020.1852929

[2] Kollins SH, et al. "A novel digital intervention for actively reducing severity of paediatric ADHD (STARS-ADHD): a randomised controlled trial." *Lancet Digital Health*. 2020;2(4):e168-e178. ; FDA De Novo Classification, DEN200026. https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN200026.pdf

[3] AI-Driven Wearable Bioelectronics in Digital Healthcare. *Biosensors*. 2025;15(7):410. doi:10.3390/bios15070410. https://pmc.ncbi.nlm.nih.gov/articles/PMC12294109/

[4] Borghouts J, et al. "Network meta-analysis comparing the effectiveness of a prescription digital therapeutic for chronic insomnia to medications and face-to-face CBT in adults." *Current Medical Research and Opinion*. 2022;38(11):1889-1900. doi:10.1080/03007995.2022.2108616. https://www.tandfonline.com/doi/full/10.1080/03007995.2022.2108616

[5] Kunkle S, et al. "Effect of a prescription digital therapeutic for chronic insomnia on post-treatment insomnia severity, depression, and anxiety symptoms: results from the real-world DREAM study." *Frontiers in Psychiatry*. 2024;15:1450615. doi:10.3389/fpsyt.2024.1450615. https://www.frontiersin.org/journals/psychiatry/articles/10.3389/fpsyt.2024.1450615/full

[6] Healthcare Brew. "New year, new digital therapeutics pilot." 2026-01-29. https://www.healthcare-brew.com/stories/2026/01/29/new-digital-therapeutics-pilot ; "Data shows growing use of new Medicare codes for digital therapeutics." 2025-07-29. https://www.healthcare-brew.com/stories/2025/07/29/growing-use-new-medicare-codes-digital-therapeutics

[7] Modern Healthcare. "Digital therapeutics industry looks to move past Pear's bankruptcy." https://www.modernhealthcare.com/digital-health/digital-therapeutics-companies-akili-are-shifting-gears/

[8] Digital Therapeutics Alliance. "Somryst Product Profile." https://dtxalliance.org/products/somryst/

[9] Chen T, et al. "Clinical study on the intervention effect of digital therapy on children with attention deficit hyperactivity disorder (ADHD)." *Scientific Reports*. 2024;14:23844. doi:10.1038/s41598-024-73934-3. https://www.nature.com/articles/s41598-024-73934-3

[10] Digital Therapeutics Market Analysis. Fortune Business Insights. "Digital Therapeutics Market $67.58B by 2034." https://www.fortunebusinessinsights.com/digital-therapeutics-market-103501

[11] Sverdlov O, et al. "Digital Therapeutics: An Integral Component of Digital Innovation in Drug Development." *Clinical Pharmacology & Therapeutics*. 2018;104(1):72-80.

[12] Towards Healthcare. "Digital Therapeutics Market Surges USD 90.83 Bn at 27.8% CAGR by 2034." https://www.towardshealthcare.com/insights/digital-therapeutics-market-sizing

---

*본 리뷰는 투자 권유가 아닌 기술 분석 목적으로 작성되었습니다. 투자 결정은 개인의 판단과 책임 하에 이루어져야 합니다.*
