import traceback
import time
import json
import hashlib
from pathlib import Path
import requests
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

from handlers.get_html import get_marks_html, get_grades_html, get_ghist_html, logout, get_calendar_html
from handlers.parse_html import get_marks_json, get_grades_json, get_cgpa_json, get_calendar_json

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
    marks_html = get_marks_html()
    marks_json = get_marks_json(marks_html)
    grades_html = get_grades_html()
    grades_json = get_grades_json(grades_html)
    cgpa_html = get_ghist_html()
    cgpa_json = get_cgpa_json(cgpa_html)
    calendar_html = get_calendar_html()
    calendar_json = get_calendar_json(calendar_html)
    
    marks_ok = marks_json.get("MARKS_STATUS") == "OK"
    grades_ok = grades_json.get("GRADES_STATUS") == "OK"
    cgpa_ok = cgpa_json.get("CGPA_STATUS") == "OK"

    global_status = "OK" if (marks_ok and grades_ok and cgpa_ok) else "ERROR"

    return {
        "STATUS": global_status,
        "data": {
            "marks": marks_json,
            "grades": grades_json,
            "cgpa": cgpa_json,
            "calendar": calendar_json
        }
    }

def get_hash(data):
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def load_previous():
    if not STATE_FILE.exists():
        return None
    if STATE_FILE.stat().st_size == 0:
        return None
    with STATE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_current(data):
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def diff_marks(old_state, new_state):
    
    old_marks = old_state["marks"].get("marks_data", [])
    new_marks = new_state["marks"].get("marks_data", [])

    def flatten(courses):
        out = {}
        for course in courses:
            ccode = course.get("course_code")
            for m in course.get("marks", []):
                key = (ccode, m.get("mark_title"))
                out[key] = m
        return out

    old_map = flatten(old_marks)
    new_map = flatten(new_marks)

    diffs = []

    all_keys = set(old_map) | set(new_map)

    for key in sorted(all_keys):
        o = old_map.get(key)
        n = new_map.get(key)

        course_code, mark_title = key

        if o is None and n is not None:
            diffs.append({
                "section": "marks",
                "type": "added",
                "course_code": course_code,
                "mark_title": mark_title,
                "new": n
            })

        elif n is None and o is not None:
            diffs.append({
                "section": "marks",
                "type": "removed",
                "course_code": course_code,
                "mark_title": mark_title,
                "old": o
            })

        elif o is not None and n is not None:
            if o.get("scored_mark") != n.get("scored_mark"):
                diffs.append({
                    "section": "marks",
                    "type": "changed",
                    "course_code": course_code,
                    "mark_title": mark_title,
                    "old": o,
                    "new": n
                })

    return diffs

def normalize_calendar(cal):
    out = {}

    for m in cal:
        month = m["month"]

        for d in m["days"]:
            key = f"{month}-{d['day']:02d}"
            out[key] = sorted(d.get("events", []))

    return out

def diff_calendar(old_cal, new_cal):
    old_map = normalize_calendar(old_cal)
    new_map = normalize_calendar(new_cal)

    changes = []

    common_keys = set(old_map) & set(new_map)

    for k in sorted(common_keys):
        old_events = old_map[k]
        new_events = new_map[k]

        if old_events == new_events:
            continue

        added = sorted(set(new_events) - set(old_events))
        removed = sorted(set(old_events) - set(new_events))

        if added or removed:
            changes.append({
                "date": k,
                "added": added,
                "removed": removed
            })

    return changes

def diff_grades(old_state, new_state):

    old_rows = old_state["grades"].get("grades_data", [])
    new_rows = new_state["grades"].get("grades_data", [])

    def to_map(rows):
        out = {}
        for r in rows:
            ccode = r.get("course_code")
            if ccode:
                out[ccode] = r
        return out

    old_map = to_map(old_rows)
    new_map = to_map(new_rows)

    diffs = []

    all_keys = set(old_map) | set(new_map)

    for ccode in sorted(all_keys):
        o = old_map.get(ccode)
        n = new_map.get(ccode)

        if o is None and n is not None:
            diffs.append({
                "section": "grades",
                "type": "added",
                "course_code": ccode,
                "new": n
            })

        elif n is None and o is not None:
            diffs.append({
                "section": "grades",
                "type": "removed",
                "course_code": ccode,
                "old": o
            })

        elif o is not None and n is not None:
            if (
                o.get("grade") != n.get("grade")
                or o.get("total") != n.get("total")
            ):
                diffs.append({
                    "section": "grades",
                    "type": "changed",
                    "course_code": ccode,
                    "old": o,
                    "new": n
                })

    return diffs


def notify(previous, current):
    diffs = []

    diffs.extend(diff_marks(previous, current))
    diffs.extend(diff_grades(previous, current))


    old_cgpa = None
    new_cgpa = None

    if previous.get("cgpa", {}).get("CGPA_STATUS") == "OK":
        old_cgpa = previous["cgpa"].get("cgpa_data")

    if current.get("cgpa", {}).get("CGPA_STATUS") == "OK":
        new_cgpa = current["cgpa"].get("cgpa_data")

    cgpa_changed = (
        old_cgpa is not None and
        new_cgpa is not None and
        old_cgpa != new_cgpa
    )
    
    calendar_diffs = diff_calendar(
        previous.get("calendar", []),
        current.get("calendar", [])
    )
   
    if not diffs and not cgpa_changed and not calendar_diffs:
        return

    lines = []
    lines.append("VTOP Watchdog")
    lines.append("Change detected\n")

    for d in diffs:
        if d["section"] == "marks":

            if d["type"] == "changed":
                lines.append(
                    f'[MARKS] [{d["course_code"]}] {d["mark_title"]}: '
                    f'{d["old"]["scored_mark"]} → {d["new"]["scored_mark"]}'
                )

            elif d["type"] == "added":
                m = d["new"]
                lines.append(
                    f'[MARKS] [{d["course_code"]}] {d["mark_title"]}: '
                    f'added = {m["scored_mark"]} / {m["max_mark"]} '
                    f'({m["status"]})'
                )

            elif d["type"] == "removed":
                m = d["old"]
                lines.append(
                    f'[MARKS] [{d["course_code"]}] {d["mark_title"]}: '
                    f'removed = {m["scored_mark"]} / {m["max_mark"]} '
                    f'({m["status"]})'
                )
                
        elif d["section"] == "grades":

            if d["type"] == "changed":
                lines.append(
                    f'[GRADES] [{d["course_code"]}]: '
                    f'{d["old"]["grade"]} ({d["old"]["total"]}) '
                    f'→ {d["new"]["grade"]} ({d["new"]["total"]})'
                )

            elif d["type"] == "added":
                g = d["new"]
                lines.append(
                    f'[GRADES] [{d["course_code"]}]: '
                    f'added = {g["grade"]} ({g["total"]})'
                )

            elif d["type"] == "removed":
                g = d["old"]
                lines.append(
                    f'[GRADES] [{d["course_code"]}]: '
                    f'removed = {g["grade"]} ({g["total"]})'
                )

    if cgpa_changed:
        lines.append(f'[CGPA]: {old_cgpa} → {new_cgpa}')
        
    for c in calendar_diffs:
        raw_date = c["date"]

        try:
            dt = datetime.strptime(raw_date, "%B %Y-%d")
            pretty_date = dt.strftime("%d-%m-%Y %A")
        except Exception:
            pretty_date = raw_date

        added = c.get("added", [])
        removed = c.get("removed", [])

        if added and removed:
            for old, new in zip(removed, added):
                lines.append(
                    f'[CALENDAR] {pretty_date}: "{old}" → "{new}"'
                )

        elif added:
            for e in added:
                lines.append(
                    f'[CALENDAR] {pretty_date}: added "{e}"'
                )

        elif removed:
            for e in removed:
                lines.append(
                    f'[CALENDAR] {pretty_date}: removed "{e}"'
                )

    msg = "\n".join(lines)
    
    print(msg)
    
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

    while True:
        try:
            current = handle_vtop()

            status = current.get("STATUS")

            if status != "OK":
                logging.info(f"{now()} STATUS: {status}")
                time.sleep(INTERVAL_SECONDS)
                continue

            current_data = current["data"]
            current_fp = get_hash(current_data)

            if previous is None:
                logging.info(f"{now()} STATUS: Initialised")
                save_current(current)
                previous = current
                previous_fp = current_fp

            elif current_fp != previous_fp:
                logging.info(f"{now()} STATUS: Changes Found")
                notify(previous["data"], current_data)
                logging.info(f"{now()} STATUS: Notification sent")
                save_current(current)
                previous = current
                previous_fp = current_fp

            else:
                logging.info(f"{now()} STATUS: No Change")
            
            logout()

        except Exception:
            logging.error(traceback.format_exc())

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()