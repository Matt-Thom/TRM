# Documentation Update Design

**Date:** 2026-04-01
**Scope:** README.md + docs/ folder
**Audience:** Developers (primary), stakeholders (secondary)

## Goal

Update all project documentation to accurately reflect the current state of the TRM codebase after Phases 1–4 partial implementation. The README is nearly empty and needs a full rewrite with a quickstart guide. Several docs are stale or incomplete.

## Approach

Research context already gathered. Parallel Sonnet agents (one per file) each receive the same ground-truth context and update their assigned file in-place. Final commit pushed to main.

## Files In Scope

| File | Change Type | Notes |
|------|-------------|-------|
| `README.md` | Full rewrite | Project overview, feature status, quickstart (Docker Compose), links to docs |
| `docs/TASK_TRACKER.md` | Update in-place | Mark Phases 1–4 tasks correctly as complete/blocked/pending |
| `docs/CHANGELOG.md` | Deduplicate & clean | Consolidate duplicate 2026-03-30 entries |
| `docs/SCHEMA.md` | Update in-place | Add `assets` and `risk_treatments` tables; fix `risk_matrix_config` column defaults |
| `docs/API_CONTRACTS.md` | Minor review | Verify against current routers; no structural changes expected |
| `docs/ARCHITECTURE.md` | Update in-place | Reflect actual implemented stack (Celery workers, ConnectWise integration, treatment state machine) |
| `docs/DESIGN_DECISIONS.md` | Additive | Add DD-007: Multiplicative risk scoring (likelihood × impact) |

## Files Not In Scope

`CONVENTIONS.md`, `TESTING_STRATEGY.md`, `ENVIRONMENT.md`, `INTEGRATION_NOTES.md`, `DATA_RESIDENCY.md` — content is still accurate, no changes needed.

## README Structure

1. Project title + 1-sentence description
2. Feature status table (Phase 1–4, what's done / blocked / pending)
3. Quickstart (Docker Compose — 5 steps)
4. Architecture overview (brief, link to ARCHITECTURE.md)
5. API reference link (link to API_CONTRACTS.md + Swagger URL)
6. Development guide link (CONVENTIONS.md, TESTING_STRATEGY.md)
7. Docs index (links to all docs/)

## Success Criteria

- README lets a new developer go from clone to running app in under 5 minutes
- All docs accurately describe the current codebase (no references to unimplemented features as if complete)
- No duplicate content across files
- Consistent tone across all docs
