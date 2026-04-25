# M2Lab.io Agent Skills

> 🌐 **Live site:** <https://m2laborg.github.io/agent-skills/>

A curated collection of reusable Cascade (Windsurf), Claude Code, Cursor, and VS Code agent skills by [M2Lab.io](https://github.com/M2LabOrg) — eval-driven development, debugging discipline, PR hygiene, spec-before-code, and more.

Skills are loaded by AI coding assistants via each workspace's `.claude/skills/` directory. See the [Anthropic skills docs](https://code.claude.com/docs/en/skills).

> ⚠️ **This repo is auto-generated.** Skills here are sanitized mirrors of a private source repo. Please open issues / PRs for ideas, but content edits will be overwritten on the next sync. To propose changes to a methodology, open an issue describing the change.

## Skills

| Skill | Description |
|---|---|
| [`debugging-discipline/`](./debugging-discipline/SKILL.md) | Bug-fixing methodology — root cause first, minimal upstream fix, regression tests. |
| [`pr-and-branch-hygiene/`](./pr-and-branch-hygiene/SKILL.md) | Branch naming, atomic commits, PR template, draft-first workflow. |
| [`research-and-report/`](./research-and-report/SKILL.md) | Investigation / benchmark / comparison deliverable format. |
| [`spec-before-code/`](./spec-before-code/SKILL.md) | Lightweight design-doc workflow with mandatory threat model (STRIDE). |
| [`mermaid-diagrams/`](./mermaid-diagrams/SKILL.md) | Always use Mermaid (not ASCII art) for diagrams in markdown. |
| [`github-pages-generation/`](./github-pages-generation/SKILL.md) | Spin up a polished GitHub Pages site for a repo. |
| [`docs-sync-on-change/`](./docs-sync-on-change/SKILL.md) | Update docs in the same PR as the code that changes their meaning. |
| [`eval-development/`](./eval-development/SKILL.md) | Eval-driven development methodology for AI service quality fixes. |
| [`local-git-excludes/`](./local-git-excludes/SKILL.md) | When to use `.git/info/exclude` vs team `.gitignore`. |

## Loading skills into a project

```bash
# Symlink (single dev machine, recommended)
git clone git@github.com:M2LabOrg/agent-skills.git ~/dev/M2LabOrg-agent-skills
mkdir -p <project>/.claude/skills
ln -s ~/dev/M2LabOrg-agent-skills/debugging-discipline \
      <project>/.claude/skills/debugging-discipline
echo ".claude/skills/" >> <project>/.gitignore

# Or as a git submodule (pinned per project)
git submodule add git@github.com:M2LabOrg/agent-skills.git .claude/skills

# Or shallow clone (CI / RunPod / ephemeral envs)
git clone --depth 1 https://github.com/M2LabOrg/agent-skills.git .claude/skills
```

Cascade (Windsurf), Claude Code, Cursor, and any IDE supporting the `.claude/skills/` convention will pick these up automatically.

## License

[MIT](./LICENSE) — use, fork, remix freely.
