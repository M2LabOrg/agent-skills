---
name: spec-before-code
description: Lightweight design-doc workflow — write a short Markdown spec with goals, non-goals, design, alternatives, and a mandatory threat model before implementing non-trivial work. Use when the user proposes a new feature, service, endpoint, data flow, or external integration, a non-trivial refactor, anything touching auth, secrets, PII, or multi-tenant data, work estimated at more than a day, or asks for a design doc, RFC, or spec. Do not use for bug fixes, small or obvious changes, or research comparisons (use research-and-report).
metadata:
  category: design
---

# Spec Before Code

For non-trivial work, write a short spec **before** writing code. Specs prevent over-engineering, surface unknowns early, and record *why* a design was chosen.

## 1. Decide whether a spec is needed

Write one when **any** of these is true:

- More than about a day of work
- Touches authentication, authorization, secrets, PII, or tenant boundaries
- Adds a service, queue, table, bucket, endpoint, or external integration
- Changes a public API contract
- Spans more than one service or repository
- The user asks for a design doc, RFC, or spec

Otherwise skip it, and record the design decision in the pull request description.

## 2. Create the file

```
specs/
├── README.md              # Index: one line per spec
├── 0001-feature-name.md   # Numbered, kebab-case, never reused
└── archive/               # Optional: shipped specs
```

Copy [assets/spec-template.md](assets/spec-template.md) to the next free number, and add a line to `specs/README.md`.

## 3. Write it in this order

1. **Problem:** who has it, why now, with concrete examples. A spec without a problem statement solves the wrong thing.
2. **Goals and non-goals:** measurable goals. Non-goals matter just as much.
3. **Design:** architecture (as a Mermaid diagram), data model, API shapes, failure modes.
4. **Threat model:** always. Use [assets/threat-model.md](assets/threat-model.md) (STRIDE). For features with no realistic security surface, one paragraph is enough, but writing it forces the question.
5. **Alternatives considered:** at least one real alternative, and why it lost.
6. **Rollout, open questions, test plan, success metrics.**

## 4. Discipline

- **Keep it short:** one to three pages. A longer spec usually means the design isn't settled yet.
- **Review it on its own:** open the spec as a small pull request before the implementation, so the design discussion happens before 800 lines of code exist.
- **Keep `Status` current:** Draft → In review → Accepted → Implemented, or Superseded or Rejected.
- **Archive after shipping,** or leave it in place marked `Implemented`.

## Anti-patterns

- Skipping the spec "to save time", then building it twice.
- Goals that merely restate the feature, with nothing measurable.
- An empty "Alternatives considered" section.
- "No security implications" as the whole threat model.
- A stale `Status` after implementation has drifted from the design.
