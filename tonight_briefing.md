# 야간 작업 브리핑 (2026-03-26)

## 실행 요약

| 기능 | 상태 | 테스트 | 커밋 |
|------|------|--------|------|
| A: 모닝 이메일 Graceful Degradation | ✅ 완료 | 7/7 통과 | `98c56cf` |
| B: RSS 수집기 안정성 + 실패 추적 | ✅ 완료 | 7/7 통과 | `8610168` |
| C: 뉴스 수집기 단위 테스트 | ✅ 완료 | 17/17 통과 | `27d3078` |

**총 테스트: 31건 전부 통과**

---

## 기능 A: 모닝 이메일 Graceful Degradation (1-26)

### 문제
외부 API(FRED, 환율, 크립토) 하나라도 장애나면 `send_morning_email.py` 전체가 크래시 → 이메일 미발송.

### 해결
- `send_morning_email.py`: 각 수집 단계(FRED/FX/Crypto/Charts)를 개별 try-except로 격리
- 부분 실패 시: 가용 데이터로 이메일 발송 + 제목에 `[일부 누락]` 접두사
- 전체 실패 시(FRED+FX 모두): 이메일 발송 스킵 + exit(1)
- 이메일 HTML 템플릿: 누락 섹션 배너 (⚠️ 데이터 누락: FRED, Crypto)

### 코드리뷰 결과
- CRITICAL 이슈 0건
- except: pass 패턴 없음, 시크릿 로깅 없음, 수신자 하드코딩 없음

---

## 기능 B: RSS 수집기 안정성 보강 (1-27)

### 문제
개별 소스 실패 시 카운터가 결과에 포함되지 않아 운영 모니터링 불가.

### 해결
- `rss_collector.py`: `collect()`에 성공/실패 소스 추적 (`failed_sources` property)
- `news_pipeline.py`: `PipelineResult.failed_sources` 필드 추가, `summary()`에 "소스실패 N" 표시

### 기존 안정성 확인
- `_fetch_source`: 이미 try-except로 개별 소스 격리 ✅
- `_fetch_rss`: tenacity 3회 재시도 + exponential backoff ✅
- `requests.get`: timeout=15초 설정 ✅

### 코드리뷰 결과
- CRITICAL 이슈 0건
- 무한 재시도 없음 (stop_after_attempt(3)), URL 검증 불필요 (config에서 로딩)

---

## 기능 C: 뉴스 수집기 단위 테스트 (1-28)

### 테스트 목록 (17건)

**TickerExtractor (9건)**:
- KR 종목명 → 티커, US 심볼 → 티커, US 회사명 → 티커
- 복수 티커, 빈 입력, 매칭 없음
- title+summary 동시 스캔, 대소문자 무시, 부분 매칭 방지

**NewsPipeline (6건)**:
- 정상 실행, 티커 자동 매핑, 시장 필터
- 빈 수집, 수집 예외, DB 중복 제거

**BreakingDetection (2건)**:
- 3소스 이상 동일 키워드 → HIGH 승격
- 2소스만 → 미승격

### 발견 및 조치
- `\b` 경계가 한글 조사와 결합 시 작동하지 않는 엣지케이스 발견 (예: "NVIDIA가")
  - 현재 영문 뉴스에서는 문제없음
  - 한국어 뉴스에서 US 티커 검출 시 영향 가능 → 향후 lookaround 패턴 개선 가능

---

## 변경 파일 요약

| 파일 | 변경 |
|------|------|
| `scripts/send_morning_email.py` | 수집 단계 try-except 격리 |
| `src/publishers/email_publisher.py` | failed_sections 파라미터, [일부 누락] 접두사 |
| `templates/email/morning_report.html.j2` | 누락 배너 |
| `src/collectors/news/rss_collector.py` | 실패/성공 소스 추적 |
| `src/collectors/news/news_pipeline.py` | PipelineResult.failed_sources |
| `tests/test_email_graceful.py` | 신규 (7건) |
| `tests/test_rss_collector.py` | 신규 (7건) |
| `tests/test_news_collectors.py` | 신규 (17건) |
| `docs/프로젝트/TASK.md` | 1-26, 1-27, 1-28 완료 등록 |
