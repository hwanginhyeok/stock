# Finished Tasks

> 2026-03 이전 → [TASK_ARCHIVE/2026-03.md](TASK_ARCHIVE/2026-03.md)

| # | 태스크 | 완료일 | 비고 |
|---|--------|--------|------|
| 1-49 | 자체 차트 시스템 구축 (TSLA) | 2026-04-15 | TV 위젯 + lightweight-charts + yfinance + SMA6/VWMA100/VPVR/RSI/MACD + 멀티 타임프레임(1H/4H/D/W/M) + 매수매도 시그널 + 인범 빗각(고고저/저저고) + 평행 채널 + VP 교차 + XY축 독립 줌. 후속: 1-50~53. D-006 기록 |
| 5-9 | trend_detector Ollama→Gemini Flash 전환 | 2026-04-08 | gemini -p 1차 + Ollama fallback, dry-run 통과 |
| 1-41 | 엔티티 노이즈 필터 강화 — 금액/수량/비자 패턴 | 2026-04-08 | 공통 모듈 + DB 45개 정리 (3183→3138) |
| 1-42 | 뉴스 티커 최신화 + GEO/US/KR 핫뉴스 2개씩 | 2026-04-08 | published_at 정렬, 카테고리별 선별 |
| 1-37 | 관계 브리핑 가독성 개선 — 중요도 순 + 한국어 라벨 | 2026-04-08 | 엔티티별 집계, 빈도×신뢰도 소팅 |
| 1-38 | 관계도 깊이/밀도 제어 — BFS depth + pruning | 2026-04-08 | depth 1/2/3 선택, 하위 30% 자동 제거 |
| 5-10 | 온톨로지 이론 기반 문서화 (276줄) | 2026-04-08 | 철학 계보 + 본질론 + 공학 방법론 + FIBO |
| 1-39 | Stock 엔티티 온톨로지 설계 — 본질적 속성 추출 | 2026-04-08 | 프롬프트 + config 스키마 (essential/propria) |
| 1-36 | 관계도 Top N 필터 + 이벤트 카테고리 확장 | 2026-04-07 | Top 10/20/50/전체 필터, degree 랭킹 |
| 1-35 | InvestOS 이벤트 체계 대개편 — EventType 분리 + 스토리 체이닝 + 타임라인 뷰 | 2026-04-07 | 275개 이벤트, 121개 story_thread |
| 1-34 | 심층분석 파이프라인 + cron 재설계 | 2026-04-06 | Ollama 하루2회(05:30/17:30), 수집 15분→1시간 |
| 1-33 | cron 뉴스 수집 URL/도메인 노이즈 3단 필터 | 2026-04-06 | title 소스명 제거 + 저장 필터 + 92개 오염 엔티티 삭제 |
| 1-31a | InvestOS US/KR 주식 탭 + 엔티티 추출 + 리뷰 파이프라인 | 2026-04-04 | 3탭, Ollama 추출 cron, 리뷰(타입368+병합55+중복159), 번역, 캐시 |
| 1-31b | GeoInvest Ollama 전환 (Claude API 제거) | 2026-04-04 | API 비용 0원 |
| 1-31c | 뉴스 티커 한국어 번역 + 속도 조절 | 2026-04-04 | Ollama 일괄 번역, 10분 캐시 |
| 1-31d | 타임라인 최신순 정렬 + entity_type 유효성 | 2026-04-04 | reverse=True, institution fallback |
| 1-23 | 크립토 이메일 Section 6 | 2026-04-03 | COIN/HOOD/MSTR/SQ/BLK/BMNR |
| 2-13 | naver HTML 한글 깨짐 수정 + briefing_server | 2026-04-01 | fragment→full document wrapper |
