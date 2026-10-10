# <Topic> — <One-line conclusion>

**Date:** <YYYY-MM-DD>  **Author:** <name>  **Branch / commit:** <ref>
**Reproduce:** `<exact command>`

## TL;DR

<!-- 2–4 sentences. The verdict first. -->

## Question

<!-- What we tried to find out, and why it matters. -->

## Method

- **Inputs:** <data sources, sample size, how they were selected>
- **Variants:** <what was compared; runs per variant>
- **Environment:** <hardware, library / model / service versions>
- **Metrics:** <how success was measured; pass criteria decided in advance>

## Results

| Variant | Metric A | Metric B | Pass rate (95% CI) |
|---|---:|---:|---|
| baseline | | | k/n (lo–hi%) |
| candidate | | | |

<!-- Charts in plots/. Show the data, not adjectives. -->

## Findings

- <Specific finding, tied to a number above>

## Verdict

<!-- Recommend / Do not recommend / Inconclusive, with the reasoning, tied back to the Question. -->

## Caveats and threats to validity

<!-- Sample size, confounders, what could not be tested, where this may not generalize. -->

## Next steps

- [ ] <follow-up>

## Reproducing

```bash
<commands that regenerate data/ and plots/ from a fresh checkout>
```
