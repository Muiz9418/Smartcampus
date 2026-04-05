"""
data/seed.py - In-memory fallback data for SmartCampus.
"""

def grade_letter(total: int) -> str:
    if total >= 70: return "A"
    if total >= 60: return "B"
    if total >= 50: return "C"
    if total >= 45: return "D"
    return "F"

def grade_points(letter: str) -> int:
    return {"A": 5, "B": 4, "C": 3, "D": 2, "F": 0}.get(letter, 0)

db = {
"users": {
    "student@unilag.edu.ng": {"id":"USR-STU-001","email":"student@unilag.edu.ng","password":"password","role":"student","name":"Obi Ade","initials":"OA","matric":"2021/CS/0042","department":"Computer Science","faculty":"Science","level":"300L","mode_of_entry":"UTME","admission_date":"Sept 2021","status":"active"},
    "deze@unilag.edu.ng":    {"id":"USR-LEC-001","email":"deze@unilag.edu.ng","password":"password","role":"lecturer","name":"Dr. David Eze","initials":"DE","staff_id":"STF-0041","department":"Computer Science","title":"Dr.","status":"active"},
    "faliyu@unilag.edu.ng":  {"id":"USR-ADM-001","email":"faliyu@unilag.edu.ng","password":"password","role":"admin","name":"Fatima Aliyu","initials":"FA","staff_id":"ADM-001","department":"Registry","status":"active"},
},
"students": [
    {"matric":"2021/CS/0042","name":"Obi Ade",      "dept":"Computer Sci.","level":"300L","email":"student@unilag.edu.ng","status":"active"},
    {"matric":"2021/CS/001", "name":"Amaka Obi",     "dept":"Computer Sci.","level":"300L","email":"amaka@unilag.edu.ng",  "status":"active"},
    {"matric":"2021/CS/002", "name":"Bode Lawal",    "dept":"Computer Sci.","level":"300L","email":"bode@unilag.edu.ng",   "status":"active"},
    {"matric":"2020/MTH/010","name":"Chisom Eze",    "dept":"Mathematics",  "level":"400L","email":"chisom@unilag.edu.ng", "status":"inactive"},
    {"matric":"2022/PHY/005","name":"Dayo Femi",     "dept":"Physics",      "level":"200L","email":"dayo@unilag.edu.ng",   "status":"active"},
    {"matric":"2021/ENG/030","name":"Efe Igho",      "dept":"Engineering",  "level":"300L","email":"efe@unilag.edu.ng",    "status":"active"},
    {"matric":"2023/CS/011", "name":"Funke Adeyemi", "dept":"Computer Sci.","level":"100L","email":"funke@unilag.edu.ng",  "status":"active"},
],
"lecturers": [
    {"id":"STF-0041","name":"Dr. David Eze",    "dept":"Computer Sci.","courses":4,"students":312,"email":"deze@unilag.edu.ng",    "status":"active"},
    {"id":"STF-0029","name":"Dr. Adaora Nwosu", "dept":"Mathematics",  "courses":3,"students":280,"email":"adaora@unilag.edu.ng",  "status":"active"},
    {"id":"STF-0018","name":"Prof. Amina Bello","dept":"Physics",      "courses":2,"students":180,"email":"abello@unilag.edu.ng",  "status":"active"},
    {"id":"STF-0055","name":"Mr. Chidi Okonkwo","dept":"English",      "courses":5,"students":450,"email":"cokonkwo@unilag.edu.ng","status":"active"},
    {"id":"STF-0033","name":"Dr. Emeka Obi",    "dept":"Computer Sci.","courses":3,"students":220,"email":"eobi@unilag.edu.ng",    "status":"inactive"},
],
"departments": [
    {"name":"Computer Science","students":620,"lecturers":22,"courses":14,"avg_attendance":83,"at_risk":12,"avg_gpa":3.52,"pass_rate":97,"trend":"up"},
    {"name":"Mathematics",     "students":540,"lecturers":18,"courses":12,"avg_attendance":79,"at_risk":18,"avg_gpa":3.40,"pass_rate":95,"trend":"flat"},
    {"name":"Physics",         "students":380,"lecturers":15,"courses":10,"avg_attendance":77,"at_risk":15,"avg_gpa":3.31,"pass_rate":93,"trend":"up"},
    {"name":"Engineering",     "students":890,"lecturers":28,"courses":18,"avg_attendance":82,"at_risk":20,"avg_gpa":3.48,"pass_rate":96,"trend":"up"},
    {"name":"Economics",       "students":460,"lecturers":16,"courses": 8,"avg_attendance":80,"at_risk":10,"avg_gpa":3.38,"pass_rate":94,"trend":"flat"},
],
"courses": [
    {"code":"CSC 301","name":"Algorithms & Complexity",  "dept":"Comp. Sci.", "units":3,"lecturer":"Dr. Eze",    "lecturer_id":"STF-0041","students":87, "status":"active",    "venue":"Hall B",   "days":"Mon/Wed",    "time":"08:00-09:30"},
    {"code":"MTH 202","name":"Calculus II",               "dept":"Mathematics","units":3,"lecturer":"Dr. Adaora","lecturer_id":"STF-0029","students":120,"status":"active",    "venue":"LT 1",     "days":"Tue/Thu",    "time":"11:00-12:30"},
    {"code":"ENG 210","name":"Technical Writing",         "dept":"English",    "units":2,"lecturer":"Mr. Chidi","lecturer_id":"STF-0055","students":95, "status":"active",    "venue":"Room 14A", "days":"Fri",        "time":"14:00-16:00"},
    {"code":"PHY 305","name":"Electromagnetism",          "dept":"Physics",    "units":3,"lecturer":"Prof. Bello","lecturer_id":"STF-0018","students":80,"status":"active",   "venue":"LT 2",     "days":"Mon/Thu",    "time":"13:00-14:30"},
    {"code":"CSC 315","name":"Database Systems",          "dept":"Comp. Sci.", "units":3,"lecturer":"Dr. Eze",   "lecturer_id":"STF-0041","students":92, "status":"active",    "venue":"Hall C",   "days":"Tue/Fri",    "time":"09:00-10:30"},
    {"code":"CSC 401","name":"Advanced Algorithms",       "dept":"Comp. Sci.", "units":3,"lecturer":"Dr. Eze",   "lecturer_id":"STF-0041","students":54, "status":"active",    "venue":"Room 3A",  "days":"Tue/Thu",    "time":"14:00-15:30"},
    {"code":"STA 201","name":"Statistics for Engineers",  "dept":"Statistics", "units":2,"lecturer":"Dr. Alabi","lecturer_id":"STF-0060","students":160,"status":"completed", "venue":"LT 3",     "days":"Wed",        "time":"10:00-12:00"},
    {"code":"CSC 210","name":"Data Structures",           "dept":"Comp. Sci.", "units":3,"lecturer":"Dr. Eze",   "lecturer_id":"STF-0041","students":120,"status":"active",    "venue":"Hall A",   "days":"Mon/Wed/Fri","time":"07:00-08:00"},
    {"code":"CSC 110","name":"Intro to CS",               "dept":"Comp. Sci.", "units":3,"lecturer":"Dr. Eze",   "lecturer_id":"STF-0041","students":51, "status":"active",    "venue":"Hall D",   "days":"Tue/Thu",    "time":"16:00-17:00"},
],
"timetable_events": [
    {"day":"Mon","time":"08:00","label":"CSC 301","color":"#dbeafe","tc":"#1d4ed8"},
    {"day":"Mon","time":"13:00","label":"PHY 305","color":"#ede9fe","tc":"#6d28d9"},
    {"day":"Tue","time":"09:00","label":"CSC 315","color":"#dcf5e8","tc":"#15803d"},
    {"day":"Tue","time":"11:00","label":"MTH 202","color":"#fef3c7","tc":"#92400e"},
    {"day":"Wed","time":"08:00","label":"CSC 301","color":"#dbeafe","tc":"#1d4ed8"},
    {"day":"Wed","time":"15:00","label":"STA 201","color":"#fee2e2","tc":"#b91c1c"},
    {"day":"Thu","time":"11:00","label":"MTH 202","color":"#fef3c7","tc":"#92400e"},
    {"day":"Thu","time":"13:00","label":"PHY 305","color":"#ede9fe","tc":"#6d28d9"},
    {"day":"Fri","time":"09:00","label":"CSC 315","color":"#dcf5e8","tc":"#15803d"},
    {"day":"Fri","time":"14:00","label":"ENG 210","color":"#fce7f3","tc":"#be185d"},
],
"attendance": {
    "2021/CS/0042": [
        {"code":"CSC 301","name":"Algorithms",       "attended":14,"total":16,"rate":87.5,"status":"good"},
        {"code":"MTH 202","name":"Calculus II",       "attended":11,"total":16,"rate":68.8,"status":"bad"},
        {"code":"ENG 210","name":"Technical Writing", "attended":10,"total":12,"rate":83.3,"status":"good"},
        {"code":"PHY 305","name":"Electromagnetism",  "attended": 8,"total":10,"rate":80.0,"status":"ok"},
        {"code":"CSC 315","name":"Database Systems",  "attended":12,"total":14,"rate":85.7,"status":"good"},
        {"code":"STA 201","name":"Statistics",        "attended": 9,"total":10,"rate":90.0,"status":"good"},
    ],
},
"mark_att_sessions": {
    "CSC 301": [
        {"id":"2021/CS/001","name":"Amaka Obi",    "status": None},
        {"id":"2021/CS/002","name":"Bode Lawal",   "status": None},
        {"id":"2021/CS/003","name":"Chisom Eze",   "status": None},
        {"id":"2021/CS/004","name":"Dayo Femi",    "status": None},
        {"id":"2021/CS/005","name":"Efe Igho",     "status": None},
        {"id":"2021/CS/006","name":"Funke Adeyemi","status": None},
    ],
},
"grades": {
    "2021/CS/0042": [
        {"code":"CSC 301","name":"Algorithms",       "ca":32,"exam":52,"total":84,"grade":"A","units":3},
        {"code":"MTH 202","name":"Calculus II",       "ca":28,"exam":45,"total":73,"grade":"B","units":3},
        {"code":"ENG 210","name":"Technical Writing", "ca":35,"exam":49,"total":84,"grade":"A","units":2},
        {"code":"PHY 305","name":"Electromagnetism",  "ca":24,"exam":40,"total":64,"grade":"C","units":3},
        {"code":"CSC 315","name":"Database Systems",  "ca":33,"exam":50,"total":83,"grade":"A","units":3},
        {"code":"STA 201","name":"Statistics",        "ca":30,"exam":48,"total":78,"grade":"B","units":2},
    ],
},
"grade_upload": {
    "CSC 301": [
        {"id":"2021/CS/001","name":"Amaka Obi",    "ca":35,"exam":None},
        {"id":"2021/CS/002","name":"Bode Lawal",   "ca":22,"exam":None},
        {"id":"2021/CS/003","name":"Chisom Eze",   "ca":38,"exam":None},
        {"id":"2021/CS/004","name":"Dayo Femi",    "ca":28,"exam":None},
        {"id":"2021/CS/005","name":"Efe Igho",     "ca":19,"exam":None},
        {"id":"2021/CS/006","name":"Funke Adeyemi","ca":36,"exam":None},
    ],
},
"transcript": {
    "2021/CS/0042": {
        "cumulative_gpa": 3.52,
        "semesters": [
            {"label":"2021/22 Semester 1","gpa":3.40,"units":16,"courses":[
                {"code":"CSC 101","name":"Intro to Computing",  "grade":"B","units":3},
                {"code":"MTH 101","name":"Elementary Maths I",  "grade":"A","units":3},
                {"code":"GST 101","name":"Communication Skills","grade":"B","units":2},
            ]},
            {"label":"2021/22 Semester 2","gpa":3.60,"units":14,"courses":[
                {"code":"CSC 102","name":"Programming Fundamentals","grade":"A","units":3},
                {"code":"MTH 102","name":"Elementary Maths II",      "grade":"B","units":3},
                {"code":"PHY 101","name":"Physics I",                "grade":"B","units":2},
            ]},
            {"label":"2024/25 Semester 1 (Current)","gpa":3.60,"units":16,"courses":[
                {"code":"CSC 301","name":"Algorithms",       "grade":"A","units":3},
                {"code":"MTH 202","name":"Calculus II",       "grade":"B","units":3},
                {"code":"ENG 210","name":"Technical Writing", "grade":"A","units":2},
            ]},
        ],
    },
},
"notifications": {
    "student": [
        {"id":"n1","unread":True, "icon":"📢","title":"Assignment Due: CSC 301",       "desc":"Your Algorithms assignment must be submitted by Friday March 15 at 11:59 PM.","time":"2 hours ago","tag":"Academic"},
        {"id":"n2","unread":True, "icon":"📋","title":"Mid-Semester Results Released",  "desc":"Your results for 2024/25 Semester 1 mid-semester exams are now available.",  "time":"Yesterday", "tag":"Results"},
        {"id":"n3","unread":False,"icon":"🗓","title":"Campus Closed - Public Holiday", "desc":"The university will be closed on Wednesday March 25, 2026.",                "time":"3 days ago","tag":"Admin"},
        {"id":"n4","unread":False,"icon":"📣","title":"Semester Registration Open",     "desc":"Registration for 2024/25 Semester 2 is now open. Deadline is April 5.",     "time":"Last week", "tag":"Admin"},
        {"id":"n5","unread":False,"icon":"⚠","title":"Attendance Warning - MTH 202",   "desc":"Your attendance is below 70%. Please attend upcoming classes.",             "time":"2 weeks ago","tag":"Attendance"},
    ],
    "lecturer": [
        {"id":"n1","unread":True, "icon":"📢","title":"Grade Submission Deadline - Apr 1","desc":"Grades for CSC 301 and CSC 401 must be submitted by April 1, 2026.",         "time":"Today",     "tag":"Admin"},
        {"id":"n2","unread":True, "icon":"📋","title":"Faculty Meeting - Wednesday 4pm", "desc":"All teaching staff are expected at the faculty board meeting in Room 101.",  "time":"Today",     "tag":"Meeting"},
        {"id":"n3","unread":False,"icon":"📣","title":"Exam Timetable Released",          "desc":"The final examination timetable for 2024/25 Semester 1 has been published.","time":"Yesterday", "tag":"Exams"},
        {"id":"n4","unread":False,"icon":"⚠","title":"2 Students At-Risk in CSC 301",    "desc":"Students Bode Lawal and Efe Igho are below the 70% attendance threshold.", "time":"2 days ago","tag":"Attendance"},
    ],
    "admin": [
        {"id":"n1","unread":True, "icon":"📢","title":"Grade Submission Deadline Tomorrow","desc":"6 courses have not yet submitted grades. Deadline: April 1, 2026.",         "time":"Today",     "tag":"Grades"},
        {"id":"n2","unread":True, "icon":"⚠","title":"87 Students At-Risk",               "desc":"Attendance below 70% threshold campus-wide. Action may be required.",      "time":"Today",     "tag":"Attendance"},
        {"id":"n3","unread":False,"icon":"📣","title":"Semester 2 Registration Open",      "desc":"Students can now register for 2024/25 Semester 2 courses.",                "time":"Yesterday", "tag":"Admin"},
        {"id":"n4","unread":False,"icon":"✅","title":"System Backup Completed",           "desc":"Scheduled backup completed successfully at 03:00 AM.",                     "time":"2 days ago","tag":"System"},
    ],
},
"broadcasts": [
    {"id":"b1","title":"Semester 2 Registration Now Open","body":"Students can now register for 2024/25 Semester 2. Deadline is April 5, 2026.",         "audience":"All Students","sent_at":"2026-03-25 09:00","tag":"Admin"},
    {"id":"b2","title":"Campus Closed - Public Holiday",  "body":"The university will be closed on Wednesday March 25 in observance of a public holiday.","audience":"Everyone",   "sent_at":"2026-03-22 14:30","tag":"Admin"},
    {"id":"b3","title":"Grade Submission Reminder",       "body":"All lecturers must upload final grades no later than April 1, 2026.",                   "audience":"All Lecturers","sent_at":"2026-03-20 11:00","tag":"Grades"},
],
"analytics": {
    "attendance_trend":   {"months":["Sep","Oct","Nov","Dec","Jan","Feb","Mar"],"values":[72,76,74,78,80,82,81]},
    "grade_distribution": {"labels":["A","B","C","D","E","F"],"values":[10,25,35,20,7,3]},
    "summary":            {"campus_attendance":"81%","courses_completed":8,"avg_gpa":3.41,"dropout_rate":"1.2%"},
},
"system_settings": {
    "institution_name":"University of Lagos","current_semester":"2024/2025 Semester 1",
    "current_week":11,"attendance_threshold":70,"grade_deadline":"2026-04-01",
    "registration_deadline":"2026-04-05","email_notifications":True,
    "sms_notifications":False,"auto_at_risk_alerts":True,"maintenance_mode":False,
},
"lecturer_att_report": {
    "CSC 301": {
        "total_classes": 16,
        "students": [
            {"id":"2021/CS/001","name":"Amaka Obi",    "attended":16,"absent":0,"rate":100,  "risk":False},
            {"id":"2021/CS/002","name":"Bode Lawal",   "attended":10,"absent":6,"rate":62.5, "risk":True},
            {"id":"2021/CS/003","name":"Chisom Eze",   "attended":15,"absent":1,"rate":93.8, "risk":False},
            {"id":"2021/CS/004","name":"Dayo Femi",    "attended":13,"absent":3,"rate":81.3, "risk":False},
            {"id":"2021/CS/005","name":"Efe Igho",     "attended":11,"absent":5,"rate":68.8, "risk":True},
            {"id":"2021/CS/006","name":"Funke Adeyemi","attended":14,"absent":2,"rate":87.5, "risk":False},
        ],
    },
},
"materials": {
    "CSC 301": [
        {"icon":"📄","name":"Week 1 - Introduction to Algorithms","meta":"PDF 2.4 MB"},
        {"icon":"📄","name":"Week 2 - Sorting Algorithms",         "meta":"PDF 1.8 MB"},
        {"icon":"📄","name":"Week 3 - Graph Theory",               "meta":"PDF 3.1 MB"},
        {"icon":"📋","name":"Assignment 1 - Due Mar 15",           "meta":"Problem set"},
        {"icon":"📋","name":"Mid-Semester Exam Guide",             "meta":"Study material"},
    ],
},
"lecturer_schedule": {
    "STF-0041": {
        "today": [
            {"time":"09:00","course":"CSC 301 - Algorithms",        "venue":"Hall B",  "students":87},
            {"time":"14:00","course":"CSC 401 - Advanced Algorithms","venue":"Room 3A","students":54},
        ],
        "courses": [
            {"code":"CSC 301","name":"Algorithms",         "students":87, "avg_attendance":"84%"},
            {"code":"CSC 401","name":"Advanced Algorithms","students":54, "avg_attendance":"81%"},
            {"code":"CSC 210","name":"Data Structures",    "students":120,"avg_attendance":"76%"},
            {"code":"CSC 110","name":"Intro to CS",        "students":51, "avg_attendance":"91%"},
        ],
    },
},
}
