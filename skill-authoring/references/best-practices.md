# Skill authoring best practices

## Contents

1. [How agents load skills](#1-how-agents-load-skills)
2. [Frontmatter](#2-frontmatter)
3. [Writing the description](#3-writing-the-description)
4. [Writing the body](#4-writing-the-body)
5. [Choosing folders](#5-choosing-folders)
6. [Writing scripts](#6-writing-scripts)
7. [Portability](#7-portability)
8. [Security](#8-security)
9. [Testing](#9-testing)
10. [Maintenance](#10-maintenance)

## 1. How agents load skills

Skills load in three stages, and each stage should carry only what it needs:

| Stage | What loads | When | Budget |
|---|---|---|---|
| Discovery | `name` and `description` of every installed skill | Session start | ~100 words per skill, paid by every session |
| Activation | The full `SKILL.md` body | When the description matches the task | Under 500 lines |
| Execution | Files in `scripts/`, `references/`, `assets/` | Only when `SKILL.md` points to them | Unlimited, read or run on demand |

The description therefore does all the triggering work, the body does all the instructing, and everything else stays out of context until needed.

## 2. Frontmatter

| Field | Required | Rules |
|---|---|---|
| `name` | Yes | 1–64 characters; lowercase letters, digits and single hyphens; no leading, trailing or double hyphens; equals the folder name |
| `description` | Yes | 1–1024 characters; see section 3 |
| `license` | No | License name or bundled file |
| `compatibility` | No | Up to 500 characters: required tools, network access, platforms |
| `metadata` | No | String keys and values for your own use (category, version, author) |
| `allowed-tools` | No | Pre-approved tools, where the agent supports it (experimental) |

Put custom fields under `metadata`, not at the top level. Avoid `claude` and `anthropic` in names; some tools reserve them.

## 3. Writing the description

Use three parts, in this order:

1. **What it does:** one sentence starting with a verb, in the third person. "Creates…", "Validates…", "Applies…".
2. **When to use it:** `Use when …`, listing the situations, including indirect phrasings where the user describes the need without naming the topic. Those are where wording matters most.
3. **When not to use it:** `Do not use for …`, naming near-miss tasks that share vocabulary, and pointing to the neighbouring skill when there is one.

Guidelines:

- **Describe user intent, not implementation.** The agent matches against what the user asked.
- **Be concrete.** Name file types, tools, artefacts and verbs users actually say.
- **Don't keyword-stuff.** Long lists of trigger phrases overfit; describe the category of task instead.
- **Stay well under the limit.** 300–700 characters is typical. Every installed description is paid for in every session.

Weak:

```yaml
description: Helps with PDFs.
```

Strong:

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges or splits documents. Use when the user has a PDF to read, convert, fill, combine or split, even if they only say "this document" or "the form". Do not use for creating Word or slide files, or for scanned images without a PDF.
```

## 4. Writing the body

- **Imperative and procedural.** Numbered steps for workflows; one action per step.
- **Defaults, not menus.** Recommend one approach and mention alternatives only where the choice really depends on the situation.
- **Explain why, briefly,** when a rule might look arbitrary. Agents follow rules better when they understand them, and handle edge cases better.
- **One worked example** (input → output, or before → after) beats a paragraph of rules.
- **Name the anti-patterns:** tempting wrong moves, each with the right alternative.
- **Consistent terms.** Pick one word per concept and keep it.
- **Assume a capable reader.** Don't explain what the agent already knows (what JSON is, how git works); spend the words on what is specific to this method.
- **Under 500 lines.** When it grows, move detail to `references/`.

## 5. Choosing folders

Create a folder only when the skill needs it. Empty folders add nothing.

| Folder | Holds | The agent… | Example |
|---|---|---|---|
| `scripts/` | Deterministic, repeatable operations | **runs** it | Validator, calculator, scaffolder, converter |
| `references/` | Detail needed only sometimes | **reads** it when `SKILL.md` says to | Full guide, API notes, catalogue of variants, long checklists |
| `assets/` | Files that end up in the user's project | **copies** it | Templates, config files, starter HTML, workflow YAML |
| `evals/` | Trigger tests for maintainers | — (not used at runtime) | `trigger-queries.json` |

Decision rules:

- **Would the agent otherwise write the same code each time?** Put it in `scripts/`. Code that runs is cheaper and more reliable than code regenerated from instructions.
- **Would the agent copy text into the user's project?** Put it in `assets/`, not inline in `SKILL.md`.
- **Is the detail needed in fewer than about half of uses?** Put it in `references/` and link it from the step that needs it, saying when to read it.

Linking rules:

- Link from `SKILL.md` with relative paths, one level deep: `references/guide.md`, not `references/a/b/c.md`, and not chains where one reference sends the agent to another.
- Give references over ~100 lines a **Contents** section so the agent can jump to the part it needs.
- Never link outside the skill folder. An installed skill is copied on its own.

## 6. Writing scripts

- **Standard library only**, or declare dependencies in `compatibility`. Users install skills by copying a folder; nothing else gets installed.
- **`--help` that explains usage**, with examples in the module docstring.
- **Clear errors and exit codes:** non-zero on failure, with a message saying what to fix.
- **Deterministic:** the same input gives the same output. Seed any randomness.
- **No surprise side effects:** don't modify files the user didn't name; refuse to overwrite without a flag.
- **No network access** unless it is the script's purpose, and then say so in `compatibility`.
- **Tested.** A script the agent runs on user data deserves unit tests in the repository that hosts the skill.

## 7. Portability

Skills are plain folders, so the same skill works in Claude Code (`.claude/skills/`), GitHub Copilot (`.github/skills/`), Codex and other tools sharing `.agents/skills/`, and OpenCode (`.opencode/skills/`). Keep it that way:

- Relative paths only. No tool-specific variables such as `${CLAUDE_PLUGIN_ROOT}` in `SKILL.md`.
- Don't assume a particular tool name for reading files or running commands; say what to do ("run", "read", "copy").
- Mention other skills by name if useful, but never depend on them being installed.

## 8. Security

- Never put secrets, tokens, internal URLs, or personal or employer details in a skill.
- Scripts must not download and execute code.
- Treat skills from others like code: review `SKILL.md` and every script before installing. Anyone who can commit to a repository can add a skill that loads automatically.

## 9. Testing

1. **Validate the format:** `python3 scripts/validate_skill.py <skill>`.
2. **Test triggering:** write `evals/trigger-queries.json` with about 20 realistic queries, half should-trigger (including indirect phrasings) and half near-miss should-not-trigger. Run each several times with your agent and record whether the skill loaded.
3. **Test outcomes:** run a few real tasks with and without the skill, and compare the results against criteria decided in advance.
4. **Read results honestly:** small samples can only show large effects. Use the `skill-eval-statistics` skill to size the eval and interpret the numbers.
5. **Hold out queries** when tuning the description, so you don't overfit to the queries you score on.

## 10. Maintenance

- Re-run trigger evals when the description changes, and when you add a skill with neighbouring scope: neighbours compete for the same queries.
- When a user reports a misfire, add that query to `evals/` with its correct label before fixing the description.
- Version breaking changes in `metadata` (for example `version: "2"`), and note them where the skill is published.
