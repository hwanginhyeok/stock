# 1-33: cron 뉴스 수집 URL/도메인 노이즈 제거

> 발행일: 2026-04-06 | 상태: 조사 완료, 해결 방안 선택 대기

## 문제

cron으로 수집되는 뉴스 데이터에 URL/도메인이 섞여 들어와서 전체 데이터가 복잡해짐.

## 조사 결과 (2026-04-06)

### 데이터 흐름

```
RSS 수집 (15분) → DB 저장 → Ollama 엔티티 추출 (10분/1시간) → 엔티티 리뷰 (매일 04시)
                                    ↑ 오염 발생 지점
```

### 원인 1: Google News RSS title에 소스 도메인 포함

Google News RSS의 title 형식:
```
"Some headline - marketplace.org"
"Another headline - DW.com"  
"뉴스 제목 - v.daum.net"
```

`" - 소스명"` 접미사가 그대로 Ollama에 전달됨.

### 원인 2: Google News RSS content가 사실상 빈 껍데기

| 필드 | Google News 실제 값 | 유용성 |
|------|---------------------|--------|
| title | "헤드라인 - 소스명" | △ (소스명 노이즈) |
| content | "헤드라인 소스명" (title과 동일) | ✗ |
| summary | "헤드라인 소스명" (content과 동일) | ✗ |
| url | `https://news.google.com/rss/articles/CBMi...` (opaque base64 redirect) | ✗ (원본 URL 아님) |

→ Google News는 실질적으로 **title 한 줄**만 제공. content/summary는 중복.

### 원인 3: Ollama(gemma3:4b)가 도메인/노이즈를 엔티티로 추출

엔티티 리뷰 리포트에서 확인된 오염 (2026-04-06):
- **도메인/URL**: `cnn.com`, `startupfortune.com`, `DW.com`, `scmp.com`, `marketplace.org`, `news.az`, `gjia.georgetown.edu`
- **기술 용어**: `metadata`, `capabilities`, `endpoints`, `operational details`
- **숫자/날짜**: `$71,500-$81,200`, `140주년`, `2월`
- **잘못된 entity_type**: `website` → `institution`, `technology` → `institution`, `policy` → `institution`

### 영향

- **엔티티 DB 오염**: 1,954개 엔티티 중 상당수가 도메인/노이즈
- **관계 그래프 오염**: 노이즈 엔티티에 연결된 무의미한 관계
- **InvestOS 대시보드 품질 저하**: 도메인명이 엔티티로 표시

### 수치

- 전체 뉴스: 262,762건
- URL 필드 채워진 비율: 99.99% (262,761건)
- content 내 URL 포함 비율: 0.4% (content 자체는 깨끗)
- 평균 URL 길이: 111.2자 (Google News redirect URL)

## 해결 방안 (택일 또는 조합)

### A. 수집 단계 — title에서 소스명 제거 (추천)

**위치**: `src/collectors/news/rss_collector.py` → `_parse_entry()`

```python
# title에서 " - Source Name" 접미사 제거
import re
title = re.sub(r'\s*[-–—]\s*[A-Za-z][A-Za-z0-9\s.]+$', '', title).strip()
```

- 장점: 근본 원인 해결, Ollama 입력이 깨끗해짐
- 주의: source 필드에 이미 출처가 저장되므로 title에서 제거해도 정보 손실 없음

### B. 추출 단계 — Ollama 프롬프트에 필터 규칙 추가

**위치**: `scripts/update_geoinvest.py`, `scripts/update_stockinvest.py` → `EXTRACTION_PROMPT`

```
IMPORTANT: Do NOT extract these as entities:
- Website domains (cnn.com, marketplace.org, etc.)
- News source names (CNBC, Reuters, Bloomberg, etc.)
- Generic words (metadata, capabilities, etc.)
- Numbers or dates standing alone
```

- 장점: 간단, 코드 변경 최소
- 단점: gemma3:4b는 작은 모델이라 프롬프트 준수 불확실

### C. 저장 단계 — 엔티티 저장 전 도메인 필터

**위치**: `_save_extraction()` 함수

```python
# 도메인 패턴 필터
DOMAIN_PATTERN = re.compile(r'^[\w.-]+\.(com|org|net|io|gov|edu|co\.kr|co\.jp)$', re.I)
NOISE_WORDS = {"metadata", "capabilities", "endpoints", "operational details"}

for ent_data in entities:
    name = ent_data.get("name", "")
    if DOMAIN_PATTERN.match(name) or name.lower() in NOISE_WORDS:
        continue  # 스킵
```

- 장점: 확실한 방어, 기존 데이터에도 적용 가능
- 단점: 사후 처리 (Ollama 토큰은 이미 소비됨)

### D. 기존 오염 데이터 정리

**위치**: `scripts/review_entities.py`에 Phase 추가

- 도메인 패턴 엔티티 일괄 삭제
- 연결된 관계도 cascade 삭제

## 추천: A + C + D 조합

1. **A**: title 정제로 근본 원인 차단
2. **C**: 방어적 필터로 혹시 빠져나오는 것 차단
3. **D**: 기존 오염 데이터 정리

## 관련 파일

| 파일 | 역할 |
|------|------|
| `src/collectors/news/rss_collector.py:265-315` | RSS 파싱, title/content 추출 |
| `scripts/update_geoinvest.py:196-211` | Ollama 프롬프트 구성 |
| `scripts/update_stockinvest.py:125-138` | Ollama 프롬프트 구성 |
| `scripts/review_entities.py` | 엔티티 정리 (매일 04시) |
| `data/reports/entity_review_*.md` | 리뷰 리포트 |
