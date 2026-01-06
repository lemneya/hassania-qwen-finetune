# DECISIONS LOG

## 2026-01-06 — AUTOCLAUDE-0 (Auto-Claude Governance)

| Decision | Rationale |
|----------|-----------|
| Two-Step PR for L2/L3 | Spec PR locks intent before Build PR executes |
| Memory OFF for L2/L3 | Prevents context leakage on sensitive work |
| WIP limit of 3 | Prevents chaos from too many parallel tasks |
| AI merge is suggestion-only | Humans must approve all merges |
| Escalation triggers defined | Auto-Claude must STOP and open Issue when stuck |

## 2026-01-06 — HITL Governance

| Decision | Rationale |
|----------|-----------|
| Implement 4-level risk ladder (L0-L3) | Allows agents to run fast on low risk, but must stop on high risk |
| L0 can auto-merge | Docs/formatting don't need human review |
| L2/L3 require two-key approval | Prevents catastrophic mistakes in sensitive areas |
| QA Sheriff role created | Separates quality control from CEO intent control |

## 2026-01-06 — SSOT Bootstrap

| Decision | Rationale |
|----------|-----------|
| GitHub repo is the Single Source of Truth (SSOT) | Eliminates context decay + session amnesia + repo drift |
| No PR = no progress | Forces artifacts, tests, evidence, and history |
| Multi-agent workflow with defined roles | CEO oversees, ChatGPT as Gatekeeper, Manus/Auto-Claude as Builder |
