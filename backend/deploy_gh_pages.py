#!/usr/bin/env python3
"""
PocketSmart AI: Deploy to GitHub Pages
Creates and pushes the gh-pages branch, then enables GitHub Pages via the GitHub API.
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
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

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}\n{res.stderr}")
        raise RuntimeError(res.stderr)
    return res.stdout.strip()

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(root_dir, "frontend")

    print(f"📦 Packaging frontend from {frontend_dir} for GitHub Pages...")
    
    # 1. Create a temporary directory for gh-pages contents
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy frontend files to root
        for fname in ["index.html", "styles.css", "app.js"]:
            src = os.path.join(frontend_dir, fname)
            dst = os.path.join(tmp_dir, fname)
            shutil.copy2(src, dst)
            
        # Add .nojekyll
        with open(os.path.join(tmp_dir, ".nojekyll"), "w") as f:
            f.write("")

        # Add a README for gh-pages
        with open(os.path.join(tmp_dir, "README.md"), "w") as f:
            f.write("# PocketSmart AI - Live GitHub Pages Preview\n\nHosted automatically from the `frontend/` build.\n")

        print("🚀 Creating gh-pages branch commit...")
        # Initialize temp repo
        run_cmd(["git", "init"], cwd=tmp_dir)
        run_cmd(["git", "config", "user.name", OWNER], cwd=tmp_dir)
        run_cmd(["git", "config", "user.email", f"{OWNER}@users.noreply.github.com"], cwd=tmp_dir)
        run_cmd(["git", "checkout", "-b", "gh-pages"], cwd=tmp_dir)
        run_cmd(["git", "add", "."], cwd=tmp_dir)
        run_cmd(["git", "commit", "-m", "Deploy PocketSmart AI to GitHub Pages"], cwd=tmp_dir)

        token = get_token()
        if not token:
            print("❌ Error: No GITHUB_TOKEN found.")
            sys.exit(1)

        remote_url = f"https://{token}@github.com/{OWNER}/{REPO}.git"
        run_cmd(["git", "remote", "add", "origin", remote_url], cwd=tmp_dir)
        
        print("📤 Pushing gh-pages branch to GitHub...")
        run_cmd(["git", "push", "origin", "gh-pages", "--force"], cwd=tmp_dir)
        print("✅ gh-pages branch pushed successfully!")

    # 2. Enable GitHub Pages via GitHub API
    print("🌐 Enabling GitHub Pages via API...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "PocketSmart-Deployer"
    }
    
    pages_url = f"https://api.github.com/repos/{OWNER}/{REPO}/pages"
    body = json.dumps({
        "source": {
            "branch": "gh-pages",
            "path": "/"
        }
    }).encode("utf-8")

    req = urllib.request.Request(pages_url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            site_url = res_data.get("html_url", f"https://{OWNER}.github.io/{REPO}/")
            print(f"🎉 GitHub Pages configured successfully! Live URL: {site_url}")
    except urllib.error.HTTPError as e:
        if e.code == 409: # Already enabled
            print(f"ℹ️ GitHub Pages is already enabled for this repo.")
        else:
            err_body = e.read().decode("utf-8")
            print(f"Pages API returned {e.code}: {err_body}")

    # Check live status
    try:
        check_req = urllib.request.Request(pages_url, headers=headers)
        with urllib.request.urlopen(check_req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            site_url = res_data.get("html_url") or f"https://{OWNER}.github.io/{REPO}/"
            print(f"\n========================================================")
            print(f"✨ PUBLIC SHARABLE LINK:")
            print(f"👉 {site_url}")
            print(f"========================================================")
    except Exception as e:
        print(f"Check error: {e}")
        print(f"👉 https://{OWNER}.github.io/{REPO}/")

if __name__ == "__main__":
    main()
