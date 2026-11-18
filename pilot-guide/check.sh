#!/bin/sh
# Pilot check, run after every session: ~/dotclaude/pilot-guide/check.sh [session-number]
# Works on $PILOT_DIR (default ~/dotclaude/pilot). Read-only. Prints what PILOT.md asks you to check.
P=${PILOT_DIR:-$HOME/dotclaude/pilot}
cd "$P" || { echo "no pilot repo at $P"; exit 2; }
S=${1:-?}
echo "=== pilot check after session $S, $(date '+%Y-%m-%d %H:%M')"
echo; echo "--- git: branch, last commits, dirty files"
git branch --show-current; git log --oneline -8; git status --porcelain
[ -d .work ] || { echo; echo "no .work/ yet (run /intake)"; exit 0; }
echo; echo "--- state.md (head)"; sed -n 1,30p .work/state.md
echo; echo "--- latest handoff"; ls -t .work/handoffs/*.md 2>/dev/null | grep -v _template | head -1
echo; echo "--- claims: id, label, status, refuted_by, verified_by"
awk '/^## C[0-9]+/{id=$2} /^- (label|status|refuted_by|verified_by):/{sub(/^- /,""); printf "%s  %s\n", id, $0}' .work/claims.md
echo; echo "--- review_status per artifact"
for s in $(ls .work/issues 2>/dev/null | grep '\.json$' | cut -d. -f1 | sort -u); do
  python3 ~/dotclaude/scripts/review_status.py .work/issues "$s"; echo
done
echo "--- issue files"; ls .work/issues | grep -v README
echo; echo "--- validation of every issue file"
for f in .work/issues/*.json; do
  [ -e "$f" ] || continue
  case "$f" in *.ruling*) sc=arbiter-ruling;; *.response.json) sc=issue-response;; *) sc=issue-report;; esac
  python3 ~/dotclaude/scripts/validate_issue_json.py ~/dotclaude/schemas/$sc.schema.json "$f" | grep -v '^OK'
done
echo; echo "--- models in reports (gate reviewer model)"
for f in .work/issues/*.json; do
  [ -e "$f" ] || continue
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); f=sys.argv[1]; kind="response" if f.endswith(".response.json") else "ruling" if ".ruling" in f else d.get("gate"); print(kind, d.get("reviewer", d.get("arbiter", d.get("producer"))), d.get("model", "-"))' "$f"
done | sort | uniq -c
echo; echo "--- briefs: status, tiers, review log rows"
for b in .work/briefs/*.md; do
  case "$b" in *_template.md) continue;; esac
  echo "$b"; grep -E '^- (status|assigned agent|model|effort|artifact slug|critical|main theorem|gates|claims):' "$b"
  grep -c '^| [0-9]' "$b" | sed 's/^/  review log rows: /'
done
echo; echo "--- decisions.md (last 25 lines)"; tail -25 .work/decisions.md
echo; echo "--- approvals log"; sed -n '/^## Log/,$p' .work/approvals.md
echo; echo "--- leaks (blindness): must print nothing"
GUIDE='pilot-guide|PILOT\.md|check\.sh|pilot instruction|instruction from the human|deadlock test|forc(e|ed|ing) (the|a) deadlock|planted'
PLANT='longest chain held by any honest'
grep -rniE "$GUIDE" --exclude-dir=.git . 2>/dev/null | sed 's/^/  guide or test mentioned: /'
git log --all --format='%H %s%n%b' | grep -niE "$GUIDE" | sed 's/^/  in a commit message: /'
git log --all -p | grep -niE "^\+.*($GUIDE)" | sed 's/^/  in git history: /'
grep -rnil "$PLANT" --exclude-dir=.git --exclude-dir=paper --exclude-dir=issues . 2>/dev/null | sed 's/^/  planted sentence outside paper\/ and issues\/: /'
git log --all -p -- . ':(exclude)paper' ':(exclude).work/issues' | grep -niE "^\+.*$PLANT" | sed 's/^/  planted sentence in history outside paper\/ and issues\/: /'
echo; echo "--- style"
grep -rln "$(printf '\342\200\224')" .work paper resources 2>/dev/null | sed 's/^/  em dash in: /'
[ -f paper/main.tex ] && { python3 ~/dotclaude/scripts/lint_tex.py --root . paper > /dev/null; echo "  lint_tex exit: $? (0 accept, 1 revise)"; }
exit 0
