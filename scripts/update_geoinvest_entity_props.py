#!/usr/bin/env python3
"""GeoInvest 9개 이슈 핵심 엔티티 프로퍼티 보강.

이란 전쟁 엔티티에 이미 채워진 objectives/strategy/achievements/failures 패턴을
나머지 9개 이슈의 핵심 엔티티에도 동일하게 적용한다.

실행 이력:
    2026-04-02: 전체 9개 이슈 24개 엔티티 보강 완료

Usage:
    python scripts/update_geoinvest_entity_props.py [이슈번호]
    python scripts/update_geoinvest_entity_props.py          # 전체 실행
    python scripts/update_geoinvest_entity_props.py 1        # 비트코인 지정학만
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.database import init_db  # noqa: E402
from src.storage import OntologyEntityRepository  # noqa: E402


def _merge_props(existing: dict, new_props: dict) -> dict:
    """기존 properties에 새 프로퍼티를 병합 (리스트는 중복 제거 추가)."""
    merged = dict(existing)
    for key, value in new_props.items():
        if isinstance(value, list) and isinstance(merged.get(key), list):
            existing_set = set(merged[key])
            for item in value:
                if item not in existing_set:
                    merged[key].append(item)
                    existing_set.add(item)
        else:
            merged[key] = value
    return merged


def _update_entity(
    entity_repo: OntologyEntityRepository,
    name: str,
    new_props: dict,
) -> bool:
    """엔티티 프로퍼티를 업데이트. 존재하지 않으면 False 반환."""
    entity = entity_repo.find_by_name(name)
    if not entity:
        print(f"  WARN: '{name}' 엔티티 없음 — 스킵")
        return False

    merged = _merge_props(entity.properties, new_props)
    entity_repo.update(entity.id, properties=merged)
    print(f"  UPDATE: {name} — {len(new_props)}개 필드")
    return True


# ============================================================
# 1. 비트코인 지정학
# ============================================================
def update_bitcoin_geopolitics(entity_repo: OntologyEntityRepository) -> int:
    """비트코인 지정학 이슈 핵심 엔티티 보강."""
    print("\n=== 1. 비트코인 지정학 ===")
    count = 0

    # Bitcoin
    if _update_entity(entity_repo, "Bitcoin", {
        "역할": "디지털 금, 탈중앙 가치 저장 수단",
        "objectives": [
            "법정화폐 대안으로서의 글로벌 준비자산 지위 확보",
            "기관투자자 포트폴리오 편입 확대 (ETF 승인 후)",
            "국가 단위 전략 비축자산 채택 확대",
        ],
        "strategy": [
            "반감기(2024.4) 기반 공급 희소성 강화",
            "현물 ETF(2024.1 승인) 통한 기관 자금 유입",
            "Lightning Network 등 L2 확장으로 결제 실용성 확보",
            "금과의 디지털 골드 서사 강화",
        ],
        "achievements": [
            "2024.1 미국 현물 BTC ETF 승인 — 기관투자 본격화",
            "BlackRock IBIT 단일 펀드 500억 달러 AUM 돌파",
            "엘살바도르 법정화폐 채택 (2021) 선례 확립",
            "2024-25 가격 $100K 돌파, 시가총액 금 대비 10% 도달",
            "국가 전략비축자산 논의 시작 (미국 트럼프 행정부)",
        ],
        "failures": [
            "높은 변동성 — 금 대비 4배 변동성으로 준비자산 신뢰 부족",
            "에너지 소비 비판 — ESG 기관투자자 회피 요인",
            "중국 전면 금지(2021) 이후 채굴 지리적 집중(미국·카자흐)",
            "결제 수단으로서 실사용 여전히 미미",
            "규제 불확실성 — 국가별 대응 편차 극심",
        ],
    }):
        count += 1

    # US SEC
    if _update_entity(entity_repo, "US SEC", {
        "역할": "크립토 규제 주도 기관, 투자자 보호 명목 감독",
        "objectives": [
            "크립토 시장 투자자 보호 체계 구축",
            "증권법 적용 범위를 디지털자산으로 확대",
            "스테이블코인·DeFi 감독 체계 확립",
        ],
        "strategy": [
            "겐슬러 시대(2021-24): '집행 우선(enforcement first)' 접근",
            "Howey Test 적용해 대부분 토큰을 증권으로 분류 시도",
            "대형 거래소(바이낸스·코인베이스) 소송으로 선례 확보",
            "트럼프 행정부(2025~): 규제 완화·혁신 친화 전환",
        ],
        "achievements": [
            "현물 BTC ETF 승인(2024.1) — 시장 제도권 편입 결정적 전환",
            "현물 ETH ETF 승인(2024.5)",
            "바이낸스 $43억 합의 — 역대 최대 크립토 집행",
            "FTX 붕괴 후 투자자 보호 정당성 확보",
        ],
        "failures": [
            "리플(XRP) 소송 패소 — 2차 시장 거래는 증권 아님 판결",
            "과도한 집행 비판 — 혁신 해외 유출 초래",
            "FTX 사전 감지 실패 — 감독 공백 노출",
            "트럼프 행정부 전환 후 기존 집행 방침 후퇴",
        ],
    }):
        count += 1

    # China (비트코인 관점)
    if _update_entity(entity_repo, "China", _merge_props(
        {},  # 기존 것은 entity_repo에서 가져오므로 새 것만
        {
            "objectives": [
                "디지털 위안(e-CNY)을 통한 위안화 국제화",
                "달러 의존도 감소 — BRICS 결제 네트워크 구축",
                "크립토 자본 유출 차단 — 자본통제 유지",
            ],
            "strategy": [
                "크립토 전면 금지(2021) — 채굴·거래·ICO 모두 불법",
                "디지털 위안(e-CNY) CBDC 독자 개발·시범 운영",
                "블록체인 기술은 육성, 탈중앙 화폐는 억제",
                "홍콩을 규제 샌드박스로 활용 (2023~ 현물 ETF 허용)",
            ],
            "achievements": [
                "e-CNY 시범 운영 1.8조 위안(~$2,500억) 거래량 달성",
                "BRICS Pay 결제 시스템에 e-CNY 통합 추진",
                "크립토 채굴 해외 유출로 에너지 절감 효과",
                "홍콩 통한 선별적 크립토 시장 참여 유지",
            ],
            "failures": [
                "크립토 금지에도 OTC·P2P 거래 완전 근절 실패",
                "e-CNY 실사용 채택률 저조 — 알리페이·위챗페이 대비 매력 부족",
                "달러 패권 약화 속도 기대 이하 — SWIFT 대체 미완",
                "블록체인 혁신 인력 해외 유출",
            ],
        },
    )):
        count += 1

    # MicroStrategy
    if _update_entity(entity_repo, "MicroStrategy", {
        "역할": "기업 비트코인 최대 보유, BTC 재무전략 선도",
        "objectives": [
            "BTC를 기업 재무 핵심 자산으로 확립",
            "BTC 보유를 통한 주주가치 극대화",
            "기관·기업의 BTC 채택 선도",
        ],
        "strategy": [
            "전환사채·유상증자로 조달한 자금 전액 BTC 매입",
            "'BTC Yield' 지표로 주당 BTC 보유량 증가 입증",
            "BI 소프트웨어 사업 유지하면서 BTC 재무전략 병행",
            "마이클 세일러 개인 브랜딩을 통한 BTC 에반젤리즘",
        ],
        "achievements": [
            "BTC 500,000+ 개 보유 — 단일 기업 최대 (전체 공급의 ~2.4%)",
            "평균 매입가 대비 상당한 미실현 수익",
            "주가 2024-25년 BTC 랠리 연동 500%+ 상승",
            "나스닥 100 편입 (2024.12)",
            "기업 BTC 재무전략 트렌드 창출 (테슬라, 메타플래닛 등 후발주자)",
        ],
        "failures": [
            "극단적 BTC 집중 리스크 — BTC 하락 시 주가 레버리지 하락",
            "지속적 희석 발행 — 기존 주주 지분율 하락",
            "BI 본업 매출 정체 — 사실상 BTC 투자회사화",
            "마진콜 리스크 — BTC $20K 이하 시 담보 부족 가능성",
        ],
    }):
        count += 1

    # Tether
    if _update_entity(entity_repo, "Tether", {
        "역할": "최대 스테이블코인(USDT) 발행사, 크립토 유동성 핵심",
        "objectives": [
            "USDT 시장 지배력 유지 (시장점유율 ~70%)",
            "달러 패권의 디지털 확장 도구로 포지셔닝",
            "규제 준수 이미지 확보 — 투명성 강화",
        ],
        "strategy": [
            "미국 국채 기반 준비금 운용 — $900억+ 국채 보유",
            "신흥국·고인플레 국가 타겟 (아르헨티나, 터키, 나이지리아)",
            "Tether Gold(XAUt) 등 자산 다각화",
            "USDT를 BTC 트레이딩·DeFi 기축통화로 포지셔닝",
        ],
        "achievements": [
            "USDT 시가총액 $1,400억+ — 스테이블코인 시장 70% 지배",
            "2024년 순이익 $62억 — 역대 최대 수익성",
            "미국 국채 7대 보유주체 (국가 수준)",
            "24시간 거래량 BTC 능가 — 크립토 시장 실질 기축통화",
        ],
        "failures": [
            "준비금 투명성 논란 — 완전 감사(full audit) 미시행",
            "미국 규제 리스크 — GENIUS Act 등 스테이블코인법 통과 시 준수 비용 증가",
            "탈중앙화 이념과 충돌 — 중앙 발행·동결 권한 보유",
            "USDT 디페그(1:1 이탈) 역사 — 2022 $0.95까지 하락 사례",
        ],
    }):
        count += 1

    # Circle
    if _update_entity(entity_repo, "Circle", {
        "역할": "USDC 발행사, 규제 친화적 스테이블코인",
        "objectives": [
            "USDC를 '규제 받는 디지털 달러'로 포지셔닝",
            "IPO 통한 기업가치 실현 (2025 IPO 추진)",
            "글로벌 결제 인프라로 성장",
        ],
        "strategy": [
            "미국 규제 완전 준수 — 뉴욕 BitLicense, 머니서비스 라이선스 보유",
            "준비금 100% 미국 국채 + 현금 — 투명성 차별화",
            "SWIFT 대안 크로스보더 결제 시장 공략",
            "코인베이스와 전략적 파트너십 (USDC 수익 공유)",
        ],
        "achievements": [
            "USDC 시가총액 $350억+ — 2위 스테이블코인",
            "규제 준수 이미지로 기관 선호도 1위",
            "EU MiCA 규제 최초 승인 스테이블코인 (2024)",
            "트럼프 행정부 스테이블코인 정책 수혜 포지션 확보",
        ],
        "failures": [
            "SVB 뱅크런(2023.3) 시 USDC $0.88 디페그 — 은행 리스크 노출",
            "USDT 대비 시장점유율 30% → 25% 하락 추세",
            "IPO 여러 차례 연기 — 시장 환경 불확실",
            "바이낸스 BUSD 종료 후 기대한 점유율 회복 미흡",
        ],
    }):
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 2. IMEC 회랑
# ============================================================
def update_imec_corridor(entity_repo: OntologyEntityRepository) -> int:
    """IMEC 회랑 이슈 핵심 엔티티 보강."""
    print("\n=== 2. IMEC 회랑 ===")
    count = 0

    # India
    if _update_entity(entity_repo, "India", {
        "역할": "IMEC 동쪽 기점, 제조업 허브, 중국 대안 공급망",
        "objectives": [
            "IMEC을 통해 유럽·중동 직결 무역 루트 확보",
            "중국 일대일로 대항마로서 지정학적 레버리지 확대",
            "Make in India + 글로벌 공급망 재편 수혜 극대화",
            "에너지 수입 다변화 — 중동 직결 인프라 확보",
        ],
        "strategy": [
            "G20 의장국(2023) 지위 활용해 IMEC 공식 발표 주도",
            "UAE·사우디와 양자 FTA 강화 (I2U2 프레임워크)",
            "반도체·전자 제조 유치로 IMEC 수요 기반 구축",
            "이스라엘과 기술·군사 협력 심화",
        ],
        "achievements": [
            "2023 G20에서 IMEC MoU 체결 — 미국·EU·사우디·UAE·이스라엘 참여",
            "인도-중동-유럽 해저케이블 + 철도 + 항만 통합 구상 합의",
            "Mundra 항구 IMEC 인도측 허브로 지정",
            "I2U2(인도·이스라엘·UAE·미국) 프레임워크 작동",
        ],
        "failures": [
            "이란 전쟁(2026)으로 IMEC 핵심 구간(이스라엘·UAE·사우디) 안보 위협",
            "실제 건설 착공 전무 — MoU 단계에서 진전 미미",
            "파키스탄 경유 회피로 육로 비용 증가 불가피",
            "중국 BRI 대비 자금 규모·실행력 열세",
        ],
    }):
        count += 1

    # IMEC Corridor
    if _update_entity(entity_repo, "IMEC Corridor", {
        "역할": "인도-중동-유럽 경제 회랑, 중국 일대일로 대항마",
        "objectives": [
            "인도-중동-유럽 무역 시간 40% 단축",
            "중국 BRI 대안 루트로 서방 공급망 다변화",
            "에너지·데이터·물류 3중 연결 인프라 구축",
            "중동 국가 경제 다변화(탈석유) 지원",
        ],
        "strategy": [
            "동부(인도-걸프) + 북부(걸프-유럽) 2개 회랑 구성",
            "철도·항만·해저케이블·수소 파이프라인 복합 인프라",
            "기존 BRI 항구 회피 — 독자 네트워크 구축",
            "민관 합작(PPP) 투자 모델",
        ],
        "achievements": [
            "2023 G20 MoU — 미국·인도·사우디·UAE·EU·이스라엘·프랑스·독일·이탈리아 서명",
            "수에즈 운하 대안 + 중국 BRI 대항 서사 확립",
            "글로벌 공급망 재편 논의의 핵심 의제로 부상",
        ],
        "failures": [
            "이란 전쟁(2026)으로 이스라엘 구간 실현 가능성 급감",
            "사우디-이스라엘 정상화 후퇴 → 북부 회랑 핵심 고리 약화",
            "건설 착공 0% — 구상 단계 정체 (MoU 후 2년 경과)",
            "BRI 대비 투자 규모 $200억 vs $1조 — 10배 열세",
            "후티 홍해 공격으로 해상 구간 안보 위협",
        ],
    }):
        count += 1

    # China (BRI 관점)
    # China는 이미 비트코인 이슈에서 업데이트했으므로, BRI 관련 내용은 추가만
    china = entity_repo.find_by_name("China")
    if china:
        props = dict(china.properties)
        bri_context = {
            "BRI_역할": "일대일로(BRI) 주도국 — IMEC의 직접적 경쟁 상대",
            "BRI_규모": "$1조+ 투자, 150개국 참여, 항만·철도·도로·발전소 건설",
            "BRI_전략": "인프라 투자→자원 접근→정치적 영향력 확보 삼위일체",
            "BRI_성과": "파키스탄 과다르항, 스리랑카 함반토타항, 그리스 피레우스항 확보",
            "BRI_한계": "부채 함정 비판, 스리랑카·잠비아 채무불이행, 수익성 의문",
        }
        merged = _merge_props(props, bri_context)
        entity_repo.update(china.id, properties=merged)
        print(f"  UPDATE: China — BRI 관점 5개 필드 추가")
        count += 1

    # Israel (IMEC 관점) — 이미 이란 전쟁에서 채워져 있지만 IMEC 관련 보완
    israel = entity_repo.find_by_name("Israel")
    if israel:
        props = dict(israel.properties)
        imec_context = {
            "IMEC_역할": "IMEC 북부 회랑 핵심 연결점 (하이파항 → 그리스)",
            "IMEC_전략": "하이파항을 IMEC 지중해 허브로 포지셔닝, 아브라함 협정 확대와 연계",
            "IMEC_리스크": "이란 전쟁(2026)으로 IMEC 참여 실현 불투명, 사우디 정상화 후퇴",
        }
        merged = _merge_props(props, imec_context)
        entity_repo.update(israel.id, properties=merged)
        print(f"  UPDATE: Israel — IMEC 관점 3개 필드 추가")
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 3. 트럼프 관세전쟁 2.0
# ============================================================
def update_tariff_war(entity_repo: OntologyEntityRepository) -> int:
    """트럼프 관세전쟁 2.0 이슈 핵심 엔티티 보강."""
    print("\n=== 3. 트럼프 관세전쟁 2.0 ===")
    count = 0

    # United States (관세 관점) — 이미 이란에서 채워져 있으나 관세 관련 보완
    us = entity_repo.find_by_name("United States")
    if us:
        props = dict(us.properties)
        tariff_context = {
            "관세_역할": "관세전쟁 2.0 발동국, IEEPA 비상권한 원용",
            "관세_objectives": [
                "무역적자 $1.2조 축소",
                "제조업 리쇼어링 가속화",
                "중국 기술 디커플링 완성",
                "관세 수입으로 소득세 대체 (트럼프 구상)",
            ],
            "관세_strategy": [
                "IEEPA(국제비상경제권한법) 기반 일방 관세 — 의회 우회",
                "상호관세(reciprocal tariffs) 전면 적용 (2025.4)",
                "중국 145%, EU 20%, 한국 25% 등 차등 관세",
                "반도체·의약품 별도 섹터 관세 예고",
            ],
            "관세_achievements": [
                "2025.4 전면 상호관세 발동 — 역대 최대 관세 장벽",
                "USMCA 재협상 압박으로 멕시코·캐나다 양보 확보",
                "중국산 제품 사실상 수입 차단 수준(145%) 달성",
                "일부 기업 리쇼어링 발표 (TSMC 애리조나, 삼성 텍사스)",
            ],
            "관세_failures": [
                "소비자 물가 상승 — CPI +1.5%p 추가 인플레 추정(Fed)",
                "미 연방법원 위헌 판결(2025.5) — IEEPA 관세 권한 부정",
                "대법원 계류 중 — 법적 불확실성 지속",
                "동맹국(한국·일본·EU) 관계 악화 — 안보 협력에 부정적",
                "글로벌 교역량 -3.5% 감소 (WTO 전망 하향)",
            ],
        }
        merged = _merge_props(props, tariff_context)
        entity_repo.update(us.id, properties=merged)
        print(f"  UPDATE: United States — 관세 관점 필드 추가")
        count += 1

    # China (보복 관점)
    china = entity_repo.find_by_name("China")
    if china:
        props = dict(china.properties)
        tariff_china = {
            "관세_역할": "미국 관세전쟁 2.0 최대 타겟 + 보복 관세 발동국",
            "관세_objectives": [
                "미국 경제 의존도 축소 — 내수 전환",
                "희토류·배터리 등 공급망 무기화로 협상력 확보",
                "위안화 결제 확대로 달러 의존 감소",
                "RCEP·BRICS 통한 대안 무역 네트워크 강화",
            ],
            "관세_strategy": [
                "보복 관세 125% (미국산 전품목)",
                "희토류·갈륨·게르마늄 수출통제 — 서방 공급망 타격",
                "위안화 절하 허용(7.3→7.5) — 관세 충격 흡수",
                "아시아·아프리카·남미 시장 전환 가속",
            ],
            "관세_achievements": [
                "희토류 수출통제로 서방 반도체·방산 공급망 불안 야기",
                "RCEP 역내 교역 확대 — 아세안 최대 교역국 지위 유지",
                "미국 농산물 보복 관세 — 미국 중서부 농가 타격",
                "애플·테슬라 등 미국 기업의 탈중국 비용 부각",
            ],
            "관세_failures": [
                "GDP 성장률 5% → 4.2% 하향 (관세 충격)",
                "외국인 직접투자(FDI) 30% 감소 — 기업 탈중국 가속",
                "청년실업률 20%+ — 수출 감소 영향",
                "기술 자립 목표(반도체) 달성 지연",
            ],
        }
        merged = _merge_props(props, tariff_china)
        entity_repo.update(china.id, properties=merged)
        print(f"  UPDATE: China — 관세 보복 관점 필드 추가")
        count += 1

    # South Korea (피해 관점) — 이미 objectives 등이 있으므로 관세 맥락 추가
    sk = entity_repo.find_by_name("South Korea")
    if sk:
        props = dict(sk.properties)
        tariff_sk = {
            "관세_역할": "미국 상호관세 25% 부과 대상, 수출 의존 취약국",
            "관세_objectives": [
                "25% 상호관세 인하 협상 (목표: 10% 이하)",
                "반도체·자동차 섹터 관세 면제 확보",
                "미국 투자 확대로 무역 불균형 해소 명분 제공",
            ],
            "관세_strategy": [
                "삼성·현대 대미 투자 확대 패키지로 협상",
                "한미 FTA 재협상 선제 수용 자세",
                "반도체 CHIPS Act 연계로 면제 논리 구축",
                "LNG·방산 추가 구매로 무역적자 축소 시도",
            ],
            "관세_achievements": [
                "반도체 관세 일시 면제 확보 (2025.4 기준)",
                "현대차 미국 공장 증설 발표 — 협상 카드 활용",
                "한미 FTA 조기 개정 협상 개시",
            ],
            "관세_failures": [
                "자동차 25% 관세 적용 — 연간 $60억 추가 부담",
                "철강·알루미늄 관세 25% 유지 (2018년부터 지속)",
                "수출 -18.6%(자동차), -15%(철강) 감소",
                "코스피 2,200선 — 관세 불확실성 할인 지속",
                "GDP 성장률 0.5%p 하향 전망",
            ],
        }
        merged = _merge_props(props, tariff_sk)
        entity_repo.update(sk.id, properties=merged)
        print(f"  UPDATE: South Korea — 관세 피해 관점 필드 추가")
        count += 1

    # EU (관세 관점)
    eu = entity_repo.find_by_name("EU")
    if eu:
        props = dict(eu.properties)
        tariff_eu = {
            "역할": "미국 상호관세 20% 타겟, 보복 관세 검토 중",
            "objectives": [
                "미국 관세 인하 협상 (TTIP 재추진 가능성)",
                "무역 다변화 — 인도·아세안·메르코수르 FTA 가속",
                "전략적 자율성(strategic autonomy) 강화",
            ],
            "strategy": [
                "보복 관세 $260억 규모 준비 (미국산 농산물·에너지 타겟)",
                "WTO 제소 병행 — 다자 규범 기반 대응",
                "EU-메르코수르 FTA 비준 가속 (대안 시장 확보)",
                "디지털서비스세(DST)·탄소국경조정(CBAM) 연계 압박",
            ],
            "achievements": [
                "EU-메르코수르 FTA 정치적 합의(2024.12) — 8억 인구 시장",
                "탄소국경조정(CBAM) 2026 본격 시행 — 무역 레버리지",
                "일본·한국·캐나다와 공동 대응 전선 형성 시도",
            ],
            "failures": [
                "대미 무역 의존도 높아 보복 관세 실행 주저",
                "27개국 합의 필요 — 대응 속도 느림",
                "우크라이나 전쟁 + 에너지 위기로 경제적 여력 부족",
                "독일 자동차 업계 보복 관세 반대 — 내부 분열",
            ],
        }
        merged = _merge_props(props, tariff_eu)
        entity_repo.update(eu.id, properties=merged)
        print(f"  UPDATE: EU — 관세 관점 필드 추가")
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 4. AI/반도체 패권전쟁
# ============================================================
def update_ai_chip_war(entity_repo: OntologyEntityRepository) -> int:
    """AI/반도체 패권전쟁 이슈 핵심 엔티티 보강."""
    print("\n=== 4. AI/반도체 패권전쟁 ===")
    count = 0

    # Nvidia
    if _update_entity(entity_repo, "Nvidia", {
        "역할": "AI GPU 시장 지배자, AI 인프라 핵심 공급자",
        "objectives": [
            "AI 학습·추론 GPU 시장 90%+ 점유율 유지",
            "데이터센터 GPU 매출 $2,000억+ (연간) 달성",
            "CUDA 생태계 잠금효과(lock-in) 강화",
            "AI 소프트웨어·클라우드 서비스로 사업 확장",
        ],
        "strategy": [
            "매년 신규 아키텍처 출시 (Hopper→Blackwell→Rubin) — 무어의 법칙 대체",
            "CUDA 생태계 독점 — 개발자 전환비용 극대화",
            "CoWoS 패키징 TSMC 독점 확보 — 경쟁사 물량 제한",
            "NIM(Nvidia Inference Microservices) 소프트웨어 레이어 구축",
            "중국 규제 우회 '디튠(detune)' 칩(H20) 별도 공급",
        ],
        "achievements": [
            "2024 데이터센터 매출 $475억 — YoY 217% 성장",
            "시가총액 $3.4조 — 세계 1위 기업 (2024.6 달성)",
            "Blackwell GB200 수요 초과 — 2025 전량 사전판매 완료",
            "AI 학습 GPU 시장 점유율 92% (2025 기준)",
            "CUDA 개발자 500만 명+ — 사실상 산업 표준",
        ],
        "failures": [
            "H20 중국 수출 규제(2025.4) — 연 $120억 매출 차질",
            "AMD MI300X·Intel Gaudi3 경쟁 — 추론 시장 점유율 잠식 시작",
            "TSMC CoWoS 병목 — 수요 대비 공급 부족 지속",
            "미국 수출통제 강화로 글로벌 시장 축소 리스크",
            "고객사(MS·Google·Meta) 자체 칩 개발 가속 — 장기 점유율 위협",
        ],
    }):
        count += 1

    # TSMC
    if _update_entity(entity_repo, "TSMC", {
        "역할": "세계 최대 파운드리, 첨단 반도체 독점 생산",
        "objectives": [
            "첨단 파운드리 시장 90%+ 독점 유지",
            "3nm→2nm→A16 기술 로드맵 선도",
            "해외 팹(미국·일본·독일) 건설로 지정학 리스크 분산",
            "CoWoS 첨단 패키징 역량 3배 증설 (2025-26)",
        ],
        "strategy": [
            "N3/N2 공정 기술 격차 2년 이상 유지 (삼성·인텔 대비)",
            "미국 애리조나 Fab 21/22 건설 — $400억 투자",
            "일본 구마모토 Fab(JASM) — 소니·도요타 합작",
            "독일 드레스덴 Fab — 차량용 반도체",
            "해외 팹은 성숙 공정 위주 — 첨단은 대만 유지",
        ],
        "achievements": [
            "2024 매출 $880억, 순이익 $340억 — 사상 최대",
            "AI GPU 파운드리 100% 독점 (Nvidia·AMD·Broadcom 전량 TSMC)",
            "N3 공정 양산 성공 — 세계 유일 3nm 양산",
            "애리조나 Fab 21 첫 양산 시작(2025.Q1)",
            "시가총액 $1조+ — 아시아 최대 기업",
        ],
        "failures": [
            "대만 해협 지정학 리스크 — 최대 실존적 위협",
            "해외 팹 비용 50-70% 추가 — 수익성 압박",
            "애리조나 팹 인력 확보 난항 — 미국 엔지니어 부족",
            "2nm 양산 일정 2025 하반기 → 2026 지연 가능성",
            "CoWoS 병목 — 2025년 내내 수요 미충족 전망",
        ],
    }):
        count += 1

    # Huawei
    if _update_entity(entity_repo, "Huawei", {
        "역할": "미국 제재 하 중국 반도체 자립 선봉, AI칩 자체 개발",
        "objectives": [
            "미국 제재 하에서 첨단 반도체 자급 달성",
            "Ascend 910C/920으로 Nvidia 대체 시장 확보",
            "HarmonyOS 생태계로 Android/iOS 탈피",
            "5G 장비 글로벌 시장 지배력 유지",
        ],
        "strategy": [
            "SMIC 7nm 공정으로 Kirin 9000s·Ascend 910B/C 자체 생산",
            "미국 제재 우회 — 제3국 우회수입·역설계·인력 영입",
            "정부 보조금 활용 — 국내 시장 AI 인프라 독점 공략",
            "Mate 60 Pro 상징적 출시로 '기술 자립' 서사 강화",
        ],
        "achievements": [
            "Mate 60 Pro(2023.8) — 7nm Kirin 9000s 자체 칩 탑재, 제재 돌파 상징",
            "Ascend 910C AI칩 양산 — H100 대비 60% 추론 성능 (2026.2 기준)",
            "중국 정부·국영기업 AI 인프라 수주 독점",
            "HarmonyOS 글로벌 3위 모바일 OS (중국 내 Android 대체)",
            "5G 장비 글로벌 점유율 30% 유지 (서방 제외)",
        ],
        "failures": [
            "SMIC 7nm 수율 낮음 — 대량생산 한계, 비용 3배+",
            "EUV 장비 확보 불가 — 5nm 이하 진입 불가능",
            "Ascend 910C 성능 Nvidia H100 대비 40% 열세",
            "해외 시장(유럽·인도) 5G 장비 퇴출 가속",
            "소프트웨어 생태계(CUDA 대응) 미성숙 — 개발자 채택률 낮음",
        ],
    }):
        count += 1

    # US Commerce Dept
    if _update_entity(entity_repo, "US Commerce Dept", {
        "역할": "반도체 수출통제 집행 기관, Entity List 관리",
        "objectives": [
            "중국의 첨단 반도체·AI 역량 획득 차단",
            "미국 반도체 제조 리쇼어링 촉진 (CHIPS Act 집행)",
            "동맹국 수출통제 협조 체계 구축 (네덜란드·일본)",
        ],
        "strategy": [
            "Entity List 확대 — Huawei·SMIC·CXMT 등 150개+ 중국 기업",
            "AI칩 수출 성능 기준 강화 (TOPS 기준 → 대역폭·메모리 기준 추가)",
            "CHIPS Act $527억 보조금 집행 — 인텔·TSMC·삼성 미국 팹 유치",
            "제3국 우회 수출 단속 강화 (말레이시아·싱가포르·UAE 경유)",
            "일본(장비)·네덜란드(ASML) 수출통제 동조 확보",
        ],
        "achievements": [
            "Nvidia H20 중국 수출 금지(2025.4) — 디튠칩까지 차단",
            "ASML DUV 장비 중국 수출 제한 합의 (네덜란드)",
            "도쿄일렉트론 등 일본 장비 수출통제 동참 확보",
            "CHIPS Act 보조금 배분 시작 — 인텔 $85억, TSMC $66억",
            "중국 AI 칩 성능 격차 2년 이상 유지 성공",
        ],
        "failures": [
            "Huawei Mate 60 Pro — 제재에도 7nm 칩 생산 성공 (SMIC)",
            "우회 수출 근절 불가 — 동남아·중동 경유 지속",
            "동맹국 기업(ASML·도쿄일렉트론) 매출 타격 → 저항",
            "CHIPS Act 보조금 집행 지연 — 관료주의 비판",
            "중국 희토류 보복 수출통제 — 역풍",
        ],
    }):
        count += 1

    # Samsung Electronics
    if _update_entity(entity_repo, "Samsung Electronics", {
        "역할": "파운드리 2위, HBM 메모리 공급, AI 반도체 후발주자",
        "objectives": [
            "파운드리 점유율 TSMC 격차 축소 (현재 11% vs 62%)",
            "HBM3E Nvidia 공급 인증 확보",
            "2nm GAA 공정 선제 양산으로 기술 리더십 회복",
            "미국 텍사스 테일러 팹 완공 — 지정학 리스크 분산",
        ],
        "strategy": [
            "GAA(Gate-All-Around) 트랜지스터 기술 선도 (TSMC보다 먼저 적용)",
            "HBM3E 12단 적층 기술로 Nvidia 공급 인증 재도전",
            "시스템 반도체 투자 $300조원 (2030년까지)",
            "텍사스 테일러 $170억 팹 + 파운드리 고객 유치",
            "AI 가속기 Mach-1 자체 설계 추진",
        ],
        "achievements": [
            "HBM3E 8단 SK하이닉스 이후 2위 양산 성공",
            "3nm GAA 공정 세계 최초 양산 (수율은 개선 중)",
            "Nvidia HBM3E 공급 인증 일부 확보 (2025.Q1)",
            "텍사스 테일러 팹 건설 진행 — 2026 가동 목표",
            "DRAM·NAND 시장 1위 유지 — AI 서버 수요 수혜",
        ],
        "failures": [
            "파운드리 수율 문제 지속 — 3nm 수율 TSMC 대비 20%p 열세",
            "Nvidia GPU 파운드리 수주 실패 — TSMC 독점",
            "HBM3E 12단 Nvidia 인증 지연 — SK하이닉스에 후발",
            "텍사스 팹 건설 지연 + 비용 초과",
            "퀄컴·구글 등 주요 고객 TSMC 이탈 — 파운드리 점유율 하락",
        ],
    }):
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 5. 러시아-우크라이나 전쟁
# ============================================================
def update_russia_ukraine(entity_repo: OntologyEntityRepository) -> int:
    """러시아-우크라이나 전쟁 이슈 핵심 엔티티 보강."""
    print("\n=== 5. 러시아-우크라이나 전쟁 ===")
    count = 0

    # Russia
    if _update_entity(entity_repo, "Russia", {
        "역할": "침공국, 점령지 합병 선언, 장기 소모전 수행",
        "objectives": [
            "우크라이나 NATO 가입 영구 차단",
            "돈바스 4개주 + 크림반도 합병 기정사실화",
            "우크라이나 비무장화·중립화",
            "서방 제재 체제 와해 — 제재 피로감 활용",
            "구소련 영향권 회복",
        ],
        "strategy": [
            "소모전·진지전(trench warfare) — 인력·포탄 물량 우세 활용",
            "글라이드 폭탄(KAB) + 드론 대량 투입 — 저비용 정밀타격",
            "에너지 인프라 집중 타격 — 우크라이나 겨울 약화 전략",
            "북한 병력 투입(~12,000명) — 인력 소모 보충",
            "중국·인도 석유 수출로 제재 우회 재원 확보",
            "정전 협상 지연 전략 — 트럼프 중재 거부 또는 최대 요구",
        ],
        "achievements": [
            "돈바스 동부(도네츠크·루한스크) 점령 확대 — 2024-25 서진",
            "우크라이나 에너지 인프라 70% 파괴 (2024-25 겨울 공세)",
            "경제 제재에도 GDP 성장 유지 — 2024년 3.6%, 군수 경기",
            "서방 제재 피로감 확산 — 유럽 내 '협상론' 대두",
            "크림반도 군사 요새화 완료",
            "북한·이란으로부터 무기·병력 확보 — 동맹 다변화",
        ],
        "failures": [
            "하르키우 공세(2024.5) 실패 — 국경 완충지대 미확보",
            "쿠르스크 우크라이나 역습(2024.8) — 러시아 본토 영토 상실",
            "흑해함대 주력함 격침 — 세바스토폴 기지 무력화",
            "서방 무기(HIMARS·Storm Shadow) 투입으로 종심 타격 허용",
            "병력 손실 60만+ 추정 — 인구 감소 장기 위기",
            "SWIFT 배제·자산 동결로 외환보유액 $3,000억 접근 불가",
        ],
    }):
        count += 1

    # Ukraine
    if _update_entity(entity_repo, "Ukraine", {
        "역할": "방어국, NATO 가입 추진, 영토 탈환 작전 수행",
        "objectives": [
            "1991년 국경 회복 — 크림반도·돈바스 포함",
            "NATO 가입 — 안보 보장 확보",
            "EU 가입 — 경제·제도 통합",
            "전후 재건 투자 유치 ($1조+ 추정)",
        ],
        "strategy": [
            "장거리 미사일(ATACMS·Storm Shadow)로 러시아 종심 타격",
            "드론 혁신 — 자체 FPV 드론 월 10만 대 생산",
            "쿠르스크 역습 — 러시아 본토 진입으로 협상 레버리지 확보",
            "서방 무기 지원 의존 + 외교적 압박으로 지원 지속 확보",
            "에너지 인프라 분산·지하화 — 러시아 공습 복원력 강화",
        ],
        "achievements": [
            "쿠르스크 역습(2024.8) — 러시아 본토 1,000km² 점령",
            "흑해함대 주력함 격침 — 크리미아 해상 봉쇄 사실상 해제",
            "드론 전쟁 혁신 — 세계 군사 전술 패러다임 변화 주도",
            "EU 가입 협상 개시(2024.6)",
            "F-16 전투기 수령·실전 배치(2024.8~)",
            "서방 동결 러시아 자산 이자 $500억 지원금 확보",
        ],
        "failures": [
            "2023 반격 실패 — 영토 탈환 미미",
            "병력 부족 심각 — 동원령 확대에도 전선 인력 부족",
            "에너지 인프라 70% 파괴 — 겨울 인도적 위기",
            "트럼프 행정부 지원 축소·조건부화 — 최대 불확실성",
            "전쟁 피로감 — 국내 여론 '영토 양보 협상' 소수 의견 증가",
            "GDP -30%(2022) 후 회복 더디 — 경제 전시 체제 한계",
        ],
    }):
        count += 1

    # NATO
    if _update_entity(entity_repo, "NATO", {
        "역할": "우크라이나 무기 지원, 동유럽 방어 강화, 대러 억지",
        "objectives": [
            "러시아 확전 억지 — NATO 영토 방어",
            "우크라이나 주권 회복 지원 (NATO 가입은 전후 과제)",
            "동부 측면(Eastern Flank) 방어 태세 강화",
            "유럽 방위비 GDP 2%+ 달성",
        ],
        "strategy": [
            "우크라이나 무기·탄약·훈련 지원 — 직접 참전 없이",
            "핀란드(2023)·스웨덴(2024) NATO 가입 — 러시아 포위 강화",
            "동유럽 전진배치 병력 30만 명 고준비태세(High Readiness) 전환",
            "국방비 GDP 2% → 3% 목표 상향 논의",
            "핵 억지력 재확인 — 러시아 핵 위협 대응",
        ],
        "achievements": [
            "핀란드·스웨덴 가입 — 나토-러시아 국경 2배 확대, 발트해 NATO 호수화",
            "우크라이나 무기 지원 $1,500억+ (미국·유럽 합산)",
            "동유럽 4개 전투단 → 8개 전투단 증강",
            "HIMARS·Patriot·Storm Shadow·F-16 등 첨단 무기 공급",
            "회원국 31→32개국 — 냉전 후 최대 확장",
        ],
        "failures": [
            "우크라이나 NATO 가입 시점 미정 — '전쟁 중 가입' 거부",
            "탄약 생산량 부족 — 유럽 방산 산업 역량 한계 노출",
            "미국 트럼프 행정부 NATO 관여 축소 리스크 — 유럽 부담 전가",
            "회원국 간 대러 온도차 — 헝가리·터키 이탈 행보",
            "전쟁 종결 후 우크라이나 안보 보장 모델 합의 실패",
        ],
    }):
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 6. 대만 해협 위기
# ============================================================
def update_taiwan_strait(entity_repo: OntologyEntityRepository) -> int:
    """대만 해협 위기 이슈 핵심 엔티티 보강."""
    print("\n=== 6. 대만 해협 위기 ===")
    count = 0

    # China (대만 관점)
    china = entity_repo.find_by_name("China")
    if china:
        props = dict(china.properties)
        taiwan_china = {
            "대만_역할": "대만 통일 목표국, 군사적 압박 강화 중",
            "대만_objectives": [
                "대만 통일 — '하나의 중국' 원칙 실현 (시진핑 역사적 과업)",
                "미국의 대만 군사개입 억지·비용 극대화",
                "대만 반도체 공급망 통제 — TSMC 확보",
            ],
            "대만_strategy": [
                "회색지대 전략 — 군사훈련·해상봉쇄 연습·사이버공격 상시화",
                "반접근/지역거부(A2/AD) — 미군 대만해협 접근 차단 역량 구축",
                "경제적 압박 — 대만 과일·수산물 수입 금지, 관광 차단",
                "외교적 고립 — 대만 수교국 13→12개국으로 축소",
                "2027 군사 역량 달성 목표 (미 국방부 보고서)",
            ],
            "대만_achievements": [
                "대만 해협 군사 연습 상시화 — 중간선 무력화(2022~)",
                "대만 수교국 12개로 축소 — 나우루(2024.1) 단교",
                "해군력 세계 1위 함정 수(350척+) — 양적 우세",
                "DF-21D/DF-26 대함탄도미사일 — 항모 킬러 배치",
                "대만 경제 의존도 유지 — 대중 수출 비중 35%+",
            ],
            "대만_failures": [
                "무력 통일 시 글로벌 반도체 공급망 붕괴 — 자국 피해 극심",
                "미국·일본·호주 대만 방어 의지 강화 — 억지력 증가",
                "대만 여론 90%+ '현상유지 or 독립' — 통일 지지 5% 미만",
                "상륙작전 역량 부족 — 대만해협 130km 도해 능력 의문",
                "라이칭더(민진당) 총통 당선(2024) — 친중 정권 교체 실패",
            ],
        }
        merged = _merge_props(props, taiwan_china)
        entity_repo.update(china.id, properties=merged)
        print(f"  UPDATE: China — 대만 관점 필드 추가")
        count += 1

    # Taiwan
    if _update_entity(entity_repo, "Taiwan", {
        "역할": "사실상 독립국, 반도체 핵심 거점, 미중 각축 최전선",
        "objectives": [
            "현상유지 — 사실상 독립 지위 수호",
            "미국·일본·EU와 안보 협력 강화",
            "반도체 '실리콘 방패' 지위 유지 — 억지력의 핵심",
            "국방력 비대칭 전력 강화 — 중국 상륙 저지",
        ],
        "strategy": [
            "'고슴도치 전략(porcupine strategy)' — 비대칭 방어에 집중",
            "하푼 대함미사일·기뢰·해안방어 역량 강화",
            "병역 1년 복원(2024) + 예비군 현대화",
            "TSMC를 '실리콘 방패'로 활용 — 전쟁 시 글로벌 경제 피해 과시",
            "미국 무기 조달 가속 — $190억 무기 패키지",
        ],
        "achievements": [
            "라이칭더 총통 취임(2024.5) — 민진당 3연속 집권",
            "미국 무기 $190억 조달 추진 — 역대 최대",
            "TSMC 실리콘 방패 서사 국제 공감 확보",
            "일본 유사시 개입 공식화(2022 안보전략) — 안보 파트너 확대",
            "잠수함 자체 건조 프로그램 시작 (해곤급, 2023 진수)",
        ],
        "failures": [
            "중국 의존도 높은 경제구조 — 수출 35% 대중 의존",
            "군사력 비대칭 심각 — 중국 국방비 대비 1/15 수준",
            "무기 조달 지연 — 미국 무기 인도 수년 대기",
            "32% 미국 관세 부과(2025) — 경제 타격 + 동맹 불안",
            "국내 '전쟁 회피론' 확산 — 젊은 세대 방어 의지 의문",
        ],
    }):
        count += 1

    # TSMC (리스크 관점) — 이미 AI/반도체에서 업데이트했으므로 대만 리스크만 추가
    tsmc = entity_repo.find_by_name("TSMC")
    if tsmc:
        props = dict(tsmc.properties)
        tsmc_risk = {
            "대만_리스크": "대만 해협 분쟁 시 글로벌 반도체 생산 92% 차질 — 세계 GDP $1조+ 손실 추정",
            "대만_대응": "미국·일본·독일 해외 팹 건설로 분산, 그러나 첨단 공정은 2030년까지 대만 집중 불가피",
            "대만_시나리오": "중국 봉쇄 시 TSMC 가동 중단 → Nvidia·Apple·AMD·Qualcomm 전량 생산 차질",
        }
        merged = _merge_props(props, tsmc_risk)
        entity_repo.update(tsmc.id, properties=merged)
        print(f"  UPDATE: TSMC — 대만 리스크 관점 3개 필드 추가")
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 7. 유럽 정치 위기
# ============================================================
def update_europe_crisis(entity_repo: OntologyEntityRepository) -> int:
    """유럽 정치 위기 이슈 핵심 엔티티 보강."""
    print("\n=== 7. 유럽 정치 위기 ===")
    count = 0

    # France
    if _update_entity(entity_repo, "France", {
        "역할": "EU 핵심국, 정치 불안정으로 유럽 리더십 공백",
        "objectives": [
            "정치 안정 회복 — 불신임 후 안정 정부 구성",
            "재정적자 GDP 6% → 3% 감축 (EU 재정규율 복귀)",
            "연금개혁 유지 + 사회적 합의 도출",
            "EU 내 독일과 공동 리더십(Franco-German axis) 복원",
        ],
        "strategy": [
            "중도 연립(마크롱) 소수정부 운영 — 사안별 법안 통과",
            "극우(RN)·극좌(NFP) 양날개 견제 — 중도 실용주의",
            "국방비 증액으로 유럽 안보 리더십 주장",
            "원자력 재투자 — 에너지 자립 + 탈탄소 동시 추구",
        ],
        "achievements": [
            "EU 유일 핵보유국으로 유럽 핵우산 논의 주도",
            "원전 6기 신규 건설 결정(2022) — 에너지 자립 추진",
            "마크롱 유럽군 구상 — 미국 의존 탈피 의제 설정",
            "2024 파리 올림픽 성공적 개최 — 국가 위상 유지",
        ],
        "failures": [
            "2024 조기총선 → 헝 의회(hung parliament) — 안정 정부 불가",
            "바르니에 총리 불신임(2024.12) — 5공화국 이래 가장 짧은 총리",
            "재정적자 GDP 6.1% — EU 재정규율 위반",
            "노란조끼·연금개혁 시위 — 사회 분열 지속",
            "극우 RN 르펜 30%+ 지지율 — 2027 대선 위협",
            "신용등급 Fitch AA- 하향 (2024)",
        ],
    }):
        count += 1

    # Germany
    if _update_entity(entity_repo, "Germany", {
        "역할": "EU 최대 경제국, 연립 붕괴 후 정치 리셋 중",
        "objectives": [
            "경제 침체 탈출 — 2년 연속 역성장 후 회복",
            "안정 정부 구성 — 2025.2 총선 후 연립 재건",
            "Zeitenwende(시대전환) — 국방비 GDP 2%+ 달성",
            "에너지 전환(Energiewende) 완수 — 탈원전 후 재생에너지 비중 80%",
        ],
        "strategy": [
            "CDU/CSU 메르츠 중심 대연정 또는 3당 연립 추진",
            "국방비 특별기금 €1,000억 집행 가속",
            "산업전기료 보조금으로 제조업 유출 방지",
            "미국 관세 대응 — EU 공동 대응 주도",
        ],
        "achievements": [
            "국방비 특별기금 €1,000억 확보(2022) — 역대 최대 군비 증강",
            "LNG 인프라 6개월 만에 구축(2022-23) — 러시아 가스 탈피",
            "재생에너지 전력 비중 55%+ 달성(2024)",
            "2025.2 총선 → CDU 프리드리히 메르츠 총리 취임 — 정치 리셋",
        ],
        "failures": [
            "GDP 2023 -0.3%, 2024 -0.2% — 2년 연속 역성장 ('유럽의 병자')",
            "자동차 산업 위기 — VW 공장 폐쇄 검토, 중국 EV에 밀림",
            "에너지 비용 미국 대비 3배 — 산업 경쟁력 약화",
            "극우 AfD 20%+ 지지 — 동독 지방선거 1위",
            "우크라이나 무기 지원 속도 비판 — '주저하는 리더십'",
            "탈원전(2023.4) 후 전력 비용 상승 — 정책 재검토 논의",
        ],
    }):
        count += 1

    # Russia (하이브리드전 관점) — 이미 러-우 전쟁에서 업데이트했으므로 하이브리드전 맥락 추가
    russia = entity_repo.find_by_name("Russia")
    if russia:
        props = dict(russia.properties)
        hybrid = {
            "하이브리드전_역할": "유럽 대상 하이브리드 전쟁 수행 — 사이버·정보·에너지 무기화",
            "하이브리드전_objectives": [
                "유럽 정치 분열 촉진 — 극우·극좌 지원으로 NATO 약화",
                "에너지 의존 레버리지 유지 — LNG·파이프라인 무기화",
                "유럽 내 '우크라이나 전쟁 피로감' 극대화",
            ],
            "하이브리드전_strategy": [
                "소셜미디어 허위정보 캠페인 — 선거 개입",
                "에너지 공급 차단·가격 조작 — 유럽 경제 압박",
                "사이버 공격 — 인프라·정부기관 타겟",
                "극우 정당 자금·네트워크 지원 (AfD·RN 의혹)",
            ],
            "하이브리드전_achievements": [
                "유럽 에너지 위기 촉발(2022) — 가스 가격 10배 급등",
                "극우 정당 약진에 간접 기여 — AfD(독일), RN(프랑스) 지지율 사상 최고",
                "유럽 내 '협상론' 확산 — 전쟁 피로감 활용",
            ],
            "하이브리드전_failures": [
                "에너지 무기화 역효과 — 유럽 러시아 가스 의존도 45%→15% 급감",
                "핀란드·스웨덴 NATO 가입 촉발 — 전략적 역풍",
                "유럽 방위 각성 — 국방비 증액·방산 투자 가속",
            ],
        }
        merged = _merge_props(props, hybrid)
        entity_repo.update(russia.id, properties=merged)
        print(f"  UPDATE: Russia — 하이브리드전 관점 필드 추가")
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 8. 글로벌 AI 규제
# ============================================================
def update_ai_regulation(entity_repo: OntologyEntityRepository) -> int:
    """글로벌 AI 규제 이슈 핵심 엔티티 보강."""
    print("\n=== 8. 글로벌 AI 규제 ===")
    count = 0

    # EU AI Act
    if _update_entity(entity_repo, "EU AI Act", {
        "역할": "세계 최초 포괄적 AI 규제법, 글로벌 AI 거버넌스 기준점",
        "objectives": [
            "AI 시스템의 안전성·투명성·책임성 보장",
            "고위험 AI 사용 규제로 기본권 보호",
            "'신뢰할 수 있는 AI(Trustworthy AI)' 글로벌 표준 선도",
            "브뤼셀 효과(Brussels Effect) — EU 규제를 글로벌 디팩토 표준화",
        ],
        "strategy": [
            "리스크 기반 4단계 분류 — 금지/고위험/제한/최소 리스크",
            "범용 AI(GPAI) 모델 별도 규제 — 투명성 의무",
            "AI Office 신설 — 집행 기관",
            "위반 시 매출 7% 과징금 — GDPR 수준 제재",
        ],
        "achievements": [
            "2024.3 유럽의회 최종 통과 — 세계 최초 포괄적 AI법",
            "2024.8 발효, 2025.2 1단계 시행(금지 AI 유형)",
            "글로벌 AI 규제 논의 촉발 — 미국·일본·한국 참조",
            "챗봇 AI 공개 의무 등 투명성 조항 선도",
        ],
        "failures": [
            "혁신 저해 우려 — EU AI 스타트업 투자 미국 대비 1/6",
            "범용 AI 규제 모호 — OpenAI·Google 적용 범위 논쟁 중",
            "프랑스 반발 — 자국 AI 기업(Mistral) 보호 요구로 타협",
            "시행 세칙 미완 — 2026 전면 시행까지 불확실성",
            "미국·중국 미채택 — '브뤼셀 효과' 한계 가능성",
        ],
    }):
        count += 1

    # OpenAI
    if _update_entity(entity_repo, "OpenAI", {
        "역할": "AI 선두 기업, GPT 시리즈 개발, AI 규제 논쟁 핵심",
        "objectives": [
            "AGI(범용 인공지능) 달성 — 회사 미션",
            "GPT 시리즈로 AI 시장 지배력 유지",
            "비영리→영리 전환 완료로 기업가치 극대화",
            "AI 안전과 상업화 균형 — 규제 환경 유리하게 형성",
        ],
        "strategy": [
            "GPT-4o/o1/o3 모델 순차 출시 — 성능 리더십 유지",
            "ChatGPT 구독 모델 + API 플랫폼 — B2C + B2B 동시 공략",
            "마이크로소프트 $130억 투자 + Azure 독점 파트너십",
            "AI 안전 연구 공개 — 규제 기관과 선제적 협력",
            "영리 전환(2025) — $1,570억 기업가치 달성",
        ],
        "achievements": [
            "ChatGPT 주간 활성 사용자 3억 명(2025) — AI 역사상 최대",
            "기업가치 $3,000억(2025.3 펀딩 라운드)",
            "GPT-4o 멀티모달 — 텍스트·이미지·음성·비디오 통합",
            "AI 대중화 주도 — 'AI 시대' 개막 트리거",
            "마이크로소프트 통한 엔터프라이즈 AI 시장 장악",
        ],
        "failures": [
            "샘 알트만 해임·복귀 사태(2023.11) — 거버넌스 혼란",
            "비영리 미션 후퇴 비판 — 공동창업자(머스크·수츠케버) 이탈",
            "GPT-5 출시 지연 — 스케일링 법칙 한계 논쟁",
            "EU AI Act 범용 AI 규제 대상 — 컴플라이언스 비용 증가",
            "저작권 소송 다수 — NYT, Getty 등 콘텐츠 무단 학습 논란",
            "Google(Gemini)·Anthropic(Claude) 경쟁 심화 — 독주 체제 약화",
        ],
    }):
        count += 1

    # China (AI 규제 관점)
    china = entity_repo.find_by_name("China")
    if china:
        props = dict(china.properties)
        ai_reg = {
            "AI규제_역할": "국가 주도 AI 육성 + 선택적 규제 — 미국과 이중 패권",
            "AI규제_objectives": [
                "2030 AI 세계 1위 목표 (국무원 AIDP 계획)",
                "AI 기술 주권 확보 — 미국 의존도 제로화",
                "AI를 사회 통제 도구로 활용 — 감시·검열 체계 강화",
            ],
            "AI규제_strategy": [
                "생성AI 관리조치(2023.8) — 세계 최초 생성AI 규제",
                "딥페이크 금지, AI 생성 콘텐츠 라벨링 의무",
                "알고리즘 추천 규제(2022) — 플랫폼 알고리즘 등록 의무",
                "AI 기업 국가 보조금 + 데이터 접근 우대 (바이두, 알리바바)",
            ],
            "AI규제_achievements": [
                "세계 최초 생성AI 규제법 시행(2023.8)",
                "DeepSeek R1 오픈소스 모델 — GPT-4 수준 성능 저비용 달성",
                "AI 특허 출원 세계 1위 — 미국 추월",
                "Baidu ERNIE, Alibaba Qwen 등 자체 LLM 생태계 구축",
            ],
            "AI규제_failures": [
                "첨단 AI칩(H100급) 자급 실패 — 미국 수출통제 영향",
                "AI 검열 의무 → 모델 성능 제약 (정치적 민감 주제 필터링)",
                "글로벌 AI 오픈소스 생태계 참여 제한 — 기술 고립 리스크",
                "AI 인재 미국 유출 지속",
            ],
        }
        merged = _merge_props(props, ai_reg)
        entity_repo.update(china.id, properties=merged)
        print(f"  UPDATE: China — AI 규제 관점 필드 추가")
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 9. 일본 금리 전환
# ============================================================
def update_japan_rate(entity_repo: OntologyEntityRepository) -> int:
    """일본 금리 전환 이슈 핵심 엔티티 보강."""
    print("\n=== 9. 일본 금리 전환 (BOJ) ===")
    count = 0

    # Bank of Japan
    if _update_entity(entity_repo, "Bank of Japan", {
        "역할": "일본 중앙은행, 30년 만의 금리 정상화 추진",
        "objectives": [
            "물가 안정 목표 2% 지속적 달성",
            "마이너스 금리·YCC 탈피 → 정상 통화정책 복귀",
            "엔화 과도한 약세 방지 — 수입 물가 안정",
            "부작용 최소화하며 점진적 금리 인상",
        ],
        "strategy": [
            "2024.3 마이너스 금리 해제(0.0%) — 17년 만의 금리 인상",
            "2024.7 0.25%, 2025.1 0.5% 추가 인상 — 점진적 접근",
            "YCC(수익률곡선통제) 사실상 폐지(2024.3)",
            "ETF·REIT 신규 매입 중단 — 비전통적 수단 정리",
            "우에다 총재 '데이터 의존' 접근 — 신중한 커뮤니케이션",
        ],
        "achievements": [
            "마이너스 금리 17년 만에 종료(2024.3) — 역사적 전환",
            "YCC 폐지 성공 — 시장 충격 최소화",
            "CPI 2%+ 24개월 연속 달성 — 디플레이션 탈출 선언",
            "금리 0.5% 도달 — 2008년 이후 최고",
            "경제 연착륙 진행 중 — GDP 양의 성장 유지",
        ],
        "failures": [
            "2024.8 금리 인상 쇼크 — 닛케이 -12.4% 역대 최대 폭락 촉발",
            "엔 캐리트레이드 급격한 청산 — 글로벌 금융시장 혼란",
            "엔화 약세 지속 — 150엔대 유지, 금리 인상에도 효과 제한",
            "실질임금 상승 미약 — 명목 임금 - 물가 = 마이너스 지속",
            "국채 이자 부담 급증 — GDP 260% 부채에 금리 인상 = 재정 압박",
            "추가 금리 인상 시기 불확실 — 미국 경기·관세 변수",
        ],
    }):
        count += 1

    # Japanese Yen
    if _update_entity(entity_repo, "Japanese Yen", {
        "역할": "세계 3대 준비통화, 캐리트레이드 핵심 통화",
        "objectives": [
            "적정 환율 회복 — 130~140엔대 (현재 150엔대)",
            "캐리트레이드 질서 있는 축소",
            "안전자산 지위 회복 — 위기 시 엔 강세 복원",
        ],
        "strategy": [
            "BOJ 금리 인상과 연동한 점진적 엔화 강세 유도",
            "재무성 환율 개입 — 2024년 $620억 규모 개입 실시",
            "미일 금리차 축소로 자연스러운 엔 강세 유도",
        ],
        "achievements": [
            "161엔(2024.7 역사적 약세) → 140엔대 반등(2024.9)",
            "재무성 환율 개입 효과 — 급격한 약세 방어 성공",
            "BOJ 금리 인상 기대로 캐리트레이드 일부 청산 진행",
        ],
        "failures": [
            "150엔대 고착화 — BOJ 금리 인상에도 미일 금리차 여전",
            "2024.8 캐리트레이드 청산 쇼크 — 글로벌 주식시장 폭락 동반",
            "엔 약세 → 수입 물가 상승 → 실질 구매력 감소 악순환",
            "안전자산 지위 약화 — 위기 시에도 엔 강세 반응 둔화",
            "미국 금리 인하 지연 시 엔 약세 지속 리스크",
        ],
    }):
        count += 1

    print(f"  총 {count}개 엔티티 업데이트 완료")
    return count


# ============================================================
# 메인 실행
# ============================================================
ISSUE_MAP = {
    1: ("비트코인 지정학", update_bitcoin_geopolitics),
    2: ("IMEC 회랑", update_imec_corridor),
    3: ("트럼프 관세전쟁 2.0", update_tariff_war),
    4: ("AI/반도체 패권전쟁", update_ai_chip_war),
    5: ("러시아-우크라이나 전쟁", update_russia_ukraine),
    6: ("대만 해협 위기", update_taiwan_strait),
    7: ("유럽 정치 위기", update_europe_crisis),
    8: ("글로벌 AI 규제", update_ai_regulation),
    9: ("일본 금리 전환", update_japan_rate),
}


def main() -> None:
    """메인 실행."""
    init_db()
    entity_repo = OntologyEntityRepository()

    # 인자로 이슈 번호 지정 가능
    if len(sys.argv) > 1:
        issue_num = int(sys.argv[1])
        if issue_num not in ISSUE_MAP:
            print(f"ERROR: 이슈 번호 {issue_num} 없음 (1-9)")
            sys.exit(1)
        title, func = ISSUE_MAP[issue_num]
        print(f"이슈 {issue_num}: {title} 엔티티 프로퍼티 보강 시작...")
        func(entity_repo)
    else:
        print("GeoInvest 9개 이슈 엔티티 프로퍼티 전체 보강 시작...\n")
        total = 0
        for num, (title, func) in ISSUE_MAP.items():
            total += func(entity_repo)
        print(f"\n전체 완료! 총 {total}개 엔티티 업데이트")


if __name__ == "__main__":
    main()
