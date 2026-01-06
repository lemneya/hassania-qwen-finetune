# HITL Policy (Human-in-the-Loop)

This document defines how humans stay in control while AI agents do the work.

---

## Auto-Claude Integration (Builder Engine)

Auto-Claude is an autonomous builder. It can plan/build/validate with minimal human intervention.
Governance remains SSOT/HITL:

- SSOT: /ops/STATE.md and /gates/*
- Output: PR only (no direct main)
- Evidence required: logs/tests/repro
- Two-Step PR required for L2/L3 (Spec PR → Build PR)
- AI-powered merge is suggestion-only; humans approve final merge
- Memory policy: OFF by default for L2/L3 and client/government work unless explicitly approved

Full rules: `/ops/AUTO_CLAUDE_RULES.md`

---

## Risk Ladder (L0–L3)

| Level | Name | Description | Approval | Auto-merge |
|-------|------|-------------|----------|------------|
| L0 | Safe | Docs, formatting, typos | None | Yes |
| L1 | Normal | Features, non-sensitive code | 1 human | No |
| L2 | Sensitive | Governance, CI, security, infra | 2 humans (Two-Key) | No |
| L3 | Critical | Auth, payments, secrets, client data | CEO Gate + 2 humans | No |

---

## Three Human Loops

| Loop | Name | When | Who |
|------|------|------|-----|
| A | Intent Control | Before work starts | CEO approves Gate spec |
| B | Quality Control | Before merge | QA Sheriff checks evidence |
| C | Risk Control | L2/L3 changes | Two-Key approval required |

---

## Escalation Triggers (Agent Must STOP)

Any agent (Auto-Claude, Manus, Copilot, freelancer) must escalate to CEO if:

1. Requirement is unclear or missing from gate
2. Tests fail repeatedly (>3 attempts)
3. Change requested is outside gate scope
4. Sensitive files touched but Risk Level not declared
5. Secrets, env keys, or credentials needed
6. External API/service credentials required
7. Conflict with existing code that agent cannot resolve

Escalation = Open a GitHub Issue with label `escalation` and tag @lemneya.

---

## Sensitive Paths (Automatic L2+)

Any change touching these paths is automatically treated as L2 or higher:

- `/ops/` — governance files
- `/gates/` — gate specifications
- `/.github/workflows/` — CI/CD
- `/security/` — security code
- `/deploy/` — deployment scripts
- `/infra/` — infrastructure
- `.env` — environment files
- `secrets/` — secrets

---

## Two-Step PR Rule (L2/L3)

For L2/L3 work, the process is:

1. **SPEC PR** — Intent Control
   - Creates or updates the gate file
   - Locks acceptance criteria
   - Approved by CEO + Trusted Enforcer

2. **BUILD PR** — Execution
   - Code + tests + logs + evidence
   - Reviewed under normal HITL/Two-Key rules

L0/L1 can use single PR if scope is clear.

---

## AI Merge Policy

AI agents may SUGGEST conflict resolution.
AI agents must NOT merge automatically.

| Risk Level | AI Suggestion | Human Review |
|------------|---------------|--------------|
| L0/L1 | Allowed | Required |
| L2/L3 | Allowed | Required + detailed review |

---

## Memory Policy (Data Safety)

| Work Type | Memory |
|-----------|--------|
| L0/L1 internal | ON (allowed) |
| L2/L3 | OFF (unless approved in gate) |
| Client work | OFF |
| Government work | OFF |

If memory is enabled:
- Prefer local embeddings/memory store
- Never store secrets, credentials, PII, or sensitive data

---

## Arabic Summary / ملخص بالعربية

سياسة HITL تضمن بقاء البشر في السيطرة:
- سلم المخاطر L0-L3 يحدد مستوى المراجعة
- ثلاث حلقات بشرية: نية، جودة، مخاطر
- L2/L3 يتطلب خطوتين: PR المواصفات ثم PR البناء
- الذاكرة مغلقة للعمل الحساس
- التصعيد إلزامي عند الشك
