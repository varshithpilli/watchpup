import requests

url = "https://vtopcc.vit.ac.in/vtop/examinations/doStudentMarkView"

headers = {
    "Origin": "https://vtopcc.vit.ac.in",
    "Referer": "https://vtopcc.vit.ac.in/vtop/content",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0",
}

# Only the important cookies
cookies = {
    "JSESSIONID": "354A199245E69B66FBF05BAE2A1E65E6",
    "SERVERID": "vt1"
}

# multipart/form-data payload
files = {
    "authorizedID": (None, "23BPS1136"),
    "semesterSubId": (None, "CH20252601"),
    "_csrf": (None, "9e0e1e10-042b-4323-b0c7-ba64e1761a7d"),
}

response = requests.post(
    url,
    headers=headers,
    cookies=cookies,
    files=files,   # important: files -> multipart/form-data
    timeout=30
)

print("Status:", response.status_code)
print(response.text[:1000])   # print first 1000 chars
