# Architecture

## Directory structure

- `config/` - YAML config files
- `agents/` - Agent role definitions
- `src/core/` - Shared infrastructure (config, logger, models, db, claude_client)
- `src/collectors/` - Data collection (news, market)
- `src/analyzers/` - Analysis (technical, fundamental, sentiment, screener)
- `src/generators/` - Content generation (article, summary, insight, image, hashtag)
- `src/publishers/` - SNS publishing (instagram, x, formatter, media)
- `src/storage/` - DB CRUD, table definitions
- `src/exporters/` - Excel report builder (signals, dashboard, sector, etc.)
- `src/backtesting/` - Backtesting engine (strategy, metrics, report)
- `src/services/` - Independent services (news timeline, etc.)
- `src/web/` - Web server (briefing pages, etc.)
- `src/workflows/` - Orchestration (morning, closing, weekly, breaking, research)
- `templates/` - Jinja2 templates (articles, sns, prompts)
- `data/` - Data (raw, processed, cache, db, articles, briefings, facts, timelines, research) - git ignored
- `logs/` - Log files - git ignored
- `tests/` - Tests
- `scripts/` - Utility scripts
- `docs/프로젝트/` - TASK management + detailed logs

## Agent roles

0. **Team lead** - Workflow orchestration / quality gate / exception handling / agent direction
1. **News analyst** - News collection / classification / sentiment analysis
2. **Market analyst** - Market data collection / technical & fundamental analysis / screening
3. **Article writer** - Claude API-based content generation / quality management
4. **SNS manager** - Instagram/X format conversion / publishing / schedule management
5. **Research assistant** - On-demand deep research / SWOT / comparative analysis

### AI model policy
- **Opus**: Article writer, Research assistant (writing & deep analysis — quality is the deliverable itself)
- **Sonnet**: Team lead, News analyst, Market analyst, SNS manager (orchestration, collection, format conversion)
- Parameter tuning via per-task max_tokens / temperature differentiation
- Config: `config/settings.yaml` → `claude.models`
