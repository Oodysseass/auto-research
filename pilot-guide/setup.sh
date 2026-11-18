#!/bin/sh
# Create a fresh pilot project in the two-repo layout: ~/dotclaude/pilot-guide/setup.sh
# Works on $PILOT_DIR (default ~/dotclaude/pilot). Refuses if it exists: archive the previous run first (see PILOT.md).
# The project repo starts empty: resources/ is excluded by .git/info/exclude, never committed. /intake makes .work/ its own repo.
set -eu
GUIDE=$(cd "$(dirname "$0")" && pwd)
P=${PILOT_DIR:-$HOME/dotclaude/pilot}
if [ -e "$P" ]; then
  echo "pilot: $P exists. Archive the previous run (PILOT.md, section 0), then remove it." >&2
  exit 2
fi
mkdir -p "$P/resources"
cp "$GUIDE/resources/BRIEF.md" "$GUIDE/resources/notes.md" "$P/resources/"
git init -q "$P"
python3 "$GUIDE/../scripts/repos.py" --root "$P" init >/dev/null
echo "pilot: created $P"
echo "  project repo: $(git -C "$P" status --porcelain --untracked-files=all | wc -l | tr -d ' ') visible paths (must be 0)"
echo "  resources/: $(ls "$P/resources" | tr '\n' ' ')"
echo "  next: cd $P && claude, then /intake"
