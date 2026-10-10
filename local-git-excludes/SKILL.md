---
name: local-git-excludes
description: Ignores personal or machine-local files with .git/info/exclude or a global gitignore instead of the shared, tracked .gitignore. Use when the user wants to ignore a file only for themselves, asks whether colleagues will see an ignore rule, adds personal tooling, editor config, symlinks, or scratch files to a shared repository, or before adding a clearly personal pattern to a tracked .gitignore. Do not use for ignore rules every contributor needs (build output, dependency folders, secrets patterns) — those belong in the tracked .gitignore.
metadata:
  category: git
---

# Local Git Excludes

The repository's `.gitignore` is tracked and shared: every line is committed for everyone to see. Personal files (symlinks to your own tooling, scratch notes, editor configuration nobody else uses) belong in a local-only mechanism.

## 1. Pick the mechanism

| Mechanism | Scope | Tracked? | Use for |
|---|---|---|---|
| `.gitignore` | This repository, every clone | Yes | Build output, dependency folders, secrets patterns: what every contributor needs |
| `.git/info/exclude` | One clone of one repository | No | Personal files in one shared repository |
| Global gitignore (`core.excludesFile`) | Every repository on this machine | No | Patterns you always want ignored, such as `.DS_Store` and editor swap files |

Before adding a line to `.gitignore`, ask: **would every contributor benefit from this rule?** If not, use a local mechanism. If unsure, start local; promoting a rule later is easy.

## 2. Exclude in one clone

Run [scripts/exclude-locally.sh](scripts/exclude-locally.sh) from inside the repository:

```bash
scripts/exclude-locally.sh notes.md .claude/skills/my-personal-skill
```

It finds the correct exclude file (including in worktrees), adds each pattern once, and verifies with `git check-ignore`. To do it by hand:

```bash
echo "notes.md" >> "$(git rev-parse --git-path info/exclude)"
git check-ignore -v notes.md   # shows which rule matched
```

`.git/info/exclude` does not travel with the repository: a fresh clone starts without it.

## 3. Exclude everywhere on this machine

```bash
git config --global core.excludesFile ~/.gitignore_global
printf '%s\n' .DS_Store '*.swp' >> ~/.gitignore_global
```

Keep global patterns narrow. A broad pattern can hide a file that *should* be tracked in some project.

## 4. Keep local edits to a tracked file

To keep a local change to a tracked file (for example, a config value) out of commits:

```bash
git update-index --skip-worktree path/to/file      # stop tracking local changes
git update-index --no-skip-worktree path/to/file   # undo
git ls-files -v | grep '^S'                        # list skip-worktree files
```

Prefer `--skip-worktree` over `--assume-unchanged`: Git documents the latter as a performance hint that can be reset at any time, not as a way to protect local changes. If this need recurs, redesign the file as a tracked template plus an ignored local override.

## 5. If personal lines already reached `.gitignore`

Remove them in a small pull request, and add the same patterns locally on each machine you use. Ignore rules are harmless, but they are noise for everyone else.

## Anti-patterns

- Adding editor folders, `.DS_Store`, or personal symlinks to the team `.gitignore` for convenience.
- Ignoring a personal scratch file in `.gitignore`: the rule itself advertises the file.
- Telling colleagues to add a line to their own `.gitignore`: share the global-gitignore recipe instead.
- Forgetting that `.git/info/exclude` is per clone.
