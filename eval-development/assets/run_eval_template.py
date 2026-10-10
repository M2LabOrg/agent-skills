#!/usr/bin/env python3
"""Eval driver template. Copy to evals/<eval-name>/run_eval.py and fill in the TODOs.

    python3 run_eval.py                       # all models, all cases
    python3 run_eval.py --models model-a --cases c01 c02
    python3 run_eval.py --jsonl results.jsonl # also write per-run rows for skillstats

cases.json format:
    [{"id": "c01", "input": "...",
      "expected": ["..."], "acceptable": ["..."], "wrong": ["..."]}]
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS = ["model-a", "model-b"]  # TODO: every model or strategy a user can select
TARGET = 1.0  # agreed acceptable rate; the script exits non-zero below it


def call_service(model, text):
    """TODO: call the service through the same interface users hit, return its output text."""
    raise NotImplementedError


def classify(output, case):
    """Deterministic classification. Order matters: a wrong marker overrides the rest."""
    low = output.lower()
    if any(m.lower() in low for m in case.get("wrong", [])):
        return "FAIL"
    if any(m.lower() in low for m in case.get("expected", [])):
        return "PASS"
    if any(m.lower() in low for m in case.get("acceptable", [])):
        return "PASS_NEUTRAL"
    return "FAIL"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="*", default=MODELS)
    ap.add_argument("--cases", nargs="*", help="case ids to run (default: all)")
    ap.add_argument("--runs", type=int, default=1, help="runs per case and model")
    ap.add_argument("--out", default=str(HERE / "report.md"))
    ap.add_argument("--jsonl", help="also write one JSON line per run")
    a = ap.parse_args()

    cases = json.loads((HERE / "cases.json").read_text())
    if a.cases:
        cases = [c for c in cases if c["id"] in set(a.cases)]

    rows, jsonl = [], []
    for model in a.models:
        for case in cases:
            for run in range(a.runs):
                output = call_service(model, case["input"])
                status = classify(output, case)
                rows.append((model, case["id"], run, status, output))
                jsonl.append({"query": case["id"], "variant": model, "pass": status != "FAIL"})

    lines = ["# Eval report", "", "| Model | Pass | Neutral | Fail | Acceptable |", "|---|---:|---:|---:|---:|"]
    worst = 1.0
    for model in a.models:
        c = Counter(r[3] for r in rows if r[0] == model)
        total = sum(c.values()) or 1
        ok = c["PASS"] + c["PASS_NEUTRAL"]
        worst = min(worst, ok / total)
        lines.append(f"| {model} | {c['PASS']} | {c['PASS_NEUTRAL']} | {c['FAIL']} | {ok}/{total} |")
    lines += ["", "## Per case", "", "| Model | Case | Run | Status | Output (start) |", "|---|---|---:|---|---|"]
    for model, cid, run, status, output in rows:
        snippet = output[:80].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {model} | {cid} | {run} | {status} | {snippet} |")

    Path(a.out).write_text("\n".join(lines) + "\n")
    if a.jsonl:
        Path(a.jsonl).write_text("".join(json.dumps(r) + "\n" for r in jsonl))
    print("\n".join(lines[:4 + len(a.models)]))
    sys.exit(0 if worst >= TARGET else 1)


if __name__ == "__main__":
    main()
