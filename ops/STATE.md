# OPS STATE (Single Source of Truth)

## Current Snapshot

| Field | Value |
|-------|-------|
| Project | Hassania-Qwen-Finetune |
| Current Gate | HITL-1 |
| Status | IN PROGRESS |
| CEO/Gatekeeper | @lemneya |
| Orchestrator | Claude |
| Builder | Manus |

## One-liner Objective
Establish human oversight controls (HITL) so the CEO manages a governed production line.

## CEO Control Knobs (Cockpit Metrics)

| Metric | Target | Current | Description |
|--------|--------|---------|-------------|
| pass@1 | 80% | -- | PRs that pass CI on first try |
| escalation_cap | 2 | 0 | Max escalation issues per gate |
| cost_per_success | Track | -- | Time/effort per merged PR |
| sampling_rate | 33% | -- | Review rate for L1 PRs |

## Risk Ladder Summary

| Level | Name | Approval | Auto-merge |
|-------|------|----------|------------|
| L0 | Safe | None | Yes |
| L1 | Normal | 1 human | No |
| L2 | Sensitive | 2 humans | No |
| L3 | Critical | CEO Gate | No |

## Hard Constraints (Must Not Break)

1. Proof > summaries. Claims require logs/tests/examples.
2. No scope creep: only what's inside the current Gate file.
3. No progress unless committed in repo and linked from a PR.
4. L2/L3 changes require two-key approval.

## HITL Loops Active

| Loop | Name | Status |
|------|------|--------|
| A | Intent Control (CEO approves Gates) | Active |
| B | Quality Control (QA reviews evidence) | Pending QA Sheriff |
| C | Risk Control (Two-key for L2/L3) | Active via CODEOWNERS |

## Definitions (Canonical)

- **Gate**: A scoped unit with objective + acceptance criteria + evidence requirements.
- **Evidence**: Test output, logs, screenshots, recordings, or reproducible steps.
- **HITL**: Human-in-the-Loop checkpoint requiring human approval.
- **Risk Level**: L0 (Safe) / L1 (Normal) / L2 (Sensitive) / L3 (Critical)

## Tooling Reality

- Chat tools are NOT memory.
- Repo files ARE memory.
- AI without HITL is just automation risk.

## Links

| Resource | Path |
|----------|------|
| Gates folder | /gates |
| Evidence ledger | /ops/EVIDENCE.md |
| Next tasks | /ops/NEXT.md |
| Decisions log | /ops/DECISIONS.md |
| HITL Policy | /ops/HITL_POLICY.md |
| QA Checklist | /ops/QA_SHERIFF_CHECKLIST.md |
