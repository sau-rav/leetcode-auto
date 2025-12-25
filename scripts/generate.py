import requests
import json
import os
import random
from datetime import datetime, date
from collections import defaultdict

# ================= CONFIG =================
LEETCODE_USER = "saurav_ksharma"
SOLVED_AFTER = datetime(2025, 12, 25)

STATE_FILE = "data/state.json"
GRAPHQL = "https://leetcode.com/graphql"

DAILY_TARGET = 5
DIFFICULTY_QUOTA = {"Easy": 2, "Medium": 2, "Hard": 1}

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
# ==========================================


def graphql(query, variables):
    r = requests.post(
        GRAPHQL,
        headers=HEADERS,
        json={"query": query, "variables": variables},
        timeout=20
    )
    r.raise_for_status()
    return r.json()["data"]


def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# -------- STEP 1: FETCH RECENT SOLVED --------
def fetch_recent_solved():
    query = """
    query recentAc($username: String!) {
      recentAcSubmissionList(username: $username, limit: 100) {
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


# -------- MAIN LOGIC --------
def run():
    today = date.today().isoformat()
    print(f"Running LeetCode problem generation for {today}")

    state = load_state()
    problems = state["problems"]

    # ---- 1. MARK SOLVED PROBLEMS ----
    solved_recent = fetch_recent_solved()
    print(f"Found {len(solved_recent)} problems solved since {SOLVED_AFTER.date()}")

    solved_count = 0
    for p in problems:
        if p["status"] == "pending" and p["slug"] in solved_recent:
            p["status"] = "solved"
            p["solved_on"] = today
            p["assigned_on"] = None
            solved_count += 1

    print(f"Marked {solved_count} problems as solved")

    # ---- 2. COUNT CURRENT PENDING (EXCLUDING solve_later) ----
    pending_today = [
        p for p in problems
        if p["status"] == "pending"
        and p["assigned_on"] == today
        and not p["solve_later"]
    ]

    pending_by_diff = defaultdict(int)
    for p in pending_today:
        pending_by_diff[p["difficulty"]] += 1

    print(f"Currently {len(pending_today)} pending problems (excluding solve_later)")

    if len(pending_today) >= DAILY_TARGET:
        print("Daily quota already satisfied")
        save_state(state)
        return

    # ---- 3. ELIGIBLE POOL ----
    pool = [
        p for p in problems
        if p["status"] == "pending"
        and not p["solve_later"]
        and p["assigned_on"] is None
    ]

    buckets = defaultdict(list)
    for p in pool:
        buckets[p["difficulty"]].append(p)

    for d in buckets:
        random.shuffle(buckets[d])

    new_assigned = []

    # ---- 4. DIFFICULTY BALANCING ----
    for diff, quota in DIFFICULTY_QUOTA.items():
        need = max(0, quota - pending_by_diff[diff])
        while need > 0 and buckets[diff]:
            q = buckets[diff].pop()
            new_assigned.append(q)
            need -= 1

    # ---- 5. FILL TO 5 ----
    while len(new_assigned) + len(pending_today) < DAILY_TARGET:
        for diff in ["Easy", "Medium", "Hard"]:
            if buckets[diff]:
                new_assigned.append(buckets[diff].pop())
                break
        else:
            break

    # ---- 6. ASSIGN ----
    for p in new_assigned:
        p["assigned_on"] = today

    state["meta"]["last_generated_on"] = today
    save_state(state)

    print(f"Assigned {len(new_assigned)} new problems")


if __name__ == "__main__":
    run()

