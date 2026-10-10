# Agent Skills, Measured


**A statistician's guide to evaluating agent skills: how many runs you need, what a pass rate actually tells you, and when "it got better" is real.**

Tool-agnostic. Works for Claude Code, Codex, Cursor, Gemini CLI, or any agent that loads `SKILL.md` files. Part of the [`skill-eval-statistics`](../SKILL.md) skill, which bundles the zero-dependency calculator ([`scripts/skillstats.py`](../scripts/skillstats.py)) used for every number below. Commands assume you run them from the skill folder.

---

You rewrote a skill description. The trigger rate went from **9/20 to 14/20**. Ship it?

```console
$ python3 scripts/skillstats.py diff 14 20 9 20
new 14/20 vs old 9/20: difference +25% (95% interval -5% to +50%), p = 0.110
The interval includes zero: this data cannot tell the versions apart.
```

A 25-point jump, and you still don't know whether the new description is better. Most skill-eval advice tells you *what* to run. This guide tells you *what the results mean*.

## Five numbers worth knowing

| | |
|---|---|
| **3 out of 3** | Passing 3 of 3 runs is consistent with a true pass rate anywhere from **44% to 100%**. |
| **65%** | A query that triggers only 60% of the time still passes a "2 of 3 runs" check **65%** of the time. |
| **294** | Independent runs *per version* needed to reliably detect an improvement from 70% to 80%. |
| **40** | 20 queries × any number of runs can never be worth more than **40** independent observations when runs within a query are moderately correlated (ICC 0.5). |
| **91%** | Score five equally good descriptions (each truly 75%) on 8 validation queries and keep the best: its expected score is **91%**. |

Every number above comes from [`skillstats.py`](../scripts/skillstats.py) and is explained below.

## Contents

1. [Decide what you are measuring](#1-decide-what-you-are-measuring)
2. [The unit is the query, not the run](#2-the-unit-is-the-query-not-the-run)
3. [How many queries, how many runs](#3-how-many-queries-how-many-runs)
4. [Reading a single pass rate](#4-reading-a-single-pass-rate)
5. [Trigger evals](#5-trigger-evals)
6. [Comparing two versions](#6-comparing-two-versions)
7. [Tuning without fooling yourself](#7-tuning-without-fooling-yourself)
8. [LLM-as-judge is a measuring instrument](#8-llm-as-judge-is-a-measuring-instrument)
9. [Reporting](#9-reporting)
10. [Cheatsheet](#cheatsheet)
11. [The calculator](#the-calculator)

---

## 1. Decide what you are measuring

A skill can fail in three separate places. Measure them separately, because each one needs a different fix.

| Question | Metric | Failure means |
|---|---|---|
| Does it load when it should? | **Trigger recall**: should-trigger queries that loaded the skill | Description too narrow |
| Does it stay out of the way? | **Trigger precision / false-trigger rate** on should-*not*-trigger queries | Description too broad |
| Does it help once loaded? | **Outcome lift**: task success *with* the skill minus success *without* it | Instructions don't help, or hurt |

Two rules before you collect any data:

- **Pick one primary metric in advance.** If you measure ten things and report the one that moved, you have found noise. Secondary metrics are fine; label them as such.
- **Always measure the no-skill baseline.** A skill that scores 85% is useless if the agent scores 85% without it. Outcome lift, not outcome level, is what the skill is responsible for.

## 2. The unit is the query, not the run

This is the single most common statistical mistake in skill evals.

Agents are nondeterministic, so we run each query several times. But runs of the *same query* are not independent: an easy phrasing tends to pass every time, a hard one tends to fail every time. Twenty queries × 10 runs is not 200 independent observations.

The **intra-class correlation (ICC)** measures how alike runs within a query are, from 0 (every run is a fresh coin flip) to 1 (each query always gives the same answer). The **design effect** tells you how much information you lose:

```text
design effect = 1 + (runs per query − 1) × ICC
effective sample size = total runs ÷ design effect
```

```console
$ python3 scripts/skillstats.py deff --queries 20 --runs 3 --icc 0.5
20 queries x 3 runs = 60 runs, design effect 2.00: worth ~30 independent observations (adding runs can never take you past 40)

$ python3 scripts/skillstats.py deff --queries 20 --runs 10 --icc 0.5
20 queries x 10 runs = 200 runs, design effect 5.50: worth ~36 independent observations (adding runs can never take you past 40)
```

Tripling the runs from 3 to 10 bought you six effective observations. **The ceiling is `queries ÷ ICC`, and only more queries raise it.** Trigger behaviour is often strongly query-dependent (some phrasings almost always trigger, others almost never), which means a high ICC, so the ceiling arrives quickly. Estimate the ICC from your own runs (`analyze` reports it) rather than assuming a value.

What to do about it:

- **Report per-query rates, then average them.** Each query gets equal weight, whatever its run count.
- **Compute intervals by resampling queries** (a cluster bootstrap), never by treating runs as independent. `skillstats.py analyze` does this for you.
- **Spend your budget on queries first.** 3 runs per query is usually enough to see nondeterminism; past that, write more queries.

> With fewer than ~15 queries, bootstrap intervals are too narrow. Treat them as optimistic, or collect more queries.

## 3. How many queries, how many runs

Interval width for a single pass rate, assuming independent observations (worst case, rate near 50%):

| Target precision (95%) | Observations needed |
|---|---:|
| ±20 points | 25 |
| ±15 points | 43 |
| ±10 points | 97 |
| ±5 points | 385 |
| ±3 points | 1,068 |

Observations *per version* to detect an improvement (80% power, 5% two-sided test, independent samples):

| From → to | Per version | Total |
|---|---:|---:|
| 50% → 75% | 58 | 116 |
| 80% → 90% | 199 | 398 |
| 70% → 80% | 294 | 588 |
| 50% → 60% | 388 | 776 |
| 90% → 95% | 435 | 870 |
| 85% → 90% | 686 | 1,372 |

"Observations" here means *effective* observations (section 2). With correlated runs, read these as a lower bound on the number of **queries** you need. The good news is in section 6: a paired design needs far fewer.

The practical reading of these tables:

- **Small evals detect big effects only.** 20 queries can confirm that a skill went from broken to working. It cannot confirm a 5-point polish.
- **Before you run, write down the smallest improvement you care about.** If your eval cannot detect it, either make the eval bigger or accept that you are doing a smoke test, and call it that.

## 4. Reading a single pass rate

Never report a bare percentage. Report `k/n` and an interval.

| Observed | 95% interval (Wilson) |
|---|---|
| 3/3 | 44% – 100% |
| 10/10 | 72% – 100% |
| 9/10 | 60% – 98% |
| 18/20 | 70% – 97% |
| 45/50 | 79% – 96% |
| 90/100 | 83% – 94% |

Use the **Wilson** interval, not the textbook `p ± 1.96·√(p(1−p)/n)`. The textbook (Wald) interval gives `[100%, 100%]` for 10/10, which is nonsense, and skill evals live near 0% and 100%.

**Zero failures is not zero risk.** After *n* passes and no failures, the failure rate could still be as high as about `3/n` (the *rule of three*):

```console
$ python3 scripts/skillstats.py zero 20
0 failures in 20: the true failure rate could still be up to 13.9% (95% one-sided)
```

## 5. Trigger evals

The [Agent Skills guide](https://agentskills.io/skill-creation/optimizing-descriptions) gives a sensible starting recipe: about 20 realistic queries, half should-trigger and half near-miss should-not-trigger, each run 3 times, and a query "passes" if its trigger rate is above 0.5. Here is what that recipe can and can't tell you.

**A threshold check blurs everything near the threshold.** It turns a rate into pass/fail, and queries near 0.5 flip at random:

| True trigger rate | Passes "> 0.5 over 3 runs" |
|---:|---:|
| 30% | 22% of the time |
| 50% | 50% |
| 60% | 65% |
| 70% | 78% |
| 90% | 97% |

More runs don't fix this for queries close to the line: at 10 runs, a 60% query passes 63% of the time. **Report the trigger rate, not just pass/fail**, and treat queries between roughly 0.3 and 0.7 as "unreliable" in their own category. They are the most informative ones for improving the description.

**Report precision and recall separately.** One "pass rate" across positive and negative queries hides the trade-off: a description can get more aggressive, gain recall, lose precision, and keep the same total.

**Negatives must be near-misses.** "What's the weather?" tests nothing. Negatives that share vocabulary with the skill but need something else are the only ones that measure precision.

**Watch for skills competing with each other.** If several installed skills cover nearby ground, trigger rates depend on the *set* of skills installed, not on your description alone. Evaluate with the skill set your users actually have.

## 6. Comparing two versions

**Pair your comparisons.** Run both versions on the *same* queries and analyze per-query differences. Query difficulty cancels out, which is usually the biggest source of variance, so a paired design detects the same effect with far fewer queries than two independent samples.

```console
$ python3 scripts/skillstats.py analyze examples/results.jsonl
new: 57% pass (95% CI 40% to 73%) | 20 queries x 5.0 runs = 100 runs | ICC 0.49 -> worth ~34 independent runs
old: 54% pass (95% CI 40% to 68%) | 20 queries x 5.0 runs = 100 runs | ICC 0.31 -> worth ~45 independent runs
paired new - old over 20 shared queries: +3% (95% CI -9% to +15%) | 8 queries improved, 8 got worse, sign test p = 1.000
The interval includes zero: this data cannot tell the versions apart.
```

(This [example data](../examples/) is synthetic and reproducible.) A hundred runs per version, and the honest conclusion is "no detectable difference". Notice the per-query count: **8 queries improved and 8 got worse.** That is often the most telling line. A description change that helps some phrasings and hurts others is a trade-off, not an improvement.

**"No significant difference" does not mean "no regression".** Absence of evidence is not evidence of absence, especially with small evals. For regression checks, decide on a tolerance in advance (say, 5 points) and pass only if the **lower end** of the interval for `new − old` is above `−5`. That is an equivalence (non-inferiority) test, and it can actually fail.

**Fix the sample size before you look.** Running more queries until the result looks good, or stopping as soon as it does, inflates false positives far beyond the nominal 5%. If you must look early, decide when you'll look before you start, and require a stricter threshold at each look.

**Many models, many metrics: correct for it.** Testing a change across 7 models and 4 metrics gives 28 chances for a fluke. Either name a primary comparison in advance or adjust (Holm's method is simple and always at least as powerful as Bonferroni).

## 7. Tuning without fooling yourself

Description tuning is model selection. The usual machine-learning hygiene applies, and small evals make it more pressing.

The Agent Skills guide recommends a 60/40 train/validation split and choosing the best of several iterations by validation score. That keeps you from tuning directly on the queries you score on, which is good. But with 20 queries, validation is only 8 queries, and **picking the best of several noisy scores is biased upward**:

> Five description variants, all truly passing 75% of queries, each scored on 8 validation queries. The best observed score is **91% on average**, and **41%** of the time at least one variant scores a perfect 8/8.

This is the *winner's curse*. The fix:

- **Three-way split.** Train (find failures), validation (choose between variants), **test** (score the winner once). Report the test score.
- **Touch the test set once.** If you go back and tune after seeing the test score, it has become a validation set.
- **If you can't afford a test set,** say that the reported score is the best of *k* and is optimistic.

## 8. LLM-as-judge is a measuring instrument

When an LLM grades outcomes, your pass rate is the judge's verdict, not the truth. Calibrate the judge like any instrument:

1. Hand-label 50–100 outputs, including hard cases.
2. Measure the judge's **sensitivity** (passes it confirms) and **specificity** (failures it catches) against those labels. Also report Cohen's κ for agreement beyond chance.
3. Correct the observed pass rate (Rogan–Gladen):

```console
$ python3 scripts/skillstats.py judge 0.80 --sens 0.95 --spec 0.5
Judge reports 80%; corrected for sens=0.95, spec=0.5: 67%
```

A lenient judge (catching only half of real failures) turned 67% into 80%. Lenient judges are common.

Also:

- **Prefer deterministic graders when you can.** Checking that a file exists, a test passes, or a regex matches has no measurement error. Use rubric or LLM judges only for what code can't check.
- **Keep the judge fixed** (model, prompt and temperature) for every version you compare. A judge upgrade halfway through an eval changes the measurement, not the skill.
- **Re-check calibration** when the judge model changes.

## 9. Reporting

A result someone else can trust contains:

- [ ] `k/n` per version, with 95% intervals computed over **queries**
- [ ] Number of queries, runs per query, and the ICC or effective sample size
- [ ] The paired difference with its interval, plus how many queries improved and how many got worse
- [ ] The no-skill baseline (for outcome evals)
- [ ] Precision and recall separately (for trigger evals)
- [ ] Which split the number comes from, and whether it is a best-of-*k*
- [ ] Judge calibration, if an LLM graded the outputs
- [ ] Agent, model and version, date, and skill set installed

A fill-in version is in [`assets/eval-report.md`](../assets/eval-report.md).

---

## Cheatsheet

| Situation | Do this |
|---|---|
| Planning an eval | Write down the smallest improvement you care about. Check you can detect it (`compare`). |
| Budget to spend | More queries before more runs. ~3 runs per query is usually enough. |
| Any pass rate | Report `k/n` and a Wilson interval (`ci`). Never a bare percentage. |
| All runs passed | Failure rate could still be ~`3/n` (`zero`). |
| Repeated runs per query | Analyze by query; resample queries, not runs (`analyze`). |
| Old vs new version | Same queries for both; paired analysis; count queries improved vs worse. |
| "No regression" | Use an equivalence margin, not "not significant". |
| Tuning a description | Train / validation / test. Report the test score, and use the test set once. |
| LLM judge | Calibrate on human labels, then correct the rate (`judge`). |
| Many models or metrics | One primary comparison, or adjust with Holm. |

## The calculator

[`scripts/skillstats.py`](../scripts/skillstats.py) is a single file using only the Python standard library. Copy it anywhere.

```bash
python3 scripts/skillstats.py ci 18 20                     # interval for a pass rate
python3 scripts/skillstats.py zero 50                      # bound after zero failures
python3 scripts/skillstats.py runs --margin 0.10           # sample size for a target precision
python3 scripts/skillstats.py compare 0.70 0.80            # sample size to detect a lift
python3 scripts/skillstats.py deff --queries 20 --runs 5 --icc 0.4
python3 scripts/skillstats.py threshold 0.6 --runs 3       # how often a k-of-n check passes
python3 scripts/skillstats.py diff 14 20 9 20              # two independent pass rates
python3 scripts/skillstats.py judge 0.8 --sens 0.95 --spec 0.5
python3 scripts/skillstats.py analyze results.jsonl        # clustered + paired, from raw results
```

`analyze` reads one JSON object per line, whatever eval tool produced the runs:

```json
{"query": "q01", "variant": "old", "pass": true}
{"query": "q01", "variant": "new", "pass": false}
```

Use `old`/`new` (or `baseline`/anything) as variant names to get the paired comparison.

## Further reading

- Miller, E. (2024). [*Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations*](https://arxiv.org/abs/2411.00640). The same ideas (clustered standard errors, paired differences, power analysis) applied to model benchmarks.
- [Agent Skills: Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions), the recipe that section 5 builds on.
- [mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices) covers how to *write* skills well. This guide covers how to *measure* them.
- [anthropics/skills: skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) automates trigger evals and description tuning.
- Wilson (1927); Newcombe (1998) for intervals on proportions and their differences. Kish (1965) for design effects. Rogan & Gladen (1978) for correcting rates measured with an imperfect test. Hanley & Lippman-Hand (1983) for the rule of three.
