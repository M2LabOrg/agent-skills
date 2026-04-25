---
name: pr-and-branch-hygiene
description: Michel's standards for branch naming, commit discipline, and pull-request authoring across all projects. Use whenever the user creates a branch, opens or updates a pull request, prepares a commit, drafts a PR description, or asks how to organize work for review. Triggers on phrases like "open a PR", "push the branch", "create a commit", "draft PR description", "ready for review", "merge this", and on any work involving Azure DevOps PBIs / GitHub issues that will land via PR.
---

# Pull Request and Branch Hygiene

Apply consistently for every change that ships through a PR — Azure DevOps (`Azure DevOps`), GitHub (personal `M2LabOrg/*`), or any other host.

## 1. Branch Naming

- **Always** start from a fresh `main`. Never branch off `master` (it's stale or absent on most of Michel's repos).
- Format: `mdsm/<short-kebab-case-summary>`
- Tie to a tracked work item when one exists: `mdsm/<id>-<summary>` is also fine (e.g. `mdsm/443029-cross-paragraph-gender`).

```bash
git checkout main && git pull
git checkout -b mdsm/<descriptive-name>
```

## 2. Commit Discipline

- **Atomic commits.** One logical change per commit. Easier to revert, easier to review.
- **Imperative subject**, max ~72 chars: `"Fix gender enforcement for AWS Translate"` not `"Fixed bug"`.
- **Body when non-trivial**: explain *why*, not *what*. The diff shows what.
- Keep refactors and behavior changes in **separate commits**. Reviewers can ignore the refactor and focus on the behavior diff.
- Never `--force` push a branch under review without coordinating. Use `--force-with-lease` if you must.

## 3. Pre-Push Checklist

Run before every `git push`:

- Lint + format (project-specific; e.g. `python -m manage checks --fix` for `<your AI services project>`)
- Unit tests for affected area
- For `<your AI services project>`: bump `container.toml` / `layer.toml` version if you touched containers / layers
- Eval suite (when a relevant skill applies, e.g. `eval-development`)
- Verify no secrets, debug prints, or commented-out blocks slipped in: `git diff --staged`

## 4. PR Description Template

Always use this exact structure:

```markdown
## Summary
<2–4 sentence problem statement and approach>

## Linked work
- PBI: #<id>  (Azure DevOps)
- Issue: #<id>  (GitHub)

## Changes
- <bullet> <file or area> — <what changed>
- ...

## Validation
- [ ] Unit tests pass
- [ ] Lint/format clean
- [ ] Local stack run (Docker) — paste eval table or summary
- [ ] DEV deploy verified (if applicable)

## Eval / Results
<paste markdown table or summary metrics — see eval-development skill>

## Risks / Rollback
<anything reviewers should know; how to roll back if needed>

## Screenshots / Diagrams
<if UI or architecture changed — prefer Mermaid per mermaid-diagrams skill>
```

## 5. PR Mode

- **Open as Draft** until the eval/validation section is filled and CI is green. Promote to "Ready for review" only when you'd be comfortable merging it yourself.
- Self-review the diff in the PR UI before requesting reviewers — catches roughly half of "obvious" feedback.
- Tag reviewers explicitly. Don't rely on auto-assignment.

## 6. Targeting & Merging

- **Target `main`.** Never `master`.
- Prefer **squash merge** unless commits are individually meaningful and well-crafted.
- Delete the branch after merge.

## 7. Hosts

| Host | Account | URL pattern |
|---|---|---|
| Azure DevOps (work) | Azure DevOps org / MEPS | `https://dev.azure.com/Azure DevOps/_git/<repo>` |
| GitHub (personal) | **M2LabOrg** | `https://github.com/M2LabOrg/<repo>` |

For personal projects under `M2LabOrg`, mirror the same PR template and discipline. Use GitHub Issues in place of PBIs.

## 8. Updating an Open PR

- Address each review comment with either a code change *or* an inline reply explaining why not.
- Push as **additional commits** during review (don't rebase). Squash at merge time if needed.
- Re-run the eval / validation suite and update the PR description's results section so reviewers don't have to ask.

## 9. Anti-Patterns to Avoid

- "WIP" commits with broken state pushed to a PR branch under review.
- Mega-PRs (>500 lines diff) for non-mechanical changes — split them.
- PR descriptions that say only "see PBI". Reviewers should not have to context-switch.
- Renaming the branch after the PR exists; create a new branch and a new PR instead.
