# Archive — 사용하지 않는 코드

## scripts_seed/
DB 초기 데이터 적재용 1회성 스크립트. 이미 실행 완료.
- seed_iran_issue.py — 이란 지정학 이슈
- seed_tariff_war.py — 트럼프 관세전쟁
- seed_ai_chips_war.py — AI 반도체 패권전쟁
- seed_bitcoin_issue.py — 비트코인 지정학
- seed_imec_issue.py — IMEC 회랑
- seed_overnight_expansion.py — 야간 확장
- seed_stock_issues.py — 주식 이슈

## scripts_migrate/
DB 마이그레이션/수정용 1회성 스크립트.
- migrate_geoinvest.py — GeoInvest DB 컬럼 추가
- fix_issue_entity_ids.py — 이슈 엔티티 ID 수정
- update_geoinvest_entity_props.py — 엔티티 속성 업데이트

## scripts_standalone/
독립 실행 스크립트 중 레거시.
- benchmark_geoinvest.py — AI 온톨로지 품질 벤치마크
- briefing_server.py — 브리핑 서버 (미사용)

## 아카이브 기준
- 1회 실행 후 재사용 없음
- 기능이 다른 코드로 대체됨
- DB 마이그레이션 완료
