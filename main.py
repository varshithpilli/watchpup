import traceback
import time
import logging
import os
from dotenv import load_dotenv

from utils import handle_vtop, get_hash, load_previous, save_current, diff_calendar, diff_grades, diff_marks, notify, now
from handlers.get_html import logout

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    filename="watchpup.log",
    filemode="a",
    level=logging.INFO,
    format="%(message)s"
)

load_dotenv()

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
            current = handle_vtop()

            status = current.get("STATUS")

            if status != "OK":
                logging.info(f"{now()} STATUS: {status}")
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
            return
        
        except Exception:
            logging.error(traceback.format_exc())


if __name__ == "__main__":
    main()