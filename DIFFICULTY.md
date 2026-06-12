# Difficulties & Know-how

## D-001: Naver HTML Korean text corruption
- **Date**: 2026-03-23 ~ 2026-04-01
- **Situation**: When pasting the briefing HTML into the Naver blog, Korean text is rendered corrupted
- **Issue**: Even after adding `<meta charset="utf-8">`, the browser ignores the encoding. When the Naver editor renders an HTML fragment directly, the charset declaration is not applied
- **Trial and error**: (1) Added meta charset at the top of the HTML → no effect (2) Tried adding a BOM → Naver strips the BOM (3) Tried a Content-Type header → since it's a file paste, an HTTP header is not possible
- **Solution**: Created a `briefing_server.py` local server that wraps the HTML fragment into a full document `<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>...` and serves it. Render in the browser, then copy-paste
- **Alternatives**: (a) Calling the Naver API directly from Python → the API does not support HTML body (b) Auto-pasting with Playwright → unstable because the Naver editor DOM structure is complex
- **Know-how**: When viewing an HTML fragment in the browser, you must serve it as a full document wrapper with the charset inside `<head>`. The charset does not work with a fragment alone
- **Retrospective**: If I had built a local preview server from the start, debugging would have been much faster. I started from "why doesn't meta charset work?", but the question itself was wrong — a fragment has no head, so the meta is meaningless
- **Related files**: `scripts/briefing_server.py`, `src/generators/briefing_generator.py`

## D-002: RSS news collection source domain/URL noise
- **Date**: 2026-03-25 ~ 2026-04-06
- **Situation**: RSS collection every 15 min → Ollama entity extraction → domains like `cnn.com`, `marketplace.org` show up as entities in the InvestOS dashboard
- **Issue**: The Google News RSS title is in the format `"헤드라인 - CNBC"`, including the source name. Ollama gemma3:4b extracts this as an entity. It also extracts noise such as `$71,500`, `metadata`, `2월`
- **Trial and error**: (1) Added "do not extract domains" to the Ollama prompt → gemma3:4b ignores it (2) Searched the content field for URLs → only 0.4% applied, not the core cause (3) Checked the RSS summary → Google News includes the URL in the HTML but `_extract_text()` handles it well
- **Solution**: A 3-stage filter combination: (A) regex-remove the trailing `" - SourceName"` from the title in `_parse_entry()` (B) filter domain patterns/noise words in `_save_extraction()` (C) delete 92 existing polluted entries in `review_entities.py` Phase 0
- **Alternatives**: (a) Use a larger model (12b) → slow on an RTX 2060 6GB (b) Extract with the Claude API → incurs cost (c) Improve only the prompt → a limit of small models
- **Know-how**: LLM extraction results must always go through a post-filter. A 3-stage defense is needed: input cleansing (A) + output filter (B) + periodic cleanup (C). Do not try to overcome a small model's limits with a single prompt
- **Retrospective**: If I had looked at the RSS content closely at first, I would have quickly grasped Google News's thin data structure where "title = content = summary (identical)". I wasted time looking for URLs in the content
- **Related files**: `src/collectors/news/rss_collector.py`, `scripts/update_geoinvest.py`, `scripts/update_stockinvest.py`, `scripts/review_entities.py`

## D-003: Whole morning-email send halted on partial failure
- **Date**: 2026-03-26
- **Situation**: A temporary FRED API outage caused liquidity data collection to fail → the entire morning email was not sent
- **Issue**: When `send_morning_email.py` raises an exception in the FRED data collection step, the entire process halts. Even though other sections like FX, crypto, and charts are fine, the email itself is not sent
- **Trial and error**: (1) Added 3 retries to the FRED API → meaningless if the API itself is down (2) Tried using cached data → there was no cache structure
- **Solution**: Wrap each data collection step (FRED/FX/Crypto/Charts) in its own try-except, and even on partial failure, send the email with whatever data is available. Add a `[일부 누락]` prefix to the subject and show a ⚠️ banner in the template. Only halt sending when FRED+FX fail simultaneously (no core data)
- **Alternatives**: (a) Add a local cache layer to all APIs → high implementation complexity, data freshness issues (b) A retry cron after 30 min on failure → complex and risks duplicate sends
- **Know-how**: Design data pipelines as "best-effort" (as much as possible), not "all-or-nothing". Especially for daily recurring cron jobs, sending a partial result is better than sending nothing
- **Retrospective**: It would have been good to design each section independently from the start. If you build thinking only about the "happy path", the whole thing collapses at the first failure
- **Related files**: `scripts/send_morning_email.py`, `src/publishers/email_publisher.py`, `templates/email/morning_report.html.j2`

## D-004: deep_analysis.py Market enum mapping error
- **Date**: 2026-04-06
- **Situation**: On the first LIVE run of the deep-analysis pipeline, a Pydantic ValidationError occurred on a stock_kr issue
- **Issue**: When creating `OntologyEvent(market=...)`, passing `"kr"` → the Market enum only has `"korea"`, `"us"`. `stock_kr` → `replace("stock_", "")` → `"kr"` → error. The correction code is **after** event creation, so it's meaningless
- **Trial and error**: (1) Found the error on the first run → fixed and re-ran → same error (mistook the previous run's log as the new run's result) (2) Pydantic validates immediately in the constructor, so the "correct after creation" strategy itself is impossible
- **Solution**: Map `market = "korea" if "kr" in cat else "us"` before event creation. Delete the correction code
- **Alternatives**: (a) Add `KR = "kr"` to the Market enum → affects the whole system, other places expect "korea" (b) Auto-convert with `model_validator` → excessive magic
- **Know-how**: A Pydantic BaseModel validates immediately in `__init__`. "Create it then fix it" won't work. Determine enum values before creation. Also, always check timestamps when reviewing error logs — do not confuse a previous run's log with the current log
- **Retrospective**: Instead of testing only via dry-run, if I had tested even one stock_kr issue LIVE, I would have caught it right away. A dry-run does not go through the DB save path, so it passes Pydantic validation
- **Related files**: `scripts/deep_analysis.py`, `src/core/models.py` (Market enum)

## D-005: matplotlib Korean font rendering
- **Date**: 2026-02 (early project)
- **Situation**: When generating matplotlib charts on WSL Ubuntu, Korean appears as □ (tofu)
- **Issue**: Setting `plt.rcParams["font.family"] = "Noto Sans CJK KR"` alone is not enough. matplotlib does not auto-discover system fonts
- **Trial and error**: (1) Set only `rcParams` font.family → font not found (2) After checking the font path with `fc-list`, specified `font_manager.FontProperties` directly → has to be repeated for every chart (3) Searched by the name `Noto Sans CJK KR` → for a .ttc collection, only the first font (JP) is registered
- **Solution**: Explicitly register the .ttc file via `fontManager.addfont()`, then set family to the registered name `"Noto Sans CJK JP"` (JP is registered first). The JP font also contains Korean glyphs, so rendering is fine. `axes.unicode_minus = False` is required (prevents the minus sign from breaking)
- **Alternatives**: (a) Install a Korean-only font (Nanum Gothic) → requires an extra package on WSL (b) Don't use Korean in images → unrealistic
- **Know-how**: matplotlib + a CJK font requires 2 steps: `addfont()` → `rcParams["font.family"]`. Be aware that only the first font is registered for a .ttc collection. In a headless environment, the `matplotlib.use("Agg")` backend setting is required
- **Retrospective**: This problem is "solve once and done", but the trial-and-error took a long time. Recording it as a snippet in `.claude/rules/coding.md` was the right call — afterwards every chart script solves it by copy-paste
- **Related files**: `.claude/rules/coding.md` (Korean font snippet), the entire `src/exporters/`

## D-006: lightweight-charts fitContent/setVisibleLogicalRange invalidated after setData
- **Date**: 2026-04-12
- **Situation**: On chart period switch (e.g., 6M→MAX), `fitContent()` was called but the visible range stayed fixed on the previous 6M span. The code calls it but it has no effect
- **Issue**: lightweight-charts performs an internal async auto-scroll after `setData()`, and this runs later than the fitContent inside setTimeout(300ms~600ms), overwriting the range we set. Additionally, the time-scale sync listeners of the 3 charts (main/RSI/MACD) cause a feedback loop that resets the range immediately
- **Trial and error**: (1) Gradually increased setTimeout 100ms→300ms→600ms → no effect (2) Nested `requestAnimationFrame` twice → no effect (3) A one-time `subscribeVisibleLogicalRangeChange` listener that sets the range on the first trigger → at the first setData moment the data is incomplete (4) Manual calls from the browser console work → only the automatic call fails
- **Solution**: Keep the `_isSyncingTimeScale` flag true throughout setData (disabling the sync listeners) + a 2-stage setTimeout (100ms → fitContent → 100ms → subchart sync). Instead of deleting/recreating the SMA series each time, create it only once in `initLightweightChart()` and only call `setData()`
- **Alternatives**: (a) Remove the timeScale sync itself → main/RSI/MACD would move independently (b) `setVisibleRange` (time-based) → string-time parsing issues (c) `scrollToPosition(-N)` → no precise range control
- **Know-how**: In lightweight-charts, dynamically adding/removing series triggers the internal auto-scroll every time → **create series only once and refresh only the data via setData**. Multi-chart sync requires a feedback-loop-prevention flag. Force-set the visible range with a separate setTimeout only after all data loading is finished
- **Retrospective**: The official lightweight-charts docs don't explicitly cover a "data updates and auto-scaling" section. I should have designed with the series-reuse pattern from the start. Repeating removeSeries→addLineSeries also performs poorly
- **Related files**: `src/web/static/app.js` (initLightweightChart, loadChartData, syncTimeScale)

## D-007: numba/coverage dependency conflict makes pandas_ta entirely unusable
- **Date**: 2026-05-15
- **Situation**: A 500 error on the `import pandas_ta as ta` call in chart_api.py
- **Problem**: pandas_ta → numba → references `coverage.types.Tracer` → that attribute was removed in coverage 7.4.4. Because only `except ImportError` was used, the `AttributeError` slipped through
- **Trial and error**: Changing `except ImportError` → `except Exception` solves `_compute_indicators`. But the `get_trend_signals` function also has a bare `import pandas_ta as ta`, so the 500 recurs
- **Solution**: Fix both places. Replace the entire pandas_ta in `get_trend_signals` with `vwma_series/sma_series` from `sma_signals.py` + manual RSI rolling. Remove ADX from the conditions (the RSI-only filter is sufficient)
- **Know-how**: Catching only `except ImportError` misses `AttributeError/ImportError` variants in the middle of the dependency chain. Always import third-party libraries with `except Exception`. VWMA/SMA/RSI can be implemented directly with pandas rolling without pandas_ta (within 20 lines)
- **Related files**: `src/web/chart_api.py`, `src/analyzers/sma_signals.py`
