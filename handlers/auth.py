import requests
from dotenv import load_dotenv
import os
import urllib3
from .html import save_captcha_image, extract_csrf, check_captcha
from .captcha import solve_captcha
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

MAX_RETRIES = eval(os.getenv("MAX_RETIRES"))
REGD = os.getenv("REGD")
PASS = os.getenv("PASS")

BASE = "https://vtopcc.vit.ac.in/vtop"

def get_csrf_auth(username, password):
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
    csrf_unauth = extract_csrf(r1.text)
    print("csrf_unauth:", csrf_unauth)

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


    for attempt in range(MAX_RETRIES):

        r3 = session.get(
            f"{BASE}/login",
            headers=headers,
            timeout=30,
            verify=False
        )
        r3.raise_for_status()

        if check_captcha(r3.text):
            save_captcha_image(r3.text)
            break

        print("captchaBlock not found – retrying...")
        time.sleep(1)
    
    r4 = session.post(
        f"{BASE}/login",
        data={
            "_csrf": csrf_unauth,
            "username": username,
            "password": password,
            "captchaStr": solve_captcha()
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
    csrf_auth = extract_csrf(r5.text)
    print("csrf_auth:", csrf_auth)

    return csrf_auth, session

if __name__ == "__main__":
    get_csrf_auth(REGD, PASS)