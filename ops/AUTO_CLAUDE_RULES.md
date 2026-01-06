# AUTO-CLAUDE RULES (Builder Engine)

## What Auto-Claude is
Auto-Claude is a spec-driven, multi-agent autonomous builder engine:
- Planning → Coding → QA validation
- Multi-session execution (parallel)
- Isolated workspace (worktrees/branches)
- Optional memory layer
- Can run via UI (Kanban) or CLI/headless

Auto-Claude is a WORKER. GitHub SSOT is the BOSS.

---

## Non-negotiable rule
**No PR = no progress.**

Auto-Claude must never "finish in chat/UI only."
It must always produce:
- a PR
- with Risk Level
- and Evidence (logs/tests/repro steps)

---

## Two-Step PR policy (Spec PR → Build PR)
### Required for L2/L3 (Sensitive/Critical)
If a task touches sensitive paths or is labeled L2/L3:
1) **SPEC PR (Intent Control)**
   - updates/creates the gate file
   - locks acceptance criteria + evidence checklist
   - approved by CEO + Trusted Enforcer (or CEO + QA)

2) **BUILD PR (Execution)**
   - code + tests + logs + evidence
   - reviewed under normal HITL/Two-Key rules

### Optional for L0/L1
L0/L1 can be single PR if scope is clear.

---

## Sensitive paths (trigger extra rules)
Any change touching these is automatically treated as sensitive:
- /ops/
- /gates/
- /.github/workflows/
- /security/ /deploy/ /infra/
- .env, secrets/

---

## AI-powered merge policy
Auto-Claude may SUGGEST conflict resolution.
It must NOT merge automatically.
- L0/L1: suggestion allowed, human reviews
- L2/L3: human must review every conflict resolution

---

## Memory policy (data safety)
Auto-Claude memory can increase productivity, but it can also leak context.

Default:
- L0/L1 internal work: memory allowed
- L2/L3 or any client/government work: memory OFF unless explicitly approved in gate

If memory is enabled:
- Prefer local embeddings/memory store
- Do not store secrets, credentials, client PII, or government-sensitive data

---

## WIP limit (prevent chaos)
Max parallel tasks:
- Default: 3 active tasks
- Only Trusted Enforcer can raise this temporarily

---

## Escalation triggers (Auto-Claude must STOP and open an Issue)
- unclear requirement or missing gate details
- tests failing repeatedly
- changes requested outside gate scope
- sensitive files touched but Risk Level missing
- secrets/env keys needed
- build requires external credentials

---

## Arabic Summary / ملخص بالعربية

أوتو-كلود هو محرك بناء مستقل. يعمل داخل نظام SSOT/HITL:
- لا PR = لا تقدم
- L2/L3 يتطلب خطوتين: PR المواصفات ثم PR البناء
- الذاكرة مغلقة افتراضياً للعمل الحساس
- حد أقصى 3 مهام متوازية
- يجب التصعيد عند الشك أو نقص المعلومات
