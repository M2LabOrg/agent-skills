# Eval report: <skill name> — <what changed>

**Date:** YYYY-MM-DD · **Agent / model:** <agent> <version> / <model id> · **Skills installed:** <list or "this skill only">

## Question

<One sentence: what decision does this eval inform?>

- **Primary metric:** <trigger recall | false-trigger rate | outcome lift>
- **Smallest improvement worth detecting:** <e.g. +10 points>
- **Regression tolerance:** <e.g. −5 points>

## Design

| | |
|---|---|
| Queries | <n> (<n+> should-trigger, <n−> should-not-trigger near-misses) |
| Runs per query | <r> |
| Split | train <n> / validation <n> / test <n> — numbers below are from **<split>** |
| Grader | <deterministic check / rubric / LLM judge (model, prompt version)> |
| Judge calibration | <sens, spec, κ against n human labels — or "n/a"> |

## Results

| Variant | Pass | 95% CI (over queries) | ICC | Effective n |
|---|---:|---|---:|---:|
| baseline (no skill) | k/n | | | |
| old | k/n | | | |
| new | k/n | | | |

**Paired difference (new − old):** <+x points> (95% CI <lo> to <hi>), <a> queries improved, <b> got worse.

For trigger evals:

| Variant | Recall (should-trigger) | False-trigger rate (should-not) | Unreliable queries (rate 0.3–0.7) |
|---|---|---|---:|
| old | | | |
| new | | | |

## Conclusion

<One of: "new is better", "cannot tell apart at this sample size", "no regression beyond tolerance", "new is worse". Say which result supports it.>

## Caveats

- <best-of-k selection? small query set? judge changed? skill set differs from users'?>

<!-- Generated numbers: python3 tools/skillstats.py analyze <results.jsonl> -->
