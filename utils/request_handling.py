import certifi
import requests
from dotenv import load_dotenv
import os

load_dotenv()

JSESSIONID = os.getenv("VTOP_JSESSIONID")
CSRF = os.getenv("VTOP_CSRF")
REGD = os.getenv("VTOP_REGD")
SEM = os.getenv("VTOP_SEMID")

url = "https://vtopcc.vit.ac.in/vtop/examinations/doStudentMarkView"

def return_response():
    print(f"return_response() called\n\n")
    
    headers = {
        "Origin": "https://vtopcc.vit.ac.in",
        "Referer": "https://vtopcc.vit.ac.in/vtop/content",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
    }

    cookies = {
        "JSESSIONID": JSESSIONID,
        "SERVERID": "vt1"
    }

    files = {
        "authorizedID": (None, REGD),
        "semesterSubId": (None, SEM),
        "_csrf": (None, CSRF),
    }

    response = requests.post(
        url,
        headers=headers,
        cookies=cookies,
        files=files,
        verify=False,
        timeout=30
    )

    return response

# text = return_response().text
# with open("temp.html", "a", encoding="utf-8") as f:
#         f.write(f"{text}")