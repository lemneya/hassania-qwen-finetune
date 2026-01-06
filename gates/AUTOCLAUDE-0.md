# GATE: AUTOCLAUDE-0 — Auto-Claude Governance Update

## Objective
Update repo guides so Auto-Claude can operate autonomously inside SSOT/HITL safely.

## Scope (In)
- Add /ops/AUTO_CLAUDE_RULES.md
- Update HITL policy + QA checklist + PR template + STATE knobs
- Define two-step PR rule for L2/L3 and memory policy

## Scope (Out)
- Implementing new CI enforcement (optional later)
- Running the first Auto-Claude build task (AUTOCLAUDE-1)

## Acceptance Criteria
1) AUTO_CLAUDE_RULES.md exists and is referenced by HITL_POLICY.md
2) QA checklist includes Auto-Claude checks
3) PR template supports SPEC PR vs BUILD PR
4) STATE includes WIP limit + memory mode
5) PR includes evidence of documentation update (links + file list)

## Evidence Required
- PR shows new/updated files
- PR body includes summary + evidence section

## Why This Gate Matters
Auto-Claude's power is that it can run for hours. That's great — but only if humans control direction and risk. This update turns Auto-Claude into a high-output worker inside your governed factory:

- You control what and how risky (gates + L2/L3 rules)
- Auto-Claude controls execution (plan/build/QA)
- Your enforcer + Brahim control quality (QA checklist + Two-Key)

## Arabic Summary / ملخص بالعربية
هذه البوابة تدمج أوتو-كلود في نظام SSOT/HITL:
- قواعد واضحة للبناء المستقل
- سياسة الذاكرة والخطوتين
- حدود WIP وتصعيد
