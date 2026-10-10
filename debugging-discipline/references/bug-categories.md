# Bug categories and unsticking techniques

## Categories

| Category | Signature | Strategy |
|---|---|---|
| **Logic** | Wrong output for valid input | Trace where state diverges from intent; minimal upstream fix |
| **State** | Works once, fails on retry or under concurrency | Inspect mutation, caching, shared state, initialization order |
| **Boundary** | Empty input, maximum length, Unicode, time zones, off-by-one | Add edge-case regression tests for each boundary |
| **Integration** | Two components disagree | Pin the contract first (schema, types, units), then decide which side is wrong |
| **Environment** | Works locally, fails when deployed | Diff environment variables, secrets, permissions, network, dependency versions |
| **Flaky** | Intermittent | Find the race, ordering, or timing dependency before "fixing" anything |

A flaky test is a deterministic bug that is not understood yet. Do not retry it away.

## When stuck

- **Bisect.** Use `git bisect`, or binary-search manually through commits, configuration, or input.
  ```bash
  git bisect start
  git bisect bad                 # current commit is broken
  git bisect good <known-good>   # last commit known to work
  git bisect run <test-command>  # let git find the first bad commit
  ```
- **Reduce.** Strip the failing case down until removing one more thing makes it pass. The last thing removed is usually the clue.
- **Rubber-duck.** Write the symptom and the current hypothesis as prose. For each suspect, write why it is or isn't the cause.
- **Diff working and broken.** Compare a working run and a failing run side by side: inputs, configuration, logs, versions.
- **Take a break.** Many root causes surface after stepping away.
