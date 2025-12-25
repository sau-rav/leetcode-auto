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


# ---------------- LEETCODE DATA ----------------
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
    state = load_state()
    state.setdefault(today, [])

    solved_recent = fetch_recent_solved()

    # Auto-mark solved problems
    for problems in state["assigned"].values():
        for p in problems:
            if p["status"] == "pending" and p["slug"] in solved_recent:
                p["status"] = "solved"
                p.setdefault("revision", False)

    # Count existing pending for today
    existing_today_slugs = {p['slug'] for p in state[today] if p['status'] == 'pending'}
    pending_today_count = len(existing_today_slugs)

    # Skip adding new if already have DAILY_TARGET pending
    if pending_today_count >= DAILY_TARGET:
        save_state(state)
        print(f"{DAILY_TARGET} problems already assigned today. Nothing new added.")
        return

    # Fetch all problems
    free = fetch_free_problems()
    buckets = defaultdict(list)

    # Prepare buckets by difficulty
    for p in free:
        if ((p["slug"] not in existing_today_slugs and p["slug"] not in solved_recent)
            and not p.get("solve_later", False)):
            buckets[p["difficulty"]].append(p)

    for d in buckets:
        random.shuffle(buckets[d])

    # Select new problems according to difficulty quota
    new = []
    pending_count_by_diff = defaultdict(int)
    for p in state[today]:
        if p["status"] == "pending":
            pending_count_by_diff[p["difficulty"]] += 1

    for diff, quota in DIFFICULTY_QUOTA.items():
        need = max(0, quota - pending_count_by_diff[diff])
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

    # Fill remaining slots to reach DAILY_TARGET
    while len(new) + pending_today_count < DAILY_TARGET:
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
            break  # no more free problems

    state[today].extend(new)
    save_state(state)
    print(f"Assigned {len(new)} new problems today.")


if __name__ == "__main__":
    run()

