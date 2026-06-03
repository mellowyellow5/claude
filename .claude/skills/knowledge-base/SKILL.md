# Skill: knowledge-base

## Trigger
User types `/knowledge-base` (with or without a description after it).

## What to do

Write a new journal entry into `~/knowledge-base/JOURNAL.md` by prepending it after the header block (before the first `---` entry divider).

### Entry format

```
### YYYY-MM-DD — <one-line title describing what was built or learned>
**Category:** <comma-separated topics, e.g. Python | Git | Steam Deck / Linux>

**Goal:** <one sentence — what we were trying to achieve>

**What happened:**
<2–4 sentences. Tell the story: what was tried, what broke, how it was fixed.
Write it in plain English as if explaining to a beginner who wasn't there.>

**Key learnings:**
- <concrete fact or rule learned, written as a standalone sentence>
- <another learning — be specific, not vague like "learned about git">
- ...

**Real examples from this session:**
```bash
# short comment explaining what this does
<actual command or code snippet used>
```

**Left open:**
- <anything unfinished, still broken, or worth revisiting next time>
- ...

---
```

### Rules
- Use today's date (from context: `currentDate`).
- Draw the content from the current conversation — what the user actually built, broke, fixed, and learned.
- Key learnings must be concrete and reusable — things a beginner could apply next time without needing to re-derive them.
- Real examples must be commands or code that were actually run in this session.
- "Left open" captures genuinely unfinished threads, not a summary of the session.
- Append the new entry at the top of the journal (directly after the title + intro block, before the previous entry).
- Do not truncate or remove existing entries.
- Confirm to the user when done and show them the title of the new entry.
