---
name: debugging-discipline
description: Michel's bug-fixing methodology — root cause first, minimal upstream fix, no over-engineering. Use whenever the user reports a bug, asks to investigate a failure, says something is broken / not working / unexpected, asks why a test is failing, requests a hotfix, or describes flaky behavior. Triggers on phrases like "this is broken", "fix the bug", "investigate", "why does X happen", "regression", "flaky", "intermittent", "the test fails", and on any stack trace / error output the user pastes.
---

# Debugging Discipline

Bug-fixing should be **diagnostic-first, change-second**. Apply this loop to every bug.

## 1. Establish the Symptom Precisely

Before writing a single line of fix:

- Reproduce locally with the **smallest possible input**. If you can't reproduce, do not fix — diagnose more.
- Capture the exact error message, stack trace, log line, or wrong output.
- Note environment: branch, commit, container version, OS, dataset.
- Determine **scope**: does it affect one input, one user, one model, all models, all environments? Scope narrows the search space dramatically.

## 2. Form a Hypothesis Before Reading Code

State out loud (or in a comment): *"I think this happens because <X>."* Then read code to confirm or refute. This avoids the trap of editing the first plausible-looking line.

## 3. Find the Root Cause, Not a Symptom

- Trace the bug to the **earliest point** at which the program's state diverges from intent.
- A fix at the symptom site (later in the call chain) almost always papers over the real issue and creates a second one. Prefer **minimal upstream fixes**.
- For specialized codebases (translation pipelines, GPU containers, infra), **verify the bug location carefully** — a similar-looking symptom can have multiple roots.

## 4. Prefer the Smallest Fix That Works

- A one-line change at the right place beats a refactor.
- Resist the urge to clean up adjacent code in the same commit. File a follow-up.
- If the fix is complex, that is a signal you may not have found the root cause yet — re-examine.

## 5. Always Add a Regression Test

- A bug without a regression test will return.
- The test should **fail before the fix** and pass after. Verify both directions.
- Keep the test minimal; it documents the bug, not the entire feature.

## 6. Never Weaken Existing Tests

- Don't delete or relax assertions to make a failing test pass. That's hiding the bug.
- If a test is genuinely wrong, prove it with reasoning in the PR description before touching it.

## 7. Logging > Print Statements

When diagnosing:

- Use the project's logger (Pino / Python logging / etc.) at `debug` or `info` level, not `print`.
- Log **state**, not just "got here". Log variable values, sizes, ids — anything that disambiguates which branch ran.
- Remove or downgrade temporary logs before commit unless they have lasting diagnostic value.

## 8. Distinguish Bug Categories

| Category | Signature | Strategy |
|---|---|---|
| **Logic bug** | Wrong output for valid input | Trace state divergence; minimal upstream fix |
| **State bug** | Works once, fails on retry / concurrent | Inspect mutation, caching, shared state |
| **Boundary bug** | Empty input, max length, unicode, timezone | Add input-edge regression tests |
| **Integration bug** | Component A vs B disagree | Pin the contract first (schema, types) |
| **Environment bug** | Works locally, fails deployed | Diff env vars, secrets, IAM, network |
| **Flaky** | Intermittent | Find the race / ordering / timing dependency before "fixing" |

A "flaky" test is a deterministic bug you haven't understood yet. **Do not retry-loop it away.**

## 9. When You're Stuck

- **Bisect**. `git bisect` or manual binary search through commits / config / inputs.
- **Reduce**. Strip the failing case down until removing one more thing makes it pass.
- **Rubber-duck**. Write the symptom and your current hypothesis as prose; explain why each suspect is or isn't the cause.
- **Sleep on it.** Genuinely. Many root causes surface after a break.

## 10. After the Fix

- Confirm the regression test fails on the parent commit and passes on yours.
- Note the **root cause** in the commit message and PR description — not just "fixed bug".
- If the same root cause could affect other places, search for them and either fix or file follow-ups.
- If the bug escaped review, briefly note **why** in the PR (missing test? unclear spec? infrastructure gap?). Treat it as a signal, not a blame.

## Anti-Patterns

- Adding a `try / except` to make the error message disappear.
- "It works now" without understanding why.
- Bumping retries to mask a race condition.
- Reformatting the file while fixing a one-line bug (review noise).
- Editing the test until it passes, then claiming the bug is fixed.
