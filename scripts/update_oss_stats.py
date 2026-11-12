#!/usr/bin/env python3
"""Rewrite the open-source metrics row in README.md from GitHub's records.

Counted automatically:
  merged pull requests  PRs by USER that were merged into repositories USER
                        does not own
  upstream projects     distinct repositories those PRs were merged into

Set by hand below, because GitHub cannot tell what counts as a tool or a
maintained package:
  TOOLS_AUTHORED, PACKAGES_MAINTAINED

Needs the `gh` CLI and a token in GH_TOKEN. Run from the repository root.
"""
import json
import re
import subprocess
import sys

USER = "kroy3"
TOOLS_AUTHORED = 1        # scDblFinder Galaxy tool
PACKAGES_MAINTAINED = 2   # Decant, GeoShift
README = "README.md"
START, END = "<!-- oss-stats:start -->", "<!-- oss-stats:end -->"


def merged_upstream_prs():
    query = f"author:{USER} type:pr is:merged -user:{USER}"
    repos, total, page = set(), 0, 1
    while True:
        out = subprocess.run(
            ["gh", "api", "-X", "GET", "search/issues", "-f", f"q={query}",
             "-f", "per_page=100", "-f", f"page={page}"],
            check=True, capture_output=True, text=True).stdout
        data = json.loads(out)
        items = data["items"]
        total += len(items)
        repos.update(i["repository_url"].split("/repos/")[1] for i in items)
        if total >= data["total_count"] or not items:
            return total, len(repos)
        page += 1


def main():
    prs, projects = merged_upstream_prs()
    row = (f"{START}\n"
           "| Merged pull requests | Upstream projects | Tools authored | Packages maintained |\n"
           "|:---:|:---:|:---:|:---:|\n"
           f"| **{prs}** | **{projects}** | **{TOOLS_AUTHORED}** | **{PACKAGES_MAINTAINED}** |\n"
           f"{END}")
    text = open(README, encoding="utf-8").read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"markers {START} / {END} not found in {README}")
    new = pattern.sub(lambda _: row, text, count=1)
    if new != text:
        open(README, "w", encoding="utf-8").write(new)
    print(f"merged PRs: {prs}, upstream projects: {projects}, "
          f"README {'updated' if new != text else 'unchanged'}")


if __name__ == "__main__":
    main()
