import certifi
import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

from .auth import get_csrf_auth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

REGD = os.getenv("REGD")
PASS = os.getenv("PASS")
SEM = os.getenv("VTOP_SEMID")
CSRF, session = get_csrf_auth()

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

def get_calendar_html():
    data1 = {
        "authorizedID": REGD,
        "classGroupId": "ALL",
        "semSubId": SEM,
        "paramReturnId": "getListForSemester",
        "_csrf": CSRF,
    }
    
    r1 = session.post(
        f"{BASE}/getListForSemester",
        headers=headers,
        data=data1,
        timeout=30,
        verify=False
    )

    soup = BeautifulSoup(r1.text, "html.parser")
    dates = []

    for a in soup.select("#getListForSemester a"):
        onclick = a.get("onclick", "")
        m = re.search(r"processViewCalendar\('([^']+)'\)", onclick)
        if m:
            dates.append(m.group(1))

    responses = []
    
    for date in dates:
        data2 = {
            "_csrf": CSRF,
            "calDate": date,
            "semSubId": SEM,
            "classGroupId": "ALL",
            "authorizedID": REGD,
        }
        
        r2 = session.post(
            f"{BASE}/processViewCalendar",
            headers=headers,
            data=data2,
            timeout=30,
            verify=False
        )
        
        responses.append(r2.text)
    
    return "".join(responses)

def logout():
    data = {
        "authorizedID": REGD,
        "_csrf": CSRF,
    }

    session.post(
        f"{BASE}/logout",
        headers=headers,
        data=data,
        timeout=30,
        verify=False
    )
    
if __name__ == "__main__":
    # text = get_ghist_html().text
    # with open("temp.html", "w", encoding="utf-8") as f:
    #         f.write(f"{text}")
    text = get_calendar_html()
    with open("temp.html", "w", encoding="utf-8") as f:
            f.write(text)