"""Collect a user's public GitHub stats with the REST + Search APIs (no GraphQL)."""
import os
import time
from datetime import datetime

import requests

API = "https://api.github.com"


def _session(token):
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json",
                      "User-Agent": "gh-stats-card"})
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    return s


def _search_count(s, kind, q):
    """Total count from the search API, retrying once on secondary rate limits."""
    for attempt in range(2):
        r = s.get(f"{API}/search/{kind}", params={"q": q, "per_page": 1})
        if r.status_code == 403 and "rate limit" in r.text.lower():
            time.sleep(8)
            continue
        r.raise_for_status()
        return r.json().get("total_count", 0)
    return 0


def collect(user, token=None):
    s = _session(token)

    prof = s.get(f"{API}/users/{user}")
    prof.raise_for_status()
    prof = prof.json()

    # all owned, non-fork repos -> stars, forks, languages
    repos, page = [], 1
    while True:
        r = s.get(f"{API}/users/{user}/repos",
                  params={"per_page": 100, "page": page, "type": "owner", "sort": "pushed"})
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos += [x for x in batch if not x["fork"]]
        if len(batch) < 100:
            break
        page += 1

    stars = sum(x["stargazers_count"] for x in repos)
    forks = sum(x["forks_count"] for x in repos)

    langs = {}
    for x in repos:
        lr = s.get(x["languages_url"])
        if lr.ok:
            for name, b in lr.json().items():
                langs[name] = langs.get(name, 0) + b

    commits = _search_count(s, "commits", f"author:{user}")
    prs = _search_count(s, "issues", f"author:{user} type:pr")
    issues = _search_count(s, "issues", f"author:{user} type:issue")

    stats = {
        "name": prof.get("name") or prof["login"],
        "login": prof["login"],
        "followers": prof.get("followers", 0),
        "stars": stars,
        "forks": forks,
        "commits": commits,
        "prs": prs,
        "issues": issues,
        "contributed": len(repos),
        "since": datetime.utcnow().year,
    }
    langs_sorted = sorted(langs.items(), key=lambda kv: -kv[1])
    return stats, langs_sorted
