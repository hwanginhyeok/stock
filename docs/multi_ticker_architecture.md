# Multi-Ticker 아키텍처 설계

> 목적: `market_config.yaml` watchlist를 SSOT로 삼아, TSLA 하드코딩을 전면 제거하고
> 미국/한국/암호화폐 멀티 티커를 일관되게 처리하는 구조로 전환한다.
>
> 작성일: 2026-05-12 | 대상 브랜치: `feat/multi-ticker`

---

## 1. 현재 TSLA 하드코딩 위치 전수 조사

### 1-1. `src/web/chart_api.py` — 6곳

| 위치 | 코드 | 문제 |
|------|------|------|
| L237 | `symbol: str = "TSLA"` | `/ohlcv` 엔드포인트 기본값 |
| L340 | `symbol: str = "TSLA"` | `/events` 엔드포인트 기본값 |
| L366 | `tesla_keywords = ["Tesla", "TSLA", "Musk", ...]` | 이벤트 필터 엔티티 목록이 Tesla 전용 |
| L369 | `ent.ticker == "TSLA"` | 엔티티 조회 시 TSLA만 매칭 |
| L652 | `symbol: str = "TSLA"` | `/trendlines` 엔드포인트 기본값 |
| L680 | `symbol: str = "TSLA"` | `/signals` 엔드포인트 기본값 |

추가 연관 문제:
- `tesla_only: bool` 파라미터 (L342) — 범용 `symbol_only` 로 대체 가능
- `is_tesla` 마커 필드 (L423, L441, L444) — `is_primary` 로 범용화 필요

### 1-2. `src/generators/briefing_generator.py` — 1곳

| 위치 | 코드 | 문제 |
|------|------|------|
| L26–49 | `_TICKER_TO_NAME: dict[str, str]` 하드코딩 | US/KR/Crypto 100+ 종목을 코드에 직접 기재 |

현황: 매핑 자체는 포괄적이지만, `market_config.yaml` 추가/삭제가 이 파일까지 동기화되지 않음.

### 1-3. `src/analyzers/regime.py` — 2곳 (코드) + config 종속

| 위치 | 코드 | 문제 |
|------|------|------|
| L14 | docstring `{"TSLA": 0.25, "BTC": 0.15, ...}` | API 문서가 TSLA/BTC/ETH 고정 예시 |
| L63 | `sizing` 필드 docstring 동일 패턴 | |
| `_CRYPTO_TICKER_MAP` (L35–38) | `{"BTC": "BTC-USD", "ETH": "ETH-USD"}` | crypto watchlist 확장 시 누락 종목 발생 |
| `regime_sizing.yaml` | positions에 TSLA/BTC/ETH 3종목 고정 | watchlist 변경 시 수동 업데이트 필요 |

### 1-4. `src/analyzers/fact_extractor.py` — 구조적 문제

| 위치 | 코드 | 문제 |
|------|------|------|
| L87–157 | `_TICKER_DICT` 하드코딩 | 200+ 줄 정적 딕셔너리. config watchlist와 이중 관리 |

---

## 2. 목표 아키텍처 — market_config.yaml SSOT

### 2-1. market_config.yaml 확장안

현재 `crypto` 섹션 없음. 다음을 추가한다:

```yaml
# config/market_config.yaml

korea:
  watchlist:
    - { ticker: "005930", name: "삼성전자",  yf_suffix: ".KS" }
    - { ticker: "000660", name: "SK하이닉스", yf_suffix: ".KS" }
    # ... 기존 8개 유지

us:
  watchlist:
    - { ticker: "AAPL",  name: "Apple" }
    - { ticker: "MSFT",  name: "Microsoft" }
    - { ticker: "NVDA",  name: "NVIDIA" }
    - { ticker: "GOOGL", name: "Alphabet" }
    - { ticker: "AMZN",  name: "Amazon" }
    - { ticker: "META",  name: "Meta" }
    - { ticker: "TSLA",  name: "Tesla" }   # 유지, 특별 취급 제거
    - { ticker: "TSM",   name: "TSMC" }
    - { ticker: "AVGO",  name: "Broadcom" }
    - { ticker: "JPM",   name: "JPMorgan" }

# ── 신규 추가 ──
crypto:
  watchlist:
    - { ticker: "BTC", name: "Bitcoin",  yf_symbol: "BTC-USD" }
    - { ticker: "ETH", name: "Ethereum", yf_symbol: "ETH-USD" }
    - { ticker: "XRP", name: "XRP",      yf_symbol: "XRP-USD" }
    - { ticker: "SOL", name: "Solana",   yf_symbol: "SOL-USD" }
```

**필드 설계:**

| 필드 | 용도 | 없으면 |
|------|------|--------|
| `ticker` | 내부 PK (DB ticker 컬럼, URL 파라미터) | 필수 |
| `name` | 브리핑 표시명 | `ticker` 값 사용 |
| `yf_suffix` | 한국 종목 yfinance 심볼 접미사 (`.KS`) | 없으면 `ticker` 그대로 |
| `yf_symbol` | crypto yfinance 심볼 전체 (`BTC-USD`) | 없으면 `ticker` 그대로 |

### 2-2. 헬퍼 함수 — config에서 심볼 변환

`src/core/config.py`에 다음 헬퍼를 추가한다:

```python
# src/core/config.py

class WatchlistItem(BaseModel):
    ticker: str
    name: str
    yf_suffix: str = ""      # 한국 ".KS"
    yf_symbol: str = ""      # crypto "BTC-USD"

    @property
    def yf_ticker(self) -> str:
        """yfinance에 넘길 심볼을 반환한다."""
        if self.yf_symbol:
            return self.yf_symbol
        if self.yf_suffix:
            return self.ticker + self.yf_suffix
        return self.ticker

    @property
    def is_korean(self) -> bool:
        return bool(self.yf_suffix)

    @property
    def is_crypto(self) -> bool:
        return bool(self.yf_symbol)


class CryptoMarket(BaseModel):               # 신규
    watchlist: list[WatchlistItem] = Field(default_factory=list)


class MarketConfig(BaseModel):
    korea: KoreaMarket = Field(default_factory=KoreaMarket)
    us: USMarket = Field(default_factory=USMarket)
    crypto: CryptoMarket = Field(default_factory=CryptoMarket)  # 신규
    technical: TechnicalConfig = ...
    ...


def get_watchlist_map() -> dict[str, WatchlistItem]:
    """전체 watchlist를 ticker → WatchlistItem 딕셔너리로 반환."""
    cfg = get_config().market
    items: dict[str, WatchlistItem] = {}
    for item in cfg.korea.watchlist + cfg.us.watchlist + cfg.crypto.watchlist:
        items[item.ticker] = item
    return items


def resolve_yf_ticker(ticker: str) -> str:
    """내부 ticker → yfinance 심볼로 변환. watchlist에 없으면 그대로 반환."""
    wl = get_watchlist_map()
    if ticker in wl:
        return wl[ticker].yf_ticker
    return ticker
```

---

## 3. 모듈별 변경 계획

### 3-1. `src/web/chart_api.py`

#### 변경 1: 기본 심볼을 config 첫 번째 US 종목으로

```python
# 변경 전
symbol: str = "TSLA"

# 변경 후
from src.core.config import get_config

def _default_symbol() -> str:
    wl = get_config().market.us.watchlist
    return wl[0].ticker if wl else "AAPL"

# 엔드포인트 시그니처
@router.get("/ohlcv")
def get_ohlcv(
    symbol: str = Query(default=None),   # None이면 _default_symbol() 사용
    ...
)
```

실질적으로 프론트엔드가 항상 symbol을 넘기므로 기본값은 폴백용. 기본값을 None → 첫 US watchlist 종목으로 처리.

#### 변경 2: yfinance 심볼 자동 변환

```python
# 모든 yfinance 호출 전
from src.core.config import resolve_yf_ticker

yf_symbol = resolve_yf_ticker(symbol)  # "005930" → "005930.KS", "BTC" → "BTC-USD"
df = yf.download(yf_symbol, ...)
```

#### 변경 3: `tesla_keywords` → `symbol_keywords` (범용화)

```python
# 변경 전 (L366–369)
tesla_keywords = ["Tesla", "TSLA", "Musk", "xAI", "SpaceX", ...]
tesla_entity_ids: set[str] = set()
for ent in entity_repo.get_active():
    if any(kw.lower() in ent.name.lower() for kw in tesla_keywords) or ent.ticker == "TSLA":
        tesla_entity_ids.add(ent.id)

# 변경 후
wl = get_watchlist_map()
item = wl.get(symbol)
primary_entity_ids: set[str] = set()
for ent in entity_repo.get_active():
    if ent.ticker == symbol:
        primary_entity_ids.add(ent.id)
    elif item and item.name.lower() in ent.name.lower():
        primary_entity_ids.add(ent.id)
```

`tesla_keywords` 배열은 완전 제거한다. 이벤트 연결은 `ent.ticker == symbol` 매칭으로 통일.

#### 변경 4: API 응답 필드명

```python
# 변경 전
"tesla_events": len(tesla_event_ids),

# 변경 후
"primary_events": len(primary_entity_ids),
```

프론트엔드 호환성을 위해 구버전 필드는 deprecated 경고 후 1 릴리즈 유예.

#### 변경 5: `tesla_only` 파라미터 → `primary_only`

```python
# 변경 전
tesla_only: bool = False

# 변경 후
primary_only: bool = False   # 해당 symbol 직접 연결 이벤트만
```

---

### 3-2. `src/generators/briefing_generator.py`

#### 변경: `_TICKER_TO_NAME`을 config에서 동적 로드

```python
# 변경 전 (L26–49)
_TICKER_TO_NAME: dict[str, str] = {
    "TSLA": "Tesla", "NVDA": "NVIDIA", ...  # 100줄 하드코딩
}

# 변경 후
from src.core.config import get_watchlist_map

def _build_ticker_name_map() -> dict[str, str]:
    """watchlist에서 ticker→name 맵을 구성한다. 하드코딩 폴백 포함."""
    result: dict[str, str] = {}
    for ticker, item in get_watchlist_map().items():
        result[ticker] = item.name
    # crypto: yf_symbol도 매핑 (BTC-USD → Bitcoin)
    for item in get_config().market.crypto.watchlist:
        result[item.yf_symbol] = item.name
    return result

# 모듈 수준 캐시 (앱 시작 시 1회)
_TICKER_TO_NAME: dict[str, str] = _build_ticker_name_map()
```

기존 `_TICKER_TO_NAME` 딕셔너리는 삭제. `_TICKER_LABELS`(지수용)는 유지.

#### 변경: 관심종목 전체 브리핑 섹션 추가

```python
def _build_watchlist_section(
    facts: list[NewsFact],
) -> list[BriefingFact]:
    """watchlist 전 종목의 팩트를 모아 브리핑 섹션으로 만든다."""
    wl_tickers = set(get_watchlist_map().keys())
    wl_facts = [f for f in facts if any(t in wl_tickers for t in f.tickers)]
    return _prepare_facts(wl_facts)[:10]
```

`generate_briefing()` 템플릿 컨텍스트에 `watchlist_facts` 키로 주입.

---

### 3-3. `src/analyzers/regime.py`

#### 변경 1: `_CRYPTO_TICKER_MAP`을 config에서 동적 생성

```python
# 변경 전 (L35–38)
_CRYPTO_TICKER_MAP: dict[str, str] = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}

# 변경 후
from src.core.config import get_config

def _build_crypto_map() -> dict[str, str]:
    crypto_wl = get_config().market.crypto.watchlist
    return {item.ticker: item.yf_symbol for item in crypto_wl if item.yf_symbol}

_CRYPTO_TICKER_MAP: dict[str, str] = _build_crypto_map()
```

#### 변경 2: `_compute_technical_score` — watchlist 동적 로드

```python
# 변경 전 (L293)
tickers = list(self._config["positions"]["RISK_ON"].keys())  # regime_sizing.yaml 고정

# 변경 후
from src.core.config import get_config

def _get_regime_tickers(self) -> list[str]:
    """regime 분석 대상 종목: US watchlist + crypto watchlist."""
    cfg = get_config().market
    us_tickers = [item.ticker for item in cfg.us.watchlist]
    crypto_tickers = [item.ticker for item in cfg.crypto.watchlist]
    # 분석 부하 고려: 상위 5개 US + 전체 crypto
    return us_tickers[:5] + crypto_tickers
```

`regime_sizing.yaml`의 `positions` 섹션은 watchlist 기반으로 자동 생성하도록:

```python
# regime_sizing.yaml (변경 후)
positions:
  RISK_ON:
    us_weight: 0.60      # US watchlist 합산 비율
    crypto_weight: 0.25  # crypto watchlist 합산 비율
    per_ticker_equal: true  # 동일 비중 분배
  NEUTRAL:
    us_weight: 0.40
    crypto_weight: 0.17
  RISK_OFF:
    us_weight: 0.16
    crypto_weight: 0.08
```

이렇게 하면 watchlist 추가 시 regime_sizing.yaml 수정 없이 자동 반영.

#### 변경 3: docstring 업데이트

```python
# 변경 전 (L63)
sizing: dict[str, float]  # {"TSLA": 0.25, "BTC": 0.15, ...}

# 변경 후
sizing: dict[str, float]  # {"AAPL": 0.12, "MSFT": 0.12, ..., "BTC": 0.125, ...}
# watchlist 기반 동적 생성 — 고정값 없음
```

---

### 3-4. `src/analyzers/fact_extractor.py`

#### 변경: `_TICKER_DICT`에 config watchlist 동적 반영

완전 대체가 아닌 **보강(augment)** 방식으로 변경한다. 정적 딕셔너리(한글명 매핑)는 유지하되, config watchlist를 런타임에 추가:

```python
# 변경 전 (L87)
_TICKER_DICT: dict[str, str] = {
    "테슬라": "TSLA", "Tesla": "TSLA", ...  # 정적 하드코딩
}

# 변경 후
_TICKER_DICT_STATIC: dict[str, str] = {
    "테슬라": "TSLA", "Tesla": "TSLA", ...  # 한글명 매핑은 유지
}

def _build_ticker_dict() -> dict[str, str]:
    """정적 사전 + config watchlist를 합쳐 매핑 딕셔너리를 반환한다."""
    result = dict(_TICKER_DICT_STATIC)
    try:
        from src.core.config import get_watchlist_map
        for ticker, item in get_watchlist_map().items():
            result[ticker] = ticker        # "AAPL" → "AAPL"
            result[item.name] = ticker     # "Apple" → "AAPL"
    except Exception:
        pass  # config 로드 실패 시 정적 사전만 사용
    return result

_TICKER_DICT: dict[str, str] = _build_ticker_dict()
```

로딩은 모듈 임포트 시 1회. 재로딩이 필요한 경우 `_TICKER_DICT = _build_ticker_dict()`로 갱신.

---

## 4. DB 스키마 변경 필요 여부

### 결론: 변경 불필요

`src/core/models.py` `OHLCVRecord` (L369):

```python
class OHLCVRecord(BaseEntity, TimestampMixin):
    date: str
    ticker: str          # ← 이미 generic
    market: Market = Market.US   # Market.KOREA / Market.US / Market.CRYPTO 추가 필요
    open: float = 0.0
    ...
```

**`Market` Enum에 `CRYPTO` 추가만 필요:**

```python
# src/core/models.py

class Market(str, Enum):
    KOREA = "korea"
    US = "us"
    CRYPTO = "crypto"   # 신규 추가
```

**기존 데이터 영향 없음:**
- `ticker="TSLA"`, `market="us"` 행은 그대로 유지
- `ticker="005930"`, `market="korea"` 신규 행 추가 시 충돌 없음
- `ticker="BTC"`, `market="crypto"` 신규 행 추가 시 충돌 없음

**주의:** 한국 종목의 DB ticker는 `"005930"` (6자리 코드). yfinance 조회 시에만 `"005930.KS"`로 변환. DB와 URL 파라미터는 항상 `"005930"` 사용.

---

## 5. API 엔드포인트 변경

### 현재 → 목표 엔드포인트

| 엔드포인트 | 현재 | 변경 후 |
|-----------|------|---------|
| `GET /api/chart/ohlcv` | `?symbol=TSLA` | `?symbol={ticker}` (기본: 첫 US watchlist) |
| `GET /api/chart/events` | `?symbol=TSLA&tesla_only=false` | `?symbol={ticker}&primary_only=false` |
| `GET /api/chart/trendlines` | `?symbol=TSLA` | `?symbol={ticker}` |
| `GET /api/chart/signals` | `?symbol=TSLA` | `?symbol={ticker}` |
| `GET /api/chart/watchlist` | **신규** | watchlist 전체 목록 반환 |

### 신규 엔드포인트: `/api/chart/watchlist`

```python
@router.get("/watchlist")
def get_watchlist() -> dict:
    """현재 watchlist 전체를 마켓별로 반환한다."""
    from src.core.config import get_config

    cfg = get_config().market
    return {
        "korea": [{"ticker": i.ticker, "name": i.name} for i in cfg.korea.watchlist],
        "us": [{"ticker": i.ticker, "name": i.name} for i in cfg.us.watchlist],
        "crypto": [{"ticker": i.ticker, "name": i.name} for i in cfg.crypto.watchlist],
    }
```

프론트엔드가 이 엔드포인트로 드롭다운 목록을 동적으로 구성한다.

### symbol 유효성 검사

임의 티커 입력 시 yfinance 오류가 발생하므로 watchlist 기반 제한 옵션:

**옵션 A (엄격):** watchlist에 없는 symbol → 400 Bad Request
```python
wl = get_watchlist_map()
if symbol and symbol not in wl:
    raise HTTPException(status_code=400, detail=f"Unknown symbol: {symbol}")
```

**옵션 B (유연):** watchlist에 없어도 허용, yfinance에 그대로 넘김
```python
yf_sym = resolve_yf_ticker(symbol)  # 없으면 그대로 반환
```

**권장: 옵션 B** — 자유로운 심볼 조회를 허용하되, watchlist 외 심볼은 이벤트 마커가 비어있을 수 있음을 문서화.

---

## 6. 마이그레이션 전략

### 6-1. 기존 TSLA 데이터 보존

```sql
-- ohlcv_history에 TSLA 데이터가 있다면:
-- ticker='TSLA', market='us' 행은 변경 없이 유지.
-- 신규 종목은 INSERT만 발생. UPDATE/DELETE 없음.
```

DB 마이그레이션 스크립트:

```python
# scripts/migrate_market_enum.py
"""Market Enum에 'crypto' 추가 — SQLite ALTER TABLE."""

from sqlalchemy import text
from src.core.database import engine

with engine.connect() as conn:
    # SQLite는 CHECK constraint 수정 불가 → 재생성 없이 값 삽입만 가능
    # 기존 'us'/'korea' 데이터 유지, 'crypto' 값 허용 확인
    result = conn.execute(text("SELECT DISTINCT market FROM ohlcv_history"))
    existing = [row[0] for row in result]
    print(f"기존 market 값: {existing}")
    # 'crypto' 미존재 확인 후 신규 데이터 삽입 가능
```

SQLite의 경우 Enum은 단순 TEXT 컬럼이므로 새 값 삽입 즉시 가능. PostgreSQL이라면 `ALTER TYPE market_enum ADD VALUE 'crypto'` 실행.

### 6-2. 코드 변경 순서 (의존성 순)

```
1. config/market_config.yaml  — crypto 섹션 추가 (데이터 변경, 안전)
2. src/core/config.py          — CryptoMarket, WatchlistItem.yf_ticker, helpers 추가
3. src/core/models.py          — Market.CRYPTO 추가
4. src/analyzers/fact_extractor.py — _build_ticker_dict() 적용
5. src/analyzers/regime.py     — _build_crypto_map(), _get_regime_tickers() 적용
6. src/generators/briefing_generator.py — _build_ticker_name_map() 적용
7. src/web/chart_api.py        — 기본값, tesla_keywords, yfinance 심볼 변환 적용
8. tests/                      — 각 모듈 단위 테스트 갱신
```

각 단계는 독립적으로 PR 가능. 단, 2번(config.py) 완료 전에 다른 모듈 변경 금지.

### 6-3. 피처 플래그 없이 단계적 적용

피처 플래그 대신 **기본값 fallback** 방식:
- `resolve_yf_ticker("TSLA")` → `"TSLA"` (변환 없음, 기존 동작 유지)
- `resolve_yf_ticker("005930")` → `"005930.KS"` (신규)
- `resolve_yf_ticker("BTC")` → `"BTC-USD"` (신규)

기존 TSLA 경로는 아무것도 바뀌지 않음.

---

## 7. 한국 종목 지원

### 7-1. yfinance 심볼 체계

| 시장 | 내부 ticker | yfinance 심볼 | 예시 |
|------|------------|--------------|------|
| 미국 | `AAPL` | `AAPL` | 동일 |
| 코스피 | `005930` | `005930.KS` | 삼성전자 |
| 코스닥 | `035720` | `035720.KQ` | 카카오 |
| 암호화폐 | `BTC` | `BTC-USD` | 비트코인 |

코스피/코스닥 구분: `market_config.yaml`의 `yf_suffix`로 지정 (`.KS` / `.KQ`).

### 7-2. `WatchlistItem.yf_ticker` 자동 처리

```python
# 005930 (삼성전자, .KS suffix)
item.yf_ticker  # → "005930.KS"

# 035720 (카카오, .KQ suffix)
item.yf_ticker  # → "035720.KQ"

# BTC (yf_symbol="BTC-USD")
item.yf_ticker  # → "BTC-USD"

# AAPL (suffix/yf_symbol 없음)
item.yf_ticker  # → "AAPL"
```

### 7-3. 가격 포맷팅

한국 종목은 원화(₩), 미국/암호화폐는 달러($) 표시:

```python
def format_price(ticker: str, price: float) -> str:
    wl = get_watchlist_map()
    item = wl.get(ticker)
    if item and item.is_korean:
        return f"₩{price:,.0f}"
    return f"${price:,.2f}"
```

### 7-4. 이벤트 마커 (`/api/chart/events`) 한국 종목

한국 종목은 온톨로지 이벤트 DB에 한국어 뉴스 기반 이벤트가 쌓임. `OntologyEntityRepository.get_active()`에서 `ticker="005930"` 매칭으로 자동 처리 — 특별 처리 불필요.

단, 한국 종목은 `macro critical` 필터가 KR 매크로에도 적용되도록:
```python
is_macro_critical = (
    ev.event_type == "macro" and ev.severity == "critical"
) or (
    ev.event_type == "regulation" and ev.severity in ("critical", "major")
    and item and item.is_korean  # 한국 규제 뉴스 중요도 상향
)
```

---

## 8. 작업 체크리스트

```
[ ] config/market_config.yaml — crypto 섹션 추가, korea watchlist yf_suffix 추가
[ ] src/core/config.py         — CryptoMarket 모델, WatchlistItem.yf_ticker 프로퍼티
[ ] src/core/config.py         — get_watchlist_map(), resolve_yf_ticker() 헬퍼
[ ] src/core/models.py         — Market.CRYPTO 추가
[ ] src/analyzers/fact_extractor.py — _build_ticker_dict() 전환
[ ] src/analyzers/regime.py    — _build_crypto_map(), watchlist 기반 tickers 로드
[ ] src/analyzers/regime.py    — regime_sizing.yaml positions 재설계
[ ] src/generators/briefing_generator.py — _build_ticker_name_map() 전환
[ ] src/generators/briefing_generator.py — watchlist 전체 브리핑 섹션 추가
[ ] src/web/chart_api.py       — 4곳 기본값 수정, tesla_keywords 제거
[ ] src/web/chart_api.py       — GET /watchlist 엔드포인트 추가
[ ] src/web/chart_api.py       — tesla_only → primary_only 파라미터 전환
[ ] tests/ — 멀티 티커 단위 테스트 (US/KR/Crypto 각 1종목 이상)
[ ] 프론트엔드 — watchlist API 기반 심볼 드롭다운 구현
```

---

## 부록 A — 영향받지 않는 모듈

다음 모듈은 이번 변경 범위 밖이다:

- `src/collectors/` — 뉴스 수집은 ticker 무관
- `src/storage/` — DB 레이어는 ticker를 문자열로만 취급
- `templates/briefing/` — 템플릿은 컨텍스트 변수 변경으로 대응
- `src/collectors/macro/` — FRED/FX 수집은 watchlist 무관

## 부록 B — 한국 종목 yfinance 제약사항

- 실시간 데이터: 코스피 종목은 15분 딜레이 (yfinance 정책)
- 거래량: `Volume` 컬럼 단위가 주(株)로 미국과 동일, 문제 없음
- 기간 제한: `interval=1h`는 최대 730일 (한국도 동일)
- 종목코드 없는 인덱스: `^KS11`(KOSPI), `^KQ11`(KOSDAQ) — watchlist 대상 아님, briefing_generator.py `_KR_INDICES`로 별도 관리
