import requests
import json
import os
import random
from datetime import datetime, date
from collections import defaultdict

# ---------------- CONFIG ----------------
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


# ---------------- HELPERS ----------------
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


# ---------------- MAIN ----------------
def run():
    today = date.today().isoformat()
    print(f"Running LeetCode problem generation for {today}...")

    state = load_state()

    solved_recent = fetch_recent_solved()
    print(f"Found {len(solved_recent)} problems solved since {SOLVED_AFTER.date()}")

    # Auto-mark solved
    updated_count = 0
    for problems in state["assigned"].values():
        for p in problems:
            if p["status"] == "pending" and p["slug"] in solved_recent:
                p["status"] = "solved"
                p.setdefault("revision", False)
                updated_count += 1
    print(f"Marked {updated_count} problems as solved")

    # Count existing pending problems
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

    print(f"Currently {len(pending)} pending problems")

    # Fetch free problems
    free = fetch_free_problems()
    print(f"Fetched {len(free)} free problems from LeetCode")

    buckets = defaultdict(list)
    for p in free:
        if ((p["slug"] not in solved_slugs or p["slug"] in revision_slugs)
            and not p.get("solve_later", False)):
            buckets[p["difficulty"]].append(p)

    for d in buckets:
        random.shuffle(buckets[d])
        print(f"{len(buckets[d])} free {d} problems available after filtering")

    new = []

    # Select problems based on quota
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

    # Fill remaining if needed
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

    if new:
        print(f"Assigning {len(new)} new problems today:")
        for p in new:
            print(f"- {p['title']} ({p['difficulty']})")
    else:
        print("No new problems available today (all free problems assigned or solved).")

    state["assigned"].setdefault(today, []).extend(new)
    save_state(state)
    print(f"Saved state.json with {len(state['assigned'].get(today, []))} problems for today")


if __name__ == "__main__":
    run()

