---
name: research-and-report
description: Michel's standard format for investigations, comparisons, benchmarks, experiments, and any "go look into X and tell me what you find" task. Use whenever the user asks to investigate, compare, evaluate, benchmark, analyze, audit, profile, measure, or "find out" something — and a written deliverable (markdown report) is appropriate. Triggers on phrases like "investigate", "compare", "benchmark", "evaluate", "look into", "what's the impact of", "is X better than Y", "audit", and on any task that involves running multiple variants and writing up findings.
---

# Research and Report

For any non-trivial investigation, produce a **self-contained markdown report** under `scripts/<topic>/` (or the project's equivalent). The report is the deliverable — chat summaries are not.

## 1. Folder Layout

```
scripts/<topic>/
├── README.md          # The report (entry point, always start here)
├── data/              # Raw inputs, raw outputs, JSON dumps
├── plots/             # Generated charts (if any)
├── <script>.py        # Reproducible script that produced data/
└── notes.md           # Optional: scratch / dead ends / negative results
```

`<topic>` is kebab-case and descriptive: `swedish-caps-test`, `prompt-token-comparison`, `gender-consistency-eval`.

## 2. Report Structure (Use Exactly)

```markdown
# <Topic> — <One-Line Conclusion>

**Date:** <YYYY-MM-DD>  **Author:** Michel  **Branch:** <branch>
**Reproduces with:** `python3 scripts/<topic>/<script>.py`

## TL;DR
<2–4 sentences. State the verdict first. The reader should know the answer without scrolling.>

## Question
<What were we trying to find out? Why does it matter?>

## Methodology
- Inputs: <data sources, sample size, selection criteria>
- Variants: <what was compared, how many runs each>
- Environment: <local Docker / DEV / lib versions / model names>
- Metrics: <how success was measured; pass criteria>

## Results
<Tables. Charts. Real numbers. Show the data, not adjectives.>

| Variant | Metric A | Metric B | Pass rate |
|---|---:|---:|---:|
| baseline | ... | ... | ... |
| candidate | ... | ... | ... |

## Findings
- <Concrete, specific finding tied to the data above>
- ...

## Verdict
<Recommend / Do not recommend / Inconclusive — with reasoning. Tie to the original Question.>

## Caveats / Threats to Validity
<Sample size, confounders, things you could not test, where this might not generalize.>

## Next Steps
- [ ] <follow-up>
- ...

## Reproducing
<Exact commands. Should work on a fresh checkout.>
```

## 3. Discipline

- **Verdict first.** TL;DR appears before Methodology. Readers are busy.
- **Show numbers, not adjectives.** "Faster" is not a finding; "23% lower p95 latency over 100 runs" is.
- **Reproducibility is non-negotiable.** Anyone should be able to clone the repo, run the script, and regenerate `data/` and `plots/`. If your investigation isn't reproducible, it isn't done.
- **Capture negative results.** A variant that *didn't* help is still data — log it in `notes.md` or in the report itself. Saves future-you (and others) from re-trying.
- **Pin versions.** Note the exact container / layer / library version that produced each result. Reproductions in 6 months depend on it.
- **Statistical honesty.** Note sample size. If n is small, say so. Don't average over 3 runs and call it benchmark data.

## 4. Posting Findings

- For Azure DevOps PBIs: post the TL;DR + Results table as an HTML-formatted PBI comment via `System.History`.
- For GitHub issues: post markdown directly.
- Always link to the report file in the repo so the full context is one click away.

## 5. When NOT to Use This Skill

- Trivial fact-finding ("what version of node does X use?") — answer inline.
- Simple bug investigations — use the `debugging-discipline` skill instead and capture findings in the PR description.
- Use this skill when there are **multiple variants, measurable outcomes, and a decision to be made**.

## 6. Examples in the Wild

Reference these as templates:

- `scripts/cross-paragraph-gender/` — eval-driven investigation
- `scripts/title-subtitle-consistency/` — multi-model comparison + LaTeX report
- `scripts/swedish-caps-test/` — focused single-question investigation

## Anti-Patterns

- Summary in chat, no committed report → it never happened.
- Conclusions before methodology → cherry-picking risk.
- "Run it yourself to see" → not a finding.
- Mixing exploration code and the final reproducible script → keep `notes.md` separate.
