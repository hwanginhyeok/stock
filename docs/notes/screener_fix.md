# 주식 스크리너 에러 해결

## 문제 분석

### 1. ANSS/SGEN delisted
```
HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: ANSS"}}}
$ANSS: possibly delisted; no price data found (period=1y) (Yahoo error = "No data found, symbol may be delisted")
```

### 2. S&P 500 HTTP 403
```
[WARN] S&P 500 리스트 로드 실패: HTTP Error 403: Forbidden
```

---

## 해결 방안

### 1. ANSS/SGEN 제거
```python
# NASDAQ_100 리스트에서 제거
NASDAQ_100 = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","GOOG","TSLA","AVGO","COST",
    # ... 다른 종목들
    "MTCH","OKTA"
    # 제거: ANSS, SGEN (delisted)
]
```

### 2. S&P 500 대안
```python
# 방법 1: Wikipedia 리스트 사용
import requests
sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(sp500_url)
# 파싱하여 리스트 추출

# 방법 2: yfinance.tickers 사용
import yfinance as yf
sp500 = yf.Tickers('^GSPC').history(period="1d")
# 주요 종목 리스트 하드코딩
```

### 3. 에러 핸들링 추가
```python
try:
    data = yf.download(symbol, period=PERIOD)
except Exception as e:
    log(f"종목 {symbol} 다운로드 실패: {e}")
    continue
```

---

## 우선순위

1. **긴급**: ANSS/SGEN 제거 (코드 수정)
2. **중간**: S&P 500 대안 (Wikipedia 또는 하드코딩)
3. **권장**: 에러 핸들링 강화

---

## 다음 단계

1. 스크립트 수정 (ANS/SGEN 제거)
2. S&P 500 리스트 대안 추가
3. 테스트 실행
4. cron 등록 확인

---

**담당자**: 사용자 확인 필요
**기한**: 긴급 (주식 스크리너 매일 실행)