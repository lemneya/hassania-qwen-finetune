# QA Sheriff Checklist

This is the one-page checklist for the QA Sheriff role. Use this for every PR review.

## Before You Start

- [ ] PR is linked to a Gate file
- [ ] PR is linked to an Issue (if applicable)
- [ ] Risk level is declared (L0/L1/L2/L3)

## Evidence Verification

### For L1 (Normal) PRs
- [ ] At least ONE of: test output, log, OR screenshot present
- [ ] Evidence is real (not placeholder text)
- [ ] Evidence matches what the PR claims to do

### For L2 (Sensitive) PRs
- [ ] Test output present AND relevant
- [ ] Repro steps are exact and followable
- [ ] Demo or recording provided (if UI/UX involved)
- [ ] "What Could Go Wrong?" section is thoughtful

### For L3 (Critical) PRs
- [ ] Full audit trail documented
- [ ] CEO has pre-approved in Gate file
- [ ] Rollback plan is concrete and tested

## Quick Sanity Test (Pick 1-2 steps to verify)

- [ ] I can follow the repro steps
- [ ] The test output matches expected behavior
- [ ] The screenshot shows what the PR claims
- [ ] No obvious security red flags (hardcoded secrets, exposed endpoints)

## Final Decision

| Decision | When to Use |
|----------|-------------|
| **Approve** | Evidence is complete, sanity test passes |
| **Request Changes** | Evidence missing or incomplete |
| **Escalate to CEO** | Risk level seems wrong, unclear scope, or suspicious |

## Red Flags (Escalate Immediately)

- [ ] PR touches auth/payments but marked as L0/L1
- [ ] Evidence looks fabricated or copy-pasted
- [ ] PR is > 500 lines with no clear breakdown
- [ ] Builder says "I'm not sure" anywhere
- [ ] Any mention of secrets, keys, or credentials

## Sign-Off

```
QA Sheriff: _______________
Date: _______________
Verdict: APPROVE / REQUEST CHANGES / ESCALATE
Notes: _______________
```
