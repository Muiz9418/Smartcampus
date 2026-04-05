import sys, os
sys.path.insert(0, "/Users/mac/Documents/my project")

import importlib.util
spec = importlib.util.spec_from_file_location("app_module", "/Users/mac/Documents/my project/app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app
from extensions import db
from app.models import *
from app.models.attendance import Attendance
from app.models.grade import Grade
from app.models.department import Department
from app.models.broadcast import Broadcast
from app.models.settings import Settings
from app.models.timetable import TimetableEvent
from app.models.transcript import TranscriptSemester, TranscriptCourse
from data.seed import db as old

with app.app_context():
    db.drop_all()
    db.create_all()

    # Users
    from app.models.user import User
    for email, u in old["users"].items():
        db.session.add(User(id=u["id"], email=u["email"], password=u["password"],
            role=u["role"], name=u["name"], initials=u["initials"],
            staff_id=u.get("staff_id"), department=u.get("department"),
            matric=u.get("matric"), status=u["status"]))

    # Students
    from app.models.student import Student
    for s in old["students"]:
        db.session.add(Student(**s))

    # Lecturers
    from app.models.lecturer import Lecturer
    for l in old["lecturers"]:
        db.session.add(Lecturer(id=l["id"], name=l["name"],
            dept=l["dept"], email=l["email"], status=l["status"]))

    # Courses
    from app.models.course import Course
    for c in old["courses"]:
        db.session.add(Course(code=c["code"], name=c["name"], dept=c["dept"],
            units=c["units"], lecturer_id=c["lecturer_id"], students=c["students"],
            status=c["status"], venue=c["venue"], days=c["days"], time=c["time"]))

    db.session.flush()

    # Attendance
    for matric, records in old["attendance"].items():
        for r in records:
            db.session.add(Attendance(matric=matric, course_code=r["code"],
                course_name=r["name"], attended=r["attended"], total=r["total"]))

    # Grades
    for matric, records in old["grades"].items():
        for r in records:
            db.session.add(Grade(matric=matric, course_code=r["code"],
                course_name=r["name"], ca=r["ca"], exam=r["exam"], units=r["units"]))

    # Departments
    for d in old["departments"]:
        db.session.add(Department(**d))

    # Notifications
    from app.models.notification import Notification
    for role, notes in old["notifications"].items():
        for n in notes:
            db.session.add(Notification(role=role, icon=n["icon"], title=n["title"],
                desc=n["desc"], time=n["time"], tag=n["tag"], unread=n["unread"]))

    # Broadcasts
    for b in old["broadcasts"]:
        db.session.add(Broadcast(id=b["id"], title=b["title"], body=b["body"],
            audience=b["audience"], tag=b["tag"], sent_at=b["sent_at"]))

    # Timetable events
    for e in old["timetable_events"]:
        db.session.add(TimetableEvent(day=e["day"], time=e["time"],
            label=e["label"], color=e["color"], tc=e["tc"]))

    # Settings
    for key, value in old["system_settings"].items():
        db.session.add(Settings(key=key, value=str(value)))

    # Transcript
    transcript = old["transcript"]["2021/CS/0042"]
    for sem in transcript["semesters"]:
        ts = TranscriptSemester(matric="2021/CS/0042",
            label=sem["label"], gpa=sem["gpa"], units=sem["units"])
        db.session.add(ts)
        db.session.flush()
        for c in sem["courses"]:
            db.session.add(TranscriptCourse(semester_id=ts.id,
                code=c["code"], name=c["name"], grade=c["grade"], units=c["units"]))

    db.session.commit()
    print("✅ smartcampus.db fully seeded — no more dict dependency!")
