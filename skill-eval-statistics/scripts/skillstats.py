#!/usr/bin/env python3
"""skillstats: the arithmetic behind honest skill evals.

Zero dependencies (Python 3.8+ standard library only).

Planning
    python3 skillstats.py runs --margin 0.10      # runs for a +/-10 point interval
    python3 skillstats.py compare 0.70 0.80       # runs per arm to detect 70% -> 80%
    python3 skillstats.py deff --runs 3 --icc 0.5 # how much repeated runs are really worth

Reading results
    python3 skillstats.py ci 7 10                 # interval for 7 passes out of 10
    python3 skillstats.py zero 20                 # 20/20 passed: how bad could it still be?
    python3 skillstats.py threshold 0.6 --runs 3  # how often a 60%-reliable query passes a 2-of-3 check
    python3 skillstats.py diff 14 20 9 20         # 14/20 vs 9/20, independent samples
    python3 skillstats.py judge 0.72 --sens 0.9 --spec 0.8   # correct a pass rate for judge error
    python3 skillstats.py analyze results.jsonl   # clustered + paired analysis of raw results
"""

import argparse
import json
import math
import random
from collections import defaultdict
from statistics import NormalDist

_N = NormalDist()


# ---------------------------------------------------------------- intervals

def z(conf):
    """Two-sided critical value, e.g. 1.96 for conf=0.95."""
    return _N.inv_cdf(1 - (1 - conf) / 2)


def wilson(k, n, conf=0.95):
    """Wilson score interval for k successes in n independent trials.

    Preferred over the textbook p +/- z*sqrt(p(1-p)/n) (Wald) interval, which
    collapses to zero width at 0/n and n/n -- exactly where skill evals live.
    """
    if n == 0:
        return 0.0, 1.0
    zz = z(conf)
    p = k / n
    denom = 1 + zz**2 / n
    centre = (p + zz**2 / (2 * n)) / denom
    half = zz * math.sqrt(p * (1 - p) / n + zz**2 / (4 * n**2)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def zero_failures_bound(n, conf=0.95):
    """Exact one-sided upper bound on the failure rate after 0 failures in n.

    Approximately 3/n at 95% (the "rule of three").
    """
    return 1 - (1 - conf) ** (1 / n)


# ----------------------------------------------------------------- planning

def runs_for_margin(margin, p=0.5, conf=0.95):
    """Independent observations needed for an interval half-width <= margin.

    p=0.5 is the worst case; pass your expected rate for a tighter estimate.
    """
    return math.ceil(z(conf) ** 2 * p * (1 - p) / margin**2)


def runs_per_arm(p1, p2, alpha=0.05, power=0.8):
    """Independent observations per arm to detect p1 -> p2 (two-sided)."""
    za = z(1 - alpha)
    zb = _N.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return math.ceil((num / abs(p2 - p1)) ** 2)


def design_effect(runs, icc):
    """Variance inflation from repeating runs on the same query (Kish)."""
    return 1 + (runs - 1) * icc


def p_pass_threshold(rate, runs, threshold=0.5):
    """Probability that a query whose true trigger rate is `rate` scores
    strictly above `threshold` over `runs` independent runs."""
    k_min = math.floor(runs * threshold) + 1
    return sum(
        math.comb(runs, k) * rate**k * (1 - rate) ** (runs - k)
        for k in range(k_min, runs + 1)
    )


# --------------------------------------------------------------- comparisons

def diff_test(k1, n1, k2, n2, conf=0.95):
    """Difference in pass rates (new - old) for INDEPENDENT samples, with a
    Newcombe hybrid-score interval and a pooled two-sided z-test p-value.

    If both versions ran on the same queries, use `analyze` instead: the
    paired analysis is both more correct and more powerful.
    """
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1, conf)
    l2, u2 = wilson(k2, n2, conf)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    pval = 1.0 if se == 0 else 2 * (1 - _N.cdf(abs(d) / se))
    return d, lo, hi, pval


def judge_corrected(observed, sens, spec):
    """Rogan-Gladen estimate of the true pass rate given an imperfect grader.

    sens = P(judge says pass | truly passes), spec = P(judge says fail | truly fails),
    both measured against human labels.
    """
    youden = sens + spec - 1
    if youden <= 0:
        raise ValueError("judge is no better than chance (sens + spec <= 1)")
    return min(1.0, max(0.0, (observed + spec - 1) / youden))


# ------------------------------------------------------- clustered analysis

def icc_anova(groups):
    """One-way ANOVA estimate of the intra-class correlation for binary
    outcomes, where `groups` is a list of per-query lists of 0/1 results."""
    k = len(groups)
    sizes = [len(g) for g in groups]
    total = sum(sizes)
    if k < 2 or total <= k:
        return float("nan")
    p = sum(sum(g) for g in groups) / total
    means = [sum(g) / len(g) for g in groups]
    msb = sum(n * (m - p) ** 2 for n, m in zip(sizes, means)) / (k - 1)
    msw = sum(n * m * (1 - m) for n, m in zip(sizes, means)) / (total - k)
    n0 = (total - sum(n * n for n in sizes) / total) / (k - 1)
    denom = msb + (n0 - 1) * msw
    return 0.0 if denom == 0 else max(0.0, min(1.0, (msb - msw) / denom))


def percentile(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo, hi = math.floor(i), math.ceil(i)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def cluster_bootstrap(queries, stat, reps=10000, conf=0.95, seed=0):
    """Percentile interval for stat(sample) resampling whole queries."""
    rng = random.Random(seed)
    draws = [stat([rng.choice(queries) for _ in queries]) for _ in range(reps)]
    a = (1 - conf) / 2
    return percentile(draws, a), percentile(draws, 1 - a)


def query_mean(sample, variant):
    """Mean of per-query pass rates: every query weighs the same."""
    return sum(q[variant] for q in sample) / len(sample)


def analyze(path, conf=0.95, reps=10000, seed=0):
    """Read JSONL rows {"query": id, "variant": name, "pass": bool} and report
    per-variant rates with query-level bootstrap intervals, the ICC and
    effective sample size, and -- for two variants -- the paired difference."""
    runs = defaultdict(lambda: defaultdict(list))
    with open(path) as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                runs[row["variant"]][str(row["query"])].append(int(bool(row["pass"])))

    variants = sorted(runs)
    out = []
    for v in variants:
        groups = list(runs[v].values())
        n_runs = sum(len(g) for g in groups)
        rates = [{v: sum(g) / len(g)} for g in groups]
        rate = query_mean(rates, v)
        lo, hi = cluster_bootstrap(rates, lambda s: query_mean(s, v), reps, conf, seed)
        rho = icc_anova(groups)
        m = n_runs / len(groups)
        n_eff = n_runs / design_effect(m, rho) if rho == rho else float("nan")
        out.append(f"{v}: {pct(rate)} pass ({pct(conf)} CI {pct(lo)} to {pct(hi)}) | "
                   f"{len(groups)} queries x {m:.1f} runs = {n_runs} runs | "
                   f"ICC {rho:.2f} -> worth ~{n_eff:.0f} independent runs")

    if len(variants) == 2:
        old, new = variants if variants[0] in ("old", "baseline", "a", "before") else variants[::-1]
        shared = sorted(set(runs[old]) & set(runs[new]))
        if shared:
            pairs = [{old: sum(runs[old][q]) / len(runs[old][q]),
                      new: sum(runs[new][q]) / len(runs[new][q])} for q in shared]
            delta = lambda s: query_mean(s, new) - query_mean(s, old)  # noqa: E731
            d = delta(pairs)
            lo, hi = cluster_bootstrap(pairs, delta, reps, conf, seed)
            better = sum(p[new] > p[old] for p in pairs)
            worse = sum(p[new] < p[old] for p in pairs)
            # Exact two-sided sign test on queries that changed.
            n_changed = better + worse
            tail = sum(math.comb(n_changed, i) for i in range(min(better, worse) + 1)) / 2**n_changed \
                if n_changed else 1.0
            out.append(f"paired {new} - {old} over {len(shared)} shared queries: {d:+.0%} "
                       f"({pct(conf)} CI {lo:+.0%} to {hi:+.0%}) | "
                       f"{better} queries improved, {worse} got worse, sign test p = {min(1.0, 2 * tail):.3f}")
            if lo <= 0 <= hi:
                out.append("The interval includes zero: this data cannot tell the versions apart.")
    return out


# ---------------------------------------------------------------------- CLI

def pct(x):
    return f"{100 * x:.0f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ci", help="interval for k passes out of n independent runs")
    s.add_argument("k", type=int)
    s.add_argument("n", type=int)
    s.add_argument("--conf", type=float, default=0.95)

    s = sub.add_parser("zero", help="upper bound on failure rate after n passes, 0 failures")
    s.add_argument("n", type=int)
    s.add_argument("--conf", type=float, default=0.95)

    s = sub.add_parser("runs", help="observations needed for a target margin")
    s.add_argument("--margin", type=float, required=True, help="e.g. 0.10 for +/-10 points")
    s.add_argument("--p", type=float, default=0.5, help="expected rate (0.5 = worst case)")
    s.add_argument("--conf", type=float, default=0.95)

    s = sub.add_parser("compare", help="observations per arm to detect a lift")
    s.add_argument("p1", type=float, help="baseline rate")
    s.add_argument("p2", type=float, help="rate you hope to reach")
    s.add_argument("--alpha", type=float, default=0.05)
    s.add_argument("--power", type=float, default=0.8)

    s = sub.add_parser("deff", help="what repeated runs per query are really worth")
    s.add_argument("--runs", type=int, required=True, help="runs per query")
    s.add_argument("--icc", type=float, required=True, help="intra-class correlation, 0..1")
    s.add_argument("--queries", type=int, default=20)

    s = sub.add_parser("threshold", help="chance a query passes a k-of-n trigger check")
    s.add_argument("rate", type=float, help="true per-run trigger rate")
    s.add_argument("--runs", type=int, default=3)
    s.add_argument("--threshold", type=float, default=0.5)

    s = sub.add_parser("diff", help="compare two pass rates from independent samples")
    s.add_argument("k_new", type=int)
    s.add_argument("n_new", type=int)
    s.add_argument("k_old", type=int)
    s.add_argument("n_old", type=int)
    s.add_argument("--conf", type=float, default=0.95)

    s = sub.add_parser("judge", help="correct an observed pass rate for grader error")
    s.add_argument("observed", type=float)
    s.add_argument("--sens", type=float, required=True, help="P(judge pass | true pass)")
    s.add_argument("--spec", type=float, required=True, help="P(judge fail | true fail)")

    s = sub.add_parser("analyze", help="clustered and paired analysis of a results JSONL file")
    s.add_argument("path")
    s.add_argument("--conf", type=float, default=0.95)
    s.add_argument("--reps", type=int, default=10000)
    s.add_argument("--seed", type=int, default=0)

    a = ap.parse_args()
    if a.cmd == "ci":
        lo, hi = wilson(a.k, a.n, a.conf)
        print(f"{a.k}/{a.n} = {pct(a.k / a.n)}  ({pct(a.conf)} interval: {pct(lo)} to {pct(hi)})")
    elif a.cmd == "zero":
        print(f"0 failures in {a.n}: the true failure rate could still be up to "
              f"{100 * zero_failures_bound(a.n, a.conf):.1f}% ({pct(a.conf)} one-sided)")
    elif a.cmd == "runs":
        print(f"{runs_for_margin(a.margin, a.p, a.conf)} independent observations "
              f"for +/-{pct(a.margin)} at {pct(a.conf)} confidence")
    elif a.cmd == "compare":
        n = runs_per_arm(a.p1, a.p2, a.alpha, a.power)
        print(f"{n} independent observations per arm ({2 * n} total) to detect "
              f"{pct(a.p1)} -> {pct(a.p2)} (alpha={a.alpha}, power={a.power})")
    elif a.cmd == "deff":
        d = design_effect(a.runs, a.icc)
        total = a.runs * a.queries
        print(f"{a.queries} queries x {a.runs} runs = {total} runs, design effect {d:.2f}: "
              f"worth ~{total / d:.0f} independent observations "
              f"(adding runs can never take you past {a.queries / a.icc:.0f})" if a.icc > 0 else
              f"{a.queries} queries x {a.runs} runs = {total} runs, all independent (ICC 0)")
    elif a.cmd == "threshold":
        p = p_pass_threshold(a.rate, a.runs, a.threshold)
        print(f"A query that triggers {pct(a.rate)} of the time passes a {a.runs}-run, "
              f">{a.threshold} check {pct(p)} of the time")
    elif a.cmd == "diff":
        d, lo, hi, pval = diff_test(a.k_new, a.n_new, a.k_old, a.n_old, a.conf)
        print(f"new {a.k_new}/{a.n_new} vs old {a.k_old}/{a.n_old}: difference {d:+.0%} "
              f"({pct(a.conf)} interval {lo:+.0%} to {hi:+.0%}), p = {pval:.3f}")
        if lo <= 0 <= hi:
            print("The interval includes zero: this data cannot tell the versions apart.")
    elif a.cmd == "judge":
        t = judge_corrected(a.observed, a.sens, a.spec)
        print(f"Judge reports {pct(a.observed)}; corrected for sens={a.sens}, spec={a.spec}: {pct(t)}")
    elif a.cmd == "analyze":
        print("\n".join(analyze(a.path, a.conf, a.reps, a.seed)))


if __name__ == "__main__":
    main()
