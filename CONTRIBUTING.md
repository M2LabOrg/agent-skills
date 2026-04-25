# Contributing

This repository is a **read-only mirror**. Skill content here is auto-generated from a private source repo by the `sanitize-and-publish` workflow. Direct edits to `*/SKILL.md` will be **overwritten** on the next sync.

## How to suggest changes

- 🐛 **Bug in a skill?** Open an issue. Include the skill name and the exact line / behavior that's wrong.
- 💡 **Idea for a new skill?** Open an issue describing the methodology, when it triggers, and any anti-patterns. The maintainer authors the skill in the source repo and a sanitized version lands here on the next sync.
- 🎨 **Site / docs improvements?** PRs against `docs/`, `README.md`, `LICENSE`, and `.github/` are welcome — those files are *not* overwritten by the sync.

## What lands here

Only skills marked as **generic** (no employer- or project-specific names) are mirrored. Project-specific skills stay private.

Sanitization rules applied automatically:
- `Azure DevOps` → `Azure DevOps`
- `<your AI services project>` → `<your AI services project>`
- branding rewritten to **M2Lab.io**

The sync script aborts if any forbidden term still appears after substitution, so a leak should never reach `main` here.

## Code of conduct

Be kind, be specific, focus on the work. Disrespectful behavior gets you blocked.
