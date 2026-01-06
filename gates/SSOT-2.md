# GATE: SSOT-2 — CI Enforcement + Branch Protection + Proof Test

## Objective
CI enforcement + branch protection + proof test completed — this is the point where you stop managing people/tools and start managing a governed production line.

## Scope (In / Out)
**In:**
- Gatekeeper CI workflow merged
- Branch protection rules enabled on main
- Dummy fail/pass test verified
- Evidence logged

**Out:**
- Additional automation (auto-label, auto-assign) — future gates
- Playwright browser proof — future gates

## Acceptance Criteria (Binary)
1) Gatekeeper workflow file exists at `.github/workflows/gatekeeper.yml`
2) CI runs on PRs and validates: ops files exist, Evidence section present in PR body
3) Branch protection enabled on `main`: Require PR reviews (1+), Require status checks (Gatekeeper)
4) Proof test completed: dummy PR fails without evidence, passes with evidence

## Evidence Required (Proof)
- [ ] Screenshot of CI passing on this PR
- [ ] Screenshot of branch protection settings
- [ ] Log of dummy PR fail/pass test

## Risks & Mitigations
- Risk: Branch protection blocks emergency fixes
  - Mitigation: Admin can bypass in emergencies

## Definition of Done
- All acceptance criteria met
- Evidence attached in PR
- State updated in /ops/STATE.md

## Why This Gate Matters
This is the moment you stop being the "human RAM" and become the owner of a factory: your decisions live in the repo, not in chat sessions. With CI + branch protection, your Canton Fair V1 "trade weapon" can scale through agents without losing quality—every step becomes auditable, repeatable, and impossible to fake.
