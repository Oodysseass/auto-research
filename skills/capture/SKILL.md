---
name: capture
description: Capture dialog of a research workflow project (.work/). Lists ideas, open questions, dead ends, decisions and agenda changes from the discussion in one multi-select dialog, writes only what the human ticks, and a one-page session summary. Usage /capture, or when the converse skill offers it at a natural break, or when the session start reports a pending capture.
---

# Capture

Script: `C=~/dotclaude/scripts/capture.py`, agenda: `A=~/dotclaude/scripts/agenda.py` (`python3 $C ...`, from the project root).

1. Source. This session's discussion since the last capture. For a pending stub from the session start, read the stub's
   transcript (the human's messages and your answers) instead, and pass the stub path to `summary --covers` in step 5.
2. Candidates, each one line, self-contained (names the subject; never "the above"):
   - idea or hypothesis; open question;
   - dead end (what was tried, why it failed);
   - decision the human took in discussion (a choice of direction, an interpretation of the model);
   - agenda change: a new thread to explore, or a thread to reorder, park or drop.
   Leave out anything already in `ideas.md`, `deadends.md`, `decisions.md` or `threads.md`.
   None: say "Nothing new to capture." and stop.
3. Ask with AskUserQuestion, `multiSelect: true`, one question per kind that has candidates, at most 4 options each and
   4 questions per call (more: a second call). Label: the item in at most 5 words. Description: the full line. Recommend
   nothing; the human ticks what to keep.
4. Write only ticked items:
   - idea or question: `python3 $C idea --text "<line>" --kind idea|question --session <session id>`
   - dead end: `python3 $C deadend --what "<what>" --why "<why>" --ref "<I-ID, C-ID or discussion>"`
   - decision: `python3 $C decision --title "<one line>" --reason "<one line>"`
   - new thread: `python3 $A --by human add --title "<title>" --goal "<goal>" --status exploring`. Reorder, park, resume or drop
     of an existing thread is an agenda change: it goes through the `request` skill (it may need a card), not here.
5. Summary: write at most one page to a scratch file (what was discussed, what was concluded, what stays open, the IDs
   written in step 4), then `python3 $C summary --session <session id> --file <file> [--covers <stub path> ...]`.
6. Commit the `.work` repo: `git -C .work add -A && git -C .work commit -m "record discussion of <topic>"`. Nothing in the
   project repo.
7. Reply in one line: what was kept, with IDs.
