---
name: debugging-discipline
description: Diagnostic-first bug-fixing methodology — reproduce precisely, find the root cause, apply the smallest upstream fix, and lock it in with a regression test. Use when the user reports a bug, a failing or flaky test, a regression, unexpected behavior, or pastes an error or stack trace, or asks for a hotfix or an investigation into why something happens. Do not use for new feature work, performance benchmarking, or open-ended research comparisons (use research-and-report).
metadata:
  category: quality
---

# Debugging Discipline

Diagnose first, change second. Apply this loop to every bug.

## 1. Establish the symptom precisely

Before writing any fix:

- Reproduce with the **smallest possible input**. If it can't be reproduced, keep diagnosing; don't fix blind.
- Capture the exact error message, stack trace, log line, or wrong output.
- Record the environment: branch, commit, runtime and dependency versions, OS, data set.
- Determine the **scope**: one input, one user, one configuration, or everything? Scope narrows the search.

## 2. State a hypothesis before reading code

Write down: *"I think this happens because X."* Then read code to confirm or refute it. This prevents editing the first plausible-looking line.

## 3. Find the root cause, not the symptom

- Trace the bug to the **earliest point** where the program's state diverges from intent.
- A fix at the symptom site usually papers over the cause and creates a second bug. Prefer the **minimal upstream fix**.
- Similar symptoms can have different roots. Confirm the location before changing anything.

Classify the bug to pick a strategy. See [references/bug-categories.md](references/bug-categories.md) for the category table and for techniques to use when stuck (bisecting, reducing, rubber-ducking).

## 4. Make the smallest fix that works

- A one-line change in the right place beats a refactor.
- Leave adjacent clean-ups for a follow-up commit.
- If the fix is complicated, suspect that the root cause has not been found yet.

## 5. Add a regression test

- The test must **fail before the fix and pass after**. Verify both directions.
- Keep it minimal: it documents the bug, not the whole feature.

## 6. Never weaken existing tests

Don't delete or relax assertions to make a test pass. If a test is genuinely wrong, explain why in the pull request before touching it.

## 7. Log state, not "got here"

- Use the project's logger at `debug` level instead of print statements.
- Log values, sizes and identifiers that show which branch ran.
- Remove or downgrade temporary logging before committing, unless it has lasting diagnostic value.

## 8. After the fix

- Confirm the regression test fails on the parent commit and passes on the fix.
- Name the **root cause** in the commit message and pull request, not just "fixed bug".
- Search for the same root cause elsewhere; fix it or file follow-ups.
- If the bug escaped review, note why (missing test, unclear spec, infrastructure gap), as a signal rather than blame.

## Anti-patterns

- Wrapping the failure in `try/except` so the error disappears.
- "It works now" without knowing why.
- Raising retry counts to mask a race condition.
- Reformatting a file while fixing a one-line bug.
- Editing the test until it passes and calling the bug fixed.
- Retrying a flaky test until it goes green: a flaky test is a deterministic bug not yet understood.
