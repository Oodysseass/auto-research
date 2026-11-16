# Reviewer write guard

Second layer of reviewer write enforcement. The first layer is the PreToolUse hook (Stage 5).
The orchestrator runs this procedure around every reviewer dispatch (G1 to G4, any tier, and Codex at G3).

## Before dispatch

1. Commit all pending work. `git status --porcelain` must print nothing. If it does not, do not dispatch.
2. Record `base=$(git rev-parse HEAD)`.

## After the reviewer returns

1. Run `git status --porcelain --untracked-files=all`.
2. Allowed: new untracked files under `.work/issues/` whose names start with `<artifact-slug>.<gate>.<reviewer>.r<round>`.
3. Violation: any other line. This includes a change outside `.work/issues/`, a change to an existing file in `.work/issues/`,
   a deletion, and a new file in `.work/issues/` with another reviewer's or another round's name.
4. On a violation:
   1. Revert tracked changes: `git restore --staged --worktree --source="$base" -- <path>` for each tracked path listed.
   2. Remove untracked files the reviewer created: `git clean -f -- <path>` for each untracked path listed, including the reviewer's own report.
      The tree was clean at dispatch, so every untracked file is the reviewer's.
   3. Check that `git status --porcelain` prints nothing.
   4. Discard the review. Its issues do not count toward any round, and the round is rerun.
   5. Append to `decisions.md`: date, `made by: orchestrator`, "reviewer write violation", the reviewer, model, round, the paths it touched, and "review discarded, changes reverted".
   6. A second violation by the same reviewer on the same artifact is a deadlock. Escalate to the human.
5. On no violation: validate the report with `scripts/validate_issue_json.py`, then commit the new files.
