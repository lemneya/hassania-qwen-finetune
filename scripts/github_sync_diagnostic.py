#!/usr/bin/env python3
"""
GitHub Issues Sync Diagnostic Script for Auto-Claude
=====================================================

This script diagnoses common issues that cause GitHub Issues to blink/disappear
in Auto-Claude Desktop. It tests:
1. Token validity and permissions
2. API read/write operations
3. Rate limiting
4. Token expiration
5. Common failure modes

Usage:
    python3 github_sync_diagnostic.py [--repo OWNER/REPO] [--token TOKEN]
    
If no token is provided, uses GH_TOKEN or GITHUB_TOKEN environment variable.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
import subprocess

# Try to import requests, fall back to urllib if not available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False


class GitHubDiagnostic:
    """Diagnose GitHub API issues for Auto-Claude sync."""
    
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.owner, self.repo_name = repo.split('/')
        self.token = token or os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo": repo,
            "tests": [],
            "summary": {
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[int, Dict, Dict]:
        """Make HTTP request to GitHub API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        if HAS_REQUESTS:
            try:
                if method == "GET":
                    resp = requests.get(url, headers=headers, timeout=30)
                elif method == "POST":
                    resp = requests.post(url, headers=headers, json=data, timeout=30)
                elif method == "PUT":
                    resp = requests.put(url, headers=headers, json=data, timeout=30)
                else:
                    resp = requests.request(method, url, headers=headers, json=data, timeout=30)
                return resp.status_code, resp.json() if resp.text else {}, dict(resp.headers)
            except Exception as e:
                return 0, {"error": str(e)}, {}
        else:
            # Fallback to urllib
            try:
                req = urllib.request.Request(url, headers=headers, method=method)
                if data:
                    req.data = json.dumps(data).encode('utf-8')
                    req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return resp.status, json.loads(resp.read().decode()), dict(resp.headers)
            except urllib.error.HTTPError as e:
                return e.code, json.loads(e.read().decode()) if e.read() else {}, dict(e.headers)
            except Exception as e:
                return 0, {"error": str(e)}, {}
    
    def _add_result(self, name: str, status: str, details: Dict[str, Any]):
        """Add test result."""
        result = {
            "name": name,
            "status": status,  # "PASS", "FAIL", "WARN"
            "details": details
        }
        self.results["tests"].append(result)
        if status == "PASS":
            self.results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
        else:
            self.results["summary"]["warnings"] += 1
        return result
    
    def test_token_validity(self) -> Dict:
        """Test 1: Check if token is valid and get user info."""
        print("Testing token validity...", end=" ")
        status, data, headers = self._make_request("GET", "/user")
        
        if status == 200:
            token_type = "unknown"
            if self.token:
                if self.token.startswith("ghu_"):
                    token_type = "GitHub App user-to-server (short-lived)"
                elif self.token.startswith("ghp_"):
                    token_type = "Personal Access Token (classic)"
                elif self.token.startswith("github_pat_"):
                    token_type = "Fine-grained Personal Access Token"
                elif self.token.startswith("gho_"):
                    token_type = "OAuth token"
                    
            expiration = headers.get("Github-Authentication-Token-Expiration", "N/A")
            
            result = self._add_result("Token Validity", "PASS", {
                "user": data.get("login"),
                "token_type": token_type,
                "expiration": expiration,
                "scopes": headers.get("X-Oauth-Scopes", "N/A")
            })
            print("✓ PASS")
            
            # Check if token is expiring soon
            if expiration != "N/A":
                try:
                    exp_time = datetime.strptime(expiration.strip(), "%Y-%m-%d %H:%M:%S %Z")
                    exp_time = exp_time.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    remaining = (exp_time - now).total_seconds()
                    if remaining < 3600:  # Less than 1 hour
                        self._add_result("Token Expiration Warning", "WARN", {
                            "message": f"Token expires in {remaining/60:.0f} minutes",
                            "expiration": expiration,
                            "action": "Refresh token before it expires"
                        })
                        print("  ⚠ WARNING: Token expiring soon!")
                except:
                    pass
        else:
            result = self._add_result("Token Validity", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Unknown error"),
                "action": "Check token is valid and not expired"
            })
            print("✗ FAIL")
        return result
    
    def test_repo_access(self) -> Dict:
        """Test 2: Check repository access and permissions."""
        print("Testing repository access...", end=" ")
        status, data, headers = self._make_request("GET", f"/repos/{self.repo}")
        
        if status == 200:
            permissions = data.get("permissions", {})
            result = self._add_result("Repository Access", "PASS", {
                "repo": self.repo,
                "permissions": permissions,
                "has_issues": data.get("has_issues", False)
            })
            print("✓ PASS")
            
            # Check if issues are enabled
            if not data.get("has_issues", True):
                self._add_result("Issues Disabled", "FAIL", {
                    "message": "Issues are disabled for this repository",
                    "action": "Enable issues in repository settings"
                })
                print("  ✗ Issues disabled!")
        else:
            result = self._add_result("Repository Access", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Unknown error"),
                "action": "Check repository exists and token has access"
            })
            print("✗ FAIL")
        return result
    
    def test_issues_read(self) -> Dict:
        """Test 3: Check ability to read issues."""
        print("Testing issues read access...", end=" ")
        status, data, headers = self._make_request("GET", f"/repos/{self.repo}/issues?state=all&per_page=10")
        
        if status == 200:
            required_permission = headers.get("X-Accepted-Github-Permissions", "N/A")
            result = self._add_result("Issues Read", "PASS", {
                "issue_count": len(data),
                "required_permission": required_permission,
                "issues": [{"number": i["number"], "title": i["title"], "state": i["state"]} for i in data[:5]]
            })
            print(f"✓ PASS ({len(data)} issues)")
        else:
            result = self._add_result("Issues Read", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Unknown error"),
                "required_permission": headers.get("X-Accepted-Github-Permissions", "N/A"),
                "action": "Token needs 'issues=read' permission"
            })
            print("✗ FAIL")
        return result
    
    def test_issues_write_comment(self, issue_number: int) -> Dict:
        """Test 4: Check ability to write comments."""
        print(f"Testing issues write (comment on #{issue_number})...", end=" ")
        comment_body = f"[DIAGNOSTIC] Auto-Claude sync test - {datetime.now(timezone.utc).isoformat()}"
        
        status, data, headers = self._make_request(
            "POST", 
            f"/repos/{self.repo}/issues/{issue_number}/comments",
            {"body": comment_body}
        )
        
        if status == 201:
            result = self._add_result("Issues Write (Comment)", "PASS", {
                "comment_id": data.get("id"),
                "comment_url": data.get("html_url"),
                "required_permission": headers.get("X-Accepted-Github-Permissions", "N/A")
            })
            print("✓ PASS")
        elif status == 403:
            result = self._add_result("Issues Write (Comment)", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Permission denied"),
                "required_permission": headers.get("X-Accepted-Github-Permissions", "N/A"),
                "action": "Token needs 'issues=write' permission - THIS IS LIKELY THE ROOT CAUSE"
            })
            print("✗ FAIL (403 - Permission denied)")
        else:
            result = self._add_result("Issues Write (Comment)", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Unknown error"),
                "action": "Check token permissions"
            })
            print(f"✗ FAIL ({status})")
        return result
    
    def test_labels_write(self, issue_number: int) -> Dict:
        """Test 5: Check ability to add labels."""
        print(f"Testing label write (add to #{issue_number})...", end=" ")
        
        status, data, headers = self._make_request(
            "POST",
            f"/repos/{self.repo}/issues/{issue_number}/labels",
            {"labels": ["diagnostic-test"]}
        )
        
        if status == 200:
            result = self._add_result("Labels Write", "PASS", {
                "labels_added": [l["name"] for l in data],
                "required_permission": headers.get("X-Accepted-Github-Permissions", "N/A")
            })
            print("✓ PASS")
            
            # Clean up - remove the test label
            self._make_request(
                "DELETE",
                f"/repos/{self.repo}/issues/{issue_number}/labels/diagnostic-test"
            )
        elif status == 403:
            result = self._add_result("Labels Write", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Permission denied"),
                "required_permission": headers.get("X-Accepted-Github-Permissions", "N/A"),
                "action": "Token needs 'issues=write' permission"
            })
            print("✗ FAIL (403 - Permission denied)")
        else:
            result = self._add_result("Labels Write", "FAIL", {
                "status_code": status,
                "error": data.get("message", "Unknown error")
            })
            print(f"✗ FAIL ({status})")
        return result
    
    def test_rate_limit(self) -> Dict:
        """Test 6: Check rate limit status."""
        print("Checking rate limits...", end=" ")
        status, data, headers = self._make_request("GET", "/rate_limit")
        
        if status == 200:
            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            limit = core.get("limit", 0)
            reset_time = datetime.fromtimestamp(core.get("reset", 0), tz=timezone.utc)
            
            status_str = "PASS" if remaining > 100 else "WARN"
            result = self._add_result("Rate Limit", status_str, {
                "remaining": remaining,
                "limit": limit,
                "reset_at": reset_time.isoformat(),
                "usage_percent": f"{((limit - remaining) / limit * 100):.1f}%" if limit > 0 else "N/A"
            })
            print(f"✓ {status_str} ({remaining}/{limit} remaining)")
        else:
            result = self._add_result("Rate Limit", "WARN", {
                "error": "Could not check rate limit"
            })
            print("⚠ WARN")
        return result
    
    def run_all_tests(self, test_issue: Optional[int] = None) -> Dict:
        """Run all diagnostic tests."""
        print("=" * 60)
        print("GitHub Issues Sync Diagnostic for Auto-Claude")
        print(f"Repository: {self.repo}")
        print(f"Timestamp: {self.results['timestamp']}")
        print("=" * 60)
        print()
        
        # Run tests
        self.test_token_validity()
        self.test_repo_access()
        issues_result = self.test_issues_read()
        
        # Find a test issue if not specified
        if test_issue is None and issues_result["status"] == "PASS":
            issues = issues_result["details"].get("issues", [])
            if issues:
                test_issue = issues[0]["number"]
        
        if test_issue:
            self.test_issues_write_comment(test_issue)
            self.test_labels_write(test_issue)
        else:
            self._add_result("Issues Write Tests", "WARN", {
                "message": "No test issue available, skipping write tests"
            })
            
        self.test_rate_limit()
        
        # Print summary
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"  Passed:   {self.results['summary']['passed']}")
        print(f"  Failed:   {self.results['summary']['failed']}")
        print(f"  Warnings: {self.results['summary']['warnings']}")
        print()
        
        # Print diagnosis
        if self.results['summary']['failed'] > 0:
            print("DIAGNOSIS: Issues detected that may cause sync problems")
            print()
            for test in self.results['tests']:
                if test['status'] == 'FAIL':
                    print(f"  ✗ {test['name']}")
                    if 'action' in test['details']:
                        print(f"    → Action: {test['details']['action']}")
                    if 'error' in test['details']:
                        print(f"    → Error: {test['details']['error']}")
        else:
            print("DIAGNOSIS: All critical tests passed")
            print()
            print("If issues still blink/disappear, check:")
            print("  1. Auto-Claude's token refresh mechanism")
            print("  2. Network connectivity during sync")
            print("  3. Auto-Claude's error handling (may clear list on any error)")
            print("  4. Issue filtering settings in Auto-Claude")
        
        return self.results
    
    def save_results(self, filepath: str):
        """Save results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="GitHub Issues Sync Diagnostic for Auto-Claude")
    parser.add_argument("--repo", default="lemneya/hassania-qwen-finetune", help="Repository (owner/repo)")
    parser.add_argument("--token", help="GitHub token (or set GH_TOKEN env var)")
    parser.add_argument("--issue", type=int, help="Specific issue number to test writes on")
    parser.add_argument("--output", default="diagnostic_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    diagnostic = GitHubDiagnostic(args.repo, args.token)
    results = diagnostic.run_all_tests(args.issue)
    diagnostic.save_results(args.output)
    
    # Exit with error code if any tests failed
    sys.exit(1 if results['summary']['failed'] > 0 else 0)


if __name__ == "__main__":
    main()
