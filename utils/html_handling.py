from bs4 import BeautifulSoup
import json

def return_json(response):
    print(f"return_json() called\n\n")
    soup = BeautifulSoup(response.text, "html.parser")

    if response.status_code != 200:
        return {
            "STATUS": "ERROR",
            "data": []
        }

    main_table = soup.select_one("#fixedTableContainer > table.customTable")

    if main_table is None:
        return {
            "STATUS": "PARSE_ERROR",
            "data": []
        }

    rows = main_table.find_all("tr", recursive=False)

    courses = []

    i = 1
    while i < len(rows):
        course_row = rows[i]
        tds = course_row.find_all("td")

        if len(tds) < 9:
            i += 1
            continue

        course = {
            "sl_no": tds[0].get_text(strip=True),
            "class_nbr": tds[1].get_text(strip=True),
            "course_code": tds[2].get_text(strip=True),
            "course_title": tds[3].get_text(strip=True),
            "course_type": tds[4].get_text(strip=True),
            "course_system": tds[5].get_text(strip=True),
            "faculty": tds[6].get_text(strip=True),
            "slot": tds[7].get_text(strip=True),
            "course_mode": tds[8].get_text(strip=True),
            "marks": []
        }

        if i + 1 >= len(rows):
            courses.append(course)
            break

        marks_row = rows[i + 1]
        marks_table = marks_row.select_one("table.customTable-level1")

        if marks_table:
            mark_rows = marks_table.select("tr.tableContent-level1")

            for mr in mark_rows:
                cols = [c.get_text(strip=True) for c in mr.find_all("td")]

                if len(cols) < 10:
                    continue

                mark = {
                    "sl_no": cols[0],
                    "mark_title": cols[1],
                    "max_mark": cols[2],
                    "weightage_percent": cols[3],
                    "status": cols[4],
                    "scored_mark": cols[5],
                    "weightage_mark": cols[6],
                    "class_average": cols[7],
                    "mark_posted_strength": cols[8],
                    "remark": cols[9]
                }

                course["marks"].append(mark)

        courses.append(course)
        i += 2

    return {
        "STATUS": "OK",
        "data": courses
    }
    
if __name__ == "__main__":
    result = return_json()
    with open("temp.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)