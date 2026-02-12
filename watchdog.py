import time
import json
import hashlib
from pathlib import Path
from handlers.html import return_json
from handlers.main_request import return_response
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import logging


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    filename="watchpup.log",
    filemode="a",
    level=logging.INFO,
    format="%(message)s"
)

load_dotenv()

INTERVAL_SECONDS = os.getenv("INTERVAL_SECONDS")
INTERVAL_SECONDS = eval(INTERVAL_SECONDS)
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
STATE_FILE = Path("last_state.json")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

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
    diffs = diff_marks(previous, current)

    if not diffs:
        return

    # print("================================================================")
    # for d in diffs:
    #     if d["type"] == "changed":
    #         print(
    #             f'[{d["course_code"]}] {d["mark_title"]}: '
    #             f'{d["old_scored"]} -> {d["new_scored"]}'
    #         )
    #     elif d["type"] == "added":
    #         print(
    #             f'[{d["course_code"]}] {d["mark_title"]}: added'
    #         )
    #     elif d["type"] == "removed":
    #         print(
    #             f'[{d["course_code"]}] {d["mark_title"]}: removed'
    #         )
    # print("================================================================")

    lines = []
    lines.append("VTOP Watchdog")
    lines.append("Change detected\n")

    for d in diffs:
        if d["type"] == "changed":
            lines.append(
                f'[{d["course_code"]}] {d["mark_title"]}: '
                f'{d["old_scored"]} -> {d["new_scored"]}'
            )
        elif d["type"] == "added":
            lines.append(
                f'[{d["course_code"]}] {d["mark_title"]}: added'
            )
        elif d["type"] == "removed":
            lines.append(
                f'[{d["course_code"]}] {d["mark_title"]}: removed'
            )

    lines.append("")

    msg = "\n".join(lines)

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    previous = load_previous()

    previous_fp = (
        get_hash(previous["data"])
        if previous and previous.get("STATUS") == "OK"
        else None
    )

    # print("Watchdog started...")

    while True:
        try:
            current = handle_vtop()

            if current.get("STATUS") != "OK":
                logging.info(f"{now()} STATUS: {current.get("STATUS")}")
                print()
                time.sleep(INTERVAL_SECONDS)
                continue

            current_fp = get_hash(current["data"])

            if previous_fp is None:
                logging.info(f"{now()} STATUS: Initialised")
                save_current(current)
                previous = current
                previous_fp = current_fp

            elif current_fp != previous_fp:
                logging.info(f"{now()} STATUS: Changes Found")
                notify(previous, current)
                logging.info(f"{now()} STATUS: Notification sent")
                save_current(current)
                previous = current
                previous_fp = current_fp

            else:
                logging.info(f"{now()} STATUS: No Change")

        except Exception as e:
            logging.info(f"{now()} STATUS: Error while checking: {e}")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()