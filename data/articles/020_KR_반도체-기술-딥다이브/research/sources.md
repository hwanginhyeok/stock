# KR-02 리서치: 반도체 기술 딥다이브

> 작성일: 2026-03-04
> 아티클: KR-02 "반도체 기술 딥다이브" (제목 미정)
> 상태: 리서치 완료, 구조 확정 대기

---

## 아티클 테제

> "반도체의 미래는 더 작은 회로가 아니라, 더 잘 쌓고 더 잘 연결하는 기술에 달려 있다.
> 그리고 그 기술의 수율 격차가 곧 기업의 운명을 가른다."

**KR-01과의 관계:**
- KR-01 = "왜 HBM이 중요한가" (경제/비즈니스 — 돈의 흐름)
- KR-02 = "왜 이 기술이 이렇게 어렵고, 누가 할 수 있는가" (기술/엔지니어링)

---

## 1. HBM 제조 공정 딥다이브

### 1.1 TSV (Through-Silicon Via)

| 항목 | 수치 | 비고 |
|------|------|------|
| TSV 직경 | 5~10 μm | 세대마다 축소 추세 |
| TSV 종횡비 (aspect ratio) | ~10:1 | 직경 대비 깊이 |
| 마이크로 범프 직경 | ~25 μm | 피치 55 μm |
| HBM3 마이크로 범프 피치 | 73 μm | 고밀도 수직 I/O |
| HBM4 TSV 피치 목표 | 8~9 μm | 현재 대비 대폭 축소 |

- TSV = 실리콘 다이를 수직으로 관통하는 미세 구리 구멍
- 칩 가장자리로 신호를 우회할 필요 없이 직접 수직 연결
- 세대마다 더 많은 TSV를 더 좁은 피치로 배치해야 → 제조 난이도 지수적 증가

> 출처: SemiEngineering, Wevolver, Eureka PatSnap

### 1.2 다이 시닝 (Die Thinning)

| 항목 | 수치 |
|------|------|
| 표준 실리콘 웨이퍼 두께 | ~775 μm |
| HBM DRAM 다이 두께 (현재) | 30~50 μm |
| HBM4 16-Hi 다이 두께 | ~30 μm (머리카락의 1/3) |
| 삼성 12-Hi HBM3E 칩 간 간격 | 7 μm (업계 최소) |
| JEDEC 총 스택 높이 제한 | 720 μm (HBM3) → **775 μm** (HBM4) |

**왜 시닝이 필요한가:**
- 775 μm 높이 제한 안에 16개 다이 + 베이스 다이 + 마이크로 범프를 맞춰야
- 775 ÷ 16 ≈ 48 μm/다이 (범프와 베이스 다이 고려하면 실질 30μm 이하)

**리스크:**
- 얇을수록 휨(warpage)과 파손 위험 증가
- 휨 → 정렬 불량 → 본딩 품질 저하 → 보이드(void), 전기적 단선
- 열 성능 저하 (불완전 본딩 접점)
- 더 높은 스택(8→12→16)일수록 문제 악화

> 출처: TrendForce, SemiEngineering, Samsung Newsroom, SK Hynix Newsroom, Vik's Newsletter

### 1.3 스태킹: 12단 vs 16단

**"4장 더 쌓으면 되는 거 아닌가?"에 대한 답:**

1. **JEDEC 높이 제한**: 모든 레이어가 775 μm 안에 들어가야 → 다이를 더 얇게 깎아야
2. **TSV 밀도 증가**: 더 많은 TSV를 더 좁은 피치로 → 제조 정밀도 요구 상승
3. **열 밀도**: 같은 면적에 더 많은 다이 → 발열 문제 기하급수적 증가
4. **정렬 공차 누적**: 각 레이어 범프가 아래 레이어와 정밀 정렬 필요 — 오차 누적
5. **JEDEC 규격 완화**: 2025년 HBM4 패키지 두께를 720→775 μm로 완화 — 이 결정이 하이브리드 본딩 없이 16단을 가능하게 함

**현재 상태:**
- HBM3E: 8-Hi (24GB), 12-Hi (36GB) 양산 중
- HBM4 12-Hi (36GB): 2026년 초 양산 개시
- HBM4 16-Hi (48GB): SK하이닉스 CES 2026 시연 — 11.7 Gbps, 2 TB/s 대역폭

> 출처: TrendForce, TweakTown, WCCFTECH

### 1.4 수율의 수학 — 지수 법칙

**공식:** 최종 스택 수율 = (단일 다이 수율)^(적층 수)

| 단일 다이 수율 | 8단 | 12단 | 16단 |
|--------------|------|------|------|
| **99%** | 92% | 89% | **85%** |
| **97%** | 78% | 69% | **61%** |
| **95%** | 66% | 54% | **44%** |
| **90%** | 43% | 28% | **19%** |

- **핵심**: 다이 수율 99% vs 95%는 4%p 차이지만, 16단 스택에서는 85% vs 44% = **41%p 차이**
- SK하이닉스 HBM3E 수율 ~80% (MR-MUF)
- 삼성 HBM3 수율 초기(2024년 초) **10~20%** → HBM3E 개선 후 ~50~60%

> 출처: NomadSemi, SemiAnalysis, Eureka PatSnap

### 1.5 KGD (Known Good Die) 테스팅

- 스택에서 1개 다이라도 불량이면 **전체 패키지(8~16다이 + 베이스 다이) 폐기**
- KGD 스크리닝은 웨이퍼 단계에서 완료 → 불량 다이가 스태킹에 진입하는 것 방지
- KGD 테스팅으로 최종 수율 **10%+ 개선** 가능
- HBM3E: 9.6 GT/s 데이터 레이트 → 고속 테스트 장비 + 열 관리 MEMS 프로브 필요
- 16단으로 갈수록 웨이퍼 단계 테스트의 중요성 기하급수적 증가

> 출처: FormFactor, Semiecosystem (Mark Lapedus)

---

## 2. MR-MUF vs TC-NCF — 수율 격차의 기술적 원인

### 2.1 MR-MUF (Mass Reflow Molded Underfill) — SK하이닉스

**공정:**
1. 여러 DRAM 다이를 기판/베이스 다이 위에 배치
2. **일괄 리플로우(batch reflow)**로 전체 스택을 한 번에 본딩
3. 칩 간 간격과 마이크로 범프 갭을 **EMC(Epoxy Molding Compound)**로 동시 충전
4. 상온에서 최소 압력으로 진행
5. 리플로우 온도: ~260°C, 압력 최소

**핵심 소재:**
- EMC4: 열 전도성 우수한 열경화성 폴리머
- Advanced MR-MUF (2023 도입): EMC 열전도율 **1.6배** 향상
- EMC는 NCF 필름 대비 열전도율 **약 2배**

**장점:**
| 항목 | 수치 |
|------|------|
| 열 더미 범프 | TC-NCF 대비 **4배** 많음 |
| 방열 개선 (HBM2E vs HBM2) | **36%** |
| 최대 접합부 온도 | TC-NCF 대비 **14°C 낮음** |
| 수율 | ~**80%** |

> 출처: SK Hynix Newsroom, EE Times, NomadSemi

### 2.2 TC-NCF (Thermo-Compression Non-Conductive Film) — 삼성

**공정:**
1. 각 다이에 NCF(비전도 필름) 도포
2. **한 다이씩 순차적으로** 열압착 본딩
3. 고온 **~300°C** + 강한 압축력 필요
4. 본딩 후 NCF가 다이 간 갭을 채움

**한계:**
| 항목 | 문제 |
|------|------|
| 처리량 | 순차 본딩 → MR-MUF 대비 현저히 낮은 throughput |
| 온도 | 300°C → 휨(warpage) 위험 |
| 압력 | 강한 압축력 → 칩 물리적 손상 가능 |
| 열 성능 | NCF가 **단열재** 역할 → 층 간 열이 갇힘 |
| 수율 | **~50~60%** (MR-MUF 대비 ~20%p 낮음) |

> 출처: NomadSemi, Medium (Pouya Asrar), TrendForce

### 2.3 삼성의 선택: MR-MUF가 아닌 하이브리드 본딩

- 삼성은 MR-MUF로 전환하지 **않음**
- 대신 **하이브리드 본딩**(copper-to-copper 직접 접합, "bumpless" 스태킹)으로 세대 도약 시도
- 마이크로 범프 완전 제거 → 구리-구리 + 산화물-산화물 직접 연결
- 더 얇고 열효율 높은 스택 가능
- 2026년 3월 이후 하이브리드 구리 본딩 생산 라인 장비 설치·테스트 시작
- **초기 수율: ~10%** — 극도로 초기 단계

> 출처: Tom's Hardware, TrendForce

---

## 3. HBM4 아키텍처 전환

### 3.1 로직 베이스 다이 — 근본적 변화

**이전 세대 (HBM3E 이하):** 베이스 다이 = 기존 DRAM 공정 (단순 로직)

**HBM4:** 베이스 다이 = **첨단 파운드리 공정**으로 제조 (DRAM 공정 아님)
→ 캐시, 제어 로직, 기타 기능 통합 가능 — 이전에는 GPU/SoC가 처리하던 것들

### 3.2 로직 다이 제조사 — 3사 3색 전략

| 회사 | 파운드리 | 공정 노드 | 비고 |
|------|---------|----------|------|
| **SK하이닉스** | **TSMC** | 12nm (표준), 5nm (중급), **3nm** (커스텀, NVIDIA용) | 세계 최고 파운드리 접근, but 의존성 |
| **삼성** | **삼성 파운드리 (자체)** | 4nm (현재), **2nm** (커스텀 HBM 목표) | 유일한 "턴키" — 파운드리+패키징 통합 |
| **Micron** | DRAM 공정 (HBM4), **TSMC** (HBM4E) | HBM4E부터 파운드리 전환 (2027) | 가장 보수적, 성능 열세 리스크 |

**TSMC 상세:**
- N12 노드 HBM4 베이스 다이: 동작 전압 1.1V → **0.8V** 절감
- C-HBM4E (커스텀): N3P (3nm) 로직 다이, **~2배 효율** 향상, 2027
- 5nm HBM4 베이스 다이도 개발 중

> 출처: KED Global, TrendForce, Design-Reuse, Tom's Hardware, Digitimes

### 3.3 JEDEC HBM4 표준 (JESD270-4, 2025년 4월 16일 발행)

| 항목 | HBM3E | HBM4 |
|------|-------|------|
| 인터페이스 폭 | 1024-bit (16채널) | **2048-bit (32채널)** |
| 전송 속도 | 최대 9.6 Gb/s | 최대 **8 Gb/s** (초기), 11.7 Gbps (SK하이닉스 CES 시연) |
| 스택당 대역폭 | ~1.2 TB/s | **최대 2 TB/s** |
| 스택 구성 | 4/8/12-Hi | 4/8/12/**16-Hi** |
| 다이 밀도 | 16Gb/24Gb | 24Gb/**32Gb** |
| 최대 용량 | 36GB (12-Hi) | **64GB** (32Gb × 16-Hi) |
| 패키지 두께 | 720 μm | **775 μm** |
| 전압 | 1.1V | 0.7~0.9V (벤더별) |

> 출처: JEDEC, Tom's Hardware, All About Circuits

### 3.4 HBM4E 로드맵

| 항목 | 수치 |
|------|------|
| 발표 예상 | 2026년 하반기 |
| 양산 | 2027~2028 |
| 용량 목표 | 64GB/스택, 일부 보고 **100GB** 가능 |
| 속도 | 최대 **12.8 GT/s** |
| TSMC C-HBM4E | N3P (3nm) 로직 다이, ~2배 효율 |
| 삼성 커스텀 HBM4E | 2026년 중반 설계 목표 |
| Micron | TSMC 파운드리 파트너십, 2027 |

> 출처: Tom's Hardware, TrendForce

### 3.5 HBM4가 바꾸는 경쟁 구도

**HBM 시장 점유율 변동:**

| 시점 | SK하이닉스 | 삼성 | Micron |
|------|----------|------|--------|
| 2024 초 | ~50% | **60%+** (이전 선두) | 소량 |
| 2025 Q2 | **62%** | **17%** | 21% |
| 2025 Q3 | **57%** | 22% | 21% |
| 2026 전망 | ~50% | **30%+** (회복 시도) | ~20% |

- 삼성: 60%→17%로 점유율 붕괴. Micron에도 추월당함
- SK하이닉스: 2025년 최초로 삼성 연간 이익 추월
- HBM 시장 규모: $38B (2025) → **$58B** (2026)

**HBM4 경쟁 구도 변화:**
1. **삼성의 턴키 잠재력**: 유일하게 파운드리+패키징 통합 가능. 성공하면 최강의 원가 구조
2. **SK하이닉스의 TSMC 의존**: 최고 파운드리 접근 but 공급망 의존성
3. **Micron의 보수적 접근**: HBM4는 DRAM 공정, HBM4E부터 TSMC → 성능 열세 리스크
4. **NVIDIA의 전략**: 삼성과 하이닉스 모두 용량/수율 한계 → HBM4 스펙 완화 검토 (2026년 2월)

> 출처: Astute Group, CNBC, KED Global, Bloomberg, TrendForce

---

## 4. 어드밴스드 패키징

### 4.1 TSMC CoWoS 현황

**월간 생산능력 (KWPM):**

| 시점 | 용량 |
|------|------|
| 2024년 말 | ~35,000~40,000 |
| 2025년 말 | ~75,000~80,000 |
| 2026년 말 (목표) | **120,000~130,000** |

- 2022~2026 CAGR: **80% 이상**
- 매년 2배씩 늘려도 "sold out" 상태 지속
- NVIDIA가 2026~2027 CoWoS 용량의 **50% 이상** 확보 (CoWoS-L은 60~70%)
- 가격: 매년 **10~20% 인상**, Morgan Stanley는 향후 2년간 20% 추가 인상 전망

### 4.2 CoWoS 변형 비교

| 특성 | CoWoS-S (Standard) | CoWoS-L (LSI) | CoWoS-R (RDL) |
|------|-------------------|---------------|---------------|
| 인터포저 소재 | 실리콘 | LSI + 유기 기판 | RDL / 유기 기판 |
| 최대 면적 | ~2,500 mm² (리소그래피 한계) | CoWoS-S보다 큼 | 유연 |
| HBM 지원 | 최대 6스택 | **최대 12스택** | 가변 |
| 비용 | 최고 | S보다 낮음 | 최저 |
| 대표 제품 | H100, AMD MI300 | **NVIDIA Blackwell** (2 SoC + 8 HBM) | 네트워킹 |

### 4.3 "More than Moore" — 패러다임 전환

- 트랜지스터 축소(전통적 무어의 법칙)가 아닌 **이종 집적(heterogeneous integration)**에서 성능 향상
- 비싼 2nm/3nm은 핵심 컴퓨트에만, 저렴한 성숙 노드는 I/O/아날로그에
- 어드밴스드 패키징 시장: $42~51B (2025) → **$70~90B** (2034)
- ASML: Q3 2025 첫 어드밴스드 패키징 리소그래피 장비 출하 — 리소 장비사도 패키징 피벗

### 4.4 TSMC vs 삼성 패키징 기술

**TSMC:**
- CoWoS (S/L/R), InFO, SoIC
- **SoW-X** (2027 양산): 300mm 웨이퍼 전체 사용, 40+ 리티클 컴퓨트 다이 + 60+ HBM 통합
  - 현재 CoWoS 대비 **40배 컴퓨팅 파워**
  - 전력: 최대 17,000W, 성능/와트 **65% 향상**
- SoIC: 하이브리드 본딩 (서브마이크론 피치), 2027년 3μm 피치 목표

**삼성:**
- I-Cube4 (2.5D), X-Cube (3D), H-Cube (하이브리드)
- **SoP (System-on-Panel)**: 415 × 510 mm 초대형 패널 패키징
  - 웨이퍼 크기 한계 돌파 — 모듈 한 변 210mm+ 가능
  - **Tesla Dojo "AI6" 칩**용 개발 중
  - 도전: 가장자리 휨, 양산 안정성, 고밀도 RDL
- 삼성 요코하마 패키징 R&D 센터 $170M 투자, 2027년 3월 오픈
- **고유 장점**: 로직 + HBM + 패키징 **올인하우스** (TSMC는 메모리 안 만듦)

### 4.5 패키징이 AI 칩 공급의 병목

- TSMC CoWoS가 **바인딩 제약** — 웨이퍼 fab이 아니라 패키징이 병목
- NVIDIA 단독으로 CoWoS 용량 50~70% 차지
- OSAT 파트너(ASE CoWoP, Amkor)가 대안 제공 시도 but TSMC 품질 미달
- TSMC: 8개 CoWoS 시설 확장 중 (치아이 AP7 = 세계 최대 어드밴스드 패키징 허브)

> 출처: TrendForce, FinancialContent, SmBom, TweakTown, AJU Press, FusionWW, Digitimes

---

## 5. 차세대 메모리 기술

### 5.1 CXL 4.0 (Compute Express Link)

**사양:** CXL 4.0 스펙 2025년 11월 18일 발행

| 항목 | CXL 4.0 | HBM3e | HBM4 |
|------|---------|-------|------|
| 대역폭 | ~1.5 TB/s (x16 번들) | 4.8 TB/s | 최대 13 TB/s |
| 레이턴시 | ~200 ns 추가 | 거의 0 (온패키지) | 거의 0 |

- CXL은 HBM 대역폭의 ~30% — **대체가 아닌 보완**
- **역할 분담**: HBM = 컴퓨트 인접 고대역, CXL = 대용량 메모리 확장·풀링

**LLM 활용:**
- 70B 파라미터 모델 + 128K 컨텍스트 + 배치 32 → KV 캐시만 150+ GB (H100 80GB 초과)
- CXL 솔루션: KV 캐시를 풀링 메모리에 → 핫 레이어만 GPU VRAM에
- 성능: SSD 대비 **21.9배 처리량**, **60배 에너지 효율** / RDMA 대비 5배 이상
- Microsoft: 2025년 11월 업계 최초 CXL 장착 클라우드 인스턴스 출시

**양산 일정:**
- CXL 3.x/4.0 메모리 확장 디바이스: 2025년 양산
- 멀티랙 메모리 풀링: **2026~2027** 양산 배치 목표

> 출처: CXL Consortium, Introl, Asteral Labs, XConn/MemVerge

### 5.2 PIM (Processing-in-Memory)

**SK하이닉스 포트폴리오:**
- **AiMX**: GDDR6-AiM 칩 기반 가속 카드, LLM 추론 특화 (어텐션 연산)
  - vLLM 프레임워크 사용, CES 2026 시연, **상용 출시**
- **CuD (Compute-using-DRAM)**: DRAM 셀 내에서 연산 수행, CES 2026 시연 (프리프로덕션)
- **CMM-Ax**: CXL 메모리 모듈에 연산 기능 추가, CES 2026 시연 (프리프로덕션)

**삼성 HBM-PIM:**
- HBM 최초 PIM 통합 구현
- 성능 **2배**, 에너지 소비 **~50% 절감**
- 시스템 대비 에너지 **70% 절감**
- LPDDR5X-PIM 개발 중 (엣지/온디바이스 AI)

**PIM이 해결하는 것:**
- 데이터 이동 병목 제거 — 메모리↔컴퓨트 왕복 대신 **데이터가 있는 곳에서 연산**
- 추론 워크로드(어텐션, 추천, 음성인식)에 특히 효과적

> 출처: SK Hynix Newsroom, Samsung Semiconductor, WinBuzzer

### 5.3 GDDR7 vs HBM — 다른 레인

| 특성 | GDDR7 | HBM4 |
|------|-------|------|
| 디바이스당 대역폭 | 128~192 GB/s | 최대 2 TB/s |
| 8개 집합 대역폭 | ~1~1.5 TB/s | 최대 13 TB/s |
| 아키텍처 | 칩 주변 배치, 표준 PCB | 수직 적층, 인터포저 위 |
| 에너지 효율 | HBM 대비 낮음 (비트당) | 높음 (낮은 클럭, 넓은 버스) |
| 비용 | HBM 대비 **~50% 저렴** (GB당) | 고가, 복잡한 패키징 |
| 주요 용도 | 게이밍, 엣지 AI, 추론 | DC AI 훈련, HPC |

**NVIDIA의 이중 레인 전략:**
- **Rubin Ultra (HBM4)**: AI 훈련 + 디코드 (메모리 대역폭 바운드)
- **Rubin CPX (128GB GDDR7)**: LLM 추론 프리필 (컴퓨트 바운드). 30 PetaFLOPS NVFP4. **2026년 말 출시**
- NVL144 랙에서 HBM Rubin + GDDR7 Rubin CPX가 **코프로세서**로 협업

> 출처: TrendForce, TweakTown, NVIDIA Newsroom, Rambus

### 5.4 LPDDR6

- JEDEC LPDDR6 표준 (JESD209-6): **2025년 7월 9일** 발행
- 플랫폼 인증: 2026년
- 대량 채택: **2027년**
- SK하이닉스: ISSCC 2026에서 상세 발표
- 삼성 LPDDR6: CES Innovation Awards 2026 수상

> 출처: JEDEC, All About Circuits, Samsung

### 5.5 광학 인터커넥트

**핵심 진전:**
- IMEC + NLM Photonics: 실리콘 포토닉스로 **레인당 400 Gbps** 달성/근접
- NVIDIA Quantum-X InfiniBand: TSMC COUPE 기술로 광학 변환을 **프로세서 패키지 내부**로 이동
- **Marvell, Celestial AI $3.25B 인수** (2026년 3월 마감)
  - "Photonic Fabric": 패키지 가장자리가 아닌 **컴퓨트 다이 어느 위치로든** 광학 데이터 전달
  - CPO(co-packaged optics) 대비 **25배 대역폭, 10배 낮은 레이턴시**
  - 1세대 칩릿: 단일 칩릿 **16 Tbps**
  - 각 XPU가 다른 모든 XPU의 메모리에 직접 접근 가능 (디스어그리게이티드 컴퓨트-메모리)
  - Marvell: H2 FY2028 의미있는 매출, Q4 FY2028 **$500M ARR** 목표
- Co-packaged optics 시장: 2026~2036 **CAGR 37%**, $20B+
- 실리콘 포토닉스 시장: $2.86B (2025) → **$28.75B** (2034)

> 출처: IEEE Spectrum, Marvell, Tom's Hardware, Semiconductor-Today

### 5.6 뉴로모픽 컴퓨팅

**Intel Loihi:**
- Loihi 2 벤치마크: NVIDIA Jetson Orin Nano 대비 **75배 낮은 레이턴시**, **1,000배 에너지 효율**
- Loihi 3 상용 출시 발표. Q3 2026 상용화 계획 (헬스케어, 자율주행, 산업자동화)
- BMW: Loihi 2 클러스터로 실시간 교통 표지 인식 / Lockheed Martin: 자율 드론 항법

**시장:** $8~9.5B (2025) → $45~59B (2030~2033)

**주류 AI와의 관계:** 근기적으로는 제한적. 엣지 추론, 센서 처리, 초저전력 시나리오에 적합. GPU 기반 훈련/대규모 추론과는 경쟁 아님.

> 출처: Intel, Nature Communications, TrainTheAlgo

---

## 6. 삼성 vs SK하이닉스 기술 격차

### 6.1 공정 노드 비교

| 노드 | SK하이닉스 | 삼성 | Micron |
|------|----------|------|--------|
| 1a (4세대 10nm) | 양산 | 양산 | 양산 |
| 1b (5세대 10nm) | 양산 | 양산 (P2D, ~150K wpm) | 양산 |
| 1c (6세대 10nm) | 양산 준비, **EUV 6레이어** | 수율 ~50~60%, HBM4 2026 목표 | 1-beta (1b) 사용 |
| 1d (7세대 10nm) | 2026~2027 예상 | 2026 발표 | 2026~2027 |
| 0a (서브 10nm) | 연구 중 | 2027 목표 (**InGaO 소재** 돌파) | TBD |

### 6.2 EUV 도입 현황

| 회사 | 1b EUV 레이어 | 1c EUV 레이어 | High-NA EUV |
|------|-------------|-------------|-------------|
| SK하이닉스 | 3~4 | **5~6 (선도)** | DRAM 최초 설치 (2025) |
| 삼성 | 3~4 | 5+ | 2025년 말 수령, 총 5대 구매 |
| Micron | 비슷 | 미공개 | 평가 중 |

- SK하이닉스: 2027년까지 EUV 장비 **2배** 확대, 글로벌 3위 EUV 보유 예상

### 6.3 삼성의 조직·전략적 문제

**기술적 실패:**
- HBM3, HBM3e NVIDIA 인증 테스트 **발열·전력 소비** 문제로 탈락
- HBM3 수율: 2024년 초 **10~20%** vs SK하이닉스 60~70%
- TC-NCF 고수 → 이후 SK하이닉스 방식 일부 채택

**조직 대응:**
- 부회장 전영현 공개 사과 (Q3 2024 실적 발표 전)
- **2,000명 엔지니어** 기흥·화성 → 평택 생산기지 이동
- 통합 메모리 개발 조직 신설, HBM 개발팀 DRAM 설계 부문 직속 편입
- 파운드리 부문: 낮은 EUV 가동률 + Taylor 텍사스 $17B 시설 지연으로 지속 적자

**점유율 붕괴:**
- HBM 점유율: **60%+ → 17%**
- SK하이닉스 시가총액이 삼성전자의 **절반**을 처음 돌파 (2025년 1월)

### 6.4 삼성의 HBM4 추격 전략

| 항목 | 내용 |
|------|------|
| DRAM 공정 | 1c (6세대 10nm) — Micron(1b)보다 1세대 앞 |
| 로직 다이 | 4nm 자체 파운드리 |
| HBM4 샘플 | 2025년 11월 NVIDIA 납품, Q1 2026 계약 전 유료 샘플 |
| 생산능력 | 2026년 **50% 증산** 계획 (17만 → **25만** wpm) |
| NVIDIA 인증 | 2026년 Q2 최종 인증 예상 (Bloomberg) |
| 가격 전략 | SK하이닉스와 **동가(parity)** 목표 |

- UBS 전망: NVIDIA Vera Rubin HBM4 수요의 SK하이닉스 ~70%, 삼성+Micron 나머지
- 삼성이 Q2 2026 납품 성공 시, 격차가 ~6개월 → **~1분기**로 축소

### 6.5 CXMT (중국) — 역량과 한계

| 항목 | 수치 |
|------|------|
| 월간 웨이퍼 | 240,000~280,000 wpm (2025 말), 2026 최대 300,000 |
| 2025년 연간 생산 | 273만 장 (전년 대비 **68%** 증가) |
| 글로벌 DRAM 점유율 | **5~7%** (2025 말) |
| DDR5 수율 | 80% 달성, 90% 목표 |
| IPO | 상하이 증권거래소 **$4.2B** IPO 신청 |

**핵심 한계:**
- **서브 18nm 제조 장비 접근 불가** (미국 수출 규제)
- **EUV 리소그래피 사용 불가**
- HBM 생산 불가 (첨단 패키징 + 첨단 DRAM 노드 필요)
- **범용 DRAM (DDR4, DDR5, LPDDR5X)에서만 경쟁**
- 2025년 말~2026년 초 용량 **정체** (장비 접근 제한)

### 6.6 DRAM 시장 신규 진입 가능성

**사실상 불가능 (선단 공정 기준):**

1. **자본 집약**: 선단 DRAM 팹 = **$15~20B+**, 세대마다 재투자 필수
2. **시장 집중**: 삼성+SK하이닉스+Micron = **93%** (10년 이상 안정적 과점)
3. **기술 전문성**: 수십 년 축적된 공정 노하우. 삼성도 40년 경험에도 HBM 수율 50%
4. **IP 장벽**: 수천 건의 DRAM 공정 특허
5. **고객 인증**: NVIDIA, Apple 등 멀티쿼터 인증 프로세스

- Nanya, Winbond: 니치 세그먼트(산업용, 저전력, 자동차)에서 생존
- CXMT: 막대한 국가 지원($4.2B IPO + 정부 보조)에도 범용 DRAM만 가능

> 출처: Mordor Intelligence, Wikipedia, Z2Data, Tom's Hardware, Digitimes

---

## 7. 추가 비용 컨텍스트

| 항목 | 수치 | 출처 |
|------|------|------|
| HBM이 GPU 제조원가에서 차지하는 비율 | **50~60%** | Vik's Newsletter |
| HBM GB당 비용 | $20~100 | Vik's Newsletter |
| 표준 DRAM GB당 비용 | $10 미만 | Vik's Newsletter |
| CoWoS 가격 인상 (2025~2026) | 매년 **10~20%** | TrendForce, SmBom |
| 4nm 웨이퍼 가격 | ~$20,000 | 업계 추정 |
| 2nm 웨이퍼 가격 예상 | **$30,000 이상** | Morgan Stanley |

---

## 출처 종합

### HBM 제조 공정
- SemiEngineering — What's Next For TSVs
- SemiEngineering — What's Next for High Bandwidth Memory
- Wevolver — HBM Deep Dive
- Eureka PatSnap — HBM4 TSV Pitch Density Targets
- Eureka PatSnap — HBM4 Stack Configurations
- TrendForce — Breaking the Memory Wall: HBM Basics
- Samsung Newsroom — 36GB HBM3E 12H
- SK Hynix Newsroom — Back Grinding
- Vik's Newsletter — Why is HBM so Hard to Manufacture
- NomadSemi — Deep Dive on HBM
- SemiAnalysis — Scaling the Memory Wall
- FormFactor — KGD Test for Advanced Packaging and HBM
- Semiecosystem (Mark Lapedus) — Test Challenges for DRAMs and HBM

### MR-MUF vs TC-NCF
- SK Hynix Newsroom — MR-MUF Unlocks HBM Heat Control
- EE Times — SK Hynix MR-MUF Innovations
- EE Times — How SK Hynix Redefined the Memory Market
- Medium (Pouya Asrar) — HBM Runs Hot: Samsung's Advanced TC-NCF
- Tom's Hardware — Samsung to Adopt Hybrid Bonding for HBM4
- TrendForce — Samsung Considers Hybrid Bonding a Must for 16-Stack HBM
- TrendForce — SK Hynix May Stick With MR-MUF for HBM4 16-High

### HBM4 아키텍처
- JEDEC Press Release — JESD270-4 HBM4 Standard
- Tom's Hardware — JEDEC Finalizes HBM4 Standard
- KED Global — SK Hynix to Produce HBM4 on 3nm
- TrendForce — Samsung Moves Custom HBM Logic Die to 2nm
- Design-Reuse — Samsung to Mass-Produce HBM4 on 4nm
- TrendForce — Memory Giants Diverge on HBM Base Die
- Tom's Hardware — Micron and TSMC for HBM4E
- TrendForce — TSMC C-HBM4E Details
- SK Hynix Newsroom — CES 2026
- Bloomberg — Samsung Nears Nvidia's Approval for HBM4

### 패키징
- TrendForce — TSMC CoWoS Capacity to Record 75,000 in 2025
- FinancialContent — TSMC to Quadruple CoWoS to 130K by Late 2026
- SmBom — TSMC 2025 CoWoS Pricing Soars 20%
- 7evenguy — CoWoS-S, CoWoS-R, CoWoS-L
- TrendForce — Blackwell Enters the Scene: CoWoS
- Halocarbon — More than Moore through Advanced Packaging
- TrendForce — ASML First Advanced-Packaging Tool Ships
- TrendForce — Samsung SoP Packaging on Ultra-Large Panel
- PC Gamer — TSMC SoW-X
- AJU Press — Packaging the Real Bottleneck for Samsung
- FusionWW — Inside the AI Bottleneck: CoWoS, HBM, and Capacity
- Digitimes — TSMC Expands CoWoS, Nvidia Over Half for 2026-27

### 차세대 메모리
- CXL Consortium — CXL 4.0 Release (BusinessWire)
- Introl Blog — CXL 4.0 and the Interconnect Wars
- Asteral Labs — How CXL Transforms RAG and KV Cache
- XConn/MemVerge — CXL Memory Pool for KV Cache (OCP 2025)
- JEDEC — LPDDR6 Standard Release
- IEEE Spectrum — 400 Gb/s Silicon Photonics
- Marvell — Celestial AI Acquisition
- Tom's Hardware — Marvell Celestial AI Deal
- Semiconductor-Today — Co-packaged Optics Market
- Intel — World's Largest Neuromorphic System
- Nature Communications — Neuromorphic Technologies

### 삼성 vs SK하이닉스
- TrendForce — Samsung HBM Chips Failing Nvidia Tests
- TrendForce — Samsung Adopts SK Hynix Techniques
- Digitimes — Samsung Reassigns 2,000 Engineers
- Astute Group — SK Hynix 62% HBM, Micron Overtakes Samsung
- DataCenterDynamics — Samsung Apology Q3 2024
- TrendForce — Samsung Plans 50% HBM Capacity Surge in 2026
- TrendForce — NVIDIA May Relax HBM4 Specs (Feb 2026)
- TweakTown — SK Hynix 1c DRAM 6 EUV Layers
- TweakTown — Samsung 1c DRAM for HBM4 Yields ~50%
- TrendForce — SK Hynix Doubling EUV Fleet by 2027
- TrendForce — Samsung Sub-10nm DRAM Breakthrough (InGaO)

### CXMT / 신규 진입
- Tom's Hardware — CXMT DDR5-8000 Despite Export Restrictions
- Digitimes — CXMT's Growth Ceiling Arrives Early
- Digitimes — CXMT Muscles into DRAM's Top Tier
- TrendForce — CXMT 80% DDR5 Yield
- WebProNews — CXMT $4.2B IPO
- Mordor Intelligence — DRAM Market Analysis

### NVIDIA 차세대
- TweakTown — NVIDIA Rubin CPX 128GB GDDR7
- NVIDIA Newsroom — Rubin CPX Unveil
- SK Hynix Newsroom — AI Infra Summit 2025
- Samsung Semiconductor — HBM-PIM Tech Blog
