# HITL Policy (Human-in-the-Loop Governance)

This document defines the CEO contract for human oversight in the AI factory.

## The Three Human Loops

| Loop | Name | When | How | Why |
|------|------|------|-----|-----|
| **A** | Intent Control | Before work starts | CEO approves Gate spec (scope, AC, evidence) | Prevents scope creep + wrong direction |
| **B** | Quality Control | Before merge | Human checks evidence (logs/tests/demo) and sanity-tests | Catches "looks good in chat" failures |
| **C** | Risk Control | Security/data/payments/deployments | Require two humans (CEO + QA) | Prevents catastrophic mistakes |

## Risk Ladder

| Level | Name | Description | Approval Required | Auto-merge |
|-------|------|-------------|-------------------|------------|
| **L0** | Safe | Docs, text, formatting, comments | None (optional review) | Yes |
| **L1** | Normal | App code changes with tests passing | 1 human (QA or CEO) | No |
| **L2** | Sensitive | Auth, payments, user data, networking, model keys, deploy scripts | 2 humans (CEO + QA) + extra evidence | No |
| **L3** | Critical | Money movement, production secrets, irreversible actions | Block by default until CEO explicitly approves in a Gate | No |

## Evidence Requirements by Risk Level

| Level | Required Evidence |
|-------|-------------------|
| L0 | None required |
| L1 | Test output OR log OR screenshot |
| L2 | Test output AND repro steps AND demo/recording |
| L3 | Full audit trail + CEO sign-off in Gate file |

## Human Sampling (Quality Control Efficiency)

To avoid CEO becoming a bottleneck:

| Level | Review Rate |
|-------|-------------|
| L0 | 0% (auto-merge allowed) |
| L1 | 33% spot-check (1 out of every 3 PRs, or any PR > 300 lines) |
| L2 | 100% mandatory review |
| L3 | 100% mandatory + Gate pre-approval |

## HITL Escalation Triggers

Agents MUST stop and open an Issue when any of these occur:

1. Tests failing
2. PR touches workflows, auth, payments, secrets
3. PR is huge (> 500 lines changed)
4. Any unclear requirement ("I'm not sure")
5. Anything with external legal/compliance risk
6. Any error that cannot be resolved in 3 attempts

## Human Roles

### Role 1: QA Sheriff (Part-time Human)

Responsibilities:
- Verify evidence in PR
- Reproduce 1-2 steps
- Approve/reject based on evidence quality

### Role 2: Repo Librarian

Responsibilities:
- Maintain ops/STATE.md correctness
- Keep decisions log updated
- Ensure gates are clean
- Verify every PR links to a gate/issue

## Two-Key Approval Paths

The following paths require approval from BOTH CEO and QA:

- `/security/` - Security-related code
- `/.github/workflows/` - CI/CD workflows
- `/ops/` - Governance files
- `/gates/` - Gate specifications
- Any file containing secrets or API keys

## CEO Control Knobs

Track these metrics in ops/STATE.md:

| Metric | Target | Description |
|--------|--------|-------------|
| pass@1 | 80% | PRs that pass CI on first try |
| escalation_cap | 2 | Max escalation issues per gate |
| cost_per_success | Track | Time/$ per merged PR |
| sampling_rate | 33% | Review rate for L1 PRs |

## Policy Enforcement

This policy is enforced through:
1. PR template requiring risk level declaration
2. CODEOWNERS requiring appropriate reviewers
3. CI checks validating evidence presence
4. Branch protection rules
