# M2Lab.io Agent Skills

[![Checks](https://github.com/M2LabOrg/agent-skills/actions/workflows/checks.yml/badge.svg)](https://github.com/M2LabOrg/agent-skills/actions/workflows/checks.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills format](https://img.shields.io/badge/format-Agent%20Skills-8A2BE2.svg)](https://agentskills.io)
[![Works with any agent](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Copilot%20%7C%20Codex%20%7C%20any-0aa.svg)](#install)
[![Last commit](https://img.shields.io/github/last-commit/M2LabOrg/agent-skills.svg)](https://github.com/M2LabOrg/agent-skills/commits/main)

> 🌐 **Browse the catalog:** <https://m2laborg.github.io/agent-skills/>

Reusable engineering methodologies, packaged as [Agent Skills](https://agentskills.io): debugging, pull-request hygiene, design specs, research reports, eval-driven development, and **statistically sound skill evaluation**. Each skill is a self-contained folder with a `SKILL.md`, plus the scripts, references and templates it needs. Nothing depends on another repository or on a particular tool.

## Skills

<!-- catalog:start -->
| Skill | Category | What it does | Bundled |
|---|---|---|---|
| [`debugging-discipline`](debugging-discipline/SKILL.md) | quality | Diagnostic-first bug-fixing methodology — reproduce precisely, find the root cause, apply the smallest upstream fix, and lock it in with a regression test. | `references/` |
| [`docs-sync-on-change`](docs-sync-on-change/SKILL.md) | docs | Keeps documentation in the same commit as the change it describes — README, docs site, wiki, CHANGELOG, embedded examples, and skill descriptions. | `assets/` |
| [`eval-development`](eval-development/SKILL.md) | evaluation | Eval-driven development for quality fixes in AI-powered services (LLM features, translation, summarization, extraction, classification) — write the eval first, cover every model or strategy users can select, classify outputs with an explicit status taxonomy, and iterate until the eval passes. | `assets/` |
| [`github-pages-generation`](github-pages-generation/SKILL.md) | docs | Creates a polished, low-maintenance GitHub Pages site for a repository — static HTML in docs/ with a data-driven card grid by default, a static-site generator only when the content needs one. | `assets/` |
| [`local-git-excludes`](local-git-excludes/SKILL.md) | git | Ignores personal or machine-local files with .git/info/exclude or a global gitignore instead of the shared, tracked .gitignore. | `scripts/` |
| [`mermaid-diagrams`](mermaid-diagrams/SKILL.md) | docs | Draws diagrams in Markdown as Mermaid code blocks instead of ASCII art — flowcharts, sequence, state, ER, and class diagrams. | `references/` |
| [`pr-and-branch-hygiene`](pr-and-branch-hygiene/SKILL.md) | git | Branch naming, atomic commits, pre-push checks, and pull-request authoring that make changes easy to review and revert. | `assets/` |
| [`research-and-report`](research-and-report/SKILL.md) | research | Produces a self-contained, reproducible Markdown report for investigations, comparisons, benchmarks, and experiments, with the verdict first and real numbers throughout. | `assets/` |
| [`skill-eval-statistics`](skill-eval-statistics/SKILL.md) | evaluation | Applies sound statistics when designing, running, or reporting evaluations of agent skills — trigger rates, outcome pass rates, description tuning, and before/after comparisons. | `scripts/`, `references/`, `assets/` |
| [`spec-before-code`](spec-before-code/SKILL.md) | design | Lightweight design-doc workflow — write a short Markdown spec with goals, non-goals, design, alternatives, and a mandatory threat model before implementing non-trivial work. | `assets/` |
<!-- catalog:end -->

Every skill also ships `evals/trigger-queries.json`: starter queries that should and should not trigger it, for testing the description (see [Testing skills](#testing-skills)).

## Featured: Agent Skills, Measured

You rewrote a skill description and its trigger rate went from **9/20 to 14/20**. The 95% interval on that difference runs from **−5 to +50 points**: this sample can't tell the two versions apart.

[`skill-eval-statistics`](skill-eval-statistics/SKILL.md) makes your agent apply sound statistics whenever it evaluates a skill. Its [guide](skill-eval-statistics/references/guide.md) explains why, with numbers worth knowing:

- Passing **3 of 3** runs is consistent with a true pass rate anywhere from **44% to 100%**.
- 20 queries can never be worth more than **40** independent observations when runs of the same query are correlated (ICC 0.5), however many runs you add.
- Pick the best of five equally good descriptions on 8 validation queries, and its expected score is **91%** when each is really **75%**.

It bundles a zero-dependency calculator ([`skillstats.py`](skill-eval-statistics/scripts/skillstats.py)) whose interval maths is tested against published reference values.

## Install

Skills are plain folders, so they work with any agent that reads the [Agent Skills format](https://agentskills.io). Pick whichever route suits you.

**Claude Code plugin** (all skills, kept up to date):

```bash
/plugin marketplace add M2LabOrg/agent-skills
/plugin install m2lab-skills@m2lab
```

**Any agent, with the [`skills` CLI](https://github.com/vercel-labs/skills):**

```bash
npx skills add M2LabOrg/agent-skills --list
npx skills add M2LabOrg/agent-skills --skill debugging-discipline --skill spec-before-code
```

**Any agent, from a clone** with the bundled installer:

```bash
git clone https://github.com/M2LabOrg/agent-skills.git
agent-skills/scripts/install.sh --agent claude                     # → .claude/skills/
agent-skills/scripts/install.sh --agent copilot debugging-discipline # → .github/skills/
agent-skills/scripts/install.sh --agent agents --global --link       # → ~/.agents/skills/, updated by git pull
agent-skills/scripts/install.sh --target path/to/skills              # any other folder
```

**By hand:** copy a skill folder into your agent's skills folder.

| Agent | Project folder | User folder |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| GitHub Copilot (VS Code) | `.github/skills/` (also reads `.claude/skills/`, `.agents/skills/`) | `~/.copilot/skills/` |
| Codex and other tools using the shared location | `.agents/skills/` | `~/.agents/skills/` |
| OpenCode | `.opencode/skills/` (also reads `.claude/skills/`, `.agents/skills/`) | — |

Check your agent's documentation if it isn't listed; most read at least one of these folders.

## How each skill is built

```
skill-name/
├── SKILL.md            # Required. Frontmatter (name, description, metadata) + instructions
├── scripts/            # Deterministic helpers the agent runs (standard library only)
├── references/         # Detail the agent reads only when needed
├── assets/             # Templates copied into the user's project
└── evals/              # Trigger tests for maintainers (not needed at runtime)
```

Conventions, enforced in CI by [`scripts/catalog.py`](scripts/catalog.py):

- **The description is the trigger.** It says what the skill does, when to use it ("Use when …"), and when not to ("Do not use …"), in under 1024 characters.
- **Progressive disclosure.** `SKILL.md` stays short (under 500 lines); detail moves to `references/` and templates to `assets/`, linked one level deep.
- **Self-contained and tool-agnostic.** Relative paths only, no tool-specific variables, no dependencies on other repositories. Skills may *mention* each other by name, but each one works alone.
- **Folder name equals `name`**, in lowercase kebab-case.
- **No personal or employer details.** A leak guard rejects work-item ids, cloud account ids and similar patterns.

## Testing skills

Each `evals/trigger-queries.json` uses the format from the [Agent Skills guide to optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions): realistic queries labeled `should_trigger`, including near-misses that share vocabulary but need something else. The starter sets have 8–9 queries; grow them toward about 20 before relying on them.

Run each query several times with your agent, record one JSON line per run (`{"query", "variant", "pass"}`), and analyze the results with [`skillstats.py analyze`](skill-eval-statistics/scripts/skillstats.py). The guide explains how to read them.

## Repository layout

| Path | Purpose |
|---|---|
| `<skill>/` | One folder per skill |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests |
| `scripts/catalog.py` | Validates skills; regenerates the table above and the docs-site catalog |
| `scripts/install.sh` | Installs skills into any agent's folder |
| `tests/` | Tests for bundled scripts |
| `docs/` | GitHub Pages catalog |

## Contributing

Issues and pull requests are welcome. This repository is the source of truth. See [CONTRIBUTING.md](CONTRIBUTING.md).

## About

Maintained by Michel Mesquita, PhD, CStat (Chartered Statistician, Royal Statistical Society), at [M2Lab.io](https://github.com/M2LabOrg). Reviewed monthly.

[MIT](LICENSE) licensed: use, adapt and share freely.
