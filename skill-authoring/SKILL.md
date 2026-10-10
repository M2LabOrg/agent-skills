---
name: skill-authoring
description: Creates and improves agent skills in the open Agent Skills format — a precise triggering description, a lean SKILL.md, and scripts/, references/, assets/ and evals/ folders used for the right purposes — then validates the result. Use when asked to create, write, scaffold, restructure, review, or fix a skill or its SKILL.md, or to turn a repeatable workflow into a skill for any agent (Claude Code, GitHub Copilot, Codex, and others). Do not use for measuring or interpreting skill eval results (use skill-eval-statistics), or for writing ordinary project documentation.
metadata:
  category: authoring
---

# Skill Authoring

A good skill triggers on the right requests, tells the agent exactly what to do, and loads detail only when needed. Follow these steps for every new or revised skill. The reasoning behind each rule is in [references/best-practices.md](references/best-practices.md); read the matching section when a rule needs adapting.

## 1. Define the job

Before writing, settle three things with the user:

- **The outcome:** what the agent produces when the skill runs.
- **Trigger cases:** 3–5 real requests that should load it, including one that never names the topic.
- **Near misses:** 2–3 requests that sound similar but need something else.

If the job is really two jobs, make two skills.

## 2. Scaffold

Pick the skills folder for the user's agent (`.claude/skills/`, `.github/skills/`, `.agents/skills/`, or the repository's own layout), then run:

```bash
python3 scripts/new_skill.py <skill-name> --dir <skills-folder> [--scripts] [--references] [--assets]
```

Request only the folders the skill needs (step 4). The script creates `SKILL.md` and `evals/trigger-queries.json` from [assets/SKILL.template.md](assets/SKILL.template.md) and [assets/trigger-queries.template.json](assets/trigger-queries.template.json).

## 3. Write the frontmatter

- `name`: lowercase kebab-case, at most 64 characters, equal to the folder name.
- `description`, in three parts, under 1024 characters (aim for 300–700):
  1. What it does, as one sentence starting with a verb, in the third person.
  2. `Use when …`: situations and phrasings, including indirect ones.
  3. `Do not use for …`: near misses, naming the neighbouring skill when there is one.
- `metadata`: custom fields such as `category`. Keep custom keys out of the top level.

## 4. Put content where it belongs

| Content | Location |
|---|---|
| Steps the agent follows every time | `SKILL.md`, as numbered imperative steps |
| An operation the agent would otherwise re-code each time | `scripts/`: the agent runs it |
| Detail needed in fewer than half of uses | `references/`: link it from the step that needs it |
| Files that end up in the user's project | `assets/`: the agent copies them |
| Trigger tests | `evals/trigger-queries.json` |

Keep `SKILL.md` under 500 lines, link with relative paths one level deep, and never link outside the skill folder. Scripts use the standard library only, support `--help`, and fail with a clear message. Delete any `PLACEHOLDER.md` once a folder has real content.

## 5. Write the body

- Numbered, imperative steps; one action each.
- One recommended approach rather than a menu of options.
- A short *why* where a rule could look arbitrary.
- One worked example, and a short list of anti-patterns.
- No tool-specific paths or variables, so the skill works in any agent.

## 6. Write trigger evals

Replace every query in `evals/trigger-queries.json` with realistic requests: at least 8 to start, growing to about 20, half should-trigger and half near-miss should-not-trigger. Use file names, casual phrasing and context, as real users do.

## 7. Validate

```bash
python3 scripts/validate_skill.py <skills-folder>/<skill-name>
```

Fix every error. Fix warnings unless there is a stated reason not to. Then run the trigger queries with the user's agent, and use the `skill-eval-statistics` skill to judge whether the results support the description.

## Example

Request: "Make a skill that formats our SQL the way the team likes."

1. Outcome: SQL reformatted to the team style. Trigger: "tidy up this query". Near miss: "optimize this slow query".
2. `python3 scripts/new_skill.py sql-style --dir .agents/skills --scripts --references`
3. Description: "Formats SQL to the team style guide (uppercase keywords, leading commas, one clause per line). Use when the user asks to format, tidy, or style SQL, or pastes SQL for review. Do not use for query optimization, schema design, or non-SQL code."
4. `scripts/format_sql.py` does the formatting; `references/style-guide.md` holds the full rules; `SKILL.md` says when to run the script and how to report changes.

## Anti-patterns

- A description that says what the skill *is* but not *when* to use it.
- Pasting long reference material or templates into `SKILL.md`.
- Instructions asking the agent to write the same helper code every time, instead of bundling a script.
- Empty `scripts/`, `references/` or `assets/` folders "for structure".
- Links to files outside the skill folder, or to tool-specific paths.
- Shipping without trigger tests, or judging a description on three runs.
