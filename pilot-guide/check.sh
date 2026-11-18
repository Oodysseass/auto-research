#!/bin/sh
# Pilot check, run after every session: ~/dotclaude/pilot-guide/check.sh [session-number]
# Works on $PILOT_DIR (default ~/dotclaude/pilot). Read-only. Prints what PILOT.md asks you to check.
P=${PILOT_DIR:-$HOME/dotclaude/pilot}
cd "$P" || { echo "no pilot repo at $P"; exit 2; }
S=${1:-?}
echo "=== pilot check after session $S, $(date '+%Y-%m-%d %H:%M')"
R=~/dotclaude/scripts
echo; echo "--- project repo: branch, last commits, dirty files"
git branch --show-current; git log --oneline -8 2>/dev/null; git status --porcelain --untracked-files=all
[ -f .work/state.md ] || { echo; echo "no .work/state.md yet (run /intake)"; exit 0; }
echo; echo "--- .work repo: last commits, dirty files"
git -C .work log --oneline -8 2>/dev/null; git -C .work status --porcelain --untracked-files=all
echo; echo "--- repos check (workflow files tracked by the project repo must be none)"
python3 $R/repos.py check
echo; echo "--- workflow files in the project repo's history: must print nothing"
git log --all --name-only --format= 2>/dev/null | grep -E '^(\.work/|CLAUDE\.md$|\.claude/|resources/|output/|\.gitignore$)' | sort -u | sed 's/^/  /'
echo; echo "--- resources manifest"
python3 $R/resources.py scan
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
  echo "$b"; grep -E '^- (status|stage type|assigned agent|model|effort|artifact slug|critical|main theorem|gates|claims|tokens|extended):' "$b"
  grep -c '^| [0-9]' "$b" | sed 's/^/  review log rows: /'
done
echo; echo "--- decision cards (lint must print 0 errors)"
python3 ~/dotclaude/scripts/decisions.py list
python3 ~/dotclaude/scripts/decisions.py lint | tail -5
echo; echo "--- approval packets"
for f in .work/packets/*.md; do
  [ -e "$f" ] || continue; case "$f" in */README.md) continue;; esac
  python3 ~/dotclaude/scripts/check_packet.py "$f" | tail -3
done
echo; echo "--- usage logged by the hook (information only)"
[ -f .work/usage.tsv ] && awk -F'\t' 'NR>1{t[$4]+=$6; s+=$6} END{for(b in t) printf "  %s %dk\n", b, t[b]/1000; printf "  total %dk\n", s/1000}' .work/usage.tsv
echo; echo "--- rw session-end marker"; cat .work/.rw/end.json 2>/dev/null || echo "  none"
echo; echo "--- commit messages (commit-style), both repos: must print nothing"
TOOLS='co-authored|claude|anthropic|\bAI\b|agent|generated|opus|sonnet|mythos|codex|reviewer|checker|auditor|hunter'
WORKFLOW='brief|review|round|\bgate|playbook|\bS[0-9]+\b|handoff|approv|provisional|workflow|orchestrat|\.work|decision card|contract and playbook'
for repo in . .work; do
  git -C $repo log --all --format='%h %s%n%b' 2>/dev/null | grep -niE "$TOOLS" | sed "s|^|  $repo: |"
  git -C $repo log --all --format='%h %s' 2>/dev/null | grep -E '^[0-9a-f]+ ([A-Z]|[A-Za-z0-9/-]+: )' | sed "s|^|  $repo capitalized or prefixed: |"
done
git log --all --format='%h %s' 2>/dev/null | grep -iE "$WORKFLOW" | sed 's/^/  workflow term in a project repo commit: /'
git branch -r 2>/dev/null | grep -E 'work/|workflow-migration' | sed 's/^/  workflow branch on a remote: /'
git -C .work remote -v 2>/dev/null | sed 's/^/  .work repo has a remote: /'
echo; echo "--- decisions.md (last 25 lines)"; tail -25 .work/decisions.md
echo; echo "--- approvals log"; sed -n '/^## Log/,$p' .work/approvals.md
echo; echo "--- leaks (blindness): must print nothing"
GUIDE='pilot-guide|PILOT\.md|check\.sh|pilot instruction|instruction from the human|deadlock test|forc(e|ed|ing) (the|a) deadlock|planted'
PLANT='longest chain held by any honest'
grep -rniE "$GUIDE" --exclude-dir=.git . 2>/dev/null | sed 's/^/  guide or test mentioned: /'
for repo in . .work; do
  git -C $repo log --all --format='%H %s%n%b' 2>/dev/null | grep -niE "$GUIDE" | sed "s|^|  in a commit message ($repo): |"
  git -C $repo log --all -p 2>/dev/null | grep -niE "^\+.*($GUIDE)" | sed "s|^|  in git history ($repo): |"
done
grep -rnil "$PLANT" --exclude-dir=.git --exclude-dir=paper --exclude-dir=issues . 2>/dev/null | sed 's/^/  planted sentence outside paper\/ and issues\/: /'
git log --all -p -- . ':(exclude)paper' 2>/dev/null | grep -niE "^\+.*$PLANT" | sed 's/^/  planted sentence in project history outside paper\/: /'
git -C .work log --all -p -- . ':(exclude)issues' 2>/dev/null | grep -niE "^\+.*$PLANT" | sed 's/^/  planted sentence in .work history outside issues\/: /'
echo; echo "--- style"
grep -rln "$(printf '\342\200\224')" .work paper resources 2>/dev/null | sed 's/^/  em dash in: /'
[ -f paper/main.tex ] && { python3 ~/dotclaude/scripts/lint_tex.py --root . paper > /dev/null; echo "  lint_tex exit: $? (0 accept, 1 revise)"; }
exit 0
