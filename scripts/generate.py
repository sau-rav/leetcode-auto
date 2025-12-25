import requests
import json
import os
import random
from datetime import datetime, date
from collections import defaultdict

LEETCODE_USER = "saurav_ksharma"
SOLVED_AFTER = datetime(2025, 12, 25)

STATE_FILE = "data/state.json"
GRAPHQL = "https://leetcode.com/graphql"

DIFFICULTY_QUOTA = {"Easy": 2, "Medium": 2, "Hard": 1}
DAILY_TARGET = 5

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

os.makedirs("data", exist_ok=True)


def graphql(query, variables=None):
    r = requests.post(
        GRAPHQL,
        headers=HEADERS,
        json={"query": query, "variables": variables or {}},
        timeout=20
    )
    r.raise_for_status()
    return r.json()["data"]


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"assigned": {}}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_recent_solved():
    query = """
    query recentAc($username: String!) {
      recentAcSubmissionList(username: $username, limit: 1000) {
        titleSlug
        timestamp
      }
    }
    """
    data = graphql(query, {"username": LEETCODE_USER})
    solved = set()

    for s in data["recentAcSubmissionList"]:
        ts = datetime.fromtimestamp(int(s["timestamp"]))
        if ts >= SOLVED_AFTER:
            solved.add(s["titleSlug"])

    return solved


def fetch_free_problems():
    query = """
    query getQuestions($skip: Int!, $limit: Int!) {
      questionList(
        categorySlug: ""
        skip: $skip
        limit: $limit
        filters: {}
      ) {
        data {
          title
          titleSlug
          difficulty
          isPaidOnly
        }
      }
    }
    """
    skip, limit = 0, 100
    free = []

    while True:
        data = graphql(query, {"skip": skip, "limit": limit})
        batch = data["questionList"]["data"]
        if not batch:
            break

        for q in batch:
            if not q["isPaidOnly"]:
                free.append({
                    "slug": q["titleSlug"],
                    "title": q["title"],
                    "difficulty": q["difficulty"]
                })
        skip += limit

    return free


def run():
    today = date.today().isoformat()
    state = load_state()

    solved_recent = fetch_recent_solved()

    for problems in state["assigned"].values():
        for p in problems:
            if p["status"] == "pending" and p["slug"] in solved_recent:
                p["status"] = "solved"
                p.setdefault("revision", False)

    pending = []
    solved_slugs = set()
    revision_slugs = set()
    pending_count = defaultdict(int)

    for problems in state["assigned"].values():
        for p in problems:
            if p["status"] == "pending":
                pending.append(p)
                pending_count[p["difficulty"]] += 1
            else:
                solved_slugs.add(p["slug"])
                if p.get("revision"):
                    revision_slugs.add(p["slug"])

    free = fetch_free_problems()
    buckets = defaultdict(list)

    for p in free:
        if ((p["slug"] not in solved_slugs or p["slug"] in revision_slugs)
            and not p.get("solve_later", False)):
            buckets[p["difficulty"]].append(p)

    for d in buckets:
        random.shuffle(buckets[d])

    new = []

    for diff, quota in DIFFICULTY_QUOTA.items():
        need = max(0, quota - pending_count[diff])
        while need > 0 and buckets[diff]:
            q = buckets[diff].pop()
            new.append({
                "slug": q["slug"],
                "title": q["title"],
                "difficulty": q["difficulty"],
                "status": "pending",
                "revision": False,
                "solve_later": False
            })
            need -= 1

    while len(pending) + len(new) < DAILY_TARGET:
        for diff in ["Easy", "Medium", "Hard"]:
            if buckets[diff]:
                q = buckets[diff].pop()
                new.append({
                    "slug": q["slug"],
                    "title": q["title"],
                    "difficulty": q["difficulty"],
                    "status": "pending",
                    "revision": False,
                    "solve_later": False
                })
                break
        else:
            break

    state["assigned"].setdefault(today, []).extend(new)
    save_state(state)


if __name__ == "__main__":
    run()

