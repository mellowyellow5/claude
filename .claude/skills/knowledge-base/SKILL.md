---
name: knowledge-base
description: Capture a structured knowledge-base entry from the current session. Use when context is about to compact, when the user invokes /knowledge-base, or when the user asks to log/journal what was learned. Fires proactively for sessions involving Steam Deck, Besedo, GitHub, Claude Code, PyQt5, MCP, hooks, debugging, or building anything. Mines the conversation for decisions, dead ends, and reusable insight, then prepends a dated entry to ~/knowledge-base/JOURNAL.md and stages a commit for review.
---

# Knowledge Base Entry

## When to run
- User invokes `/knowledge-base`
- A PreCompact nudge asks to capture the session before compaction
- User asks to log, journal, or capture what happened
- Proactively offer at the end of any session that involved building, debugging, or learning something reusable

## Capture philosophy
Capture broadly — the user prunes later. The most valuable content is the *dead ends*: approaches that failed and why. A future reader (human or AI) should be able to avoid the same wall. Routine noise can be skipped, but when in doubt, include it.

## Procedure
1. Review the session. Identify every candidate learning, decision, and dead end.
2. Read ~/knowledge-base/JOURNAL.md to match format and avoid duplicating an entry already written this session.
3. Compose ONE entry in the format below.
4. PREPEND it directly under the header block, before the first existing entry (newest-first).
5. Stage and commit in the knowledge-base repo, then STOP. Do not push. Show the user the diff and ask them to review before pushing.

## Entry format
Dated `###` heading, newest at top:

```
### YYYY-MM-DD — <short session title>
**Category:** <domain, e.g. Claude Code tooling | Git | Steam Deck>
**Phase:** <Planning | Development | Debugging | Refactor | Research>

**Goal:** <what we set out to do>

**Context at start:** <state before this session — the cold-start picture>

**Journey:** <the arc: what was tried, key decisions, pivots, in order>

**Dead ends:** <every approach that failed and WHY — the most valuable field>

**Key learnings:** <durable, reusable insights as bullets>

**Real examples:** <concrete commands, file paths, error messages, snippets>

**State at end:** <concrete delta: what changed, what now works>

**Left open:** <unresolved threads, next steps>
```

## Git step
After writing, run:
```
git -C ~/knowledge-base add JOURNAL.md
git -C ~/knowledge-base commit -m "Journal: <session title> (YYYY-MM-DD)"
git -C ~/knowledge-base --no-pager diff HEAD~1 HEAD
```
Then tell the user:
"Entry committed locally. Review the diff, then push when ready."
