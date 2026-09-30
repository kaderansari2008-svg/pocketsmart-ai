#!/usr/bin/env python3
"""
PocketSmart AI: Add GitHub Collaborators to Repository
Usage: python3 add_collaborator.py <username_or_email> [permission]
Permissions: push (default), pull, triage, maintain, admin
"""

import os
import sys
import json
import urllib.request
import urllib.error

OWNER = "kaderansari2008-svg"
REPO = "pocketsmart-ai"

def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    proj_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(proj_env):
        with open(proj_env, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def add_collaborator(username, permission="push"):
    token = get_token()
    if not token:
        print("❌ Error: No GITHUB_TOKEN found. Set GITHUB_TOKEN environment variable or add to .env")
        return False
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/collaborators/{username}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "PocketSmart-Manager"
    }
    data = json.dumps({"permission": permission}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
    
    try:
        with urllib.request.urlopen(req) as res:
            if res.status in (201, 204):
                res_body = json.loads(res.read().decode("utf-8")) if res.status == 201 else {}
                invite_url = res_body.get("html_url", "")
                print(f"✅ Successfully invited '{username}' as a collaborator ({permission} access)!")
                if invite_url:
                    print(f"🔗 Invitation URL: {invite_url}")
                return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"❌ Failed to add collaborator '{username}': HTTP {e.code} - {err_msg}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_collaborator.py <github_username> [permission]")
        sys.exit(1)
    
    user = sys.argv[1].strip()
    perm = sys.argv[2].strip() if len(sys.argv) > 2 else "push"
    add_collaborator(user, perm)
