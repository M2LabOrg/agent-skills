# Contributing

This repository is the source of truth for these skills. Issues and pull requests are merged here directly.

## Ways to help

- **Bug in a skill?** Open an issue with the skill name, what you asked your agent, and what went wrong.
- **Trigger misfires?** Add the query to that skill's `evals/trigger-queries.json` with the correct `should_trigger` label, ideally with a description fix.
- **New skill?** Open an issue first, describing the methodology, when it should trigger, and when it shouldn't.
- **Eval data.** Per-query, per-run results from real skill evals help calibrate the guidance in `skill-eval-statistics`.

## Adding or changing a skill

1. Create or edit `<skill-name>/SKILL.md`. The folder name must equal the `name` field (lowercase kebab-case).
2. Write the `description` as: what it does, `Use when …`, `Do not use …`, in under 1024 characters.
3. Add `metadata.category` (one of the categories already in the catalog, unless a new one is really needed).
4. Keep `SKILL.md` under 500 lines. Put long detail in `references/`, templates in `assets/`, and runnable helpers in `scripts/`. Link to them with relative paths from `SKILL.md`.
5. Keep the skill self-contained: no links into other skills' folders, no tool-specific paths or variables, scripts using only the standard library.
6. Add `evals/trigger-queries.json` with at least 8 queries, including near-miss negatives.
7. Regenerate the catalog and run the checks:

   ```bash
   python3 scripts/catalog.py
   python3 -m unittest discover tests
   ```

CI runs the same checks with `--check` and fails if the README table or docs site are out of date.

## Ground rules

- No personal, employer, or client details: names of internal projects, work-item ids, account ids, internal URLs. The checker catches common patterns; reviewers catch the rest.
- Every quantitative claim needs a calculation, a test, or a citation.

## Code of conduct

Be kind, be specific, focus on the work.
