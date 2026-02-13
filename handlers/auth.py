import time
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    base_dir = Path(sys.executable).parent
else:
    base_dir = Path(__file__).parent

load_dotenv(base_dir / ".env")

from .parse_html import get_captcha_image, get_csrf, check_captcha
from .captcha import solve_captcha

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_RETIRES = int(os.getenv("MAX_RETIRES"))
# MAX_RETIRES = 10
REGD = os.getenv("REGD")
PASS = os.getenv("PASS")

BASE = "https://vtopcc.vit.ac.in/vtop"

def get_csrf_auth():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    r1 = session.get(
        f"{BASE}/open/page",
        headers=headers,
        timeout=30,
        verify=False
    )
    r1.raise_for_status()
    csrf_unauth = get_csrf(r1.text)

    r2 = session.post(
        f"{BASE}/prelogin/setup",
        data={
            "_csrf": csrf_unauth,
            "flag": "VTOP"
        },
        headers=headers,
        timeout=30,
        verify=False
    )
    r2.raise_for_status()

    for attempt in range(MAX_RETIRES):
        r3 = session.get(
            f"{BASE}/login",
            headers=headers,
            timeout=30,
            verify=False
        )
        r3.raise_for_status()

        if check_captcha(r3.text):
            img = get_captcha_image(r3.text)
            break
        time.sleep(1)
        
    captchaString = solve_captcha(img)
    
    r4 = session.post(
        f"{BASE}/login",
        data={
            "_csrf": csrf_unauth,
            "username": REGD,
            "password": PASS,
            "captchaStr": captchaString
        },
        headers=headers,
        timeout=30,
        verify=False,
        allow_redirects=True
    )
    r4.raise_for_status()

    r5 = session.get(
        f"{BASE}/content",
        headers=headers,
        timeout=30,
        verify=False
    )
    r5.raise_for_status()
    csrf_auth = get_csrf(r5.text)

    return csrf_auth, session

if __name__ == "__main__":
    get_csrf_auth(REGD, PASS)