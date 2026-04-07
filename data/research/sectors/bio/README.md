# 바이오 섹터 리서치 허브

> 바이오/제약 산업의 핵심 기술을 14개 축 + AI 교차축 + 약물 전달 인프라로 정리.
> 2026년 4월 기준 최신 데이터 반영.

---

## 작용 원리 지도 (14축 + 교차 + 인프라)

```
[기존 4축 — 검증된 기반 기술]
축 1: 호르몬 흉내     → 몸을 속여서 조절 (GLP-1, 인슐린, amylin, myostatin 억제)
축 2: 유도 미사일     → 표적만 정밀 타격 (ADC, mAb, PROTAC, molecular glue)
축 3: 면역세포 조종   → 내 몸이 싸우게 (IO, CAR-T, bispecific, 암백신, NK/TIL/TCR)
축 4: 유전자 편집     → 설계도 자체를 수정 (CRISPR, 유전자치료, iPSC, 이종장기)

[신규 10축 — 차세대 기술 프론티어]
축 5: RNA 치료제      → 단백질 만들기 전에 차단 (siRNA, ASO, mRNA, saRNA, tRNA)
축 6: 방사성의약품    → 핵탄두 장착 유도 미사일 (테라노스틱스, Lu-177, Ac-225)
축 7: 마이크로바이옴  → 100조 세균 군대 조종 (장내 생태계 복원, 장-뇌 축)
축 8: 뇌-컴퓨터 IF   → 뇌와 기계 직접 연결 (BCI, 뉴로모듈레이션)
축 9: 재생의학        → 장기/조직을 새로 만듦 (3D 바이오프린팅, 엑소좀, 줄기세포)
축 10: 합성생물학     → 생명체를 프로그래밍 (세포공장, 효소공학, 유전회로)
축 11: 후성유전학     → 악보는 그대로, 연주만 변경 (DNA 메틸화, 히스톤 변형)
축 12: 디지털 치료제  → 앱이 약이 됨 (처방 소프트웨어, AI 치료 프로토콜)
축 13: 장수과학       → 노화를 질병으로 치료 (세노리틱스, 후성유전 리프로그래밍)
축 14: 메타볼로믹스   → 대사 지문으로 맞춤 의료 (정밀영양, 멀티오믹스)

[교차 & 인프라]
교차: AI            → 1-14 전체 속도를 바꿈 (AlphaFold, de novo 설계, 173+ 임상)
인프라: 약물 전달    → 1-14 전체의 "배송 기술" (LNP, mRNA, GalNAc, AAV, 엑소좀)
```

---

## 디렉토리 구조

```
bio/
├── README.md                ← 이 파일 (지도)
├── axis1_hormone/           ← 호르몬 흉내 (GLP-1, 인슐린, amylin, myostatin)
├── axis2_targeted/          ← 유도 미사일 (ADC, mAb, PROTAC, molecular glue)
├── axis3_immune/            ← 면역세포 조종 (IO, CAR-T, bispecific, 암백신)
├── axis4_gene/              ← 유전자 편집 (CRISPR, 유전자치료, iPSC, 이종장기)
├── axis5_rna/               ← RNA 치료제 (siRNA, ASO, mRNA)
├── axis6_radio/             ← 방사성의약품 (테라노스틱스)
├── axis7_microbiome/        ← 마이크로바이옴
├── axis8_neurotech/         ← 뇌-컴퓨터 인터페이스 & 뉴로테크
├── axis9_regen/             ← 재생의학 & 조직공학
├── axis10_synbio/           ← 합성생물학
├── axis11_epigenetics/      ← 후성유전학
├── axis12_digital/          ← 디지털 치료제 (DTx)
├── axis13_longevity/        ← 장수과학 / 노화 역전
├── axis14_metabolomics/     ← 메타볼로믹스 & 정밀영양
├── ai/                      ← AI 신약 발굴 (교차축)
├── infra_delivery/          ← 약물 전달 (LNP, GalNAc, AAV 등)
└── companies/               ← 기업별 리서치
```

---

## 시장 규모 비교 (2025→2035 예상)

| 축 | 2025 시장 | 2030-2035 전망 | CAGR | 성숙도 |
|----|----------|---------------|------|--------|
| 1. GLP-1/비만 | $74B | $315B | 17.5% | ★★★★★ 상용화 |
| 2. ADC | $13.5B | $32.7B | 9.2% | ★★★★ 상용화 |
| 2. PROTAC | $1B | $7-10B | 21-35% | ★★★ Phase 3 |
| 3. IO (체크포인트) | $66.2B | $303.9B | 16.6% | ★★★★★ 상용화 |
| 3. Bispecific | $11.2B | $448.6B | 44.5% | ★★★★ 상용화/확대 |
| 3. CAR-T | $12.9B | $193-268B | 29.3% | ★★★★ 상용화 |
| 3. 암백신 | $0.2B | $8.5B | 44.9% | ★★★ Phase 3 |
| 4. CRISPR | $4.8B | $18.9B | 14.8% | ★★★★ 상용화 시작 |
| 5. RNA (siRNA+ASO) | $9.1B | $15.7B | 11.5% | ★★★★ 상용화 |
| 6. 방사성의약품 | $6.8B | $13.4B | 7.8% | ★★★★ 상용화 |
| 7. 마이크로바이옴 | $0.25B | $3.4B | 33% | ★★ 초기 상용화 |
| 8. BCI | $2.8B | $8.7B | 15.1% | ★★ 임상 진입 |
| 9. 3D 바이오프린팅 | $2.2B | $23.1B | 17.7% | ★★ 연구/전임상 |
| 10. 합성생물학 | $23.6B | $53.1B | 11% | ★★★ 플랫폼 형성 |
| 11. 후성유전 약물 | $16.2B | $80.8B | 22% | ★★★★ 상용화 (혈액암) |
| 12. 디지털 치료제 | $10.2B | $52-68B | 21-24% | ★★★ 초기 상용화 |
| 13. 장수과학 | ~$85B (전체) | $120B | — | ★ 전임상 |
| 14. 정밀영양 | $17.7B | $83.4B | 18.1% | ★★ 소비자/연구 |
| AI 신약 | $1.8B | $13.1B | 18.8% | ★★★ 임상 검증 중 |

---

## 핵심 기업 매핑

| 축 | 대표 기업 (티커) | 대표 약물/기술 |
|----|-----------------|--------------|
| 호르몬 | Novo Nordisk (NVO), Eli Lilly (LLY) | Ozempic, Mounjaro, Orforglipron |
| 유도 미사일 | Daiichi Sankyo, AstraZeneca (AZN), Arvinas (ARVN) | Enhertu, ARV-471 |
| 면역 조종 | Merck (MRK), BMS (BMY), Gilead (GILD), J&J (JNJ) | Keytruda, Yescarta, Carvykti |
| 유전자 | CRISPR Tx (CRSP), Vertex (VRTX), Intellia (NTLA) | Casgevy, NTLA-2001 |
| RNA | Alnylam (ALNY), Ionis (IONS), Moderna (MRNA) | Leqvio, Spinraza, mRNA 플랫폼 |
| 방사성 | Novartis (NVS), BMS (BMY), Eli Lilly (LLY) | Pluvicto, RYZ101 |
| 마이크로바이옴 | Seres (MCRB), Ferring | VOWST, REBYOTA |
| 뉴로테크 | Neuralink, Synchron, Medtronic (MDT) | N1 칩, Stentrode, DBS |
| 재생의학 | Organovo, CELLINK(BICO), Evox | 바이오프린팅, 엑소좀 |
| 합성생물학 | Ginkgo (DNA), Twist (TWST), Absci (ABSI) | 세포 프로그래밍, DNA 합성 |
| 후성유전 | BMS (BMY), Merck (MRK), Ipsen | Vidaza, Zolinza, Tazverik |
| 디지털 치료 | Akili, Biofourmis, Click | EndeavorRx |
| 장수 | Altos Labs, Calico (GOOGL) | 후성유전 리프로그래밍 |
| 메타볼로믹스 | ZOE, Dexcom (DXCM), Thermo Fisher (TMO) | CGM+AI, 오믹스 인프라 |
| AI | Recursion (RXRX), Schrödinger (SDGR), Insilico | Boltz-2, Zasocitinib |

---

## 축 간 교차점 (Cross-Axis Synergies)

| 교차 | 설명 |
|------|------|
| 축2 + 축6 | ADC 원리 + 방사성 동위원소 = 방사성면역접합체 |
| 축2 + 축2 | ADC + PROTAC = DAC (Degrader-Antibody Conjugate) |
| 축3 + 축4 | 면역세포 + 유전자 편집 = 차세대 CAR-T, iPSC-CAR |
| 축3 + 축5 | 면역 + mRNA = 개인화 암 백신 |
| 축4 + 축9 | 유전자 편집 + 이종장기 = 돼지 장기 이식 |
| 축5 + 인프라 | RNA 치료 + LNP 전달 = 모든 RNA 모달리티의 기반 |
| 축7 + 축3 | 마이크로바이옴 + IO = 장내 세균이 면역요법 반응 좌우 |
| 축11 + 축13 | 후성유전 + 장수 = 후성유전 시계 되돌리기 |
| 축14 + 축1 | 메타볼로믹스 + GLP-1 = 비만 환자 맞춤 약물 선택 |
| AI + 전체 | AI가 모든 축의 표적 발견/약물 설계/임상 최적화 가속 |

---

## 확장 규칙

- 축이 세분화되면 하위 디렉토리로 분리
  - 예: axis3_immune/ → io/, car-t/, cancer_vaccine/
- 기업 리서치가 깊어지면 companies/{ticker}/ 생성
- 아티클로 발전하면 data/articles/ 로 이동
- 새 축 추가 시 axis{N}_{name}/ 형식 유지
