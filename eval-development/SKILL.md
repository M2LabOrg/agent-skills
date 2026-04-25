---
name: eval-development
description: Michel's personal methodology for eval-driven development of AI translation (and similar AI service) fixes in <your AI services project>. Use whenever the user asks to "build an eval", "set up an eval", "write an eval suite", "evaluate translation quality across models", iterate on translation/post-processing fixes with measurable results, or work on PBIs that follow the same eval-first pattern (e.g., gender consistency, title consistency, dictionary enforcement, citation formatting). Encodes folder layout, Docker requirement, model coverage, status taxonomy, reporting format, and deployment loop.
---

# Eval Development Skill (Michel — Local)

This skill captures **Michel's standard methodology** for eval-driven development on the `<your AI services project>` repo. Reference: PBI #443029 (Cross-paragraph gender consistency — post-processing for non-prompt-injectable models).

Apply it whenever building or extending an evaluation suite for AI translation or similar AI service quality fixes — even when the *subject* of the eval differs (gender, titles, dictionary, citations, punctuation, etc.). Methodology stays the same; the test cases and pass criteria adapt.

---

## 1. Core Principles

- **Eval-first**: Write the eval before (or alongside) the fix. Every code change is validated by re-running the eval suite locally before pushing.
- **Local Docker required**: All eval runs go through the local Docker Compose stack (`docker compose up`) hitting the API container at `http://localhost:3000`. Never iterate against DEV/STG/PRD for development — only for final validation.
- **Cover all relevant models**: An eval is not done until it tests **every model the user can pick in the UI** for that capability.
- **Three-status taxonomy**: `PASS` / `PASS_NEUTRAL` / `FAIL` — never just pass/fail. Neutral outputs (gender-neutral phrasing, ambiguous-but-acceptable translations) are first-class.
- **Reproducible report**: Every run regenerates a markdown report committed to the branch. The PBI gets a posted summary.
- **Target**: 100% pass rate (PASS + PASS_NEUTRAL) across all models before requesting language-team validation.

---

## 2. Required Setup Before Running an Eval

```bash
# 1. AWS SSO (Secrets Manager + S3 access from inside the API container)
aws sso login

# 2. Bring the local stack up
docker compose up -d

# 3. Verify AWS creds reached the API container (see retrieved memory)
docker compose exec api sh -c "wget -qO- 'http://localhost:3000/health?checkAws=true'"
# Expect: {"aws":{"ok":true,"account":"788797614830"}}
```

If the user has changed `containers/inference/python/...`, they must:

```bash
# Rebuild only the inference image (fast iteration)
docker compose up -d --build inference
```

For changes to `layers/text_lib/src/text_lib/translation.py`, also sync the container copy:

```bash
cp layers/text_lib/src/text_lib/translation.py \
   containers/inference/python/text_lib/translation.py
```

(Keep the two `translation.py` copies in sync — see retrieved memory `f529f4dc`.)

---

## 3. Folder Layout for a New Eval

Create everything under `scripts/<eval-name>/` (kebab-case, descriptive):

```
scripts/<eval-name>/
├── README.md                 # What this eval tests, how to run, current results
├── eval_<topic>.py           # The eval driver (Python 3, stdlib + requests only when possible)
├── test_cases.json           # Or inline in the .py — list of {id, source, lang_pair, expected_keywords, ...}
├── eval_report.md            # Auto-generated detailed per-test/per-model report
├── EVAL_RESULTS.md           # Human-curated summary + failure analysis (committed)
└── data/                     # Optional: raw JSON dumps from individual runs (gitignored if huge)
```

Match the pattern from `scripts/cross-paragraph-gender/` (PBI #443029) and `scripts/title-subtitle-consistency/`.

---

## 4. Recommended Test Coverage

| Dimension | Default | Rationale |
|---|---|---|
| **Test cases** | **10 minimum** | Enough variety, fast enough to run in <2 min |
| **Models** | **All UI-selectable for the capability** | E.g. for translation: `text-translation-t21a`, `text-translation-t21d`, `openai-translate`, `anthropic-translate`, `aws-translate`, `azure-translator`, `google-translate` (7 models) |
| **Languages** | At minimum the language(s) named in the PBI; for cross-language fixes, cover **PT, ES, DE, RU** | These four cover gendered Romance + Germanic + Slavic |
| **Edge cases** | Always include: multi-person articles, female subjects, male subjects, gender-neutral source | Failure patterns differ by polarity |
| **Total requests** | ~70 (10 × 7) for single-language; ~280 for 4-language | Small enough to run locally, big enough to be statistically meaningful |

For non-translation evals (e.g., punctuation, citation, title): keep 10 cases × N strategies and adapt the model list.

---

## 5. Status Taxonomy (Use Exactly These)

| Status | Meaning | Example |
|---|---|---|
| `PASS` | Output contains the **correct gendered/expected** form | `Nascida` for a female subject |
| `PASS_NEUTRAL` | Output is **acceptable gender-neutral / ambiguous** form | `Nasceu` (no gender marker) |
| `FAIL` | Output contains the **wrong** form | `Nascido` for a female subject |

Pass rate = `(PASS + PASS_NEUTRAL) / total`. Target = **100%**.

---

## 6. Eval Driver Skeleton

The driver should:

1. Accept CLI args: `--models`, `--tests`, `--out` (default `eval_report.md`).
2. POST each test to `http://localhost:3000` (the standard sync endpoint, e.g. `/api/v1/text/text-translation` for translation), with SigV4 disabled (local stack).
3. For each result, classify by **keyword inspection** of the translated output (`PASS` / `PASS_NEUTRAL` / `FAIL`) using a per-test list of `expected_keywords`, `neutral_keywords`, `wrong_keywords`.
4. Print a colored table to stdout AND write `eval_report.md` with:
   - Summary table (model × pass rate)
   - Per-test breakdown showing the actual translated snippet for each gendered/expected term
5. Exit non-zero if pass rate < 100% (so it can gate CI later).

Reference implementation: `scripts/cross-paragraph-gender/eval_gender.py`.

---

## 7. Report Template (`EVAL_RESULTS.md`)

```markdown
# <PBI Title> — Eval Results

**PBI:** #<id>  **Branch:** mdsm/<branch>  **Date:** <YYYY-MM-DD>
**Stack:** local Docker Compose, inference container `<version>`

## Summary

| Model | Pass | Neutral | Fail | Rate |
|---|---:|---:|---:|---:|
| text-translation-t21a | 10 | 0 | 0 | **100% ✅** |
| ... |

## Failure Patterns
- **<model>**: <pattern>
- ...

## Fix Strategy
- **Prompt-injectable models** (t21a, t21d, openai, anthropic): entity-context pre-pass + prompt injection
- **Non-prompt-injectable models** (aws, azure, google): post-processing enforcement (`enforce_*_consistency()` pattern, see PBI #411440)

## Next Steps
1. ...
```

Also post a condensed HTML version of this table as a PBI comment via `System.History` — see retrieved memory `165691c8`.

---

## 8. Iteration Loop

```text
edit code  →  rebuild inference container  →  run eval  →  inspect failures
            ↑                                                          │
            └──────────────────  refine fix  ←─────────────────────────┘
```

Concretely each round:

```bash
# 1. Rebuild after code change
docker compose up -d --build inference

# 2. Run eval
python3 scripts/<eval-name>/eval_<topic>.py

# 3. Inspect new eval_report.md, commit when better
git add scripts/<eval-name>/eval_report.md scripts/<eval-name>/EVAL_RESULTS.md
git commit -m "<eval-name>: results after <change>"
```

---

## 9. Two-Layer Fix Pattern (Translation Quality PBIs)

When the eval shows multi-model failures, prefer this proven pattern (PBIs #411440, #422337, #435102, #443029):

1. **Layer 1 — Prompt injection** (only models that accept system context):
   - Add an entity-extraction pre-pass in the sync handler (`containers/inference/python/sync_handlers/text_translation.py`)
   - Inject extracted context into the translation prompt builders in `translation.py`
2. **Layer 2 — Deterministic post-processing** (ALL models — safety net):
   - Add an `enforce_<topic>_consistency()` function in `containers/inference/python/text_lib/translation.py`
   - Call it from both sync and async paths
   - Mirror the change in `layers/text_lib/src/text_lib/translation.py` (keep copies in sync)

---

## 10. Pre-Push Checklist

Before opening / updating the PR:

```bash
# Lint + format
python -m manage checks --fix

# Bump versions if you touched containers/layers (see retrieved memory 27fe9a3b)
#   containers/inference/container.toml  → bump version
#   layers/text_lib/layer.toml            → bump version (if layer touched)

# Re-run eval one final time
python3 scripts/<eval-name>/eval_<topic>.py

# Commit eval artifacts
git add scripts/<eval-name>/
```

---

## 11. Deployment Loop (after PR merge)

```bash
# DEV
python -m manage push_container inference -p tma_ai_dev
python3 scripts/<eval-name>/eval_<topic>.py --env dev   # validate against DEV API

# Request language-team validation (Portuguese / Spanish / etc.)

# STG → PRD after sign-off (CDK pipeline or manage push)
```

Update PBI with HTML-formatted results table per `System.History` after each environment.

---

## 12. Branch + PR Conventions (User Rules)

- Branch: `mdsm/<short-descriptive-name>` (per global rule)
- Target branch: **`main`** (never `master`)
- PR description: link the PBI, paste the eval summary table, list the 7 models tested

---

## Quick Reference Card

| Thing | Value |
|---|---|
| Local API URL | `http://localhost:3000` |
| Stack up | `docker compose up -d` |
| Rebuild inference | `docker compose up -d --build inference` |
| Run eval | `python3 scripts/<eval-name>/eval_*.py` |
| Min test cases | 10 |
| Translation models | 7 (t21a, t21d, openai, anthropic, aws, azure, google) |
| Statuses | PASS / PASS_NEUTRAL / FAIL |
| Target pass rate | 100% |
| Reference PBI | #443029 |
| Reference scripts | `scripts/cross-paragraph-gender/`, `scripts/title-subtitle-consistency/` |
