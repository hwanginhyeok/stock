# Prepared Tasks

> **Focus on InvestOS infrastructure + Tesla entity system** — apply HIH_2 work entity patterns to stock
> All article work is on hold; infrastructure/data pipeline first

## P1 — Active

| # | Task | Priority | depends | Notes |
|---|--------|----------|---------|------|
| 1-46 | `stock-notion-sync` skill — Notion DB integration PoC | P1 | 1-43, 1-44 | Clone of hih-notion-sync. Start with 1 issue DB |
| 1-53 | Slant-line/channel-based signals (Inbeom trading method) | P1 | 1-49 | Slant-line touch = waiting to buy, recovery after breakout = strong buy, channel top = take profit |
| 1-71 | 1-47 Phase 3 — tesla_api.py DB migration + dual-read for 1 week + FK reinforcement | P1 | 1-47 ✅ | Hermes Phase 1 §8-B + §8-C recommendation. Migrate tesla_api.py's 5 functions (list_issues/get_issue_detail/list_tagged_issues/count_tagged_issues + ...) to DB read. Remove CSV read after 1 week of the CSV/DB dual-read stage. Add TeslaMilestoneDB FK columns + PRAGMA foreign_keys=ON. Awaiting PM dispatch |
| 1-48 | Tesla auxiliary data (essence_scores/master_plan/moat_status/thesis/timeline/topics/portfolio, 7 files) → SQLite ORM migration | P2 | 1-47 ✅ | 1-47 Phase 1 §8-D recommendation. 4 JSON + 3 CSV. For each, choose between creating a dedicated domain ORM or a generic key-value table strategy. tesla_api.py is using them, so compatibility must be maintained. Phase 1: mapping table → Phase 2: migration → Phase 3: tesla_api dual read |
| 1-67 | sentiment archive remaining-debt cleanup — analyzers + 5 test files | P2 | — | `src/analyzers/expected_move.py` + `src/analyzers/market_sentiment.py` + 5 files in `tests/test_collectors/test_sentiment/` reference the 6 archived classes (AAII/GoogleTrends/NaverCommunity/OptionsIV/Reddit/StockTwits). Zero operational impact since it is outside the cron path, but ImportError recurs when those modules are used. Found via the remaining-debt report of the 1-68 cron fix PR |

## On hold (temporarily suspended due to the shift to InvestOS infrastructure focus)

### Articles on hold (4-x)
| # | Task | Priority | Notes |
|---|--------|----------|------|
| 4-16 | 026 TeraFab — Tesla·xAI chip factory | P1 | ⏸️ v1 271 lines done, awaiting revision |
| 4-17 | 027 The paradox of the foundry | P1 | ⏸️ Awaiting outline |
| 4-18 | Tesla·xAI·SpaceX TeraFab | P1 | ⏸️ Awaiting research |
| 4-19 | 029 GEOPO — Hormuz/Iran/IMEC | P1 | ⏸️ v1 280 lines, geopolitics |

### Research on hold (5-x)
| # | Task | Priority | Notes |
|---|--------|----------|------|
| 5-11 | Bio sector research hub | P1 | ⏸️ On hold due to the shift to Tesla focus |

### P1 on hold (existing)
| # | Task | Priority | depends | Notes |
|---|--------|----------|---------|------|
| 4-5 | Palantir deep-dive series (6 parts) | P1 | user: X post | ⏸️ On hold |
| 4-11 | KR-03~06: Hyundai Motor series (4 parts) | P1 | | ⏸️ On hold |
| 4-6 | Blockchain #3: BMNR — ETH treasury | P1 | | ⏸️ On hold |
| 4-7 | Blockchain #4: CRCL — USDC digital dollar | P1 | | ⏸️ On hold |
| 5-8 | Iran war geopolitics ontology Phase 2 | P1 | | ⏸️ On hold |

### P2 on hold
| # | Task | Priority | depends | Notes |
|---|--------|----------|---------|------|
| 1-40 | Entity timeline merge | P2 | 1-39 done | ⏸️ On hold |
| 4-12 | KR-07: Multiplication disappears — semiconductors | P2 | user: structure proposal | ⏸️ On hold |
| 4-15 | HOOD — Robinhood retail | P2 | | ⏸️ On hold |
| 4-13 | Elon Musk ecosystem card-news | P2 | | ⏸️ On hold for now (Tesla content consolidated into 4-18) |
| 3-1 | Indicator interpretation system enhancement | P2 | | ⏸️ On hold |
| 3-2 | Two-axis linkage system — positions by regime | P2 | 3-1 | ⏸️ On hold |
| 1-29 | Iran war dashboard design review | P2 | | ⏸️ On hold |

### P3 on hold
| # | Task | Priority | depends | Notes |
|---|--------|----------|---------|------|
| 4-14 | Elon Musk ecosystem imaginative content (web roulette) | P3 | | ⏸️ On hold |
| 1-14 | articles/ article output format template | P3 | | ⏸️ On hold |
| 1-15 | Pre-start checklist per agent | P3 | | ⏸️ On hold |
| 1-16 | Skill manual per agent | P3 | | ⏸️ On hold |
| 1-17 | CI/CD pipeline | P3 | | ⏸️ On hold |
| 1-18 | Docker containerization | P3 | | ⏸️ On hold |
| 1-19 | Scheduler configuration | P3 | | ⏸️ On hold |
