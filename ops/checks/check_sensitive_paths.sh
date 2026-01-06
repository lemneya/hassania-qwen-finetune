#!/usr/bin/env bash
set -euo pipefail

# Two-Key Enforcer: Check if PR touches sensitive paths
# Used by CI to determine if two-key approval is required

echo "Checking for sensitive paths..."

# Get changed files (works in PR context)
CHANGED_FILES=$(git diff --name-only origin/main...HEAD 2>/dev/null || echo "")

# Sensitive path patterns (L2/L3 risk)
SENSITIVE_PATTERNS=(
  "^ops/"                    # Governance files
  "^gates/"                  # Gate specifications
  "^\.github/workflows/"     # CI/CD workflows
  "^\.github/CODEOWNERS"     # Code ownership
  "^security/"               # Security code
  "^deploy/"                 # Deployment scripts
  "^infra/"                  # Infrastructure
  "\.env"                    # Environment files
  "secrets/"                 # Secrets
  "auth/"                    # Authentication
  "payment/"                 # Payment processing
)

SENSITIVE_FOUND=()

for file in $CHANGED_FILES; do
  for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if echo "$file" | grep -qE "$pattern"; then
      SENSITIVE_FOUND+=("$file")
      break
    fi
  done
done

if [ ${#SENSITIVE_FOUND[@]} -gt 0 ]; then
  echo "⚠️  SENSITIVE PATHS DETECTED (Two-Key Required):"
  printf '  - %s\n' "${SENSITIVE_FOUND[@]}"
  echo ""
  echo "This PR requires:"
  echo "  1. Risk Level: L2 or L3 in PR description"
  echo "  2. Two distinct human approvals (CEO + QA)"
  echo ""
  echo "SENSITIVE_TOUCHED=true"
  exit 0
else
  echo "✅ No sensitive paths touched."
  echo "Standard review process applies."
  echo "SENSITIVE_TOUCHED=false"
  exit 0
fi
