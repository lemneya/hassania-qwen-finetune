# Auto-Claude GitHub Issues Sync Debug Report

**Repository:** `lemneya/hassania-qwen-finetune`  
**Date:** 2026-01-07  
**Status:** ✅ API Verification Complete - All Tests Passed

---

## Executive Summary

The GitHub API tests confirm that the current token has **full read/write access** to issues on `lemneya/hassania-qwen-finetune`. The blinking/disappearing behavior in Auto-Claude is **not caused by permission issues** with the GitHub API.

---

## Root Cause Analysis

### Primary Finding: Token Type and Lifecycle

The token in use is a **GitHub App user-to-server token** (`ghu_*`), which has the following characteristics:

| Property | Value |
|----------|-------|
| Token Type | `ghu_` (GitHub App user-to-server) |
| Lifespan | Short-lived (typically 1-8 hours) |
| Refresh | Requires automatic refresh via OAuth flow |
| Permissions | Full admin access to repository |

### Most Likely Root Causes (Ranked by Probability)

1. **Token Refresh Race Condition** (High Probability)
   - Auto-Claude fetches issues successfully → issues appear
   - Token expires or refresh fails mid-session
   - Subsequent API calls fail with 401/403
   - Auto-Claude clears the issue list on auth failure → issues disappear

2. **Aggressive Error Handling** (Medium Probability)
   - Auto-Claude may clear the entire issue list when any API error occurs
   - Even transient network errors could trigger this behavior

3. **State Management Bug** (Medium Probability)
   - React/Electron state may not persist correctly during re-renders
   - Issues flash briefly then disappear due to state reset

4. **Issue Filtering Logic** (Low Probability)
   - Auto-Claude may filter issues by label, assignee, or title prefix
   - Issues without required attributes get filtered out after initial display

---

## API Verification Evidence

### Test Results Summary

| Test | Status | Details |
|------|--------|---------|
| Token Validity | ✅ PASS | User: `lemneya`, Type: `ghu_` |
| Repository Access | ✅ PASS | Full permissions (admin, push, triage) |
| Issues Read | ✅ PASS | 10 issues retrieved |
| Issues Write (Comment) | ✅ PASS | Comment ID: 3717315945 |
| Labels Write | ✅ PASS | Labels added successfully |
| Rate Limit | ✅ PASS | 14911/15000 remaining |

### API Responses

**GET /repos/lemneya/hassania-qwen-finetune/issues**
```
HTTP/2.0 200 OK
X-Accepted-Github-Permissions: issues=read
```

**POST /repos/lemneya/hassania-qwen-finetune/issues/10/comments**
```
HTTP/2.0 201 Created
X-Accepted-Github-Permissions: issues=write; pull_requests=write
```

**POST /repos/lemneya/hassania-qwen-finetune/issues/10/labels**
```
HTTP/2.0 200 OK
X-Accepted-Github-Permissions: issues=write; pull_requests=write
```

---

## Recommendations

### Immediate Actions

1. **Monitor Token Expiration**
   - Current token expires: Check Auto-Claude settings for expiration time
   - Ensure Auto-Claude's OAuth refresh is working correctly

2. **Check Auto-Claude Debug Logs**
   - Open Auto-Claude → Settings → Debug & Logs
   - Look for 401/403 errors during sync
   - Look for "token expired" or "refresh failed" messages

3. **Test with Fresh Token**
   - Disconnect and reconnect GitHub in Auto-Claude
   - This forces a new token to be issued

### Auto-Claude Configuration Checks

```
Settings to verify in Auto-Claude:
├── GitHub Integration
│   ├── Repository: lemneya/hassania-qwen-finetune ✓
│   ├── Token Status: Should show "Connected"
│   └── Permissions: Should show "Issues: Read & Write"
├── Task Sync
│   ├── Auto-Sync on Load: Enable
│   ├── Sync Interval: 30-60 seconds recommended
│   └── Filter by Label: Check if any filter is applied
└── Debug & Logs
    └── Enable verbose logging for troubleshooting
```

### Code-Level Fix (If Auto-Claude Source Available)

The likely fix in Auto-Claude's GitHub sync module:

```javascript
// BEFORE (problematic pattern)
async function syncIssues() {
  try {
    const issues = await fetchIssues();
    setIssues(issues);
  } catch (error) {
    setIssues([]);  // ← This clears the list on ANY error
  }
}

// AFTER (recommended fix)
async function syncIssues() {
  try {
    const issues = await fetchIssues();
    setIssues(issues);
    setError(null);
  } catch (error) {
    // Keep existing issues visible, show error banner
    setError({
      message: error.message,
      statusCode: error.response?.status,
      action: error.response?.status === 401 ? 'refresh_token' : 'retry'
    });
    // DO NOT clear issues: setIssues([])
  }
}
```

---

## Verification Steps

To confirm the fix works:

1. Open Auto-Claude
2. Navigate to the repository
3. Verify "Issues Available" shows the issue count
4. Wait 5+ minutes (past any token refresh cycle)
5. Issues should remain visible
6. Try adding a comment to an issue
7. Verify no 401/403 errors in debug logs

---

## Files Included

| File | Description |
|------|-------------|
| `scripts/github_sync_diagnostic.py` | Diagnostic script to test API access |
| `scripts/diagnostic_results.json` | Full test results in JSON format |
| `docs/AUTO_CLAUDE_SYNC_DEBUG_REPORT.md` | This report |

---

## Contact

If issues persist after following these recommendations, the problem is likely within Auto-Claude's internal state management or OAuth implementation, which would require access to Auto-Claude's source code to debug further.
