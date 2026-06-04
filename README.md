# Claude Code Skills & Hooks — Setup Guide
*For anyone cloning this system from github.com/mellowyellow5/claude*

---

## What you're getting

This repo contains a personal Claude Code configuration — a skill and a hook that work together to automatically capture learning journal entries before context is lost.

| Component | What it does |
|---|---|
| `/knowledge-base` skill | Writes a structured 8-field journal entry to `~/knowledge-base/JOURNAL.md` on demand |
| `PreCompact` hook | Fires automatically before Claude Code compacts context — blocks compaction and nudges you to capture the session first |
| Journal repo | `~/knowledge-base/JOURNAL.md` — the actual journal, version-controlled separately |

---

## Prerequisites

- Claude Code installed and working
- Git installed (`git --version`)
- jq installed (`which jq`; if missing: `sudo apt install jq` or `sudo pacman -S jq` on Steam Deck)
- SSH key configured for GitHub (`ssh -T git@github.com`)

---

## Step 1 — Clone the journal repo

```bash
git clone git@github.com:mellowyellow5/knowledge-base.git ~/knowledge-base
```

---

## Step 2 — Copy config files into place

```bash
git clone git@github.com:mellowyellow5/claude.git ~/claude-setup
mkdir -p ~/.claude/skills ~/.claude/hooks
cp -r ~/claude-setup/.claude/skills/knowledge-base ~/.claude/skills/
cp    ~/claude-setup/.claude/hooks/precompact-journal.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/precompact-journal.sh
```

---

## Step 3 — Register the hook in settings.json

If `~/.claude/settings.json` does not exist yet:

```bash
cat > ~/.claude/settings.json << 'EOF'
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/precompact-journal.sh"
          }
        ]
      }
    ]
  }
}
EOF
```

If it already exists, merge the hooks block in manually alongside existing keys.

---

## Step 4 — Verify

```bash
ls -la ~/knowledge-base/JOURNAL.md \
       ~/.claude/skills/knowledge-base/SKILL.md \
       ~/.claude/hooks/precompact-journal.sh \
       ~/.claude/settings.json

bash ~/.claude/hooks/precompact-journal.sh | jq .
```

Hook output should be JSON with `decision: "block"`.

---

## Step 5 — Restart Claude Code

Skills are only discovered at startup. Exit and relaunch, then test:

- `/knowledge-base` — should be recognised as a command
- `/hooks` — should show precompact-journal.sh under [User]
- `/compact` — full end-to-end test; hook should block and prompt for journal entry

---

## Day-to-day usage

**Automatic:** Hook fires before compaction, blocks it, prompts you to run `/knowledge-base` first.

**Manual:** Type `/knowledge-base` any time to capture a session.

**After each entry:** Skill stages a commit but does NOT push. Review then:
```bash
git -C ~/knowledge-base push
```

---

## Journal entry format (8 fields)

```
### YYYY-MM-DD — <short session title>
**Category:** <domain>
**Phase:** <Planning | Development | Debugging | Refactor | Research>
**Goal:** <what we set out to do>
**Context at start:** <state before this session>
**Journey:** <what was tried, key decisions, pivots>
**Dead ends:** <approaches that failed and WHY>
**Key learnings:** <durable, reusable insights>
**Real examples:** <concrete commands, paths, errors>
**State at end:** <what changed, what now works>
**Left open:** <unresolved threads, next steps>
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/knowledge-base` unknown command | Claude Code started before skill existed | Restart Claude Code |
| Hook fires but no nudge | Hook outputs plain text not JSON | Check `bash ~/.claude/hooks/precompact-journal.sh | jq .` |
| `jq: command not found` | jq not on PATH in hook env | Install jq or hardcode `/usr/bin/jq` in hook script |
| `~` not expanding | Some envs don't expand `~` in hook commands | Replace `~/.claude` with `${HOME}/.claude` in settings.json |
| Push rejected | Remote has commits you lack | `git -C ~/knowledge-base pull --rebase` then push |

---

## File locations

```
~/.claude/
├── settings.json
├── hooks/
│   └── precompact-journal.sh
└── skills/
    └── knowledge-base/
        └── SKILL.md

~/knowledge-base/
└── JOURNAL.md
```
