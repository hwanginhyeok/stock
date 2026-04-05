# 바이오 기술 리뷰 #8: 뉴로테크 & 뇌-컴��터 인터페이스 — 기전, 임상 데이터, 투자 분석

> 유타 어레이에서 Neuralink N1까지: 신경 전극 기술, 신경 신호 디코딩 알고리즘, 임상 BCI의 현재와 미래

---

## 1. 기술 개요: 뇌-컴퓨터 인터페이스의 신경과학적 기반

### 1.1 신경 신호의 물리학

뇌-컴퓨터 인터페이스(Brain-Computer Interface, BCI)는 대뇌 피질 뉴런의 전기적 활동을 기록하여 디지털 명령으로 변환하거나, 역으로 전기 자극을 뇌에 전달하여 신경 활동을 조절하는 기술이다. 이 기술의 물리적 기반은 뉴런의 활동전위(action potential)이다.

**활동전위의 발생 메커니즘**:
뉴런의 안정막전위는 약 -70 mV이다. 역치(threshold, 약 -55 mV)에 도달하면 전압 의존성 Na⁺ 채널이 개방되어 급격한 탈분극이 발생하고, 막전위가 +30~+40 mV까지 상승한다(상승기, ~1 ms). 이어서 K⁺ 채널 개방과 Na⁺ 채널 불활성화에 의해 재분극이 진행된다. 전체 과정은 약 1-2 ms이며, 이 빠른 전기적 사건이 세포외 전극에서 "스파이크(spike)"로 기록된다.

**기록 가능한 신경 신호의 계층**:
| 신호 유형 | 주파수 | 공간 해상도 | 침습도 | 정보량 |
|----------|--------|-----------|--------|--------|
| 단일 뉴런 스파이크 | >300 Hz | ~100 μm | 피질 내 전극 | 최고 |
| Multi-unit activity (MUA) | >300 Hz | ~500 μm | 피질 내 전극 | 높음 |
| Local field potential (LFP) | 1-300 Hz | ~mm | 피질 내/표면 | 중간 |
| ECoG (electrocorticography) | 1-500 Hz | ~cm | 경막하 | 중간 |
| EEG (electroencephalography) | 1-100 Hz | ~cm | 두피 표면 | 낮음 |

BCI의 성능(information transfer rate, 비트/초)은 기록하는 신호의 계층과 직접적으로 비례한다. 단일 뉴런 수준의 스파이크를 기록하는 침습형 BCI가 가장 높은 정보 전달률을 달성하며, 두피 EEG 기반 비침습형 BCI는 상대적으로 낮다.

### 1.2 운동 피질의 신경 부호화

BCI의 1차 적용 표적인 운동 피질(primary motor cortex, M1)에서 뉴런은 의도한 움직임의 방향, 속도, 힘을 부호화한다. 1986년 Georgopoulos 등은 M1 뉴런이 특정 운동 방향에 최대 발화율을 보이되(preferred direction), 다른 방향에 대해서는 코사인 함수적으로 감소하는 "코사인 튜닝(cosine tuning)" 특성을 가짐을 발견했다 [1]. 이 발견은 다수 뉴런의 활동을 "집단 벡터(population vector)"로 합산하여 의도 운동 방향을 정확히 추정할 수 있음을 의미하며, 모든 운동 BCI의 이론적 토대가 되었다.

현대 BCI는 M1뿐 아니라 배측 전운동 피질(dorsal premotor cortex, PMd), 후두정엽 피질(posterior parietal cortex, PPC) 등에서의 운동 의도 신호도 활용하며, 연접 BCI는 브로카 영역(Broca's area)과 복측 감각운동 피질(ventral sensorimotor cortex)에서 발화 의도를 직접 디코딩하여 음성을 복원한다.

---

## 2. 핵심 기술 세부

### 2.1 Utah Array vs. Michigan Probe: 전통적 침습형 전극

#### 2.1.1 Utah Array (Blackrock Neurotech)

Utah Array는 1991년 Richard Normann이 개발한 실리콘 기반 미세전극 어레이로, 침습형 BCI 연구의 사실상 표준이었다 [2]:

- **구조**: 10 x 10 격자에 100개의 실리콘 니들 전극이 배열된 4 x 4 mm 크기 어레이. 각 니들 길이 1.0-1.5 mm, 간격 400 μm
- **전극 특성**: 각 니들 팁에 백금 코팅, 단일 기록 지점(single recording site per shank)
- **삽입 방식**: 공압(pneumatic) 삽입기를 사용하여 피질 표면에 수직으로 한 번에 삽입
- **채널 수**: 96채널 (100전극 중 96개에 와이어 본딩)
- **임상 실적**: BrainGate 연구 등 30명 이상의 인간에 이식, 가장 풍부한 인간 데이터 보유 [3]

**한계**:
- 강성(rigid) 실리콘 기판: 뇌 조직(Young's modulus ~0.1-1 kPa)과 실리콘(~170 GPa)의 기계적 불일치(mechanical mismatch)가 만성 이물질 반응(foreign body response, FBR)을 유발
- FBR: 이식 수주 내 활성 미세아교세포(activated microglia)와 반응성 성상세포(reactive astrocyte)가 전극 주위에 아교세포 흉터(glial scar)를 형성 → 전극-뉴런 거리 증가 → 시간 경과에 따른 신호 품질 저하
- 체외 페데스탈(pedestal): 두개골을 관통하는 외부 커넥터가 필요 → 감염 위험, 미용적 문제, 일상생활 제약

#### 2.1.2 Michigan Probe (University of Michigan)

Michigan Probe는 Utah Array와 다른 설계 철학을 가진 침습형 전극이다:

- **구조**: 얇은 실리콘 샹크(shank) 위에 다수의 기록 지점이 배열된 평판형(planar) 설계
- **다지점 기록**: 단일 샹크에 여러 깊이의 기록 지점 → 피질 층(laminar) 분석 가능
- **유연한 배치**: 샹크 수, 길이, 간격을 목적에 맞게 맞춤 설계 가능
- **Neuropixels**: Michigan Probe 개념의 극한적 확장. 단일 샹크에 5,120개 기록 지점, 384채널 동시 기록. 마우스 연구에서 수백 뉴런의 동시 기록에 혁명적이나, 인간 만성 이식은 아직 미검증

### 2.2 Neuralink N1: 차세대 완전 이식형 BCI

#### 2.2.1 하드웨어 아키텍처

Neuralink의 N1 임플란트는 Utah Array의 근본적 한계를 극복하기 위해 설계된 차세대 BCI이다 [4]:

- **전극 수**: 1,024개 전극, 64개 유연한 폴리이미드 스레드(thread)에 분배 (스레드당 ~16 전극)
- **스레드 소재**: 폴리이미드(polyimide) 기판에 박막 금 또는 백금 도체 — Utah Array 대비 1,000배 이상 유연하여 기계적 불일치 대폭 감소
- **스레드 치수**: 폭 ~24 μm, 두께 ~4-6 μm — 머리카락(~75 μm)보다 가늘어 뇌 조직 손상 최소화
- **컴퓨팅 모듈**: 두개골에 매립되는 직경 23 mm 원형 모듈, 자체 칩으로 1,024채널 신경 신호를 처리하고 Bluetooth Low Energy(BLE)로 무선 전송
- **배터리**: 무선 충전 가능한 리튬 배터리, ~12시간 연속 사용
- **삽입**: R1 수술 로봇이 개별 스레드를 ~1 mm/s 속도로 정밀 삽입, 혈관 회피 알고리즘 탑재

#### 2.2.2 N1의 성능 지표

- **스파이크 기록 수율(spike recording yield)**: 장기 동물 실험에서 전극의 ~70%가 안정적 단일 뉴런 스파이크를 기록 [4]
- **대역폭**: 1,024채널 x 20 kHz 샘플링 = 초당 ~20 메가샘플의 신경 데이터 처리
- **정보 전달률**: 첫 번째 인간 피험자(Noland Arbaugh)에서 초기 4.6 BPS(bits per second), 알고리즘 최적화 후 8.0 BPS로 향상 — 당시 BCI 세계 기록 [5]

#### 2.2.3 Utah Array 대비 비교

| 특성 | Utah Array | Neuralink N1 |
|------|-----------|-------------|
| 채널 수 | 96 | 1,024 |
| 전극 소재 | 강성 실리콘 니들 | 유연한 폴리이미드 스레드 |
| 외부 커넥터 | 체외 페데스탈 필요 | 완전 매립형, 무선 |
| 삽입 방법 | 공압 삽입기, 수동 | R1 로봇, 자동, 혈관 회피 |
| 만성 안정성 | 아교세포 흉터로 점진적 저하 | 유연 스레드로 FBR 감소 기대 |
| 기록 실적 | 30+명 인간 데이터, 20년+ | 12명 (2024-2025), 초기 |

### 2.3 혈관 내 BCI: Synchron Stentrode

#### 2.3.1 비개두술(No-Craniotomy) 접근

Synchron의 Stentrode는 뇌 수술(개두술) 없이 혈관 내 카테터를 통해 뇌에 도달하는 혁신적 BCI이다 [6]:

- **삽입 경로**: 경정맥(jugular vein) → 상시상정맥동(superior sagittal sinus) — 운동 피질 상부를 주행하는 대뇌 정맥
- **구조**: 자가팽창(self-expanding) 니티놀(nitinol) 스텐트 프레임에 16개 전극이 부착
- **신호 유형**: ECoG급 LFP 신호 — 단일 뉴런 스파이크는 기록 불가하나, 피질 표면 전위 변화를 혈관벽을 통해 기록
- **삽입 시간**: 중앙값 20분 (COMMAND 연구)
- **체내 모듈**: 흉부 피하에 매립된 내부 텔레메트리 유닛(ITU)이 무선으로 데이터 전송

#### 2.3.2 Stentrode의 전략적 포지셔닝

Stentrode는 N1 대비 정보 전달률이 낮지만(단일 뉴런 불가), 다음의 핵심 장점이 있다:
- **안전성**: 개두술 불필요 → 감염, 출혈, 뇌 조직 손상 위험이 근본적으로 낮음
- **확장성**: 인터벤션 방사선과(interventional radiology) 시설에서 시술 가능 → 특수 신경외과 센터에 국한되지 않음
- **Nvidia + Apple Vision Pro 통합**: AI 기반 신호 처리와 공간 컴퓨팅 환경의 결합으로 디지털 + 물리 환경 제어 시연

### 2.4 혈뇌장벽(Blood-Brain Barrier) 침투와 장기 생체 적합성

#### 2.4.1 이물질 반응(Foreign Body Response)의 분자 메커니즘

모든 침습형 BCI가 직면하는 근본적 과제는 뇌 조직의 이물질 반응이다:

**급성 반응 (삽입 후 수시간-수일)**:
- 전극 삽입 시 모세혈관 파열 → 혈뇌장벽(BBB) 국소 파괴
- 혈장 단백질(fibrinogen, albumin) 누출 → 전극 표면 단백질 흡착(protein fouling)
- 활성 미세아교세포(M1 표현형) 집합 → 전염증성 사이토카인(TNF-α, IL-1β, IL-6) 분비

**만성 반응 (수주-수개월)**:
- 반응성 성상세포가 전극 주위에 GFAP+ 아교세포 흉터(glial scar) 형성
- 흉터 두께: 50-200 μm → 전극과 목표 뉴런 사이 거리 증가
- 전기적 임피던스 증가 → 신호 대 잡음비(SNR) 저하
- 인접 뉴런의 사멸 또는 이동 → 기록 가능 뉴런 수 감소

**Neuralink N1의 접근**: 유연한 폴리이미드 스레드가 뇌 맥동(brain pulsation)에 동조하여 기계적 마찰을 최소화하고, 전극 단면적 축소(24 μm)로 BBB 파괴 범위를 줄여 FBR을 완화. 그러나 첫 번째 피험자에서 스레드 후퇴(retraction) 현상이 관찰되어 [5], 장기 안정성은 아직 완전히 검증되지 않았다.

#### 2.4.2 차세대 생체 적합성 전략

- **약물 방출 코팅**: 전극 표면에 덱사메타손(dexamethasone) 등 항염증제를 PLGA 미소구체에 담지하여 서방출
- **신경영양인자 방출**: BDNF, NGF 등을 전극 주위에 방출하여 뉴런 생존과 신경돌기 성장 촉진
- **전도성 고분자 코팅**: PEDOT:PSS, polypyrrole 등으로 전극 임피던스를 낮추고 전하 전달 용량(charge injection capacity) 증가
- **하이드로겔 인터페이스**: 부드러운 하이드로겔이 전극과 뇌 조직 사이 완충 층 역할

### 2.5 신경 디코딩 알고리즘

#### 2.5.1 전통적 알고리즘

**칼만 필터(Kalman Filter)**:
- 선형 동적 시스템 모델에 기반하여 시간에 따라 변하는 운동 의도(커서 위치, 속도)를 추정
- BrainGate2 등 초기 BCI의 표준 디코더
- 장점: 실시간 처리, 적은 연산량, 해석 가능성
- 한계: 선형 가정, 비정상(nonstationary) 신경 신호에 대한 적응 한계

**Population Vector Algorithm (PVA)**:
- Georgopoulos의 코사인 튜닝 모델에 기반, 각 뉴런의 preferred direction과 발화율로 운동 방향 벡터 합산
- 직관적이나, 비선형 튜닝이나 복잡한 운동 역학 모델링에 한계

#### 2.5.2 딥러닝 기반 디코더

**순환 신경망(RNN) / LSTM / GRU** [7]:
- 시계열 신경 데이터의 시간적 의존성 모델링에 적합
- LSTM(Long Short-Term Memory)이 vanishing gradient 문제를 해결하여 장기 시간 의존성 학습
- BCI 디코딩에서 칼만 필터 대비 15-30% 성능 향상 보고
- Neuralink의 디코딩 파이프라인에서 핵심 구성요소로 추정

**Transformer 기반 모델** [8]:
- Self-attention 메커니즘으로 시퀀스 내 장거리 의존성을 병렬 처리
- 운동 심상(motor imagery) EEG 분류에서 CNN, RNN 모델 대비 우수한 성능 입증
- Neural Data Transformer(NDT): 대규모 신경 데이터에서 사전학습(pretraining) 후 특정 태스크에 미세조정(fine-tuning)하는 파운데이션 모델 접근
- 장점: 병렬 연산으로 실시간 처리 가능, 교차 세션/교차 피험자 전이 학습(transfer learning) 잠재력

**CNN + RNN 하이브리드** [7]:
- CNN으로 공간적(spatial) 특징 추출 → RNN으로 시간적(temporal) 통합
- 다채널 신경 데이터의 공간-시간 구조를 동시에 활용

#### 2.5.3 적응형 학습과 폐쇄 루프

- **공동 적응(co-adaptation)**: 사용자의 뇌가 BCI에 적응하는 동시에, 디코더가 사용자의 변화하는 신경 패턴에 적응하는 양방향 학습
- **온라인 학습(online learning)**: 디코더 파라미터를 실시간으로 갱신하여 세션 간 신호 변동(비정상성)에 대응
- **폐쇄 루프(closed-loop) 제어**: 뇌 상태를 모니터링하고, 결과를 실시간으로 피드백하여 자극 파라미터를 자동 조정. DBS(Deep Brain Stimulation)에서 adaptive DBS로의 진화가 대표적

---

## 3. 임상 데이터: 주요 시험 결과

### 3.1 Neuralink PRIME Study (NCT06429735)

**설계**: Early Feasibility Study, 비무작위, 단일군
- 정식명: Precise Robotically IMplanted Brain-Computer InterfacE (PRIME)
- 대상: 사지마비(quadriplegia) 또는 ALS로 인한 상지 기능 상실
- 임플란트: N1 칩 (1,024 전극, 64 스레드)

**첫 번째 피험자 — Noland Arbaugh (2024년 1월)** [5]:
- 29세 남성, C4-C5 척수 손상으로 사지마비
- 삽입 후 수주 내: 생각만으로 컴퓨터 커서 제어, 온라인 체스, 웹 브라우징 시연
- 정보 전달률: 초기 4.6 BPS → 알고리즘 최적화 후 8.0 BPS (당시 BCI 세계 기록)
- **스레드 후퇴(thread retraction)**: 삽입 약 1개월 후 일부 스레드가 뇌 조직에서 후퇴, 유효 전극의 약 85%가 분리 — 성능 일시 저하
- Neuralink는 알고리즘 조정으로 성능을 거의 원래 수준으로 회복
- 원인 추정: 두개골 내 잔류 공기(air pocket)에 의한 스레드 움직임

**누적 데이터 (2025년 9월 기준)**:
- 12명의 피험자에 이식 완료
- 누적 2,000+ 기기일(device-days), 15,000+ 사용 시간
- ALS 환자 Brad Smith: 가정 환경에서 컴퓨터, 웹캠 독립 제어 달성

### 3.2 Synchron COMMAND Study (NCT05035823)

**설계**: Early Feasibility Study, 단일군
- 대상: 중증 운동 장애(ALS 등)
- 임플란트: Stentrode + 흉부 ITU

**결과 (2024년 10월, Congress of Neurological Surgeons 발표)** [9]:
- 6명 환자, 12개월 추적
- **1차 평가변수 (안전성)**: 기기 관련 심각한 이상반응(사망 또는 영구 장애 악화) 0건 — 100% 안전성 목표 달성
- **시술 성공**: 6/6 (100%) 정확한 운동 피질 배치, 중앙 삽입 시간 20분
- **기능 시연**: 모든 참가자에서 운동 의도 관련 뇌 신호를 digital motor output(DMO)으로 변환, iPad 제어, 디지털 태스크 수행 성공
- 3개 임상 센터: Mount Sinai, Gates Vascular Institute (UB), UPMC/CMU

### 3.3 Paradromics Connect-One Study

**FDA IDE 승인**: 2025년 11월 [10]
- 세계 최초 음성 복원(speech restoration) 적용 완전 이식형 BCI의 IDE 승인
- 대상: 중증 운동 장애로 인한 무발화증(anarthria)
- **Connexus BCI**: 7.5 mm 직경 어레이를 뇌 표면 1.5 mm 깊이에 삽입, 개별 뉴런 기록
- 전임상 정보 전달률: 200+ BPS — 업계 최고
- 표적 피질 영역: 운동 피질의 입술, 혀, 후두 제어 영역
- 첫 환자: 2026년 Q1 예정, 초기 2명 대상

### 3.4 뉴로모듈레이션: 상용화된 신경 자극 치료

#### 3.4.1 Deep Brain Stimulation (DBS)

**파킨슨병 DBS**:
- 승인 역사: 1997년 (FDA), Medtronic DBS System
- 표적: 시상하핵(subthalamic nucleus, STN) 또는 내측 창백핵(GPi)
- 효능: UPDRS 운동 점수 30-60% 개선, 약물 "off" 시간 50-60% 감소
- 글로벌 DBS 이식 누적: 200,000+ 환자

**치료 저항성 우울증 (TRD)**:
- 전측 대상회(subcallosal cingulate, SCC) DBS: Phase 2/3 연구에서 가변적 결과
- 적응형 DBS(adaptive/closed-loop DBS): 뇌 바이오마커를 실시간 모니터링하여 필요 시에만 자극 전달 → 부작용 감소와 효능 개선 기대

#### 3.4.2 반응형 신경자극 (Responsive Neurostimulation, RNS)

- **NeuroPace RNS System**: 약물 저항성 간질(epilepsy) FDA 승인 (2013년)
- 기전: 두개 내 전극이 발작 전조 패턴(seizure onset pattern)을 실시간 감지 → 자동으로 전기 자극을 전달하여 발작 전파 차단
- 장기 데이터: 9년 추적에서 발작 빈도 중앙값 75% 감소, 반응자(≥50% 감소) 비율 73%

---

## 4. 시장 분석

### 4.1 시장 규모

| 세그먼트 | 2025 | 2035 전망 | CAGR |
|---------|------|----------|------|
| BCI 임플란트 | $351M | $1.18B | 12.9% |
| BCI 전체 (비침습 포함) | $2.83B | $8.73B | 15.1% |
| 뉴로모듈레이션 (DBS 등) | $8B+ | $15B+ | ~8% |

### 4.2 경쟁 구도

**침습형 BCI (비상장 위주):**
| 기업 | 기술 | 차별점 | 밸류에이션 |
|------|------|--------|-----------|
| Neuralink | N1 (1,024ch, 완전 이식) | 최고 채널 수, 로봇 수술 | ~$8.5B (2024) |
| Synchron | Stentrode (혈관 내) | 비개두술, 안전성 | ~$500M+ |
| Paradromics | Connexus (고대역폭) | 200+ BPS, 음성 복원 | 비공개 |
| Blackrock Neurotech | Utah Array (96ch) | 20년+ 인간 데이터 | 비공개 |

**뉴로모듈레이션 (상장):**
| 기업 | 티커 | 주요 제품 | 시가총액 |
|------|------|----------|---------|
| Medtronic | MDT | DBS (StealthStation) | ~$110B |
| Abbott | ABT | Infinity DBS, SCS | ~$200B |
| Boston Scientific | BSX | Vercise DBS, SCS | ~$120B |
| NeuroPace | NPCE | RNS System | ~$500M |

### 4.3 핵심 투자 테제

1. **2025-2026이 BCI 상업화의 원년**: Neuralink 12명+, Synchron IDE 확대, Paradromics 첫 환자 — 임상 데이터 축적이 가속
2. **안전성 vs. 성능의 트레이드오프**: Neuralink(고성능/높은 침습) vs. Synchron(낮은 성능/높은 안전성) — 시장이 어디로 수렴할지는 장기 안전성 데이터에 달림
3. **뉴로모듈레이션은 이미 $8B+ 검증 시장**: MDT, ABT, BSX는 DBS/SCS로 안정적 매출. 적응형(closed-loop) DBS가 차세대 성장 동력
4. **핵심 기업 대부분 비상장**: Neuralink, Synchron, Paradromics 모두 사모 시장. 상장 IPO 시 접근 기회
5. **규제 프레임워크 형성 중**: FDA의 BCI 규제 가이드라인이 아직 확립되지 않아, 규제 리스크와 선점 기회가 공존
6. **AI + BCI = 메가트렌드**: 디코딩 알고리즘의 발전(Transformer, 파운데이션 모델)이 BCI의 정보 전달률을 비선형적으로 향상시킬 잠재력. 하드웨어보다 소프트웨어가 성능을 결정

---

## 5. AI 적용: BCI에서의 인공지능

### 5.1 실시간 신경 디코딩

AI는 BCI의 핵심 성능을 결정하는 요소이다. 하드웨어(전극 수)가 데이터의 입력 차원을 결정한다면, AI(디코딩 알고리즘)가 이 데이터로부터 의미있는 출력을 추출한다.

- **운동 디코딩**: 1,024채널 신경 데이터로부터 2D/3D 커서 궤적, 로봇 팔 관절 각도, 그립 유형을 실시간으로 추론
- **음성 디코딩**: 발화 의도를 담당하는 피질 영역(ventral sensorimotor cortex)의 신경 활동으로부터 음소(phoneme) → 단어 → 문장을 실시간 합성. 2023년 Stanford/BrainGate 팀이 RNN 디코더로 62 단어/분 속도 달성 [11]
- **감정/인지 상태 분류**: EEG/ECoG로부터 피로, 주의, 감정 상태를 ML 분류기가 실시간 추론 → 폐쇄 루프 신경자극에 활용

### 5.2 적응형 DBS와 폐쇄 루프 제어

- 전통 DBS: 고정 파라미터(주파수, 진폭, 펄스 폭)로 연속 자극 → "open-loop"
- AI 기반 적응형 DBS: 뇌 바이오마커(LFP의 베타 대역 파워 등)를 실시간 모니터링하고, RL(강화학습) 또는 제어 이론 기반 알고리즘이 자극 파라미터를 동적으로 조정 [12]
- 임상 효과: 연속 자극 대비 배터리 수명 연장, 부작용(구음 장애, 근긴장 이상) 감소, 동등 이상의 운동 증상 개선

### 5.3 뇌 영상 AI 분석

- **fMRI 디코딩**: Transformer 기반 모델이 fMRI BOLD 신호로부터 시각 자극, 언어 의미를 재구성 [7]
- **뇌 구조 세분화**: U-Net 등 딥러닝 모델이 MRI에서 피질 영역, 백질 경로를 자동 분할하여 전극 배치 계획에 활용
- **확산 모델 기반 뇌 이미지 생성**: 신경 활동 패턴으로부터 시각 장면을 재구성하는 generative AI — 시각 보철(visual prosthesis)의 기반 기술

### 5.4 파운데이션 모델과 전이 학습

2024년부터 BCI 분야에서 "Neural Foundation Model" 개념이 부상 [7]:
- 대규모 신경 데이터(다수 피험자, 다수 세션)로 사전학습한 범용 디코더
- 새로운 피험자/세션에 적은 데이터로 미세조정(few-shot adaptation)
- 교차 피험자 일반화 능력 → 임상 확장의 핵심 기술
- 이 접근이 성공하면 "개인별 디코더 훈련"이 필요 없는 즉시 사용 가능 BCI 실현

---

## 6. 참고문헌

[1] Georgopoulos AP, Schwartz AB, Kettner RE. "Neuronal population coding of movement direction." *Science*. 1986;233(4771):1416-1419.
https://www.science.org/doi/10.1126/science.3749885

[2] Normann RA. "Technology Insight: future neuroprosthetic therapies for disorders of the nervous system." *Nature Clinical Practice Neurology*. 2007;3(8):444-452.
https://www.nature.com/articles/ncpneuro0556

[3] Hochberg LR, Bacher D, Jarosiewicz B, et al. "Reach and grasp by people with tetraplegia using a neurally controlled robotic arm." *Nature*. 2012;485(7398):372-375.
https://www.nature.com/articles/nature11076

[4] Musk E, Neuralink. "An Integrated Brain-Machine Interface Platform With Thousands of Channels." *Journal of Medical Internet Research*. 2019;21(10):e16194.
https://www.jmir.org/2019/10/e16194

[5] Wikipedia. "Noland Arbaugh — First Neuralink PRIME Study Patient." 2024-2025.
https://en.wikipedia.org/wiki/Noland_Arbaugh

[6] Oxley TJ, Opie NL, John SE, et al. "Minimally invasive endovascular stent-electrode array for high-fidelity, chronic recordings of cortical neural activity." *Nature Biotechnology*. 2016;34(3):320-327.
https://www.nature.com/articles/nbt.3428

[7] Li Z, et al. "Neural decoding for EEG-BCI: from conventional machine learning to deep learning models." *Current Opinion in Biomedical Engineering*. 2026.
https://www.sciencedirect.com/science/article/pii/S2589238X26000021

[8] Kim D, et al. "Advancing BCI with a transformer-based model for motor imagery classification." *Scientific Reports*. 2025;15:6364.
https://www.nature.com/articles/s41598-025-06364-4

[9] Synchron. "Positive Results from U.S. COMMAND Study of Endovascular Brain-Computer Interface." Business Wire, October 2024.
https://www.businesswire.com/news/home/20240930433219/en/Synchron-Announces-Positive-Results-from-U.S.-COMMAND-Study-of-Endovascular-Brain-Computer-Interface

[10] Paradromics. "FDA Approval for the Connect-One Clinical Study with the Connexus Brain-Computer Interface." November 2025.
https://www.paradromics.com/news/paradromics-receives-fda-approval-for-the-connect-one-clinical-study-with-the-connexus-brain-computer-interface

[11] Willett FR, Kunz EM, Fan C, et al. "A high-performance speech neuroprosthesis." *Nature*. 2023;620(7976):1031-1036.
https://www.nature.com/articles/s41586-023-06377-x

[12] Neumann WJ, Turner RS, Bhatt B, et al. "Adaptive deep brain stimulation: From experimental evidence toward practical implementation." *Movement Disorders*. 2023;38(6):937-948.
https://movementdisorders.onlinelibrary.wiley.com/doi/10.1002/mds.29415

[13] ClinicalTrials.gov. "Precise Robotically IMplanted Brain-Computer InterfacE (PRIME)." NCT06429735.
https://clinicaltrials.gov/study/NCT06429735

[14] Angrick M, et al. "Brain-computer interfaces in 2023-2024." *Brain-X*. 2025.
https://onlinelibrary.wiley.com/doi/full/10.1002/brx2.70024

---

*면책조항: 본 리뷰는 정보 제공 목적으로 작성되었으며, 특정 종목에 대한 투자 권유가 아닙니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.*
