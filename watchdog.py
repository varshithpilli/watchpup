import time
import json
import hashlib
from pathlib import Path
from utils.request_handling import return_response
from utils.html_handling import return_json
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

INTERVAL_SECONDS = os.getenv("INTERVAL_SECONDS")
INTERVAL_SECONDS = eval(INTERVAL_SECONDS)
STATE_FILE = Path("last_state.json")

def handle_vtop():
    response = return_response()
    return return_json(response)

def get_hash(data) -> str:
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def load_previous():
    if not STATE_FILE.exists():
        return None
    with STATE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_current(data):
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def diff_marks(old, new):
    """
    old, new are the wrapped objects:
    { "STATUS": "OK", "data": [...] }
    """

    def flatten(snapshot):
        out = {}
        for course in snapshot["data"]:
            ccode = course["course_code"]
            for m in course["marks"]:
                key = (ccode, m["mark_title"])
                out[key] = m
        return out

    old_map = flatten(old)
    new_map = flatten(new)

    diffs = []

    all_keys = set(old_map) | set(new_map)

    for key in sorted(all_keys):
        o = old_map.get(key)
        n = new_map.get(key)

        course_code, mark_title = key

        if o is None:
            diffs.append({
                "type": "added",
                "course_code": course_code,
                "mark_title": mark_title,
                "new": n
            })
        elif n is None:
            diffs.append({
                "type": "removed",
                "course_code": course_code,
                "mark_title": mark_title,
                "old": o
            })
        else:
            # only care about actual value changes
            if o["scored_mark"] != n["scored_mark"]:
                diffs.append({
                    "type": "changed",
                    "course_code": course_code,
                    "mark_title": mark_title,
                    "old_scored": o["scored_mark"],
                    "new_scored": n["scored_mark"],
                })

    return diffs

def notify(previous, current):
    # TODO: Something notofication-y
    diffs = diff_marks(previous, current)

    print("================================================================")
    for d in diffs:
        if d["type"] == "changed":
            print(
                f'[{d["course_code"]}] {d["mark_title"]}: '
                f'{d["old_scored"]} -> {d["new_scored"]}'
            )
        elif d["type"] == "added":
            print(
                f'[{d["course_code"]}] {d["mark_title"]}: added'
            )
        elif d["type"] == "removed":
            print(
                f'[{d["course_code"]}] {d["mark_title"]}: removed'
            )
    print("================================================================")

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    previous = load_previous()

    previous_fp = (
        get_hash(previous["data"])
        if previous and previous.get("STATUS") == "OK"
        else None
    )

    print("Watchdog started...")

    while True:
        try:
            current = handle_vtop()

            if current.get("STATUS") != "OK":
                print(now(), "STATUS:", current.get("STATUS"))
                time.sleep(INTERVAL_SECONDS)
                continue

            current_fp = get_hash(current["data"])

            if previous_fp is None:
                print(now(), "STATUS: Initialised")
                save_current(current)
                previous = current
                previous_fp = current_fp

            elif current_fp != previous_fp:
                print(now(), "STATUS: Changes Found")
                notify(previous, current)
                save_current(current)
                previous = current
                previous_fp = current_fp

            else:
                print(now(), "STATUS: No Change")

        except Exception as e:
            print(now(), "Error while checking:", e)

        time.sleep(INTERVAL_SECONDS)



if __name__ == "__main__":
    main()