import json
import os

STATE_FILE = "data/state.json"

if not os.path.exists(STATE_FILE):
    raise FileNotFoundError(f"{STATE_FILE} not found")

title_slug = os.environ["TITLE_SLUG"]

with open(STATE_FILE) as f:
    state = json.load(f)

found = False
for day, problems in state["assigned"].items():
    for p in problems:
        if p["slug"] == title_slug:
            p["solve_later"] = True
            found = True

if not found:
    print(f"{title_slug} not found in state.json")
else:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(f"{title_slug} marked as solve_later")

