# 기능 요구사항 (Features)

> 주식부자프로젝트 핵심 기능 목록. health_check.py가 이 테이블의 각 항목을 검증한다.

| ID | 기능 | 기대 동작 | 검증 방법 | 우선순위 | 상태 |
|----|------|----------|---------|---------|------|
| F001 | 뉴스 수집+분류 | 매시 :00 실행, news_collect.log에 정상 로그 | log_freshness(news_collect.log, 2h) | P0 | ✅ |
| F002 | 지정학 엔티티 추출 | 매시 :10 실행, geoinvest_update.log 정상 | log_freshness(geoinvest_update.log, 2h) | P1 | ✅ |
| F003 | 주식 엔티티 추출 | 매시 :00 실행, stockinvest_update.log 정상 | log_freshness(stockinvest_update.log, 2h) | P0 | ✅ |
| F004 | 엔티티 리뷰 | 04:00 매일 실행, entity_review.log 정상 | log_freshness(entity_review.log, 26h) | P1 | ✅ |
| F005 | 심층분석 | 05:30+17:30 실행, deep_analysis.log 정상 | log_freshness(deep_analysis.log, 14h) | P1 | ✅ |
| F006 | 모닝 브리핑 | 06:00 실행, briefing_YYYYMMDD_morning.log 생성 | briefing_exists(morning) | P0 | ✅ |
| F007 | 이브닝 브리핑 | 18:00 실행, briefing_YYYYMMDD_evening.log 생성 | briefing_exists(evening) | P0 | ✅ |
| F008 | 실적 리포트 파이프라인 | earn_reporter.py 정상 동작, docs/earnings/ 파일 존재 | earnings_dir_check() | P2 | ✅ |
| F009 | Essence 대시보드 | 웹서버 정상, /api/tesla/essence 응답 | http_check(localhost:5001) | P1 | ✅ |
