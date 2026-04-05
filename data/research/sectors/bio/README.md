# 바이오 섹터 리서치 허브

> 약물 작용 원리 4축 + AI + 인프라 체계로 정리. 축은 계속 확장.

---

## 작용 원리 지도

```
축 1: 호르몬 흉내    → 몸을 속여서 조절 (GLP-1, 인슐린, 스테로이드)
축 2: 유도 미사일    → 표적만 정밀 타격 (ADC, 단클론항체, PROTAC)
축 3: 면역세포 조종  → 내 몸이 싸우게 (IO, CAR-T, bispecific, 암백신)
축 4: 유전자 편집    → 설계도 자체를 수정 (CRISPR, 유전자 치료, 세포치료)

교차: AI           → 1-4 전체 속도를 바꿈 (AlphaFold, AI 신약발굴)
인프라: 약물 전달    → 1-4 전체의 "배송 기술" (mRNA, LNP, DDS)
```

## 디렉토리 구조

```
bio/
├── README.md              ← 이 파일 (지도)
├── axis1_hormone/         ← 호르몬 흉내 (GLP-1, 비만약 등)
├── axis2_targeted/        ← 유도 미사일 (ADC, PROTAC 등)
├── axis3_immune/          ← 면역세포 조종 (IO, CAR-T 등)
├── axis4_gene/            ← 유전자 편집 (CRISPR 등)
├── ai/                    ← AI 신약 (AlphaFold, Recursion 등)
├── infra_delivery/        ← 약물 전달 (mRNA, LNP, DDS 등)
└── companies/             ← 기업별 리서치 (Novo, Lilly, Moderna 등)
```

## 핵심 기업 매핑

| 축 | 대표 기업 | 대표 약물/기술 |
|----|----------|--------------|
| 호르몬 | Novo Nordisk, Eli Lilly | Ozempic, Mounjaro |
| 유도 미사일 | Daiichi Sankyo, AstraZeneca, Arvinas | Enhertu, PROTAC |
| 면역 조종 | Merck, BMS, Gilead, J&J | 키트루다, Yescarta |
| 유전자 | CRISPR Therapeutics, Vertex, Intellia | Casgevy |
| AI | Recursion, Isomorphic Labs | AlphaFold |
| 약물 전달 | Moderna, BioNTech, Alnylam | mRNA 플랫폼, LNP |

## 확장 규칙

- 축이 세분화되면 하위 디렉토리로 분리
  - 예: axis3_immune/ → io/, car-t/, cancer_vaccine/
- 기업 리서치가 깊어지면 companies/{ticker}/ 생성
- 아티클로 발전하면 data/articles/ 로 이동
