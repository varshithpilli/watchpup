import certifi
import requests
from dotenv import load_dotenv
from .auth import get_csrf_auth
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

JSESSIONID = os.getenv("VTOP_JSESSIONID")
SERVERID = os.getenv("VTOP_SERVERID")
REGD = os.getenv("REGD")
PASS = os.getenv("PASS")
SEM = os.getenv("VTOP_SEMID")
CSRF, session = get_csrf_auth(REGD, PASS)

url = "https://vtopcc.vit.ac.in/vtop/examinations/doStudentMarkView"

# def return_response():
#     print(f"return_response() called\n\n")
    
#     headers = {
#         "Origin": "https://vtopcc.vit.ac.in",
#         "Referer": "https://vtopcc.vit.ac.in/vtop/content",
#         "X-Requested-With": "XMLHttpRequest",
#         "User-Agent": "Mozilla/5.0",
#     }

#     cookies = {
#         # "JSESSIONID": JSESSIONID,
#         # "SERVERID": SERVERID
#     }
    
#     print(JSESSIONID)
#     print(CSRF)
#     print(SERVERID)

#     files = {
#         "authorizedID": (None, REGD),
#         "semesterSubId": (None, SEM),
#         "_csrf": (None, CSRF),
#     }

#     response = requests.post(
#         url,
#         headers=headers,
#         cookies=cookies,
#         files=files,
#         timeout=30,
#         verify=False
#     )

#     return response

def get_marks_html():

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

    response = session.post(
        url,
        headers=headers,
        data=data,      # <-- normal form post is enough
        timeout=30,
        verify=False
    )

    return response


def get_grades_html():

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

    response = session.post(
        "https://vtopcc.vit.ac.in/vtop/examinations/examGradeView/doStudentGradeView",
        headers=headers,
        data=data,      # <-- normal form post is enough
        timeout=30,
        verify=False
    )

    return response

if __name__ == "__main__":
    text = get_grades_html().text
    with open("temp.html", "a", encoding="utf-8") as f:
            f.write(f"{text}")