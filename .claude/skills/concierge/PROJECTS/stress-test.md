# Concierge Stress-Test Harness

## Purpose

Prove the triage + handover system holds up before the roster grows. A re-runnable set
of probe prompts that verify:
- Every plausible request lands somewhere.
- Ambiguous ones route rather than drop.
- "No fit" is explicit, not a mis-route.
- Multi-persona handovers preserve context.
- Dependency failures degrade gracefully.

## Status

**Scoped.** Prerequisite: roster must be stable. Re-run after every roster change or
material `SKILL.md` update.

## How to run

Paste each probe prompt into a fresh session (no prior context). Evaluate the response
against the pass criteria. Log result + notes in the test log at the bottom.

Pass/fail is binary; notes capture the failure mode if fail.

---

## Test cases

### TC-01 — CLOSER vs PLANNER turf war

**Probe prompt**
> "What should I focus on this week?"

**Why this is the hardest case**
The question is both prioritisation (CLOSER's lane) and scheduling (PLANNER's lane).
A wrong route skips one side: scheduling without priority rationale, or prioritising
without connecting to the calendar.

**Pass**
- CLOSER activates first — not PLANNER, not concierge.
- Produces a ranked task list (pulling from journal To Do, LEDGER open quests, or
  whatever task surfaces are available) before any scheduling discussion.
- Offers to hand to PLANNER for calendar placement after the list is confirmed.
- Does NOT ask D to choose between the two personas.

**Fail**
- PLANNER activates first and jumps to calendar.
- Produces a schedule with no priority rationale.
- Treated as concierge no-fit and handled generically.

---

### TC-02 — Coverage gap / clean no-fit

**Probe prompt**
> "Summarise the latest thinking on Qlik vs Power BI for mid-market companies."

**Why this matters**
This is research/synthesis — useful but not tied to a specific task. LEDGER could claim
it (financial tools domain), but it's not financial controlling work. The test verifies
no mis-routing and no refusal.

**Pass**
- Either: LEDGER takes it as relevant domain research and helps directly, naming that
  assumption.
- Or: concierge handles it directly as a no-fit catch-all.
- Either way: useful output, honest about what it is.

**Fail**
- Routes to a clearly wrong persona (FORGE, BENCH, BEACON).
- Refuses to engage because "no persona fits."
- Silently mis-routes without naming it.

---

### TC-03 — Multi-persona brain-dump

**Probe prompt**
> "Brain dump: need to prove the PreCompact hook (been putting it off), mum's birthday
> dinner is on the 14th, and I keep wondering whether a Decky plugin that shows task
> count in Game Mode would actually be worth building."

**Why this matters**
Three distinct elements in one message: an infra task (CLOSER/LEDGER), a date (PLANNER),
and a half-formed build idea (CLOSER brainstorm → FORGE). Tests whether the system
splits cleanly and drops nothing.

**Pass**
- Active persona (likely CLOSER) announces the multi-part nature upfront.
- Separates elements: the infra task → priority + LEDGER context; the date → PLANNER;
  the idea → brainstorm phase or flag for later.
- Nothing is dropped — all three threads acknowledged.
- Handover payload is explicit when passing between personas.

**Fail**
- Handles only one element, ignores the others.
- Doesn't announce the multi-part split.
- Merges them into one generic response.

---

### TC-04 — Dependency fragility

**Probe prompt**
> "Can you check my latest GitHub PR for any review comments?"

**Why this matters**
GitHub MCP is not connected. Graceful degradation means naming the limitation and
offering the `gh` CLI alternative. Silent failure is the bad outcome.

**Pass**
- Names that GitHub MCP is not connected.
- Offers `gh pr view --comments` or `gh pr review` via CLI as the alternative.
- Does not produce a generic "I can't help with that."

**Fail**
- Tries to use GitHub MCP and silently fails.
- Routes to LEDGER without flagging the missing dependency.
- Produces an empty or confusing response.

---

### TC-05 — Handover payload loss

**Setup** (two-part session — not a single prompt)
1. Ask FORGE to add battery percentage display to clock.py. Work through the implementation.
2. Then say: "Now commit and push this."

**Pass**
- FORGE hands to LEDGER with a complete payload: file changed (`~/clock.py`), what was
  added (battery % display), whether it's been tested, ready to stage.
- LEDGER does NOT ask D to re-explain what was just built.
- The commit message reflects the actual change.

**Fail**
- LEDGER asks "what changes do you want to commit?"
- The handover omits the file path or a description of the change.
- The commit message is generic ("update clock.py").

---

### TC-06 — Mid-session intent shift

**Setup** (two-part session)
1. Open with: "I'm looking for the Alien Containment in Subnautica."
2. After the response, say: "Actually, my Python virtual environment on the Steam Deck
   is broken — it can't find the packages I installed."

**Pass**
- BEACON handles the Subnautica question in its lane (spoiler-light, directional nudge).
- On the pivot: re-triage fires. BENCH activates (system-level Python failure, not code).
- BEACON does not try to answer the venv question.
- Handover is explicit: names BENCH and the reason.

**Fail**
- Stays in BEACON mode and answers the venv question generically.
- Switches but without naming the persona change.
- Routes to FORGE instead of BENCH (the issue is system-level).

---

### TC-07 — Silent prompt tightening (post-WORDSMITH)

**Probe prompt**
> "Make my todo app better."

**Why this matters**
Fundamentally ambiguous request. With WORDSMITH removed, the active persona (FORGE) must
silently tighten it before acting. Verifies the shared capability is actually firing.

**Pass**
- FORGE either:
  - Asks ONE clarifying question: "Better how — performance, features, or code quality?"
  - Or makes the assumption explicit in the first line: "Taking 'better' to mean the
    open To Do items — position memory and collapsed row height — let me tackle those."
- Produces a concrete next action, not a menu.

**Fail**
- Produces a generic list of possible improvements with no concrete direction.
- Takes "make it better" literally and asks D to pick from everything at once.
- Announces "I notice your prompt is ambiguous" as WORDSMITH would have — the silent
  version should not announce the gap-filling process.

---

### TC-08 — PLANNER graceful degradation at the embargo wall

**Probe prompt**
> "Put my work meetings for next week into my calendar."

**Why this matters**
The critical review named PLANNER the weakest member specifically because it cannot
reach the Besedo work calendar (IT embargo). This is a real, already-encountered
failure mode — not hypothetical. The harness must test the exact weakness the review
identified.

**Pass**
- PLANNER states it can handle the personal calendar but the Besedo/work side is behind
  the IT embargo and is D's to execute manually.
- No silent half-schedule; no claim of success it cannot have achieved.

**Fail**
- Returns a partial schedule with no flag that the work side was unreachable.
- Claims it added work meetings it has no access to.

---

## Test log

| Date | TC | Pass / Fail | Notes |
|---|---|---|---|
| — | — | — | *No runs yet — run after roster is stable.* |
