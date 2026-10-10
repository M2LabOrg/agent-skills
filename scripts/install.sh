#!/bin/sh
# Install skills from this repository into any agent's skills folder.
#
# Usage: scripts/install.sh [options] [skill ...]
#
#   --agent NAME   claude   -> .claude/skills    (Claude Code)
#                  copilot  -> .github/skills    (GitHub Copilot)
#                  agents   -> .agents/skills    (Codex and other tools that share it; default)
#                  opencode -> .opencode/skills  (OpenCode)
#   --target DIR   any other skills folder (overrides --agent)
#   --global       install into the user-level folder (~/.claude/skills, ~/.copilot/skills, ~/.agents/skills)
#   --project DIR  project root for project-level installs (default: current directory)
#   --link         symlink instead of copy, so `git pull` here updates every project
#   --force        replace skills that are already installed
#   --list         list available skills and exit
#
# With no skill names, installs every skill. Examples:
#   scripts/install.sh --agent claude
#   scripts/install.sh --agent copilot --project ~/code/my-app debugging-discipline spec-before-code
#   scripts/install.sh --global --agent agents --link
set -eu

repo=$(cd "$(dirname "$0")/.." && pwd)
agent=agents target="" global=0 project=. link=0 force=0

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
available() { for d in "$repo"/*/SKILL.md; do basename "$(dirname "$d")"; done; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --agent) agent=${2:?--agent needs a value}; shift 2 ;;
    --target) target=${2:?--target needs a value}; shift 2 ;;
    --project) project=${2:?--project needs a value}; shift 2 ;;
    --global) global=1; shift ;;
    --link) link=1; shift ;;
    --force) force=1; shift ;;
    --list) available; exit 0 ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage 2 ;;
    *) break ;;
  esac
done

if [ -z "$target" ]; then
  if [ "$global" -eq 1 ]; then
    case "$agent" in
      claude) target="$HOME/.claude/skills" ;;
      copilot) target="$HOME/.copilot/skills" ;;
      agents|codex) target="$HOME/.agents/skills" ;;
      *) echo "no known global folder for '$agent'; use --target" >&2; exit 2 ;;
    esac
  else
    case "$agent" in
      claude) target="$project/.claude/skills" ;;
      copilot) target="$project/.github/skills" ;;
      agents|codex) target="$project/.agents/skills" ;;
      opencode) target="$project/.opencode/skills" ;;
      *) echo "unknown agent '$agent'; use --target" >&2; exit 2 ;;
    esac
  fi
fi

[ "$#" -eq 0 ] && set -- $(available)
mkdir -p "$target"

for skill in "$@"; do
  src="$repo/$skill"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "skip: '$skill' is not a skill here (see --list)" >&2
    continue
  fi
  dest="$target/$skill"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$force" -eq 1 ]; then
      rm -rf "$dest"
    else
      echo "exists: $dest (use --force to replace)"
      continue
    fi
  fi
  if [ "$link" -eq 1 ]; then
    ln -s "$src" "$dest"
  else
    cp -R "$src" "$dest"
    find "$dest" -name __pycache__ -type d -prune -exec rm -rf {} +
  fi
  echo "installed: $dest"
done
