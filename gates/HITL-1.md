# GATE: HITL-1 — Human-in-the-Loop Governance

## Objective
Establish human oversight controls so the CEO manages a governed production line, not individual conversations. This is the "nervous system" that gives control without labor.

## Scope (In / Out)
**In:**
- HITL policy file with risk levels (L0-L3)
- PR template with risk classification
- CODEOWNERS with two-key approval paths
- QA Sheriff checklist
- CEO control knobs in STATE.md

**Out:**
- Actual QA Sheriff hiring/assignment
- Automated risk detection CI (future gate)
- Playwright proof automation (future gate)

## Acceptance Criteria (Binary)
1) HITL policy file exists at `/ops/HITL_POLICY.md`
2) PR template includes Risk Level field (L0/L1/L2/L3)
3) PR template includes "What Could Go Wrong?" section
4) CODEOWNERS enforces two-key approvals on sensitive paths (/.github/, /ops/, /gates/)
5) QA Sheriff checklist exists at `/ops/QA_SHERIFF_CHECKLIST.md`
6) STATE.md includes CEO control knobs (pass@1, escalation_cap, cost_per_success, sampling_rate)

## Evidence Required (Proof)
- [ ] Screenshot of HITL_POLICY.md in repo
- [ ] Screenshot of updated PR template with risk levels
- [ ] Screenshot of CODEOWNERS with two-key paths
- [ ] 1 dummy PR demonstrates L2 requires 2 approvals (or shows CODEOWNERS assignment)

## Risks & Mitigations
- Risk: Policy too strict, slows down L0/L1 work
  - Mitigation: Clear auto-merge rules for L0, sampling for L1
- Risk: QA Sheriff role unfilled
  - Mitigation: CEO can act as both until role is assigned

## Definition of Done
- All acceptance criteria met
- Evidence attached in PR
- State updated in /ops/STATE.md

## Why This Gate Matters
AI without Human-in-the-Loop is just automation risk. This gate adds the CEO nervous system: human checkpoints, escalation rules, and sampling so you control quality without doing the labor. After this gate, you approve gates and merges; humans/agents do everything else.
