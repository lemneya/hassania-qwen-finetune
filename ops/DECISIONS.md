# DECISIONS LOG

## 2026-01-06
- Decision: GitHub repo is the Single Source of Truth (SSOT). Chats are disposable.
  - Why: eliminates context decay + session amnesia + repo drift.
- Decision: No PR = no progress.
  - Why: forces artifacts, tests, evidence, and history.
- Decision: Multi-agent workflow with defined roles.
  - Why: CEO (user) oversees, ChatGPT as Gatekeeper (strategy/red-team), Manus as Builder, Claude as Orchestrator.
