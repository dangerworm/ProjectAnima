# context

Operational records for the current development session and ongoing work tracking.

## Files

| File                       | Purpose                                                                                                                                                           |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `session.md`               | **Read this before starting implementation work.** Current system state, what was done last session, blockers, and the next action. Rewritten fresh each session. |
| `snagging.md`              | Running list of known issues, visual bugs, and deferred items. Add here rather than inline `TODO` comments.                                                       |
| `note-to-next-instance.md` | A note from the most recent Claude instance to the next — what felt significant, what didn't fit in `session.md`. Read this alongside `session.md`.               |
| `next-prompt.txt`          | Scratch file used during session handoffs. Not for general use.                                                                                                   |

## sessions/

Archive of all prior session logs and note-to-next files, one file each, named `YYYY-MM-DD-title.md`
or `YYYY-MM-DD-HHMM-note-to-next.md`.

Read these only when you need history on a specific decision or want to understand why something was
built a certain way. They are not required reading at session start.

## Session handoff protocol

At the end of every session (defined in `CLAUDE.md`):

1. Archive `context/session.md` → `context/sessions/YYYY-MM-DD-slug.md`
2. Write a fresh `context/session.md` with only the current session's content
3. Write `context/sessions/YYYY-MM-DD-HHMM-note-to-next.md`
