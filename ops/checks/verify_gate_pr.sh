#!/usr/bin/env bash
set -euo pipefail

echo "Running Gatekeeper checks..."

# Required ops files must exist
for f in ops/STATE.md ops/NEXT.md ops/DECISIONS.md ops/EVIDENCE.md; do
  [[ -f "$f" ]] || { echo "ERROR: Missing required file: $f"; exit 1; }
done

# STATE must declare Current Gate
grep -q "Current Gate:" ops/STATE.md || { echo "ERROR: ops/STATE.md must include 'Current Gate:'"; exit 1; }

# If PR touches gates/, ensure corresponding gate file exists
if git diff --name-only origin/main...HEAD | grep -q "^gates/"; then
  echo "Gate files modified — checking structure..."
  for gate_file in $(git diff --name-only origin/main...HEAD | grep "^gates/" | grep -v GATE_TEMPLATE.md); do
    if [[ -f "$gate_file" ]]; then
      grep -q "## Objective" "$gate_file" || { echo "ERROR: $gate_file missing '## Objective' section"; exit 1; }
      grep -q "## Acceptance Criteria" "$gate_file" || { echo "ERROR: $gate_file missing '## Acceptance Criteria' section"; exit 1; }
      grep -q "## Evidence Required" "$gate_file" || { echo "ERROR: $gate_file missing '## Evidence Required' section"; exit 1; }
    fi
  done
fi

echo "✅ All Gatekeeper checks passed!"
