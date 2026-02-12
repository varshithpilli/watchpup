import certifi
import requests
import os
from dotenv import load_dotenv

from .auth import get_csrf_auth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

JSESSIONID = os.getenv("VTOP_JSESSIONID")
SERVERID = os.getenv("VTOP_SERVERID")
REGD = os.getenv("REGD")
PASS = os.getenv("PASS")
SEM = os.getenv("VTOP_SEMID")
CSRF, session = get_csrf_auth(REGD, PASS)

BASE = "https://vtopcc.vit.ac.in/vtop"

headers = {
    "Origin": "https://vtopcc.vit.ac.in",
    "Referer": "https://vtopcc.vit.ac.in/vtop/content",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0",
}

data = {
    "authorizedID": REGD,
    "semesterSubId": SEM,
    "_csrf": CSRF,
}

def get_marks_html():
    response = session.post(
        f"{BASE}/examinations/doStudentMarkView",
        headers=headers,
        data=data,
        timeout=30,
        verify=False
    )
    return response

def get_grades_html():
    response = session.post(
        f"{BASE}/examinations/examGradeView/doStudentGradeView",
        headers=headers,
        data=data,
        timeout=30,
        verify=False
    )
    return response

def get_ghist_html():
    data = {
        "authorizedID": REGD,
        "verifyMenu": "true",
        "_csrf": CSRF,
    }
    
    response = session.post(
        f"{BASE}/examinations/examGradeView/StudentGradeHistory",
        headers=headers,
        data=data,
        timeout=30,
        verify=False
    )
    return response

if __name__ == "__main__":
    text = get_ghist_html().text
    with open("temp.html", "w", encoding="utf-8") as f:
            f.write(f"{text}")