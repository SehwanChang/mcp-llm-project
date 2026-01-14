#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

import urllib.request


def api_create_repo(token: str, name: str, private: bool = True, description: str = ""):
    url = "https://api.github.com/user/repos"
    data = json.dumps({"name": name, "private": private, "description": description}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def run(cmd, cwd=None, check=True):
    print("->", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)

    name = "mcp-llm-project"
    desc = "mcp-llm-project repo created via API"

    resp = api_create_repo(token, name, private=True, description=desc)
    if resp.get("message"):
        print("GitHub API response:", resp, file=sys.stderr)
        # If repo exists, still attempt to push

    clone_url = resp.get("clone_url") or f"https://github.com/{resp.get('owner',{}).get('login','')}/{name}.git"
    html_url = resp.get("html_url") or clone_url.replace('.git', '')
    owner = resp.get("owner", {}).get("login")

    # configure remote and push
    try:
        run(["git", "remote", "remove", "origin"], cwd=project_root, check=False)
    except Exception:
        pass
    run(["git", "remote", "add", "origin", clone_url], cwd=project_root)

    # Use token-embedded push URL to authenticate the push non-interactively
    push_url = f"https://{token}@github.com/{owner}/{name}.git"
    result = run(["git", "push", push_url, "main", "-u"], cwd=project_root)
    print(result.stdout)
    print("Repository URL:", html_url)


if __name__ == '__main__':
    main()
