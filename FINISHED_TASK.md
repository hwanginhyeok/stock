# Finished Tasks

> Before 2026-03 → [TASK_ARCHIVE/2026-03.md](TASK_ARCHIVE/2026-03.md)

| # | Task | Completed | Notes |
|---|--------|--------|------|
| 1-47 | Tesla CSV → SQLite ORM migration (issues/milestones/tagged_issues) | 2026-05-25 | Stalled 25 days (started 5/1) → 5/24 PM /hih-investigate → Hermes Phase 1 mapping table v1 (`docs/specs/1-47-csv-to-db-mapping-v1.md`) + Phase 2 migration (commit `e298e32`, 5 files +686 LOC). Load result 10/24/10 ✅ idempotency verified 3 times ✅ enum distribution 100% match. Phase 3 (tesla_api DB switch + dual-read + FK reinforcement) split off as 1-71. Auxiliary 7-file migration is 1-48 P2. A case of the global rule "Sonnet delegation + Opus L2 verification" working |
| 1-70 | earn_reporter Nasdaq API deprecated field-name handling (eps/epsForecast/name fallback) | 2026-05-24 | Found via 1-64. Pushed directly to master `a3d71a8` without a PR (1-line → 3-line expansion fix). RC: Nasdaq API silent rename — epsActual/epsEstimate/companyName are all always None; actual values are eps/epsForecast/name. Verification: 5/21 data company 55/55, eps_estimate 24/55, eps_actual 33/55 (previously 0). New memory: [[external-api-silent-field-rename]] |
| 1-69 | sector_summary cron registered for the 1st of each month (Hermes) | 2026-05-24 | Automation bonus from 1-64. `0 0 1 * * cd /home/window11/stock && /usr/bin/python3 scripts/generate_sector_summary.py 2026 Q1 --output ... >> ~/.pm_logs/sector_summary.log 2>&1`. First auto-fire 2026-06-01 00:00 KST. ⚠ Script does not use argparse → regenerates the same 2026Q1 every month. A separate task is needed to add argparse for Q2 auto-update. New memory: [[cron-line-write-first]] |
| 1-64 | 2026Q1 earnings-season sector summary analysis HTML | 2026-05-24 | Started 04-29 → stalled 25 days → resumed immediately after cron was restored. 48 tickers (season 4/29~5/22) → grouped into 11 GICS sectors + leaders/laggards (EPS surprise %) + mapping appendix. Delegated to a Sonnet subagent right after PM `/hih-investigate` cron recovery. Output: `docs/earnings/2026Q1_sector_summary.html` (50KB) + `scripts/generate_sector_summary.py` (31KB idempotent, reusable for Q2~Q4). Commit `3fea264` + GDrive upload https://drive.google.com/open?id=1QQekvCcHCa2TcZVnics_3_7krpP__WRW. 15 data issues (EPS N/A 13 + BRK.B blank + INTC cap) noted in appendix |
| 1-68 | cron death RC1+RC2 fix — sentiment ImportError + earn_reporter rows None | 2026-05-24 | PR #1 `74b38b8`. RC1 (after 5/12 c233d81 archive, follow-up __init__.py not cleaned up → kr/us news failed 90 times over 4 days) + RC2 (Nasdaq API response change `{"data": {"rows": null}}` → NoneType iter at line 240). Verification: KR 182 items / US 89 items / earn_reporter exit 0. Remaining debt split off as 1-67 |
| 1-66 | APScheduler daemon registered as a systemd service (briefing auto-restart) | 2026-05-24 | Registered `~/.config/systemd/user/stock-briefing.service` + enable + linger yes. Secondary RC4 found: numpy 2.4.4 vs system matplotlib 3.6.3 ABI conflict → resolved by upgrading ~/.local matplotlib to 3.10.9. Actual schedule: morning 08:00 / closing 16:30 / weekly SAT 10:00 / ohlcv 17:00 ET / morning_email 08:00 mon-sat (memory's 05:53/17:47 is stale, needs updating) |
| 1-45 | Tesla issue DB — TSLA-E/P/C/F/I/R/M system | 2026-04-21 | CSV seed completed: `data/research/stocks/tesla/issues.csv` 10 items + `milestones.csv` 24 items + `tagged_issues.csv` 10 items. `src/core/models.py:501` data model. CSV→DB migration is handled by 1-47 (intended separation). **Actually completed around 04-21, but marked blocked for 21 days due to memory not being updated → recognized via 2026-05-17 PM verification** |
| 1-52 | VWMA100 touch strategy backtest + screener implementation | 2026-05-15 | sma_signals backtest → pivoted to VWMA100 touch strategy. TSLA 5y A/B comparison. NASDAQ100+SP500 screener cron registered |
| 1-59 | Essence top 3-card real-data integration — weight·price·momentum | 2026-05-15 | Current price $443.30 real-time / P&L +80.35% / VWMA100 channel position / weight 28.7% dynamically calculated |
| 1-58 | Trading chart integration — pandas_ta→sma_signals switch + signals API recovery | 2026-05-15 | Resolved numba/coverage conflict. VWMA100 BUY 2026-05-08, TREND_UP |
| 1-60 | Timeline core compression — core/important/all toggle + same-day grouping | 2026-05-14 | importance-score-based filter + topic grouping. important threshold finally tuned to 10 |
| 1-63 | earn_reporter.py verification + cron registration | 2026-05-10 | Verified after fixing 3 EPS·revenue N/A bugs. crontab registration approved |
| 1-65 | Earnings report voice/tone review — user review | 2026-05-10 | 17 deep-dives reviewed. Fixed 3 bugs: EPS N/A·unit mismatch·NaN. Full regeneration + GDrive upload |
| 1-32 | X market post — Tesla | 2026-05-05 | Scrapped — held for 31 days on quality feedback, needs redirection |
| 1-62 | Earnings deep-dive — Big Tech 4 (META/GOOGL/MSFT/AMZN) | 2026-04-30 | 4 deep-dives |
| 1-61 | Earnings deep-dive report backfill | 2026-04-30 | 17 deep-dives + 9 trend |
| 1-55 | Thesis + Timeline + Topic Quarterly | 2026-04-23 | Essence Dashboard component |
| 1-56 | Timeline lane separation + collision avoidance | 2026-04-23 | swimlane rendering |
| 1-57 | occurred_at unification + factuality audit | 2026-04-24 | Event date consistency |
| 1-54 | Tesla Essence Dashboard | 2026-04-23 | Web dashboard |
| 1-44 | Tesla-specific entity schema design (essentialism-based) | 2026-04-23 | Code complete |
| 1-48 | properties dict web UI exposure (3-tier classification) | 2026-04-23 | Code complete |
| 1-51 | Future event chart display (earnings·FOMC etc.) | 2026-04-23 | Code complete |
| 1-30 | InvestOS — Tesla intelligence infrastructure | 2026-04-24 | Decomposed into 1-44~1-47 |
| 1-43 | HIH_2 entity system investigation & stock mapping design | 2026-04-23 | Blocker cleared (proceeds independently). stock current-state investigation done → decomposed into 1-44~1-48. `docs/프로젝트/task/1-43.md` |
| 1-50 | Chart event weighted filter (importance score) | 2026-04-15 | severity × relevance × freshness. Keyword-based Tesla direct/indirect/macro classification. core/important/all selector |
| 1-49 | In-house chart system build (TSLA) | 2026-04-15 | TV widget + lightweight-charts + yfinance + SMA6/VWMA100/VPVR/RSI/MACD + multi-timeframe (1H/4H/D/W/M) + buy/sell signals + diagonal lines (higher-high-lower / lower-low-higher) + parallel channels + VP crossover + independent XY-axis zoom. Follow-up: 1-50~53. D-006 recorded |
| 5-9 | trend_detector Ollama→Gemini Flash switch | 2026-04-08 | gemini -p primary + Ollama fallback, dry-run passed |
| 1-41 | Entity noise filter reinforcement — amount/quantity/visa patterns | 2026-04-08 | Common module + DB 45 cleaned up (3183→3138) |
| 1-42 | News ticker refresh + 2 hot news each for GEO/US/KR | 2026-04-08 | published_at sort, per-category selection |
| 1-37 | Relationship briefing readability improvement — by importance + Korean labels | 2026-04-08 | Per-entity aggregation, frequency×confidence sorting |
| 1-38 | Relationship-graph depth/density control — BFS depth + pruning | 2026-04-08 | depth 1/2/3 selection, bottom 30% auto-removed |
| 5-10 | Ontology-theory-based documentation (276 lines) | 2026-04-08 | Philosophical lineage + essentialism + engineering methodology + FIBO |
| 1-39 | Stock entity ontology design — essential property extraction | 2026-04-08 | Prompt + config schema (essential/propria) |
| 1-36 | Relationship-graph Top N filter + event category expansion | 2026-04-07 | Top 10/20/50/all filter, degree ranking |
| 1-35 | InvestOS event system overhaul — EventType separation + story chaining + timeline view | 2026-04-07 | 275 events, 121 story_thread |
| 1-34 | Deep-analysis pipeline + cron redesign | 2026-04-06 | Ollama twice daily (05:30/17:30), collection 15min→1hour |
| 1-33 | cron news collection URL/domain noise 3-tier filter | 2026-04-06 | title source-name removal + storage filter + 92 polluted entities deleted |
| 1-31a | InvestOS US/KR stock tabs + entity extraction + review pipeline | 2026-04-04 | 3 tabs, Ollama extraction cron, review (type 368 + merge 55 + dup 159), translation, cache |
| 1-31b | GeoInvest Ollama switch (Claude API removed) | 2026-04-04 | API cost 0 |
| 1-31c | News ticker Korean translation + speed control | 2026-04-04 | Ollama batch translation, 10-min cache |
| 1-31d | Timeline latest-first sort + entity_type validation | 2026-04-04 | reverse=True, institution fallback |
| 1-23 | Crypto email Section 6 | 2026-04-03 | COIN/HOOD/MSTR/SQ/BLK/BMNR |
| 2-13 | naver HTML Korean mojibake fix + briefing_server | 2026-04-01 | fragment→full document wrapper |
