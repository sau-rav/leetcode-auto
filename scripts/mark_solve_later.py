import json
import sys
from datetime import date

STATE_FILE = "data/state.json"

if len(sys.argv) < 2:
    print("Usage: python mark_solved.py <slug>")
    sys.exit(1)

slug = sys.argv[1]
today = date.today().isoformat()

with open(STATE_FILE) as f:
    state = json.load(f)

found = False
for p in state["problems"]:
    if p["slug"] == slug:
        p["status"] = "pending"
        p["assigned_on"] = None
        p["solve_later"] = true
        found = True
        break

if not found:
    print("Problem not found")
    sys.exit(1)

with open(STATE_FILE, "w") as f:
    json.dump(state, f, indent=2)

print(f"Marked {slug} as solved")

