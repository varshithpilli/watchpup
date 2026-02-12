from bs4 import BeautifulSoup
import json
import re
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_captcha(text):
    soup = BeautifulSoup(text, "html.parser")
    captcha_block = soup.find("div", id="captchaBlock")
    if captcha_block is None: return False
    else: return True
    
def get_marks_json(response):
    # print(f"return_json() called\n\n")
    soup = BeautifulSoup(response.text, "html.parser")

    if response.status_code != 200:
        return {
            "MARKS_STATUS": "ERROR",
            "marks_data": []
        }

    main_table = soup.select_one("#fixedTableContainer > table.customTable")

    if main_table is None:
        return {
            "MARKS_STATUS": "PARSE_ERROR",
            "marks_data": []
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
        "MARKS_STATUS": "OK",
        "marks_data": courses
    }

def get_grades_json(response):
    
    # soup = BeautifulSoup(response, "html.parser")
    
    soup = BeautifulSoup(response.text, "html.parser")
    if response.status_code != 200:
        return {
            "GRADES_STATUS": "ERROR",
            "grades_data": []
        }


    table = soup.select_one("table.table.table-hover.table-bordered")

    if not table:
        return {
            "GRADES_STATUS": "PARSE_ERROR",
            "gpa": None,
            "grades_data": []
        }

    rows = table.find_all("tr", recursive=False)

    courses = []
    gpa = None

    for tr in rows:
        tds = tr.find_all("td", recursive=False)

        # GPA row
        if len(tds) == 1 and "GPA" in tds[0].get_text():
            txt = tds[0].get_text(strip=True)
            # "GPA : 9.32"
            gpa = txt.split("GPA")[1].replace(":", "").strip()
            continue

        # normal data row
        if len(tds) < 11:
            continue

        course = {
            "sl_no": tds[0].get_text(strip=True),
            "course_code": tds[1].get_text(strip=True),
            "course_title": tds[2].get_text(strip=True),
            "course_type": tds[3].get_text(strip=True),
            "credit_l": tds[4].get_text(strip=True),
            "credit_p": tds[5].get_text(strip=True),
            "credit_j": tds[6].get_text(strip=True),
            "credit_c": tds[7].get_text(strip=True),
            "grading_type": tds[8].get_text(strip=True),
            "total": tds[9].get_text(strip=True),
            "grade": tds[10].get_text(strip=True),
        }

        courses.append(course)

    return {
        "GRADES_STATUS": "OK",
        "gpa": gpa,
        "grades_data": courses
    }


def get_captcha_image(text):
    # print("save_captcha_image() called\n\n")
    soup = BeautifulSoup(text, "html.parser")
        
    captcha_block = soup.find("div", id="captchaBlock")
    captcha_file = None
    if captcha_block:
        img = captcha_block.find("img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("data:image"):
                header, encoded = src.split(",", 1)
                data = base64.b64decode(encoded)
                
                img_bytes = BytesIO(data)
                img = Image.open(img_bytes).convert("RGB")
                
                return img
                # captcha_file = Path("captcha.jpg")
                # captcha_file.write_bytes(data)
            else:
                if src.startswith("/"):
                    src = "https://vtopcc.vit.ac.in" + src
                img_resp = session.get(
                    src,
                    headers=headers,
                    timeout=30,
                    verify=False
                )

                img_resp.raise_for_status()
                
                img_bytes = BytesIO(data)
                img = Image.open(img_bytes).convert("RGB")
                
                return img
                # captcha_file = Path("captcha.jpg")
                # captcha_file.write_bytes(img_resp.content)


def get_csrf(html):
    m = re.search(
        r'<input[^>]+name="_csrf"[^>]+value="([^"]+)"',
        html
    )
    if not m:
        raise RuntimeError("CSRF token not found in page")
    return m.group(1)

if __name__ == "__main__":
    result = get_grades_json("""<div id="main-section"> <section class="content"> <link rel="stylesheet" href="assets/css/legend.css" /> <style>.legend .lightGreen {background-color: #C0D8C0;}</style> <div class="col-md-12"> <div class="box box-info"> <div class="box-header with-border"> <h3 class="box-title">Result - Grade View</h3> </div> <div class="box-body"> <form role="form" id="studentGradeView" name="studentGradeView" method="post" autocomplete="off"> <input type="hidden" name="authorizedID" id="authorizedID" value="23BPS1136" /> <!-- th:object="${examSchedule}"> --> <div class="col-md-12" style="margin-top: 20px; margin-left: 1px;"> <div> <div class="col-sm-6 col-sm-offset-3"> <div> <label for="acadYear" class="col-sm-4 control-label">Select Semester</label> <div class="col-md-8"> <select class="form-control" name="semesterSubId" id="semesterSubId" data-validation-engine="validate[required]" onchange="doViewExamGrade();"> <option value="" selected="selected">-- Choose Semester --</option> <option value="CH20252627">Winter Semester (Industry) 2025-26</option> <option value="CH20252626">Fall Semester (Industry) 2025-26</option> <option value="CH20252618">Winter Semester LLM 2025-26</option> <option value="CH20252605">Winter Semester 2025-26</option> <option value="CH20252614">Fall Semester LLM 2025-26</option> <option value="CH20252601" selected="selected">Fall Semester 2025-26</option> <option value="CH20242509">Summer Semester - II 2024-25</option> <option value="CH20242507">Summer Semester 2024-25</option> <option value="CH20242518">Winter Semester LLM 2024-25</option> <option value="CH20242505">Winter Semester 2024-25</option> <option value="CH20242501">Fall Semester 2024-25</option> <option value="CH20242514">Fall Semester LLM 2024-25</option> <option value="CH20232407">Summer Semester 2023-24</option> <option value="CH20232406">Tri Semester III &amp; VI 2023-24</option> <option value="CH20232418">Winter Semester LLM 2023-24</option> <option value="CH20232405">Winter Semester 2023-24</option> <option value="CH20232403">Tri Semester II &amp; V 2023-24</option> <option value="CH20232414">Fall Semester LLM 2023-24</option> <option value="CH20232417">Fall Semester I year 2023-24</option> <option value="CH20222309">Summer Semester - II 2022-23</option> <option value="CH20232402">Tri Semester I &amp; IV 2023-24</option> <option value="CH20232401">Fall Semester 2023-24</option> <option value="CH20222319">Summer Semester - III 2022-23</option> <option value="CH20222308">Summer Semester - I 2022-23</option> <option value="CH20222325">Fall Inter Semester 2022-23</option> <option value="CH20222318">Winter Semester LLM 2022-23</option> <option value="CH20222306">Tri Semester III &amp; VI 2022-23</option> <option value="CH20222323">Winter Semester I year 2022-23</option> <option value="CH2022235">Winter Semester 2022-23</option> <option value="CH2022233">Tri Semester II &amp; V 2022-23</option> <option value="CH20222314">Fall Semester LLM 2022-23</option> <option value="CH20222317">Fall Semester I year 2022-23</option> <option value="CH2022232">Tri Semester I &amp; IV 2022-23</option> <option value="CH2022231">Fall Semester 2022-23</option> <option value="CH20222312">Fall Semester LAW 2022-23</option> <option value="CH2021229">Summer Semester - II 2021-22</option> <option value="CH20212219">Summer Semester - III 2021-22</option> <option value="CH2021228">Summer Semester - I 2021-22</option> <option value="CH20212218">Winter Semester LLM 2021-22</option> <option value="CH20212223">Winter Semester I year 2021-22</option> <option value="CH20212224">Winter Semester LAW I year 2021-22</option> <option value="CH2021216">Tri Semester III &amp; VI 2021-22</option> <option value="CH20212216">Win Semester LAW 2021-22</option> <option value="CH2021225">Winter Semester 2021-22</option> <option value="CH20212222">Fall Intra Semester 2021-22</option> <option value="CH2021223">Tri Semester II &amp; V 2021-22</option> <option value="CH20212214">Fall Semester LLM 2021-22</option> <option value="CH20212221">Fall Semester I LAW 2021-22</option> <option value="CH20212217">Fall Semester I YEAR 2021-22</option> <option value="CH2021221">Fall Semester 2021-22</option> <option value="CH20212212">Fall Semester LAW 2021-22</option> <option value="CH2021222">Tri Semester I &amp; IV 2021-22</option> <option value="CH2020217">Summer Semester - II 2020-21</option> <option value="CH2020218">Summer Semester - I 2020-21</option> <option value="CH20202119">Summer Semester - III 2020-21</option> <option value="CH20202118">Winter Semester LLM 2020-21</option> <option value="CH20202117">Win Semester I YEAR 2020-21</option> <option value="CH20202116">Win Semester LAW 2020-21</option> <option value="CH2020215">Winter Semester 2020-21</option> <option value="CH20202115">INTERSEM 2020-21</option> <option value="CH2020213">Tri Semester II &amp; V 2020-21</option> <option value="CH20202114">Fall Semester LLM 2020-21</option> <option value="CH20202113">ARREAR II 2020-21</option> <option value="CH2020212">Tri Semester I &amp; IV 2020-21</option> <option value="CH20202112">FALL SEM LAW 2020-21</option> <option value="CH2020211">Fall Semester 2020-21</option> <option value="CH2019204">Arrear Semester 2019-20</option> <option value="CH2019208">Summer Semester - I 2019-20</option> <option value="CH2020219">Summer Semester - II 2019-20</option> <option value="CH2019207">Summer Semester 2019-20</option> <option value="CH2019206">Tri Semester III &amp; VI 2019-20</option> <option value="CH2019205">Winter Semester 2019-20</option> <option value="CH2019203">Tri Semester II &amp; V 2019-20</option> <option value="CH2019201">Fall Semester 2019-20</option> <option value="CH2018195">Winter Semester 2018-19</option> <option value="CH2018191">Fall Semester 2018-19</option> <option value="CH2017185">Winter Semester 2017-18</option> <option value="CH2017181">Fall Semester 2017-18</option> <option value="CH2016175">Winter Semester 2016-17</option> <option value="CH2016171">Fall Semester 2016-17</option> </select> </div> </div> </div> <div class="form-group col-sm-12"></div> <span class="col-sm-12 col-md-12" style="font-size: 20px; color: green; text-align: center;"></span> <span class="col-sm-12 col-md-12" style="font-size: 20px; color: red; text-align: center;"></span> <div class="row"> <div class="col-md-12"> <div class="col-md-12"> <div class="box-body table-responsive "> <table class="table table-hover table-bordered" style="border-bottom-color: #b1dfff; border-left-color: #b1dfff; border-right-color: #b1dfff;"> <tr style="background-color: #3c8dbc; color: white;"> <th rowspan="2">Sl.No.</th> <th rowspan="2">Course Code</th> <th rowspan="2">Course Title</th> <th rowspan="2">Course Type</th> <th colspan="4" align="center">Credits</th> <th rowspan="2">Grading Type</th> <th rowspan="2">Grand Total</th> <th rowspan="2">Grade</th> <th rowspan="2">View Mark</th> </tr> <tr style="background-color: #3c8dbc; color: white;"> <th>L</th> <th>P</th> <th>J</th> <th>C</th> </tr> <tr> <td height="50">1</td> <td>BCSE204L</td> <td>Design and Analysis of Algorithms</td> <td>Theory Only</td> <td>3</td> <td>0</td> <td>0</td> <td>3</td> <td>RG</td> <td>82</td> <td>A</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BCSE204L_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">2</td> <td>BCSE204P</td> <td>Design and Analysis of Algorithms Lab</td> <td>Lab Only</td> <td>0</td> <td>1</td> <td>0</td> <td>1</td> <td>AG</td> <td>93</td> <td>S</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BCSE204P_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">3</td> <td>BCSE301L</td> <td>Software Engineering</td> <td>Theory Only</td> <td>3</td> <td>0</td> <td>0</td> <td>3</td> <td>RG</td> <td>73</td> <td>A</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BCSE301L_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">4</td> <td>BCSE301P</td> <td>Software Engineering Lab</td> <td>Lab Only</td> <td>0</td> <td>1</td> <td>0</td> <td>1</td> <td>AG</td> <td>92</td> <td>S</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BCSE301P_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">5</td> <td>BCSE355L</td> <td>Cloud Architecture Design</td> <td>Theory Only</td> <td>3</td> <td>0</td> <td>0</td> <td>3</td> <td>RG</td> <td>85</td> <td>S</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BCSE355L_00110&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">6</td> <td>BEEE303L</td> <td>Control Systems</td> <td>Theory Only</td> <td>3</td> <td>0</td> <td>0</td> <td>3</td> <td>RG</td> <td>84</td> <td>A</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BEEE303L_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">7</td> <td>BEEE303P</td> <td>Control Systems Lab</td> <td>Lab Only</td> <td>0</td> <td>1</td> <td>0</td> <td>1</td> <td>AG</td> <td>89</td> <td>A</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BEEE303P_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">8</td> <td>BMAT202L</td> <td>Probability and Statistics</td> <td>Theory Only</td> <td>3</td> <td>0</td> <td>0</td> <td>3</td> <td>RG</td> <td>81</td> <td>A</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BMAT202L_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">9</td> <td>BMAT202P</td> <td>Probability and Statistics Lab</td> <td>Lab Only</td> <td>0</td> <td>1</td> <td>0</td> <td>1</td> <td>AG</td> <td>96</td> <td>S</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BMAT202P_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">10</td> <td>BMGT101L</td> <td>Principles of Management</td> <td>Theory Only</td> <td>3</td> <td>0</td> <td>0</td> <td>3</td> <td>RG</td> <td>76</td> <td>A</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BMGT101L_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr style="background-color: #C0D8C0;"> <td height="50">11</td> <td>BSSC102N</td> <td>Indian Constitution</td> <td>Online Course</td> <td>0</td> <td>0</td> <td>0</td> <td>2</td> <td>AG</td> <td>69</td> <td>P</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BSSC102N_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr> <td height="50">12</td> <td>BSTS301P</td> <td>Advanced Competitive Coding – I</td> <td>Soft Skill</td> <td>1.5</td> <td>0</td> <td>0</td> <td>1.5</td> <td>AG</td> <td>100</td> <td>S</td> <td><button type="button" name="action" class="btn btn-primary btn-block" onclick="javascript:getGradeViewDetails(&#39;CH_BSTS301P_00100&#39;);"> <span class="glyphicon glyphicon-plus"></span> </button> </td> </tr> <tr align="center"> <td colspan="14"> <span style="font-size: 18px; font-weight: bold;">GPA : 9.32</span> <!-- CGPA - 06-03-2025 --> </td> </tr> </table> </div> <div class="col-sm-12"> <div class="col-sm-12"> <ul class="legend"> <li><span class="lightGreen"></span> &nbsp;&nbsp;&nbsp;Course not included in GPA/CGPA</li> </ul></div> </div> </div> </div> </div> </div> </div> </form> </div> </div> </div> </section> <noscript> <h2 class="text-red">Enable JavaScript to Access VTOP</h2> </noscript> <!-- Custom Scripts for VTOP Pages--> <script> /*<![CDATA[*/ jQuery(document).ready(function() { // binds form submission and fields to the validation engine jQuery("#studentGradeView").validationEngine('attach', { autoHidePrompt : true, binded : false, onValidationComplete : function(form, status) { if (status) { doViewExamGrade(); } } }); }); function doViewExamGrade() { var myform = document.getElementById("studentGradeView"); var fd = new FormData(myform); var csrfName = "_csrf"; var csrfValue = "08ff3230-4edb-4655-bd45-b84b2e989f27"; fd.append(csrfName,csrfValue); $ .blockUI({ message : '<img src="assets/img/482.GIF"> loading... Just a moment...' }); $.ajax({ url : "examinations/examGradeView/doStudentGradeView", type : "POST", data : fd, cache : false, processData : false, contentType : false, success : function(response) { $.unblockUI(); $("#main-section").html(response); } }); }; function getGradeViewDetails(courseId) { var myform = document.getElementById("studentGradeView"); var semesterSubId = document.getElementById("semesterSubId").value; var authorizedID = document.getElementById("authorizedID").value; var now = new Date(); var csrfName = "_csrf"; var csrfValue = "08ff3230-4edb-4655-bd45-b84b2e989f27"; var params = "authorizedID="+authorizedID+"&x="+now.toUTCString()+"&semesterSubId=" + semesterSubId + "&courseId=" + courseId+"&"+csrfName+"="+csrfValue; $ .blockUI({ message : '<img src="assets/img/482.GIF"> loading... Just a moment...' }); $.ajax({ url : "examinations/examGradeView/getGradeViewDetails", type : "POST", data : params, success : function(response) { $.unblockUI(); $("#main-section").html(response); } }); }; /*]]>*/ </script> </div>""")
    with open("temp.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)