---
name: local-git-excludes
description: Use `.git/info/exclude` (per-clone, never pushed) or a global gitignore for personal / machine-local files instead of polluting the team `.gitignore`. Use whenever the user wants to ignore a file privately, asks "will my colleagues see this?", adds personal tooling / IDE configs / symlinks / scratch files to a shared repo, or any time you (the assistant) are about to add a line to a tracked `.gitignore` for something that is clearly personal. Triggers on phrases like "ignore this locally", "don't commit this", "personal tooling", "scratch file", "not for the team", "my own setup", and on any addition involving symlinks to personal repos, editor configs, local notes, or `.env.local` style files.
---

# Local Git Excludes — Don't Pollute the Team `.gitignore`

The team's `.gitignore` is **tracked and shared**. Every line you add is committed and pushed for everyone to see. For anything personal — symlinks to your own dotfile/skills repos, scratch notes, IDE configs that nobody else uses, machine-local artifacts — use a **local-only** mechanism instead.

## Three Mechanisms (Pick the Right One)

| Mechanism | Scope | Tracked? | When to use |
|---|---|---|---|
| **Repo `.gitignore`** | This repo, all clones | ✅ Yes | Build outputs, secrets patterns, anything every contributor needs |
| **`.git/info/exclude`** | One clone of one repo | ❌ No | Personal files in a specific shared repo |
| **Global gitignore** (`core.excludesfile`) | Every repo on this machine | ❌ No | Patterns you always want ignored everywhere (e.g. `.DS_Store`, `*.swp`, personal IDE folders) |

## Decision Rule

Before adding a line to a tracked `.gitignore`, ask: **"Would every contributor benefit from this rule?"**

- **Yes** → tracked `.gitignore` is correct.
- **No / only me** → `.git/info/exclude` (this repo) or global gitignore (all repos).
- **Unsure** → default to `.git/info/exclude`. You can always promote it to the tracked file later.

## Mechanism 1 — Per-Clone Exclude (`.git/info/exclude`)

Lives at `<repo>/.git/info/exclude`. Same syntax as `.gitignore`. Never pushed (the entire `.git/` directory is local).

```bash
# Add a personal pattern to the current repo only
echo ".claude/skills/my-personal-skill" >> .git/info/exclude

# Verify it's working
git check-ignore -v .claude/skills/my-personal-skill
# .git/info/exclude:N:.claude/skills/my-personal-skill   .claude/skills/my-personal-skill
```

When you re-clone the repo, `.git/info/exclude` resets to the default. **Either re-add the lines** or use the global gitignore for patterns you want everywhere.

## Mechanism 2 — Global Gitignore

One file, applies to every repo on the machine. Set it once.

```bash
# One-time setup
git config --global core.excludesfile ~/.gitignore_global

# Add patterns you always want ignored, anywhere
cat >> ~/.gitignore_global <<'EOF'
.DS_Store
*.swp
.idea/
.vscode/
.cascade/
.claude/skills/*-personal/
EOF
```

Pros: survives re-clones, works in every repo automatically.
Cons: applies everywhere — be careful with overly broad patterns that might bite a project where the file *should* be tracked.

## Quick Decision Examples

| File | Where to ignore | Why |
|---|---|---|
| `dist/`, `node_modules/` | Team `.gitignore` | Everyone needs this |
| `.env.example` | Team — **not** ignored, **committed** | Documents required env |
| `.env` | Team `.gitignore` | Everyone has one, secrets |
| `.env.local` | Team `.gitignore` | Convention, everyone may use |
| Symlink to your personal skills repo | `.git/info/exclude` | Only you have it |
| Personal scratch `notes.md` in repo root | `.git/info/exclude` | Only you have it |
| `.DS_Store` | Global gitignore | Every macOS repo, everywhere |
| `*.swp` (vim) | Global gitignore | Only your editor needs it |
| Personal Aider / Claude / Cursor configs | Global gitignore | Reused in many repos |

## Workflow When Adding Personal Files

```bash
# 1. Drop or symlink the personal file in the repo
ln -s ~/dev/M2LabOrg-skills/my-skill .claude/skills/my-skill

# 2. Exclude it locally (NOT in the tracked .gitignore)
echo ".claude/skills/my-skill" >> .git/info/exclude

# 3. Verify
git status                              # should NOT list the file
git check-ignore -v .claude/skills/my-skill  # confirms which rule excluded it
```

## Auditing Before You Commit

Before pushing changes to a tracked `.gitignore`, ask yourself again per line:

```bash
git diff .gitignore
```

For each new line: *"Would I be comfortable explaining this to every reviewer?"* If the answer involves "this is just my personal setup", move it to `.git/info/exclude` instead.

## When You've Already Pushed Personal Stuff to the Team `.gitignore`

Don't panic — gitignore lines are harmless code. To clean up:

```bash
git checkout main && git pull
git checkout -b mdsm/cleanup-gitignore
# remove the personal lines from .gitignore
git commit -am "gitignore: remove personal entries (moved to local exclude)"
# add the same lines to .git/info/exclude on every machine you use
echo "<pattern>" >> .git/info/exclude
```

Open a small PR, mention briefly that you're moving them to per-clone excludes.

## Bonus — `git update-index --assume-unchanged`

For **tracked** files where you have local-only modifications you don't want to push (e.g. tweaking a config file that lives in the repo):

```bash
git update-index --assume-unchanged path/to/tracked/file
# undo:
git update-index --no-assume-unchanged path/to/tracked/file
```

Use sparingly — it can confuse you later. Prefer rewriting the file's design (template + gitignored override) when this comes up repeatedly.

## Anti-Patterns

- Adding `.idea/`, `.vscode/`, `.DS_Store`, personal symlinks, or `WARP.md`-style assistant configs to the **team** `.gitignore` "for convenience". They belong in the global gitignore.
- Committing personal scratch notes "behind" a `.gitignore` rule for them — the rule reveals you have them.
- Telling colleagues to put a specific line in their local `.gitignore` — give them the global-gitignore recipe instead.
- Forgetting that `.git/info/exclude` is per-clone; treating it as if it follows the repo.
