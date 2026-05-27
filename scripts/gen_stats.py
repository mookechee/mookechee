#!/usr/bin/env python3
"""Generate GitHub stats and language SVGs using GitHub API."""

import json
import os
import re
import subprocess
import sys

USERNAME = "mookechee"


def count_starred():
    result = subprocess.run(
        ["gh", "api", "--include", f"users/{USERNAME}/starred?per_page=1"],
        capture_output=True, text=True,
    )
    m = re.search(r'page=(\d+)>; rel="last"', result.stdout)
    return int(m.group(1)) if m else 0

LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178C6",
    "C++": "#f34b7d",
    "Kotlin": "#A97BFF",
    "Lua": "#000080",
    "Shell": "#89e051",
    "CSS": "#563d7c",
    "HTML": "#e34c26",
    "Ruby": "#701516",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Java": "#b07219",
    "C": "#555555",
    "Swift": "#F05138",
    "Dart": "#00B4AB",
    "Makefile": "#427819",
    "CMake": "#DA3434",
    "Dockerfile": "#384d54",
    "PowerShell": "#012456",
    "Roff": "#ecdebe",
    "Vim Script": "#199f4b",
}


def gh_api(path, paginate=False):
    args = ["gh", "api", "--jq", ".", path]
    if paginate:
        args.insert(2, "--paginate")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gh api error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        lines = [json.loads(line) for line in result.stdout.strip().split("\n") if line.strip()]
        return lines


def gen_stats():
    user = gh_api(f"users/{USERNAME}")

    items = [
        ("Public Repos", str(user.get("public_repos", 0))),
        ("Starred", str(count_starred())),
        ("Followers", str(user.get("followers", 0))),
        ("Following", str(user.get("following", 0))),
    ]

    rows = ""
    y = 75
    for label, value in items:
        rows += f"""  <text x="25" y="{y}" font-size="14" fill="#8b949e">{label}</text>
  <text x="200" y="{y}" font-size="15" fill="#c9d1d9" font-weight="bold" text-anchor="end">{value}</text>
"""
        y += 30

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="340" height="200" viewBox="0 0 340 200">
  <style>*{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}}</style>
  <rect width="340" height="200" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <text x="25" y="40" font-size="16" font-weight="bold" fill="#58a6ff">GitHub Stats</text>
{rows}</svg>"""


def gen_langs():
    repos = gh_api(f"users/{USERNAME}/repos?per_page=100&type=owner")
    if isinstance(repos, dict) and "message" in repos:
        repos = []

    lang_count = {}
    for r in repos:
        lang = r.get("language")
        if lang is None:
            continue
        lang_count[lang] = lang_count.get(lang, 0) + 1

    entries = sorted(lang_count.items(), key=lambda x: -x[1])[:8]
    if not entries:
        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="340" height="200" viewBox="0 0 340 200">
  <style>*{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}}</style>
  <rect width="340" height="200" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <text x="25" y="40" font-size="16" font-weight="bold" fill="#58a6ff">Top Languages</text>
  <text x="25" y="100" font-size="14" fill="#8b949e">No public repos with detected language</text>
</svg>"""
    total = sum(v for _, v in entries)

    rows = ""
    y = 65
    for lang, count in entries:
        pct = round(count / total * 100) if total else 0
        color = LANG_COLORS.get(lang, "#8b949e")
        rows += f"""  <rect x="25" y="{y}" width="14" height="14" fill="{color}" rx="3"/>
  <text x="48" y="{y + 12}" font-size="13" fill="#c9d1d9">{lang}</text>
  <text x="315" y="{y + 12}" font-size="13" fill="#8b949e" text-anchor="end">{pct}%</text>
"""
        y += 24

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="340" height="200" viewBox="0 0 340 200">
  <style>*{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}}</style>
  <rect width="340" height="200" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <text x="25" y="40" font-size="16" font-weight="bold" fill="#58a6ff">Top Languages</text>
{rows}</svg>"""


def main():
    os.makedirs("dist", exist_ok=True)
    with open("dist/stats.svg", "w") as f:
        f.write(gen_stats())
    with open("dist/lang.svg", "w") as f:
        f.write(gen_langs())
    print("Stats and lang SVGs generated.")


if __name__ == "__main__":
    main()
