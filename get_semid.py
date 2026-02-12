from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

from handlers.auth import get_csrf_auth

load_dotenv()

REGD = os.getenv("REGD")
PASS = os.getenv("PASS")

CSRF, session = get_csrf_auth()

url = "https://vtopcc.vit.ac.in/vtop/academics/common/StudentTimeTableChn"

headers = {
    "Origin": "https://vtopcc.vit.ac.in",
    "Referer": "https://vtopcc.vit.ac.in/vtop/content",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0",
}

data = {
    "authorizedID": REGD,
    "verifyMenu": "true",
    "_csrf": CSRF,
}

response = session.post(
    url,
    headers=headers,
    data=data,
    timeout=30,
    verify=False
)

soup = BeautifulSoup(response.text, "html.parser")

select = soup.find("select", id="semesterSubId")

for opt in select.find_all("option"):
    sem_id = opt.get("value", "").strip()
    sem_name = opt.get_text(strip=True)

    if not sem_id:
        continue

    print(sem_id, "->", sem_name)