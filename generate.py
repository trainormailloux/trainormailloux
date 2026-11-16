"""Generate stats.svg and languages.svg for a GitHub user.

    GH_USER=yourname GH_TOKEN=xxxx python generate.py
    python generate.py --demo        # render from sample data, no network
"""
import json
import os
import sys
from pathlib import Path

from statscard.render import langs_card, stats_card

OUT = Path(__file__).resolve().parent / "output"

DEMO = (
    {"name": "Trainor Mailloux", "login": "trainormailloux", "followers": 14, "stars": 27,
     "forks": 6, "commits": 342, "prs": 18, "issues": 9, "contributed": 11, "since": 2026},
    [("Python", 138791), ("Shell", 4346), ("HTML", 3100), ("Batchfile", 349), ("CSS", 1800)],
)


def main():
    OUT.mkdir(exist_ok=True)
    if "--demo" in sys.argv:
        stats, langs = DEMO
    else:
        from statscard.fetch import collect
        user = os.environ.get("GH_USER")
        if not user:
            sys.exit("Set GH_USER (and GH_TOKEN) or run with --demo")
        stats, langs = collect(user, os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))

    (OUT / "stats.svg").write_text(stats_card(stats), encoding="utf-8")
    (OUT / "languages.svg").write_text(langs_card(langs), encoding="utf-8")
    (OUT / "stats.json").write_text(json.dumps({"stats": stats, "languages": langs}, indent=2))
    print("Wrote output/stats.svg and output/languages.svg")
    print(f"  {stats['stars']} stars · {stats['commits']} commits · {stats['prs']} PRs · {stats['followers']} followers")


if __name__ == "__main__":
    main()
