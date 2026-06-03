#!/usr/bin/env bash
# PreCompact: nudge Claude to capture a knowledge base entry before context is lost.
jq -nc '{
  decision: "block",
  reason: "Before compacting: invoke the knowledge-base skill to capture an entry from this session. Once it is written and committed, compaction can proceed.",
  hookSpecificOutput: {
    hookEventName: "PreCompact",
    additionalContext: "Context is about to compact. Run the /knowledge-base skill now to capture this session before detail is lost, then continue."
  }
}'
