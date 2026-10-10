#!/bin/sh
# Add patterns to this clone's .git/info/exclude (never committed), once each, and verify.
# Usage: exclude-locally.sh <pattern> [<pattern> ...]
set -eu

if [ "$#" -eq 0 ]; then
  echo "usage: $0 <pattern> [<pattern> ...]" >&2
  exit 2
fi

exclude=$(git rev-parse --git-path info/exclude) || {
  echo "error: not inside a git repository" >&2
  exit 1
}
mkdir -p "$(dirname "$exclude")"
touch "$exclude"

for pattern in "$@"; do
  if grep -qxF -- "$pattern" "$exclude"; then
    echo "already excluded: $pattern"
  else
    printf '%s\n' "$pattern" >> "$exclude"
    echo "added: $pattern"
  fi
  # Verification only works for paths that exist; patterns with wildcards are reported as added.
  if [ -e "$pattern" ]; then
    git check-ignore -v -- "$pattern" || echo "warning: $pattern is still not ignored (is it already tracked? try: git rm --cached $pattern)" >&2
  fi
done
