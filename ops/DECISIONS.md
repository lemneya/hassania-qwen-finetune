# DECISIONS LOG

## 2026-01-06
- Decision: GitHub repo is the Single Source of Truth (SSOT). Chats are disposable.
  - Why: eliminates context decay + session amnesia + repo drift.
- Decision: No PR = no progress.
  - Why: forces artifacts, tests, evidence, and history.
- Decision: Multi-agent workflow with defined roles.
  - Why: CEO (user) oversees, ChatGPT as Gatekeeper (strategy/red-team), Manus as Builder, Claude as Orchestrator.
- Decision: Bilingual templates (English/Arabic) for all PR and gate documentation.
  - Why: ensures clarity for all team members and future freelancers.
- Decision: CI must enforce Evidence section in all PRs.
  - Why: proof beats summaries; prevents "sounds done" without actual verification.
