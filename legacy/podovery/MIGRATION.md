# podovery: migration notes

Items prompt 03 must apply when migrating the podovery project.

1. `glossary.md` (this folder) becomes the project's `.work/glossary.md`.
2. `writing_style_excerpts.md` (this folder) holds the podovery text removed from the global style files. Place it per the notes in that file.
3. `review-spec` moves into the project: copy `legacy/commands/review-spec.md` to `<podovery>/.claude/commands/review-spec.md`.
   It depends on the project's DROP list in its `CLAUDE.md`, so it is not global.
   After the copy works in the project, remove the global symlink `~/.claude/commands/review-spec.md`. Keep the file in `legacy/commands/`.
