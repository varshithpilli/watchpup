import certifi
import requests
from dotenv import load_dotenv
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

JSESSIONID = os.getenv("VTOP_JSESSIONID")
SERVERID = os.getenv("VTOP_SERVERID")
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
        "SERVERID": SERVERID
    }
    
    print(JSESSIONID)
    print(CSRF)
    print(SERVERID)

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
        timeout=30,
        verify=False
    )

    return response

if __name__ == "__main__":
    text = return_response().text
    with open("temp.html", "a", encoding="utf-8") as f:
            f.write(f"{text}")