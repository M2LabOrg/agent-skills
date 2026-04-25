# GitHub Pages site

Static landing page served from this `/docs/` folder.

## Local preview

```bash
open docs/index.html        # macOS
# or
python3 -m http.server -d docs 8000
```

## Enabling on GitHub

Repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch: `main` / folder: `/docs`.

Live URL: <https://m2laborg.github.io/skills/>

## Updating the skill list

The list is the JSON block at the bottom of `index.html` (id `skills-data`). Add/remove entries there when a skill is added or removed. See the `docs-sync-on-change` skill — this is part of every PR that touches a skill.
