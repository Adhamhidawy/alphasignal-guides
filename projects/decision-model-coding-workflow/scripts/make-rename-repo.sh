#!/bin/sh
# Make a small git repository holding the rename bug, so next_check.py has a diff to read.
#   scripts/make-rename-repo.sh demo          buggy code committed, Claude's recorded fix applied but not committed
#   scripts/make-rename-repo.sh demo --buggy  buggy code only, for a live Claude Code run
set -eu
PKG="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$1"
if [ -e "$DEST" ]; then
  echo "$DEST already exists" >&2
  exit 1
fi
cp -R "$PKG/cases/rename" "$DEST"
cd "$DEST"
git -c init.defaultBranch=main init -q
git add -A
git -c user.name=next-check -c user.email=next-check@example.invalid commit -q -m "Rename bug: buggy base"
if [ "${2:-}" != "--buggy" ]; then
  git apply "$PKG/cases/rename-claude-fix.diff"
fi
git status --short
