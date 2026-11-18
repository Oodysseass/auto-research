#!/usr/bin/env bash
# Gate G3 cross-model review with the Codex CLI. See SKILL.md in this directory.
#
# Usage (from the project root):
#   codex_review.sh --artifact <path[#label]> --slug <slug> --round <n> --brief <path>
#                   [--claims C1,C3] [--model <codex model>] [--effort <level>|highest]
#   --effort highest: the highest reasoning effort Codex lists for the model (G3 on critical artifacts).
#
# Exit codes: 0 report written; 2 refused; 3 Codex changed files (reverted, review discarded);
#             4 invalid output twice; 5 codex exec failed.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
DOTCLAUDE="$(cd "$SKILL_DIR/../.." && pwd -P)"
REPORT_SCHEMA="$DOTCLAUDE/schemas/issue-report.schema.json"
VALIDATOR="$DOTCLAUDE/scripts/validate_issue_json.py"
OUTPUT_SCHEMA="$SKILL_DIR/codex-output.schema.json"
PROMPT_TEMPLATE="$SKILL_DIR/prompt.md"
CODEX="${CODEX_BIN:-codex}"

die() { local code=$1; shift; echo "codex_review: $*" >&2; exit "$code"; }

# Subscription only: never pass an API key to Codex.
unset OPENAI_API_KEY CODEX_API_KEY

ARTIFACT="" SLUG="" ROUND="" BRIEF="" CLAIMS=""
MODEL="${CODEX_REVIEW_MODEL:-gpt-6.1-sol}"
EFFORT="${CODEX_REVIEW_EFFORT:-high}"
while [ $# -gt 0 ]; do
  case "$1" in
    --artifact) ARTIFACT="${2:-}"; shift 2 ;;
    --slug)     SLUG="${2:-}"; shift 2 ;;
    --round)    ROUND="${2:-}"; shift 2 ;;
    --brief)    BRIEF="${2:-}"; shift 2 ;;
    --claims)   CLAIMS="${2:-}"; shift 2 ;;
    --model)    MODEL="${2:-}"; shift 2 ;;
    --effort)   EFFORT="${2:-}"; shift 2 ;;
    -h|--help)  sed -n '2,10p' "$0"; exit 0 ;;
    *) die 2 "unknown argument: $1" ;;
  esac
done

# ---- Arguments ----
[ -n "$ARTIFACT" ] && [ -n "$SLUG" ] && [ -n "$ROUND" ] && [ -n "$BRIEF" ] \
  || die 2 "--artifact, --slug, --round and --brief are required"
[[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die 2 "slug must match [a-z0-9-]+: $SLUG"
[[ "$ROUND" =~ ^[1-9][0-9]*$ ]] || die 2 "round must be a positive integer: $ROUND"
[[ "$MODEL" =~ ^[A-Za-z0-9._-]+$ ]] || die 2 "invalid model name: $MODEL"
if [ "$EFFORT" = highest ]; then
  # Highest level Codex lists for this model, from its model cache (refreshed by the CLI).
  EFFORT="$(python3 -I - "${CODEX_HOME:-$HOME/.codex}/models_cache.json" "$MODEL" <<'PY'
import json, sys
try:
    models = json.load(open(sys.argv[1]))["models"]
    levels = next(m for m in models if m.get("slug") == sys.argv[2])["supported_reasoning_levels"]
    print(levels[-1]["effort"])
except (OSError, ValueError, KeyError, IndexError, StopIteration):
    pass
PY
)"
  [ -n "$EFFORT" ] || die 2 "cannot resolve --effort highest for $MODEL from the Codex model cache. Pass a level."
fi
[[ "$EFFORT" =~ ^[a-z]+$ ]] || die 2 "invalid effort: $EFFORT"
[ -z "$CLAIMS" ] || [[ "$CLAIMS" =~ ^C[0-9]+(,C[0-9]+)*$ ]] || die 2 "claims must look like C1,C3: $CLAIMS"
[ -f "${ARTIFACT%%#*}" ] || die 2 "artifact file not found: ${ARTIFACT%%#*}"
[ -f "$BRIEF" ] || die 2 "brief not found: $BRIEF"

# ---- Project and contract ----
[ -f .work/contract.md ] || die 2 "run from the project root (.work/contract.md not found)"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die 2 "not inside a git repository"
ROOT="$(pwd -P)"

tools_line="$(grep -m1 -E '^[[:space:]]*-?[[:space:]]*ai_tools_allowed[[:space:]]*:' .work/contract.md || true)"
if [ -n "$tools_line" ]; then
  if ! printf '%s\n' "${tools_line#*:}" | tr ',' '\n' | tr -d ' \t\r`' | grep -qx codex; then
    die 2 "codex is not in ai_tools_allowed in .work/contract.md (${tools_line#*:}). Refusing to run."
  fi
fi

# ---- Write guard, before dispatch ----
[ -z "$(git status --porcelain --untracked-files=all)" ] \
  || die 2 "working tree is not clean. Commit first (write guard, before dispatch)."
BASE="$(git rev-parse HEAD)"
COMMIT="$(git rev-parse --short HEAD)"

"$CODEX" login status 2>&1 | grep -q "ChatGPT" \
  || die 2 "Codex is not signed in with ChatGPT. Run: codex login"

OUT=".work/issues/${SLUG}.G3.codex.r${ROUND}.json"
[ -e "$OUT" ] && die 2 "report already exists, refusing to overwrite: $OUT"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/codex_review.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# ---- Prompt ----
PREVIOUS=""
if [ "$ROUND" -gt 1 ]; then
  prev=".work/issues/${SLUG}.G3.codex.r$((ROUND - 1)).json"
  if [ -f "$prev" ]; then
    PREVIOUS="6. Your previous round: $prev"
    resp="${prev%.json}.response.json"
    [ -f "$resp" ] && PREVIOUS="$PREVIOUS, and the producer's response: $resp"
  fi
fi
python3 -I - "$PROMPT_TEMPLATE" "$TMP/prompt.md" "$BRIEF" "$ARTIFACT" "${CLAIMS:-none named; use those the brief names}" "$PREVIOUS" <<'PY'
import sys
template, out, brief, artifact, claims, previous = sys.argv[1:]
text = open(template).read()
for key, value in {"BRIEF": brief, "ARTIFACT": artifact, "CLAIMS": claims, "PREVIOUS": previous}.items():
    text = text.replace("{{" + key + "}}", value)
open(out, "w").write(text)
PY

# ---- Helpers ----
run_codex() {  # $1 prompt file, $2 last-message file
  "$CODEX" exec -C "$ROOT" --sandbox read-only --ephemeral --color never \
    --model "$MODEL" -c "model_reasoning_effort=\"$EFFORT\"" \
    --output-schema "$OUTPUT_SCHEMA" --output-last-message "$2" - <"$1" >>"$TMP/codex.log" 2>&1
}

guard() {  # Write guard, after the reviewer returns. Reverts and exits 3 on any change.
  local status head
  status="$(git status --porcelain --untracked-files=all)"
  head="$(git rev-parse HEAD)"
  [ -z "$status" ] && [ "$head" = "$BASE" ] && return 0
  {
    echo
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "codex_review: CODEX CHANGED THE REPOSITORY. REVIEW DISCARDED."
    [ "$head" != "$BASE" ] && echo "HEAD moved from $BASE to $head. Not reset automatically: inspect it."
    [ -n "$status" ] && { echo "Changed paths:"; printf '%s\n' "$status"; }
  } >&2
  if [ -n "$status" ]; then
    git restore --staged --worktree --source="$BASE" -- :/ 2>/dev/null
    git clean -f -- :/ >/dev/null
    if [ -z "$(git status --porcelain --untracked-files=all)" ]; then
      echo "Reverted to $BASE. Log the violation in decisions.md (write-guard.md, step 4.5)." >&2
    else
      echo "REVERT INCOMPLETE. Remaining:" >&2; git status --porcelain --untracked-files=all >&2
    fi
  fi
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" >&2
  exit 3
}

build_report() {  # $1 last-message file, $2 report file, $3 errors file. Returns 0 if valid.
  python3 -I - "$1" "$2" "$3" "$MODEL" "$ARTIFACT" "$COMMIT" <<'PY' || return 1
import json, re, sys
last, report, errfile, model, artifact, commit = sys.argv[1:]
errors = []
try:
    out = json.loads(open(last).read())
except (OSError, ValueError) as e:
    open(errfile, "w").write(f"final message is not valid JSON: {e}\n")
    sys.exit(1)
if not isinstance(out, dict):
    errors.append("final message is not a JSON object")
    out = {}
issues = out.get("issues")
if not isinstance(issues, list):
    errors.append('"issues" must be a list')
    issues = []
ids = []
for n, issue in enumerate(issues):
    if not isinstance(issue, dict):
        errors.append(f"issues[{n}] is not an object")
        continue
    ids.append(issue.get("id"))
    if not re.fullmatch(r"G3/codex/[0-9]+", str(issue.get("id"))):
        errors.append(f"issues[{n}].id must be G3/codex/<n>, got {issue.get('id')!r}")
    if "duplicate_of" in issue:
        errors.append(f"issues[{n}] sets duplicate_of; only the orchestrator may set it")
if len(ids) != len(set(ids)):
    errors.append("issue IDs are not unique")
serious = any(isinstance(i, dict) and i.get("severity") in ("blocking", "major") for i in issues)
if out.get("verdict") == "accept" and serious:
    errors.append('verdict is "accept" but there is a blocking or major issue')
if out.get("verdict") == "revise" and not serious:
    errors.append('verdict is "revise" but there is no blocking or major issue')
full = {"gate": "G3", "reviewer": "codex", "model": model, "artifact": artifact,
        "commit": commit, "issues": issues, "verdict": out.get("verdict")}
open(report, "w").write(json.dumps(full, indent=2, ensure_ascii=False) + "\n")
open(errfile, "w").write("".join(e + "\n" for e in errors))
sys.exit(1 if errors else 0)
PY
  python3 -I "$VALIDATOR" "$REPORT_SCHEMA" "$2" >>"$3" 2>&1
}

# ---- Review, with one re-ask on invalid output ----
echo "codex_review: model $MODEL, effort $EFFORT, artifact $ARTIFACT, round $ROUND" >&2
for attempt in 1 2; do
  if [ "$attempt" = 1 ]; then
    prompt="$TMP/prompt.md"
  else
    prompt="$TMP/retry.md"
    {
      cat "$TMP/prompt.md"
      echo
      echo "Your previous output for this review was invalid. Errors:"
      cat "$TMP/errors.$((attempt - 1))"
      echo
      echo "Previous output:"
      head -c 20000 "$TMP/last.$((attempt - 1))" 2>/dev/null
      echo
      echo "Return a corrected JSON object only."
    } >"$prompt"
  fi
  run_codex "$prompt" "$TMP/last.$attempt"
  rc=$?
  guard
  if [ $rc -ne 0 ]; then
    echo "codex_review: codex exec failed (exit $rc). Last log lines:" >&2
    tail -n 20 "$TMP/codex.log" >&2
    exit 5
  fi
  if build_report "$TMP/last.$attempt" "$TMP/report.json" "$TMP/errors.$attempt"; then
    mkdir -p .work/issues
    [ -e "$OUT" ] && die 2 "report appeared during the run, refusing to overwrite: $OUT"
    cp "$TMP/report.json" "$OUT"
    python3 -I - "$OUT" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
count = {s: sum(i["severity"] == s for i in r["issues"]) for s in ("blocking", "major", "minor")}
print(f"{sys.argv[1]}: verdict {r['verdict']}, "
      f"blocking {count['blocking']}, major {count['major']}, minor {count['minor']}")
PY
    exit 0
  fi
  echo "codex_review: attempt $attempt produced invalid output:" >&2
  sed 's/^/  /' "$TMP/errors.$attempt" >&2
done
die 4 "invalid output twice. Nothing written. Escalate to the human."
