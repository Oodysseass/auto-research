#!/bin/sh
# Run the dotclaude test suite. Creates .venv/ (git-ignored) with pytest on first use.
# Uses /usr/bin/python3, the interpreter the hooks in settings.json use. Extra arguments go to pytest.
set -eu
REPO=$(cd "$(dirname "$0")/.." && pwd)
PY=/usr/bin/python3
VENV="$REPO/.venv"
if [ ! -x "$VENV/bin/python" ]; then
  "$PY" -m venv "$VENV"
fi
if ! "$VENV/bin/python" -c "import pytest" 2>/dev/null; then
  "$VENV/bin/python" -m pip install --quiet --disable-pip-version-check pytest
fi
cd "$REPO"
exec "$VENV/bin/python" -m pytest tests "$@"
