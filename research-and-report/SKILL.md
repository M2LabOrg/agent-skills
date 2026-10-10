---
name: research-and-report
description: Produces a self-contained, reproducible Markdown report for investigations, comparisons, benchmarks, and experiments, with the verdict first and real numbers throughout. Use when asked to investigate, compare, benchmark, evaluate, measure, audit, or "look into" something where several options or variants are tested and a written finding is the deliverable. Do not use for quick factual lookups (answer inline), single-bug investigations (use debugging-discipline), or design proposals (use spec-before-code).
metadata:
  category: research
---

# Research and Report

For any non-trivial investigation, the committed report is the deliverable. A summary in chat is not.

Use this skill when there are **several variants, measurable outcomes, and a decision to make**.

## 1. Lay out the folder

```
<reports-dir>/<topic>/
├── README.md        # The report: start here
├── <script>.py      # Reproducible script that produced data/
├── data/            # Raw inputs and outputs
├── plots/           # Generated charts, if any
└── notes.md         # Optional: dead ends and negative results
```

Use the project's convention for `<reports-dir>` (for example `research/`, `docs/investigations/`, or `scripts/`). Name `<topic>` in kebab-case, descriptively: `prompt-token-comparison`, `cache-eviction-benchmark`.

## 2. Write the report

Copy [assets/report-template.md](assets/report-template.md) to `<topic>/README.md` and fill it in. Its order is deliberate: **TL;DR and verdict first**, then question, method, results, findings, caveats, and how to reproduce.

## 3. Discipline

- **Verdict first.** Readers should get the answer without scrolling.
- **Numbers, not adjectives.** "Faster" is not a finding. "p95 latency 23% lower over 100 runs (95% CI 15–31%)" is.
- **Reproducible or not done.** A fresh checkout plus the documented command must regenerate `data/` and `plots/`.
- **Record negative results.** A variant that didn't help is data, and it saves someone repeating the work.
- **Pin versions** of every library, model, service, and data set that produced a result.
- **Statistical honesty.** State sample sizes. Give rates as `k/n` with intervals. Don't call a difference real when its interval includes zero. For evaluations of AI systems, apply the `skill-eval-statistics` skill.

## 4. Share the findings

- Post the TL;DR and results table on the linked issue or work item.
- Link to the committed report so the full context is one click away.

## Anti-patterns

- Findings that exist only in chat.
- Conclusions written before the method: a cherry-picking risk.
- "Run it yourself to see" in place of a finding.
- Mixing exploratory code with the final reproducible script. Keep exploration in `notes.md`.
