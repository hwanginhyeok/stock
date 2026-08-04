# Workflow Rules

## Workflow Principles

1. Strictly follow the order: **Collect** → **Analyze** → **Generate** → **Publish**
2. Store the results of every stage in the DB
3. Generated content must always include a disclaimer
4. No investment solicitation/recommendation language

## Security Rules

- Never hardcode API keys → manage them in the `.env` file
- The `.env` file must be included in `.gitignore`
- Do not output sensitive information such as API keys, tokens, etc. in logs
- When crawling, comply with robots.txt and apply rate limiting

## TASK Detailed Management

### Field Codes & Numbering

Every TASK is assigned a number in the `{field_code}-{sequence}` format. The sequence is the registration order within that field (based on publication date).

| Field code | Field | Definition |
|----------|------|------|
| `1-x` | 시스템 (System) | Building **things that run automatically** — infrastructure, pipelines, collectors, schedulers, etc. |
| `2-x` | 코드 (Code) | **Unit implementation** of algorithms, indicators, features (parts inside the system) |
| `3-x` | 분석 (Analysis) | Data **interpretation, validation, backtesting** — no code deliverable required |
| `4-x` | 아티클 (Article) | The full process: content planning → research → draft → revision → **publish** |
| `5-x` | 리서치 (Research) | **In-depth investigation** of companies/sectors/markets (develops into an article or concludes as internal reference) |

### TASK Table Column Structure

**🔥 Currently in progress:**
```
| # | 분야 | 작업 | 담당 | 진행 상황 | 다음 할 일 |
```

**⏸️ Awaiting user action (code complete, only user execution remains):**
```
| # | 분야 | 작업 | 남은 사용자 액션 |
```

**Task status (by P-grade subgroup):**
```
| # | 분야 | 작업 | 중요도 | 담당 | 발행일 | 상태 | 비고 |
```

**Completed:**
```
| # | 분야 | 작업 | 완료일 | 비고 |
```

### Status Stages

`예정` (planned) → `요청` (requested) → `진행` (in progress) → `완료` (done)

| Status | Meaning |
|------|------|
| `예정` (planned) | Something to do someday, not yet started |
| `요청` (requested) | User specifically requested it but not yet started |
| `진행` (in progress) | Currently being worked on |
| `완료` (done) | Completion conditions met, move to the completed section |

### TASK File Real-Time Update Rules

> File structure: `CURRENT_TASK.md` (in progress) / `PREPARED_TASK.md` (planned) / `FINISHED_TASK.md` (completed)

| Trigger | Action |
|--------|------|
| **On starting work** | Move from `PREPARED_TASK.md` → `CURRENT_TASK.md` + record start date |
| **When blocked** | Record the reason in the blocked column of `CURRENT_TASK.md` |
| **On completing work** | Move from `CURRENT_TASK.md` → `FINISHED_TASK.md` + record completion date |
| **On discovering new work** | Register in `PREPARED_TASK.md` + assign priority |
| **Just before commit** | Check that the TASK file status matches reality |
| **End of month** | Move from `FINISHED_TASK.md` → `TASK_ARCHIVE/YYYY-MM.md` |

### Priority Criteria (P1 / P2 / P3)

| Grade | Criteria |
|------|------|
| `P1` | Other work is blocked by this / user needs it today / directly tied to revenue/quality |
| `P2` | Needed soon / naturally follows after P1 is done |
| `P3` | Nice to have but fine without it / long-term improvement |

**P-grade subgroup divisions in the task status** (literal divider strings as used in TASK files — Korean glossed in English):
```
── P1 긴급 ──                                              (P1 Urgent)
── P2 즉시 착수 가능 ──                                     (P2 Can start immediately)
── P2 선행 작업 대기 ──  (⏳ 선행작업: X-x 완료 후 착수)      (P2 Waiting on prerequisite — ⏳ prerequisite: start after X-x is complete)
── P3 향후 ──                                              (P3 Future)
```

### Delay Emphasis

If the `예정` or `요청` status is maintained for **3 or more days** after publication, mark `**[지연]**` in front of the status.

### Definition of "Done" (by field)

| Field | Completion condition |
|------|-----------|
| `시스템` (System) | Actual execution results are produced and confirmed via dry-run or real operation |
| `코드` (Code) | The feature is reflected in a report/output and the user has confirmed it |
| `분석` (Analysis) | Findings are documented and the user has reviewed the content |
| `아티클` (Article) | Publishing complete (or the user explicitly declares it done) |
| `리서치` (Research) | The target document is written and the user has reviewed it |

### TASK Detailed Log Writing Criteria

When writing to `docs/프로젝트/task/{ID}.md`:

- Work involving design decisions (why A was chosen and B rejected)
- Work changing multiple files (change tracking needed)
- Work where a "why was it done this way?" question is expected later
- Work requiring user review (record open issues)
- **Mandatory for article tasks (4-x)** — always create one to track revision history

### Article Revision History Management Rules

**Trigger**: Record immediately whenever the user gives feedback on an article

**Recording location**: `docs/프로젝트/task/4-x.md` → `## 퇴고 이력` section

**What to record**:
1. The user's feedback verbatim or summarized
2. Change decisions (where, why, and how it was changed)
3. Deferred items (what was pushed to the next version and why)

**Principle promotion process**:
- When the same type of feedback repeats **3 or more times** → record it in `반복 패턴 메모`
- Once the pattern is confirmed → add it as a principle in `docs/guides/article-writing.md`

**Template**: `docs/프로젝트/task/TEMPLATE_article.md` (separate from code tasks)
