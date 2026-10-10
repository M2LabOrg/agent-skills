---
name: pr-and-branch-hygiene
description: Branch naming, atomic commits, pre-push checks, and pull-request authoring that make changes easy to review and revert. Use when creating a branch, preparing commits, pushing, opening or updating a pull request (GitHub, GitLab, Azure DevOps, or any host), drafting a PR description, or responding to review comments. Do not use for git troubleshooting (merge conflicts, lost commits, rebasing problems) or for choosing a repository-wide branching strategy.
metadata:
  category: git
---

# Pull Request and Branch Hygiene

Apply to every change that ships through a pull request, on any host.

## 1. Branch from a fresh default branch

```bash
git switch main && git pull
git switch -c <prefix>/<short-kebab-summary>
```

- Use the repository's default branch (often `main`). Check it with `git remote show origin | grep 'HEAD branch'`.
- `<prefix>` follows the project's convention: author initials, or a type such as `feat`, `fix`, `chore`. Follow `CONTRIBUTING.md` if it defines one.
- Include the work-item id when one exists: `fix/1234-null-total-on-empty-cart`.

## 2. Commit discipline

- **Atomic commits:** one logical change each, easy to review and revert.
- **Imperative subject** under ~72 characters: `Fix total when cart is empty`, not `Fixed bug`.
- **Body explains why**; the diff shows what.
- **Separate refactors from behavior changes**, so reviewers can skim the first and focus on the second.
- Never force-push a branch under review without telling reviewers. If you must, use `--force-with-lease`.

## 3. Before every push

- [ ] Lint and format with the project's tools
- [ ] Unit tests for the affected area pass
- [ ] Evals re-run, if the change affects AI output quality (see `eval-development`)
- [ ] Required version bumps or generated files updated
- [ ] `git diff --staged` reviewed for secrets, debug output, and commented-out code

## 4. Write the pull request

Use [assets/pull-request-template.md](assets/pull-request-template.md). To make it the repository default, copy it to `.github/pull_request_template.md` (GitHub) or the host's equivalent.

The description must stand on its own. "See ticket" is not a description.

## 5. Open as draft, promote when ready

- Open as **draft** until validation is filled in and CI is green.
- **Review the diff yourself** in the host's UI before requesting review. It catches many obvious comments.
- Request specific reviewers rather than relying on auto-assignment.

## 6. During review

- Answer every comment with a change or a reply explaining why not.
- Push follow-ups as **new commits** so reviewers see what changed. Squash at merge time if needed.
- Re-run validation and update the description's results after significant changes.

## 7. Merge

- Target the default branch.
- Prefer **squash merge**, unless the individual commits are meaningful.
- Delete the branch after merging.

## Anti-patterns

- "WIP" commits with broken state on a branch under review.
- Pull requests over ~500 changed lines for non-mechanical work: split them.
- Renaming a branch after the pull request exists.
- Mixing formatting changes with logic changes.
