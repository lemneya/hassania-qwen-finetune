# GATE: HITL-2 — Two-Key Enforcer

## Objective
Turn HITL from "guidelines" into "physics" by implementing CI enforcement that requires two distinct human approvals for L2/L3 PRs touching sensitive paths.

## Scope (In / Out)
**In:**
- Two-Key Enforcer CI workflow
- Sensitive path detection script
- Automatic approval counting
- Risk level validation

**Out:**
- Automated risk level detection (future gate)
- Slack/Discord notifications (future gate)
- Audit logging dashboard (future gate)

## Acceptance Criteria (Binary)
1) Two-Key Enforcer workflow exists at `.github/workflows/two-key-enforcer.yml`
2) Workflow detects sensitive paths: /ops/, /gates/, /.github/workflows/, /security/, /deploy/, /infra/, .env, secrets/
3) Workflow counts unique approvers (excluding PR author)
4) L2/L3 PRs touching sensitive paths fail CI unless 2 distinct approvers
5) Non-sensitive PRs skip two-key check
6) Sensitive path checker script exists at `/ops/checks/check_sensitive_paths.sh`

## Evidence Required (Proof)
- [ ] Screenshot of workflow file in repo
- [ ] Test: PR touching /ops/ with 0 approvals → CI fails
- [ ] Test: PR touching /ops/ with 1 approval → CI fails (if L2/L3)
- [ ] Test: PR touching /ops/ with 2 approvals → CI passes
- [ ] Test: PR not touching sensitive paths → CI skips two-key

## Risks & Mitigations
- Risk: Workflow can't push due to GitHub App permissions
  - Mitigation: Document manual add steps, embed workflow content in PR
- Risk: Two-key blocks emergency fixes
  - Mitigation: Admin can bypass in emergencies (documented in HITL_POLICY.md)
- Risk: False positives on sensitive path detection
  - Mitigation: Clear pattern list, easy to update

## Definition of Done
- All acceptance criteria met
- Evidence attached in PR
- State updated in /ops/STATE.md
- Workflow added manually by CEO (if needed)

## Why This Gate Matters
CODEOWNERS alone guarantees "a codeowner approves," not "two distinct humans approve." This gate adds CI enforcement that physically prevents merging L2/L3 PRs without two-key approval. After this gate, agents cannot "slide past" rules—every sensitive change requires two humans to agree.

## Arabic Summary / ملخص بالعربية
هذه البوابة تحول HITL من "إرشادات" إلى "فيزياء" - CI يمنع الدمج بدون موافقتين بشريتين منفصلتين للتغييرات الحساسة.
