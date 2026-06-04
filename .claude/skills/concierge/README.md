# Concierge

A front-door **triage and persona-handoff** layer for Claude. The concierge reads the
opening prompt, classifies the work, and hands off to the most fitting specialist
persona — adopting that persona's voice, priorities, and default tools for the turn.

A maître d', not a cook: it doesn't do the work, it seats you at the right table.

## Why

One account, many work types — financial controlling, infrastructure/skills
engineering, gameplay, hardware, drafting. A single generic voice serves all of them
adequately and none well. Personas let each response carry the right priorities and
defaults.

In the project taxonomy this is a **System** (ongoing, self-maintaining infrastructure).

## Layout

```
concierge/
├── SKILL.md            # the triage logic + routing table + registry
├── README.md           # this file
├── PERSONAS_BACKLOG.md  # planned personas to flesh out
└── personas/
    └── ledger.md       # financial controller / infra engineer (cyberpunk fixer)
```

## How it routes

See the routing table in `SKILL.md`. Match on intent, hand off, become the persona.
Ambiguous → ask one short question or pick closest and state the assumption. No fit →
stay neutral concierge.

## Status

- **LEDGER** — defined (`personas/ledger.md`). Financial + infrastructure.
- Gameplay guide, hardware tech, comms drafter — planned (see backlog).

## New-machine setup

This is a Claude.ai / Claude Code **skill**. Drop the folder into your skills directory
(e.g. `~/.claude/skills/concierge/`). If hooks are ever added here, remember
`chmod +x hooks/*.sh` after clone — the execute bit doesn't always survive.
