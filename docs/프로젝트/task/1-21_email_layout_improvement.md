# 1-21 이메일 레이아웃 개선

> 완료일: 2026-03-01

## 작업 요약

모닝 이메일 차트를 각 섹션 인라인 배치로 전환하고, 섹션별 데이터 기준일 표시 추가.

## 변경 내용

### 1. 차트 인라인 배치

**이전**: 모든 차트가 Section 6 "차트 모음"에 일괄 나열됨 → 데이터와 차트 분리
**이후**: 각 차트가 해당 데이터 섹션 하단에 인라인 배치, Section 6 제거

| 섹션 | 차트 |
|---|---|
| Section 1 (유동성) | `charts.fred_liquidity` |
| Section 2 (FX) | `charts.fx_rates` |
| Section 3 (도착지) | `charts.sectors`, `charts.destination_*` |
| Section 4 (기술적 지표) | `charts.market_overview` |
| Section 5 (크립토) | `charts.crypto_price` |

### 2. 데이터 기준일 표시

**이유**: 각 소스마다 발행 지연이 달라 독자가 데이터 신선도를 판단할 수 없었음.

#### Section 1 (FRED) — 행별 날짜

FRED 지표는 각각 발행 주기가 다름 (일별/주별/분기별). 각 행 레이블 아래 날짜 표시.

```html
<div style="font-size:10px;color:#334155;margin-top:2px;">{{ fred.walcl_date }}</div>
```

대상 지표: `walcl`, `tga`, `rrp`, `mmf_weekly`, `mmf_total`, `yield_2s10s`, `hy_spread`

#### Section 2–4 — 헤더 우측 날짜

섹션 내 모든 데이터가 동일 기준일이므로 헤더에 한 번만 표시.

**Jinja2 namespace 패턴** (루프 내 변수가 루프 밖으로 전파되지 않는 문제 해결):

```jinja2
{%- set _ns = namespace(date="") -%}
{%- for _, d in currencies.items() -%}
  {%- if _ns.date == "" and "error" not in d and d.date -%}
    {%- set _ns.date = d.date -%}
  {%- endif -%}
{%- endfor -%}
```

헤더에 float:right span 삽입:

```html
<span style="float:right;font-size:10px;color:#475569;font-weight:400;
             letter-spacing:0;text-transform:none;">기준 {{ _ns.date }}</span>
```

> `text-transform:none` 필수 — 부모 div가 `text-transform:uppercase` 적용 중

#### Section 5 (크립토) — 직접 참조

크립토는 단일 소스(yfinance)이므로 namespace 불필요:

```jinja2
기준 {{ crypto.btc.date }}
```

## 설계 결정

### Section 6 제거 이유
- 차트가 섹션 데이터에서 멀리 떨어지면 읽는 흐름이 끊김
- 이메일 클라이언트에서 스크롤 없이 맥락 유지 불가
- 섹션별 인라인 > 일괄 나열

### FRED 행별 vs 헤더 날짜
- FRED는 지표별로 발행 주기가 다름 (RRP=일별, WALCL=주별, MMMFFAQ027S=분기)
- 헤더 하나로 퉁치면 오해 발생 → 행별 표시가 정직함
- FX/섹터/크립토는 동일 소스·동일 시점 → 헤더 하나로 충분

## 변경 파일

- `templates/email/morning_report.html.j2`
  - Section 1: 7개 지표 행에 날짜 sub-label 추가
  - Section 2–4: namespace 날짜 추출 + 헤더 우측 날짜 span
  - Section 5: `crypto.btc.date` 헤더 표시
  - Section 1–5: 섹션 하단 차트 img 태그 추가
  - Section 6 전체 제거
