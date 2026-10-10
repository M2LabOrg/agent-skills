#!/usr/bin/env python3
"""Generate the SYNTHETIC example in results.jsonl.

Twenty should-trigger queries, five runs each, under two description
versions. Each query has its own latent trigger rate (some phrasings are
easy, some hard), which is what makes runs within a query correlated.
The new description helps most queries a little and hurts a few.

    python3 make_example.py > results.jsonl
    python3 ../scripts/skillstats.py analyze results.jsonl
"""

import json
import random

rng = random.Random(2026)
QUERIES, RUNS = 20, 5

for q in range(1, QUERIES + 1):
    old_rate = rng.betavariate(0.9, 0.6)  # mean 0.6; many queries near 0 or 1
    new_rate = min(1.0, max(0.0, old_rate + rng.gauss(0.08, 0.12)))
    for variant, rate in (("old", old_rate), ("new", new_rate)):
        for _ in range(RUNS):
            print(json.dumps({"query": f"q{q:02d}", "variant": variant, "pass": rng.random() < rate}))
