# Difficulties & Know-how

## D-001: 네이버 HTML 한글 깨짐
- **날짜**: 2026-03-23 ~ 2026-04-01
- **상황**: 브리핑 HTML을 네이버 블로그에 붙여넣으면 한글이 깨져서 출력
- **이슈**: `<meta charset="utf-8">`을 넣었는데도 브라우저가 인코딩을 무시. 네이버 에디터에서 HTML fragment를 직접 렌더링하면 charset 선언이 적용 안 됨
- **삽질**: (1) meta charset을 HTML 상단에 추가 → 효과 없음 (2) BOM 추가 시도 → 네이버가 BOM 제거 (3) Content-Type 헤더 시도 → 파일 붙여넣기라 HTTP 헤더 불가
- **해결**: `briefing_server.py` 로컬 서버를 만들어 HTML fragment를 `<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>...` 전체 문서로 감싸서 서빙. 브라우저에서 렌더링 후 복사-붙여넣기
- **대안**: (a) Python으로 직접 네이버 API 호출 → API가 HTML 본문 지원 안 함 (b) Playwright로 자동 붙여넣기 → 네이버 에디터 DOM 구조가 복잡해서 불안정
- **노하우**: HTML fragment를 브라우저에서 볼 때는 반드시 `<head>` 안에 charset을 넣은 full document wrapper로 서빙. fragment 단독으로는 charset이 작동 안 함
- **회고**: 처음부터 로컬 preview 서버를 만들었으면 디버깅이 훨씬 빨랐을 것. "왜 meta charset이 안 먹지?"에서 출발했는데, 질문 자체가 잘못됨 — fragment에는 head가 없으니 meta가 의미 없음
- **관련 파일**: `scripts/briefing_server.py`, `src/generators/briefing_generator.py`

## D-002: RSS 뉴스 수집 소스 도메인/URL 노이즈
- **날짜**: 2026-03-25 ~ 2026-04-06
- **상황**: 15분마다 RSS 수집 → Ollama 엔티티 추출 → InvestOS 대시보드에서 `cnn.com`, `marketplace.org` 같은 도메인이 엔티티로 표시
- **이슈**: Google News RSS title이 `"헤드라인 - CNBC"` 형식으로 소스명 포함. Ollama gemma3:4b가 이를 엔티티로 추출. 또한 `$71,500`, `metadata`, `2월` 같은 노이즈도 추출
- **삽질**: (1) Ollama 프롬프트에 "도메인 추출 금지" 추가 → gemma3:4b가 무시 (2) content 필드에서 URL 검색 → 0.4%만 해당, 핵심 원인 아님 (3) RSS summary 확인 → Google News는 HTML에 URL 포함하지만 _extract_text()가 잘 처리
- **해결**: 3단 필터 조합: (A) `_parse_entry()`에서 title 끝 `" - SourceName"` 정규식 제거 (B) `_save_extraction()`에서 도메인 패턴/노이즈 단어 필터 (C) `review_entities.py` Phase 0에서 기존 오염 92개 삭제
- **대안**: (a) 더 큰 모델(12b) 사용 → RTX 2060 6GB에서 느림 (b) Claude API로 추출 → 비용 발생 (c) 프롬프트만 개선 → 소형 모델 한계
- **노하우**: LLM 추출 결과는 반드시 사후 필터를 거쳐야 함. 입력 정제(A) + 출력 필터(B) + 정기 청소(C) 3단 방어가 필요. 프롬프트 하나로 소형 모델의 한계를 극복하려 하지 말 것
- **회고**: 처음 RSS content를 자세히 봤으면 "title = content = summary (동일)"이라는 Google News의 빈약한 데이터 구조를 빨리 파악했을 것. content에서 URL을 찾는 데 시간을 낭비
- **관련 파일**: `src/collectors/news/rss_collector.py`, `scripts/update_geoinvest.py`, `scripts/update_stockinvest.py`, `scripts/review_entities.py`

## D-003: 모닝 이메일 부분 실패 시 전체 발송 중단
- **날짜**: 2026-03-26
- **상황**: FRED API 일시 장애로 유동성 데이터 수집 실패 → 모닝 이메일 전체가 발송되지 않음
- **이슈**: `send_morning_email.py`가 FRED 데이터 수집 단계에서 예외 발생 시 전체 프로세스가 중단. FX, 크립토, 차트 등 다른 섹션은 정상인데도 이메일 자체가 안 나감
- **삽질**: (1) FRED API에 retry 3회 추가 → API 자체가 다운이면 의미 없음 (2) 캐시된 데이터 사용 시도 → 캐시 구조가 없었음
- **해결**: 각 데이터 수집 단계(FRED/FX/Crypto/Charts)를 개별 try-except로 감싸고, 부분 실패 시에도 가용 데이터로 이메일 발송. 제목에 `[일부 누락]` 접두사, 템플릿에 ⚠️ 배너 표시. FRED+FX 동시 실패(핵심 데이터 없음)일 때만 발송 중단
- **대안**: (a) 모든 API에 로컬 캐시 레이어 추가 → 구현 복잡도 높음, 데이터 신선도 문제 (b) 실패 시 30분 후 재시도 cron → 복잡하고 중복 발송 위험
- **노하우**: 데이터 파이프라인은 "전부 아니면 무(all-or-nothing)"가 아니라 "가능한 만큼(best-effort)"으로 설계. 특히 매일 반복되는 cron 작업은 부분 결과라도 보내는 게 안 보내는 것보다 나음
- **회고**: 처음부터 각 섹션을 독립적으로 설계했으면 좋았겠다. "정상 경로"만 생각하고 만들면 첫 장애에서 전체가 무너짐
- **관련 파일**: `scripts/send_morning_email.py`, `src/publishers/email_publisher.py`, `templates/email/morning_report.html.j2`

## D-004: deep_analysis.py Market enum 매핑 에러
- **날짜**: 2026-04-06
- **상황**: 심층분석 파이프라인 LIVE 첫 실행 시 stock_kr 이슈에서 Pydantic ValidationError 발생
- **이슈**: `OntologyEvent(market=...)` 생성 시 `"kr"` 전달 → Market enum에는 `"korea"`, `"us"`만 있음. `stock_kr`에서 `replace("stock_", "")` → `"kr"` → 에러. 보정 코드가 event 생성 **이후**에 있어서 의미 없음
- **삽질**: (1) 첫 실행에서 에러 발견 → 수정 후 재실행 → 같은 에러 (이전 실행의 로그를 새 실행 결과로 착각) (2) Pydantic이 생성자에서 즉시 검증하므로 "생성 후 보정" 전략 자체가 불가능
- **해결**: event 생성 전에 `market = "korea" if "kr" in cat else "us"` 매핑. 보정 코드 삭제
- **대안**: (a) Market enum에 `KR = "kr"` 추가 → 시스템 전체에 영향, 다른 곳에서 "korea" 기대 (b) `model_validator`로 자동 변환 → 과도한 마법
- **노하우**: Pydantic BaseModel은 `__init__`에서 즉시 검증. "만들고 나서 고치자"는 안 됨. enum 값은 생성 전에 확정할 것. 또한 에러 로그 확인 시 타임스탬프를 반드시 체크 — 이전 실행 로그와 현재 로그를 혼동하지 말 것
- **회고**: 테스트를 dry-run으로만 하지 말고, stock_kr 이슈 1개라도 LIVE로 테스트했으면 바로 잡았을 것. dry-run은 DB 저장 경로를 타지 않으므로 Pydantic 검증을 통과
- **관련 파일**: `scripts/deep_analysis.py`, `src/core/models.py` (Market enum)

## D-005: matplotlib 한글 폰트 렌더링
- **날짜**: 2026-02 (프로젝트 초기)
- **상황**: WSL Ubuntu에서 matplotlib 차트 생성 시 한글이 □(두부)로 표시
- **이슈**: `plt.rcParams["font.family"] = "Noto Sans CJK KR"` 설정만으로는 안 됨. matplotlib가 시스템 폰트를 자동 탐색하지 않음
- **삽질**: (1) `rcParams` font.family만 설정 → 폰트 못 찾음 (2) `fc-list`로 폰트 경로 확인 후 `font_manager.FontProperties` 직접 지정 → 매 차트마다 반복 필요 (3) `Noto Sans CJK KR` 이름으로 검색 → .ttc 컬렉션은 첫 폰트(JP)만 등록
- **해결**: `fontManager.addfont()` 호출로 .ttc 파일을 명시적 등록 후, 등록된 이름 `"Noto Sans CJK JP"` (JP가 먼저 등록됨)로 family 설정. JP 폰트도 한글 글리프 포함하므로 렌더링 정상. `axes.unicode_minus = False` 필수 (마이너스 부호 깨짐 방지)
- **대안**: (a) 한글 전용 폰트(나눔고딕) 설치 → WSL에서 추가 패키지 필요 (b) 이미지에 한글 안 쓰기 → 비현실적
- **노하우**: matplotlib + CJK 폰트는 `addfont()` → `rcParams["font.family"]` 2단계 필수. .ttc 컬렉션은 첫 번째 폰트만 등록됨을 인지. 헤드리스 환경에서는 `matplotlib.use("Agg")` 백엔드 설정 필수
- **회고**: 이 문제는 "한번 해결하면 끝"인데 삽질 시간이 길었다. `.claude/rules/coding.md`에 스니펫으로 기록해둔 게 정답 — 이후 모든 차트 스크립트에서 복사-붙여넣기로 해결
- **관련 파일**: `.claude/rules/coding.md` (한글 폰트 스니펫), `src/exporters/` 전체

## D-006: lightweight-charts setData 후 fitContent/setVisibleLogicalRange 무효화
- **날짜**: 2026-04-12
- **상황**: 차트 기간 전환 시(예: 6M→MAX) `fitContent()` 호출했지만 visible range가 이전 6M 구간에 그대로 고정. 코드에서 호출은 됐는데 효과가 없음
- **이슈**: lightweight-charts가 `setData()` 후 내부적으로 비동기 auto-scroll을 수행하는데, 이 작업이 setTimeout(300ms~600ms) 안의 fitContent보다 늦게 실행되어 우리가 설정한 range를 덮어씀. 추가로 차트 3개(메인/RSI/MACD)의 타임스케일 동기화 리스너가 피드백 루프를 일으켜 range가 즉시 리셋
- **삽질**: (1) setTimeout 100ms→300ms→600ms 점진 증가 → 효과 없음 (2) `requestAnimationFrame` 2번 중첩 → 효과 없음 (3) `subscribeVisibleLogicalRangeChange` 1회용 리스너로 첫 트리거에서 range 설정 → 첫 setData 시점이라 데이터 미완 (4) 브라우저 콘솔에서 수동 호출은 동작 → 자동 호출만 안 됨
- **해결**: `_isSyncingTimeScale` 플래그를 setData 전체 동안 true로 유지(동기화 리스너 비활성화) + 2단계 setTimeout(100ms → fitContent → 100ms → 서브차트 동기화). SMA 시리즈는 매번 삭제/재생성 대신 `initLightweightChart()`에서 한 번만 만들고 `setData()`만 호출
- **대안**: (a) timeScale 동기화 자체를 제거 → 메인/RSI/MACD가 따로 놀게 됨 (b) `setVisibleRange` (시간 기준) → string time 파싱 이슈 (c) `scrollToPosition(-N)` → 정확한 범위 제어 안 됨
- **노하우**: lightweight-charts에서 시리즈를 동적으로 추가/제거하면 내부 auto-scroll이 매번 트리거됨 → **시리즈는 한 번만 생성하고 setData로 데이터만 갱신**. 멀티 차트 동기화는 피드백 루프 방지 플래그 필수. visible range는 모든 데이터 로딩이 끝난 뒤 별도 setTimeout으로 강제 설정
- **회고**: lightweight-charts 공식 문서가 "data updates and auto-scaling" 섹션을 명시 안 함. 처음부터 시리즈 재사용 패턴으로 설계했어야. removeSeries→addLineSeries 반복은 성능도 나쁨
- **관련 파일**: `src/web/static/app.js` (initLightweightChart, loadChartData, syncTimeScale)
