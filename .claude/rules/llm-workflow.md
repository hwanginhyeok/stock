# LLM Workflow Rules (be-a-studio)

## Core: Opus does NOT touch code

Code analysis/writing/editing/refactoring — all delegated to GLM.
Opus only directs + reviews + reports to the user.

## GLM delegation targets (no exceptions)

- Writing/editing code
- Code analysis (reading files and grasping structure)
- Test generation
- Refactoring
- Debugging (simple errors)

## What Opus does

- Conversing with the user
- Task planning/design
- Writing the GLM instruction prompt
- Reviewing GLM results → reporting to the user
- Re-directing when results are insufficient (no direct editing)
- Writing documents (md)

## How to call GLM

```bash
python3 ~/project-manager/scripts/glm_client.py \
    --prompt "content to analyze" \
    --project be-a-studio \
    --feature feature-name
```

## On violation

If Opus directly analyzes code with Grep/Read, or edits code with Edit/Write, that is an **architecture violation**.
Always go through glm_client.py.
