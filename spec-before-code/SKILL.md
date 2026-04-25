---
name: spec-before-code
description: Michel's lightweight design-doc workflow — write a markdown spec under `specs/` before implementing any non-trivial feature, including a threat model. Use whenever the user proposes a new feature, a non-trivial refactor, a new service / endpoint / data flow, an integration with an external system, or anything touching auth, secrets, PII, or multi-tenant data. Triggers on phrases like "let's add", "design a", "build a new", "I want to support", "spec this out", "RFC", "design doc", and on any change estimated at >1 day of work or that has security/privacy implications.
---

# Spec Before Code

For non-trivial work, draft a short markdown spec **before** writing code. Specs prevent over-engineering, surface unknowns, and create a record of *why* a design was chosen.

## When to Write a Spec

Write one when **any** of these is true:

- Estimated effort > 1 day of work
- Touches authentication, authorization, secrets, PII, or multi-tenant boundaries
- Adds a new service, queue, table, bucket, endpoint, or external integration
- Changes a public API contract (request/response shape, status codes)
- Affects more than one container / service / repo
- The user explicitly asks for a "design doc", "RFC", or "spec"

For everything else (bug fixes, small features, refactors), skip the spec and go straight to implementation — but capture the decision in the PR description.

## Folder Layout

```
specs/
├── README.md                    # Index of specs (one-line summary each)
├── 0001-feature-name.md         # Numbered, kebab-case
├── 0002-another-feature.md
└── archive/                     # Specs whose features have shipped (optional)
```

Number specs sequentially. Don't reuse numbers.

## Spec Template (Use Exactly)

```markdown
# <NNNN> — <Feature Name>

**Status:** Draft | In review | Accepted | Implemented | Superseded by #NNNN | Rejected
**Author:** Michel  **Date:** <YYYY-MM-DD>  **Reviewers:** <names>
**Related:** PBI #<id>, Issue #<id>, Spec #<NNNN>

## Problem
<What problem does this solve? Who has it? Why now? Concrete examples.>

## Goals
- <Specific, measurable outcome>
- ...

## Non-Goals
- <Explicitly out of scope. Just as important as Goals.>
- ...

## Constraints
- <Hard constraints: deadlines, budgets, compliance, existing systems we must not break>

## Proposed Design
<The "how". Diagrams (Mermaid — see mermaid-diagrams skill). API shapes. Data model. Sequence of operations. Be concrete.>

### Architecture
```mermaid
<Mermaid diagram of components and data flow>
```

### Data Model
<Tables, fields, relationships. New columns? New indexes? Migration?>

### API / Interface
<Request/response shapes. Error codes. Backward compatibility.>

### Failure Modes
<What happens when each dependency fails? Retries? Timeouts? Idempotency?>

## Threat Model
<Required for every spec. See section below for the framework.>

## Alternatives Considered
1. **<Alt A>** — <one-paragraph description>. Rejected because <reason>.
2. **<Alt B>** — ... Rejected because ...

## Migration / Rollout
<How does this ship? Feature flag? Phased? Backfill needed? Rollback plan?>

## Open Questions
- [ ] <Specific question requiring an answer before implementation>
- ...

## Test Plan
<What unit / integration / eval / manual tests demonstrate this works? Tie to the eval-development skill if applicable.>

## Success Metrics
<How will we know it worked, post-launch? Concrete numbers / signals.>
```

## Threat Model — Always Include

Every spec includes a threat model section, even for "boring" features. Use the **STRIDE** framework, or the lighter "assets / actors / threats / mitigations" form below.

```markdown
## Threat Model

### Assets
- <What is being protected? Data, credentials, availability, integrity of X.>

### Actors / Trust Boundaries
- <Who interacts with the system? Authenticated users, unauthenticated public, internal services, third-party APIs?>
- <Where do trust boundaries lie? Mark them on the architecture diagram.>

### Threats (STRIDE)
| Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| Spoofing | <e.g. forged JWT> | Low/Med/High | Low/Med/High | <e.g. JWKS validation + audience check> |
| Tampering | <data modified in transit / at rest> | ... | ... | ... |
| Repudiation | <action attributed wrongly> | ... | ... | ... |
| Information disclosure | <PII leak, log leak, error leak> | ... | ... | ... |
| Denial of service | <unbounded input, expensive op> | ... | ... | ... |
| Elevation of privilege | <user gains admin via X> | ... | ... | ... |

### Residual Risks
<Anything we accept rather than mitigate. Why is it acceptable?>

### Secrets & PII
- <What secrets does this need? How are they stored / rotated?>
- <What PII flows through? Where is it logged? Where is it persisted? Retention?>
```

For features with no realistic security surface, you can shorten this to one paragraph — but always include it. The act of writing it forces the question.

## Discipline

- **Specs are short.** Aim for 1–3 pages of markdown. If it's longer, the design probably isn't crisp yet.
- **Spec the problem, not just the solution.** A spec that skips "Problem" is a recipe for solving the wrong thing.
- **Diagram with Mermaid**, not ASCII. See the `mermaid-diagrams` skill.
- **Reviewable in a PR.** Open the spec as its own small PR before the implementation PR, so the design conversation happens on the spec, not on 800 lines of code.
- **Status field is real.** Update it as the spec moves through review and implementation.
- **Archive after shipping.** Move implemented specs to `specs/archive/` (or just leave them in place with `Status: Implemented`) so the history stays.

## Anti-Patterns

- Skipping the spec because "it's faster" — and rebuilding twice.
- "Goals" that are just a feature description; missing measurable outcomes.
- Empty "Alternatives Considered" — at least one alternative was real, document it.
- Threat model = "no security implications". Almost never true; force yourself to think about it.
- Spec that becomes stale because nobody updates `Status` after implementation drifts.
