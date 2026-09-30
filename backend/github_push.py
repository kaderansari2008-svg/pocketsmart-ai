#!/usr/bin/env python3
"""
PocketSmart AI: Automated GitHub Repository Creator & Pusher
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    
    # Check ~/.env
    env_path = os.path.expanduser("~/.env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
                if line.startswith("GH_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
                    
    # Check project .env
    proj_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(proj_env):
        with open(proj_env, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
                if line.startswith("GH_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    return None

def main():
    token = get_token()
    if not token:
        print("ERROR: No GITHUB_TOKEN found.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "PocketSmart-Deployer"
    }

    # 1. Verify user identity
    print("🔍 Verifying GitHub credentials...")
    try:
        req = urllib.request.Request("https://api.github.com/user", headers=headers)
        with urllib.request.urlopen(req) as res:
            user_data = json.loads(res.read().decode("utf-8"))
            login = user_data.get("login")
            print(f"✅ Authenticated as GitHub user: {login}")
    except Exception as e:
        print(f"❌ Failed to authenticate with GitHub API: {e}")
        sys.exit(1)

    repo_name = "pocketsmart-ai"

    # 2. Check if repo exists, or create it
    print(f"📦 Checking if repository '{repo_name}' exists...")
    repo_exists = False
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{login}/{repo_name}", headers=headers)
        with urllib.request.urlopen(req) as res:
            repo_exists = True
            print(f"ℹ️ Repository '{login}/{repo_name}' already exists.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"🚀 Creating repository '{repo_name}' on GitHub...")
            create_payload = json.dumps({
                "name": repo_name,
                "description": "PocketSmart AI: Your Smart Budget & Recommendation Assistant",
                "private": False,
                "auto_init": False
            }).encode("utf-8")
            create_req = urllib.request.Request(
                "https://api.github.com/user/repos",
                data=create_payload,
                headers=headers
            )
            with urllib.request.urlopen(create_req) as c_res:
                print("✅ Repository created successfully!")
        else:
            print(f"Error checking repo: {e}")
            sys.exit(1)

    # 3. Configure git remote and push
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    remote_url = f"https://{token}@github.com/{login}/{repo_name}.git"

    print("📤 Pushing code to GitHub main branch...")
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=repo_dir, check=True)
    
    push_res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=repo_dir, capture_output=True, text=True)
    
    # Clean remote URL so token is not left in git config
    clean_url = f"https://github.com/{login}/{repo_name}.git"
    subprocess.run(["git", "remote", "set-url", "origin", clean_url], cwd=repo_dir, check=True)

    if push_res.returncode == 0:
        print(f"\n🎉 Successfully pushed to https://github.com/{login}/{repo_name}")
    else:
        print(f"❌ Git push failed:\n{push_res.stderr}")
        sys.exit(push_res.returncode)

if __name__ == "__main__":
    main()
