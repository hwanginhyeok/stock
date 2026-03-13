# 1-22 MMF 데이터 소스 ICI 교체

> 완료일: 2026-03-01

## 작업 요약

FRED WRMFNS(소매전용, 4주 지연) → ICI 직접 XLS 파싱(전체, ~1주 지연)으로 교체.

## 문제 인식

모닝 이메일에서 MMF 기준일이 2025-xx-xx로 표시되어 사용자가 의문 제기.
확인 결과 FRED WRMFNS는 ~4주 발행 지연 + 소매 MMF만 집계.

## 데이터 소스 비교

| 항목 | FRED WRMFNS | ICI 직접 |
|------|-------------|---------|
| 커버리지 | 소매 MMF 전용 | 기관 + 소매 전체 |
| 규모 | ~$2.3T | ~$7.8T |
| 발행 주기 | 주별 | 주별 |
| 발행 지연 | ~4주 | ~1주 (매주 목요일 전주 기준) |
| URL | FRED API | `https://www.ici.org/mm_summary_data_{year}.xls` |
| 인증 | 없음 | 없음 (User-Agent 헤더 필요) |
| 포맷 | CSV | XLS (Excel 97-2004) |

**→ ICI 채택**: 규모 3.4배, 지연 4배 감소

## ICI XLS 구조

```
Sheet: "Public Report"
Row 0~7: 메타데이터/헤더
Row 8~:  실제 데이터
  Col 0: DATE (날짜)
  Col 1: # Classes (펀드 수, 불필요)
  Col 2: Total Net Assets (TNA, 백만 달러)
```

**주의**: col 1이 TNA처럼 보이지만 펀드 수임 — col 2가 실제 TNA.

## 구현 세부사항

### URL 연도 폴백 패턴

ICI는 매년 새 파일을 생성. 연도 초에는 전년도 파일이 더 최신일 수 있음.

```python
for year in [datetime.now().year, datetime.now().year - 1]:
    try:
        url = f"https://www.ici.org/mm_summary_data_{year}.xls"
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        # ... 파싱
        return result
    except Exception:
        continue
return None
```

### User-Agent 헤더 필요

ICI는 User-Agent 없이 접근하면 403/차단 가능 → `"Mozilla/5.0"` 설정.

### 파싱 로직

```python
df = pd.read_excel(io.BytesIO(r.content), sheet_name="Public Report", header=None)
data = df.iloc[8:].reset_index(drop=True)[[0, 2]].copy()
data.columns = ["date", "tna_m"]
data["tna_m"] = pd.to_numeric(data["tna_m"], errors="coerce")
data["date"]  = pd.to_datetime(data["date"], errors="coerce")
data = data.dropna().sort_values("date")
return (data.set_index("date")["tna_m"] / 1_000).rename("mmf_weekly")  # $M → $B
```

## 변경 파일

- `src/collectors/macro/fred_collector.py`
  - 상수: `_ICI_MMF_URL`, `_ICI_HEADERS` 추가
  - `_SERIES`에서 `"mmf_weekly"` (WRMFNS) 항목 제거
  - `_fetch_ici_mmf_weekly()` 함수 신규 추가
  - `collect_series()`: ICI fetch 호출 + 결과 통합
  - `collect()`: ICI fetch 호출 + `mmf_weekly_b/date/wow` 별도 처리 블록 추가

## 실측값 비교 (2026-03-01)

| 항목 | WRMFNS | ICI |
|------|--------|-----|
| 최신 기준일 | 2026-02-02 | 2026-02-19 |
| 최신 잔고 | ~$2.3T | ~$6.8T |
| 지연 | 27일 | 10일 |

ICI 기준 WoW 변화: +$26.7B (자금 유입 지속 확인)
