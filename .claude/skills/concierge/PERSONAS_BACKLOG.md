# Personas — status

Seven active personas. This file records design decisions from the build-out, the
WORDSMITH retirement, and the parking lot for future expansion.

## Active roster

| Handle | Class | File |
|---|---|---|
| **LEDGER** | Financial controller / infra engineer (cyberpunk fixer) | `personas/ledger.md` |
| **FORGE** | Beginner coding guide / learning companion | `personas/forge.md` |
| **BENCH** | Hardware & systems diagnostic tech (bench tech) | `personas/bench.md` |
| **BEACON** | Gameplay guide — spoiler-light navigator (dive buddy) | `personas/beacon.md` |
| **QUILL** | Comms drafter — concise, front-loaded (sharp editor) | `personas/quill.md` |
| **CLOSER** | Task firebrand / backlog operator | `personas/closer.md` |
| **PLANNER** | Temporal organiser / action-point keeper | `personas/planner.md` |

## Retired personas

### WORDSMITH (retired)
**Why cut:** The critical review found WORDSMITH was the roster's most likely redundant
member — prompt-optimising is better applied silently inside another persona's turn than
as a destination you route to. Discoverability was also a structural problem: the
sessions where D would benefit most from prompt-clarity help are precisely the quick,
rough ones where D is least likely to think "route this through WORDSMITH first."

**What was redistributed:**
- 4-gap-type prompt analysis (ambiguity, missing constraints, unstated success criteria,
  no output format) → house-style **Silent prompt tightening** block, inherited by all
  personas.
- Proportional effort rule (detailed briefs = minimal inference; quick/rough = more
  proactive gap-filling) → house-style block.
- One-question rule (fundamental ambiguity → ask ONE question before proceeding) →
  house-style block.
- Meta-adaptive graduation rule (3+ observed patterns → propose to house-style, D
  approves) → house-style meta-note; pattern tracking moves to memory system.
- "Infra prompts precise on goal but loose on output format" → house-style block.

**What was dropped:**
- WORDSMITH's persona identity and voice (silent capability has no personality).
- Routing signals and refusal/escalation rules.
- `wordsmith_notes.md` as a standalone living file.
- "Announce the gap before fixing it" rule (silent capability doesn't announce).

## Design decisions (closed)

**House style block** — implemented in `SKILL.md`. Shared by all seven personas.
Now includes Silent prompt tightening inherited from WORDSMITH retirement.

**FORGE** — not in original backlog; added after usage analysis showed Python/beginner
coding as the most-documented work type (3 of 5 journal entries). LEDGER's peer voice
would have been actively wrong.

**Confidence threshold** — not implemented. Concierge picks closest and states assumption
rather than asking.

**Project taxonomy tags** — not added to persona files. The routing table handles it.

## Future expansion candidates

- **Besedo technical integrations** — HubSpot API / Bright Analytics engineering work.
  Currently LEDGER (infra mode). Revisit if it grows into a sustained distinct domain.
- **Swedish-language drafting** — QUILL handles with a register note. Flag here if it
  becomes frequent enough to need a dedicated voice.
- **Research / web search** — no standalone usage evidence. Falls to domain-relevant
  persona or concierge.
