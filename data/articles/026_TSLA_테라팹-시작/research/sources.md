# 출처 & 팩트체크

> 수집일: 2026-03-16 (초판) / 2026-03-24 (3/21 런칭 반영 전면 갱신)
> 아티클: 026 / TeraFab의 시작 — 팹을 가장 빨리 짓는 법 (Part 1)
> 관련: 028 / TeraFab의 구조 — $250억 합작의 논리 (Part 2)

---

## 1차 자료 (공식 문서/발표)

| # | 자료명 | URL/출처 | 인용 위치 |
|---|--------|----------|-----------|
| S1 | Tesla TeraFab 런칭 — $20-25B, 3사 합작(Tesla+SpaceX+xAI), 2nm, Seaholm Power Plant 이벤트 (2026-03-21) | Teslarati, FinTech Weekly, CNBC, Bloomberg | P1§1, P2§1-2 |
| S2 | 머스크 X 게시 "Terafab Project launches in 7 days" (2026-03-14) | X (@elonmusk) | P1§1 |
| S3 | 머스크 발언: "the most epic chip building exercise in history by far" | Teslarati (launch event) | P1§1 |
| S4 | 머스크 발언: "Terafab was the final missing piece of the puzzle" | FinTech Weekly (launch event) | P2§2 |
| S5 | Tesla Giga Texas 확장 — 520만 sqft 신규 건물 허가 (2026) | basenor.com / teslanorth.com | P1§3 |
| S6 | TSMC Fab 15 — 빈 땅→양산 ~30개월 (건물 12m + 장비 10m + 수율 8m) | SemiWiki | P1§1, P1§8 |
| S7 | Intel Ohio — $200억, 1기 2030년 완공 (2025년에서 지연) | CNBC / DCD | P1§3-4 |
| S8 | Samsung Taylor TX — $440억 팹, first light 달성 (2026) | Tom's Hardware | P1§3, P2§5 |
| S9 | ASML — EUV ~$2억, High-NA ~$4억, 연간 ~50대 생산 | ASML IR / CNBC | P1§5 |
| S10 | TSMC — 전 세계 EUV 설치의 56% 보유 | TrendForce | P1§5 |
| S11 | Samsung-Tesla — $16.5B 파운드리 계약, AI6, Taylor TX, 2033년까지 (**2025년 7월** 체결) | KED Global / Carbon Credits | P2§5 |
| S12 | 머스크: AI5/AI6 듀얼 파운드리 전략 (TSMC + Samsung) | Tom's Hardware | P2§5 |
| S13 | AI6 ~6개월 지연 — Samsung 2nm GAA 문제, 양산 Q4 2027 | Electrek | P2§5 |
| S14 | Intel — IFS 최대 49% 외부 매각 가능 (Citi TMT Conference, 2025) | Intel CFO 발언 | P2§4 |
| S15 | 80% 우주 / 20% 지상 컴퓨트 배분 | FinTech Weekly (launch event) | P2§2, P2§6 |
| S16 | D3 칩 — 방사선 내성(radiation-hardened) 우주용 프로세서 | FinTech Weekly | P1§6, P2§6 |
| S17 | SpaceX FCC 신청 — 100만 기 AI Sat Mini 위성 (170m, 100kW) | FinTech Weekly | P2§6 |
| S18 | TSLA -17% 주가 하락 (런칭 발표 후) | AInvest | P2§1 |
| S19 | Morgan Stanley — 실제 필요 자본 $35-45B, 첫 칩 아웃풋 빨라야 2028 중반 | Seeking Alpha / Yahoo Finance | P2§1 |
| S20 | 텍사스 주지사 Greg Abbott 런칭 이벤트 참석 | FinTech Weekly | P1§1 |
| S21 | TSMC 534개 고객, 12,682개 제품 (2025 Annual Report) | TSMC | P1§6 |

---

## 데이터 & 수치

| # | 주장 | 출처 | 검증 |
|---|------|------|------|
| D1 | 일반 첨단 팹: 착공→양산 36~60개월 | UltraFacility / Construction Physics | ✅ |
| D2 | TSMC Fab 15: 30개월 (건물 12m + 장비 10m + 수율 8m) | SemiWiki S6 | ✅ |
| D3 | 팹 전력 소비 ~100MW | 025 리서치 (검증 완료) | ✅ 재사용 |
| D4 | 팹 건물 83%는 클린룸이 아님, 오염원 75~80% 인간 | 025 리서치 (검증 완료) | ✅ 재사용 |
| D5 | Tesla Giga Texas 520만 sqft 확장 | 허가 문서 S5 | ✅ |
| D6 | TeraFab $20-25B (발표 기준), Morgan Stanley $35-45B (실제 추정) | S1, S19 | ✅ |
| D7 | ASML 연간 EUV ~50대, TSMC 56% 점유 | TrendForce / ASML S9, S10 | ✅ |
| D8 | 팹 건설 3단계: Base Build → PLS → Tool Install | JE Dunn Construction | ✅ |
| D9 | Tool Install 안전검증: SL1 → SL2 → SL3 | JE Dunn Construction | ✅ |
| D10 | 팹 건설 인력 ~7,000명 | SIA / Construction Physics | ✅ |
| D11 | TSMC 534개 고객, 12,682개 제품 (2025) | TSMC Annual Report S21 | ✅ |
| D12 | EUV 리드타임 18~24개월 | 업계 컨센서스 (복수 출처) | ✅ 추정치 |
| D13 | Samsung-Tesla $16.5B, 2025년 7월 체결 | KED Global S11 | ✅ (v1 오류 수정: 2026→2025) |
| D14 | Samsung Taylor 초기 16,000 WSPM → 40,000 WSPM 확대 협의 | Electrek S13 | ✅ |
| D15 | AI5 볼륨 프로덕션 mid-2027 (지연) | Electrek S13 | ✅ |
| D16 | AI6 ~6개월 지연, Samsung 2nm GAA 문제, 양산 Q4 2027 | Electrek S13 | ✅ |
| D17 | 80% 우주 / 20% 지상 컴퓨트 배분 | S15 | ✅ |
| D18 | SpaceX 100만 기 AI Sat Mini, 170m, 100kW | S17 | ✅ (FCC 신청 기준) |
| D19 | TSLA -17% 발표 후 주가 하락 | S18 | ✅ |
| D20 | 궤도 태양광 조도 지상 대비 ~5x | S15 (머스크 발언) | ⚠️ 물리적으로 타당 (대기 감쇠 없음), 정확한 비율은 위도/시간 의존 |
| D21 | Samsung 파운드리 CapEx 50% 삭감 (2025) | TrendForce | ✅ |
| D22 | 첨단 팹 1,000개+ 공정 단계 | 업계 컨센서스 (Construction Physics 등) | ✅ 추정치 |

---

## 인용문

| # | 인용 | 출처 | 검증 |
|---|------|------|------|
| Q1 | "Terafab Project launches in 7 days" | 머스크 X 게시 (2026-03-14) S2 | ✅ |
| Q2 | "the most epic chip building exercise in history by far" | 런칭 이벤트 (2026-03-21) S3 | ✅ |
| Q3 | "Terafab was the final missing piece of the puzzle" | 런칭 이벤트 (2026-03-21) S4 | ✅ |

---

## 025 리서치 재사용 항목

| 항목 | 025 섹션 | 026 사용 위치 |
|------|----------|---------------|
| 팹 4층 구조 (팬덱-클린룸-서브팹-유틸리티) | §2 | P1§2 (참조) |
| 팹 전력 ~100MW | §2 | P1§3 (1줄 참조) |
| 오염원 75~80% 인간 | §2 | P1§4 (1줄 참조) |
| Dirty Fab 개념 | §4 | P1§4 ("이전 글에서 봤듯이" 참조) |
| ASML 독점, EUV 가격 | §6 | P1§5 (수치 재사용) |
| TSMC 플라이휠 | §3 | P2§3 (개념 활용, 취약점 확장) |

---

## 미검증 / 추가 확인 필요

| # | 항목 | 상태 |
|---|------|------|
| U1 | TeraFab 런칭 시 ASML 발주 여부 — 공식 미확인 | 발주 미확인이 팩트 (미발주가 아니라 미공개) |
| U2 | 건설 타임라인 — 공식 미공개 | "no construction timeline" 복수 매체 확인 |
| U3 | 3사 JV 지분 구조 / CapEx 분담 비율 | 미공개 — 아티클에서 "미공개"로 처리 |
| U4 | xAI의 TeraFab 내 역할 구체 | 모델/컴퓨트 수요 제공으로 추정, 구체 미공개 |
