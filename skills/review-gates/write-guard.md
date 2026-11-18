# Reviewer write guard

Second layer of reviewer write enforcement. The first layer is the PreToolUse hook in `~/dotclaude/hooks/rw_hooks.py`:
it denies any Write, Edit or NotebookEdit by a reviewer or arbiter except creating a new file in `.work/issues/`. It cannot see Bash writes, so this procedure still runs.
The orchestrator runs this procedure around every reviewer dispatch (G1 to G4, any tier, and Codex at G3)
and every arbiter dispatch. For an arbiter, "reviewer" below means the arbiter.

A project has two repos: the project repo and the `.work` repo (`scripts/repos.py`). The project repo excludes `.work/`, so
its `git status` never shows a change to `.work/claims.md` or any other workflow file. The guard checks both repos, always through
`repos.py`, never with a plain `git status`.

The project may live in a subdirectory of the project repo (`reports/02-mitigations/`), next to coauthors' folders or
sibling projects. Then the guard covers that subdirectory only: changes elsewhere in the repo never block dispatch and are
never violations, and the project part of `base` is the last commit that touched the subdirectory, so a commit elsewhere
does not count as a moved HEAD. A revert touches only the subdirectory.

## Before dispatch

1. Commit all pending work, in the repo it belongs to (project repo: `repos.py commit`). `base=$(python3 ~/dotclaude/scripts/repos.py guard-begin)` must succeed:
   it exits 2 and lists the dirty paths if either repo is not clean. If it fails, do not dispatch.
2. Keep `base` (`<project HEAD>+<.work HEAD>`) for the check.

## After the reviewer returns

1. Run `python3 ~/dotclaude/scripts/repos.py guard-check --base "$base" --allow .work/issues/<artifact-slug>.<gate>.<reviewer>.r<round>`.
   For an arbiter, `--allow` names only the ruling file in its prompt, `.work/issues/<artifact-slug>.<gate>.<reviewer>.i<n>.ruling<k>.json`.
2. Allowed: new untracked files under `.work/issues/` whose names start with the `--allow` prefix.
3. Violation (exit 3): anything else, in either repo. This includes a change outside `.work/issues/` (in the paper, or in
   `.work/claims.md`, `.work/model.md` and the other `.work/` files), a change to an existing file in `.work/issues/`, a deletion,
   a new file with another reviewer's or another round's name, and a commit in either repo.
4. On a violation:
   1. Revert both repos: rerun the check with `--revert`. It restores tracked paths to the base and removes every untracked file,
      the reviewer's own report included (both trees were clean at dispatch, so every untracked file is the reviewer's).
   2. A moved HEAD is not reset automatically. Inspect it; resetting it is a blocking card ("Deleting or overwriting existing files").
   3. Check that `python3 ~/dotclaude/scripts/repos.py status` prints nothing.
   4. Discard the review. Its issues do not count toward any round, and the round is rerun.
   5. Append to `decisions.md`: date, `made by: orchestrator`, "reviewer write violation", the reviewer, model, round,
      the paths it touched, and "review discarded, changes reverted".
   6. A second violation by the same reviewer on the same artifact: rerun once at the next rung of its ladder (logged).
      A third: `/handoff error`. This is not a review deadlock and is not arbitrated, and it is not a research question for the human.
5. On no violation: validate the report with `scripts/validate_issue_json.py`, then commit the new files in the `.work` repo
   (`git -C .work add issues && git -C .work commit`). Message per the `commit-style` skill: "review <artifact>, round <n>".
   No reviewer or model name.
