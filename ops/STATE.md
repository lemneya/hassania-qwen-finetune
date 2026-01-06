# OPS STATE (Single Source of Truth)

## Current Snapshot
- Project: Hassania-Qwen-Finetune
- Current Gate: SSOT-1
- Status: IN PROGRESS  <!-- IN PROGRESS | READY FOR REVIEW | DONE -->
- Owner:
  - Gatekeeper: ChatGPT
  - Orchestrator: Claude
  - Builder: Manus

## One-liner Objective
Establish the SSOT infrastructure so all future work flows through Issues → PRs → CI proof.

## Hard Constraints (Must Not Break)
- Proof > summaries. Claims require logs/tests/examples.
- No scope creep: only what's inside the current Gate file.
- No progress unless committed in repo and linked from a PR.

## Definitions (Canonical)
- Gate: a scoped unit with objective + acceptance criteria + evidence requirements.
- Evidence: test output, logs, screenshots, recordings, or reproducible steps.

## Tooling Reality
- Chat tools are NOT memory.
- Repo files ARE memory.

## Links
- Gates folder: /gates
- Evidence ledger: /ops/EVIDENCE.md
- Next tasks: /ops/NEXT.md
