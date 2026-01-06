# DECISIONS LOG

## 2026-01-06 — HITL Governance

| Decision | Rationale |
|----------|-----------|
| Implement 4-level risk ladder (L0-L3) | Allows agents to run fast on low risk, but must stop on high risk |
| L0 can auto-merge | Docs/formatting don't need human review |
| L2/L3 require two-key approval | Prevents catastrophic mistakes in sensitive areas |
| QA Sheriff role created | Separates quality control from CEO intent control |
| CEO control knobs in STATE.md | Makes factory measurable (pass@1, escalation_cap, etc.) |
| HITL escalation triggers defined | Converts "agent confusion" into visible CEO decision points |

## 2026-01-06 — SSOT Bootstrap

| Decision | Rationale |
|----------|-----------|
| GitHub repo is the Single Source of Truth (SSOT) | Eliminates context decay + session amnesia + repo drift |
| No PR = no progress | Forces artifacts, tests, evidence, and history |
| Multi-agent workflow with defined roles | CEO (user) oversees, ChatGPT as Gatekeeper, Manus as Builder, Claude as Orchestrator |
| Bilingual templates (English/Arabic) | Ensures clarity for all team members and future freelancers |
| CI must enforce Evidence section in all PRs | Proof beats summaries; prevents "sounds done" without verification |
