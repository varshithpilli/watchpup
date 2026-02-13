import traceback
import time
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

load_dotenv(BASE_DIR / ".env")

from utils import handle_vtop, get_hash, load_previous, save_current, diff_calendar, diff_grades, diff_marks, notify, now
from handlers.get_html import logout

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    filename = str(Path.home() / ".watchpup" / "watchpup.log"),
    filemode="a",
    level=logging.INFO,
    format="%(message)s"
)

REGD = os.getenv("REGD")
PASS = os.getenv("PASS")
VTOP_SEMID = os.getenv("VTOP_SEMID")
INTERVAL_SECONDS = eval(os.getenv("INTERVAL_SECONDS"))
MAX_RETIRES=os.getenv("MAX_RETIRES")
TG_BOT_TOKEN=os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID=os.getenv("TG_CHAT_ID")

def main():
    previous = load_previous()

    previous_fp = (
        get_hash(previous["data"])
        if previous and previous.get("STATUS") == "OK"
        else None
    )

    while True:
        try:
            print("Watchdog running...")
            current = handle_vtop(REGD, PASS, VTOP_SEMID, MAX_RETIRES)

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
                notify(previous["data"], current_data, TG_BOT_TOKEN, TG_CHAT_ID)
                logging.info(f"{now()} STATUS: Notification sent")
                save_current(current)
                previous = current
                previous_fp = current_fp

            else:
                logging.info(f"{now()} STATUS: No Change")
            
            logout(REGD)

        except Exception:
            logging.error(traceback.format_exc())

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()