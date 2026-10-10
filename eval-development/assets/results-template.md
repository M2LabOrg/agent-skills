# <Issue title> — Eval Results

**Issue:** <link>  **Branch:** <branch>  **Date:** <YYYY-MM-DD>
**Environment:** <local / dev>, service version <version>
**Reproduce:** `python3 evals/<eval-name>/run_eval.py`

## Summary

| Model / strategy | Pass | Neutral | Fail | Acceptable rate (95% CI) |
|---|---:|---:|---:|---|
| model-a | 10 | 0 | 0 | 10/10 (72–100%) |
| model-b | | | | |

Acceptable rate = (Pass + Neutral) / total. Intervals: `python3 <path-to>/skill-eval-statistics/scripts/skillstats.py ci <k> <n>`.

## Failure patterns

- **<model>**: <pattern> (cases <ids>)

## Fix strategy

- **Steerable models** (<list>): <context pre-pass + prompt change>
- **All models**: <deterministic post-processing function>

## Remaining failures

- <case id>: <why it still fails, and whether that is acceptable>

## Next steps

1. ...
