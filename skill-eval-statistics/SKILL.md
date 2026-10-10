---
name: skill-eval-statistics
description: Applies sound statistics when designing, running, or reporting evaluations of agent skills — trigger rates, outcome pass rates, description tuning, and before/after comparisons. Use when asked to evaluate, benchmark, or A/B test a skill or its description, decide how many eval queries or runs are needed, judge whether a change "improved" a skill, or write up eval results. Do not use for general model benchmarking unrelated to skills, or for writing the skill content itself.
metadata:
  category: evaluation
---

# Skill Eval Statistics

Apply these rules whenever a skill eval is planned, run, or reported. The full reasoning, with worked numbers, is in [references/guide.md](references/guide.md). Read the relevant section when a rule below needs justifying or adapting.

Run [scripts/skillstats.py](scripts/skillstats.py) (Python 3.8+, standard library only) for every calculation instead of estimating by hand. Run `python3 scripts/skillstats.py --help` for the full command list.

## Before running

1. State the **primary metric**: trigger recall, false-trigger rate, or outcome lift over a no-skill baseline. Ask the user if it is unclear.
2. State the **smallest improvement worth detecting**, then check the eval can detect it: `python3 scripts/skillstats.py compare <baseline> <target>`. If it cannot, say so, and either enlarge the eval or label it a smoke test.
3. Spend budget on **more queries before more runs**. About 3 runs per query is enough to expose nondeterminism.
4. For description tuning, split queries into **train / validation / test**. Keep the test set untouched until the final score.

## While analyzing

1. Treat the **query** as the unit of analysis. Never treat repeated runs of one query as independent.
2. Save raw results as JSONL, one run per line: `{"query": "q01", "variant": "old", "pass": true}`. Then run `python3 scripts/skillstats.py analyze <file>` for query-level bootstrap intervals, the ICC, effective sample size, and the paired difference.
3. Compare versions **on the same queries** (paired). Report how many queries improved and how many got worse.
4. For trigger evals, report **precision and recall separately**, and report per-query trigger rates, not only pass/fail against a threshold.
5. If an LLM judge graded outputs, report its agreement with human labels. When its sensitivity and specificity are known, correct the rate with `python3 scripts/skillstats.py judge <rate> --sens <s> --spec <p>`.

## When reporting

- Report every rate as `k/n` with a 95% interval. Never a bare percentage.
- If the interval for a difference includes zero, say the data **cannot tell the versions apart**. Do not call it an improvement, a trend, or "directionally positive".
- "Not significant" is not "no regression". Claim no regression only if the lower bound of `new − old` stays above a tolerance agreed in advance.
- After zero failures in *n*, state that the failure rate could still be up to about `3/n` (`python3 scripts/skillstats.py zero <n>`).
- If the score is the best of several variants on the same validation set, say it is optimistic.
- State queries, runs per query, agent, model, and date. Use [assets/eval-report.md](assets/eval-report.md) for a full write-up.

## Example

Not: "Trigger rate improved from 9/20 to 14/20."

Instead: "14/20 vs 9/20: difference +25 points (95% CI −5 to +50). This sample cannot tell the versions apart; about 60 queries per version would be needed to confirm a lift of this size."

Check claims like the second one with `compare` before writing them.
