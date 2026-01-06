# GATE: SSOT-1 — Bootstrap Single Source of Truth Infrastructure

## Objective
Establish the SSOT infrastructure so all future work flows through Issues → PRs → CI proof, eliminating context decay and session amnesia.

## Scope (In / Out)
**In:**
- Create ops/ folder with STATE.md, NEXT.md, DECISIONS.md, EVIDENCE.md
- Create gates/ folder with GATE_TEMPLATE.md
- Create .github/ templates (PR template, issue template, CODEOWNERS)
- Create CI workflow for gatekeeper checks
- Create verification script for PR validation

**Out:**
- Actual project code changes
- Branch protection rules (manual step by repo owner)
- Additional automation scripts (future gates)

## Acceptance Criteria (Binary)
1) All ops files exist and are properly formatted
2) Gate template exists in /gates
3) PR template exists in .github/
4) Issue template for gates exists in .github/ISSUE_TEMPLATE/
5) CI workflow runs gatekeeper checks on PRs
6) CODEOWNERS file assigns gatekeeper to ops/ and gates/

## Evidence Required (Proof)
- [x] All files created and committed
- [x] CI workflow file present
- [ ] PR created and CI passes (pending)

## Risks & Mitigations
- Risk: Branch protection not enabled
  - Mitigation: Document manual steps for repo owner

## Definition of Done
- All acceptance criteria met
- Evidence attached in PR
- State updated in /ops/STATE.md
