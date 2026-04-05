from flask import Blueprint, request
from extensions import ok, err, require_auth, db
from app.models.student import Student, StudentModel
from app.models.lecturer import Lecturer, LecturerModel
from app.models.course import Course, CourseModel
from app.models.notification import Notification, NotificationModel, BroadcastModel
from app.models.department import Department
from app.models.timetable import TimetableEvent
from app.models.settings import Settings

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

def _normalise_code(code): return code.replace("-", " ").upper()
def _normalise_matric(matric): return matric.replace("-", "/")

# ── Dashboard ──────────────────────────────────────────────────────────────
@bp.route("/dashboard", methods=["GET"])
@require_auth(["admin"])
def dashboard():
    from app.models.attendance import Attendance
    from app.models.grade import Grade

    total_students  = Student.query.count()
    total_lecturers = Lecturer.query.count()
    active_courses  = Course.query.filter_by(status="active").count()
    total_courses   = Course.query.count()
    notifs          = NotificationModel.get_for_role("admin")
    settings        = {s.key: s.value for s in Settings.query.all()}
    threshold       = int(settings.get("attendance_threshold", 70))

    # Real attendance stats
    att_records = Attendance.query.all()
    if att_records:
        avg_att = round(sum(r.rate for r in att_records) / len(att_records), 1)
        at_risk = sum(1 for r in att_records if r.rate < threshold)
    else:
        avg_att, at_risk = 0, 0

    # Real grade stats
    all_grades = Grade.query.all()
    submitted_courses = Course.query.filter_by(status="completed").count()
    grades_pct = round((submitted_courses / total_courses) * 100) if total_courses else 0

    # Registration: students with at least one attendance record
    registered = db.session.query(Attendance.matric).distinct().count()
    reg_pct = round((registered / total_students) * 100) if total_students else 0

    # Departments
    depts = Department.query.all()

    return ok({
        "stats": {
            "total_students":   total_students,
            "total_lecturers":  total_lecturers,
            "active_courses":   active_courses,
            "at_risk_students": at_risk,
        },
        "system_health": {
            "campus_attendance":       f"{avg_att}%",
            "grades_submitted":        f"{grades_pct}%",
            "at_risk_students":        f"{at_risk} students",
            "pending_grade_approvals": f"{total_courses - submitted_courses} courses",
            "registration_completion": f"{reg_pct}%",
        },
        "departments": [d.to_dict() for d in depts],
        "semester": settings.get("current_semester", "2024/2025 Semester 1"),
        "recent_notifications": [n for n in notifs["notifications"] if n["unread"]][:3],
    })

# ── Analytics ──────────────────────────────────────────────────────────────
@bp.route("/analytics", methods=["GET"])
@require_auth(["admin"])
def analytics():
    from app.models.attendance import Attendance
    from app.models.grade import Grade

    depts = Department.query.all()

    # Real attendance average
    att_records = Attendance.query.all()
    avg_att = round(sum(r.rate for r in att_records) / len(att_records), 1) if att_records else 0

    # Real grade distribution
    grades = Grade.query.all()
    dist = {"A":0,"B":0,"C":0,"D":0,"F":0}
    total_units, total_points = 0, 0
    for g in grades:
        dist[g.letter] = dist.get(g.letter, 0) + 1
        total_units  += g.units
        total_points += g.points * g.units
    avg_gpa = round(total_points / total_units, 2) if total_units else 0

    completed = Course.query.filter_by(status="completed").count()

    # Real monthly attendance trend from AttendanceRecord
    from app.models.attendance_record import AttendanceRecord
    from collections import defaultdict
    import calendar

    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    # Group attendance records by month
    monthly = defaultdict(list)
    for rec in AttendanceRecord.query.all():
        try:
            month = int(rec.date.split("-")[1])
            monthly[month].append(1 if rec.status == "present" else 0)
        except: pass

    # Build trend for last 7 months
    from datetime import date
    current_month = date.today().month
    months_list, values_list = [], []
    for i in range(6, -1, -1):
        m = ((current_month - 1 - i) % 12) + 1
        months_list.append(month_map[m])
        data = monthly.get(m, [])
        values_list.append(round(sum(data)/len(data)*100, 1) if data else 0)

    return ok({
        "summary": {
            "campus_attendance": f"{avg_att}%",
            "courses_completed": completed,
            "avg_gpa":           avg_gpa,
            "dropout_rate":      "0%",
        },
        "attendance_trend": {
            "months": months_list,
            "values": values_list,
        },
        "grade_distribution": {
            "labels": ["A","B","C","D","F"],
            "values": [dist["A"],dist["B"],dist["C"],dist["D"],dist["F"]],
        },
        "departments": [d.to_dict() for d in depts],
    })

# ── Students ───────────────────────────────────────────────────────────────
@bp.route("/students", methods=["GET"])
@require_auth(["admin"])
def get_students():
    q = request.args.get("q", "")
    return ok({"students": StudentModel.list_all(q), "total": Student.query.count()})

@bp.route("/students", methods=["POST"])
@require_auth(["admin"])
def add_student():
    student, error = StudentModel.create(request.get_json(force=True))
    if error: return err(error)
    return ok(student), 201

@bp.route("/students/<matric>", methods=["PUT"])
@require_auth(["admin"])
def update_student(matric):
    student, error = StudentModel.update(_normalise_matric(matric), request.get_json(force=True))
    if error: return err(error, 404 if "not found" in error else 400)
    return ok(student)

@bp.route("/students/<matric>", methods=["DELETE"])
@require_auth(["admin"])
def delete_student(matric):
    normalised = _normalise_matric(matric)
    if not StudentModel.delete(normalised): return err("Student not found.", 404)
    return ok({"message": f"Student {normalised} deleted."})

# ── Lecturers ──────────────────────────────────────────────────────────────
@bp.route("/lecturers", methods=["GET"])
@require_auth(["admin"])
def get_lecturers():
    q = request.args.get("q", "")
    return ok({"lecturers": LecturerModel.list_all(q), "total": Lecturer.query.count()})

@bp.route("/lecturers", methods=["POST"])
@require_auth(["admin"])
def add_lecturer():
    lec, error = LecturerModel.create(request.get_json(force=True))
    if error: return err(error)
    return ok(lec), 201

@bp.route("/lecturers/<staff_id>", methods=["PUT"])
@require_auth(["admin"])
def update_lecturer(staff_id):
    lec, error = LecturerModel.update(staff_id, request.get_json(force=True))
    if error: return err(error, 404 if "not found" in error else 400)
    return ok(lec)

@bp.route("/lecturers/<staff_id>", methods=["DELETE"])
@require_auth(["admin"])
def delete_lecturer(staff_id):
    if not LecturerModel.delete(staff_id): return err("Lecturer not found.", 404)
    return ok({"message": f"Lecturer {staff_id} deleted."})

# ── Courses ────────────────────────────────────────────────────────────────
@bp.route("/courses", methods=["GET"])
@require_auth(["admin"])
def get_courses():
    q = request.args.get("q", "")
    return ok({"courses": CourseModel.list_all(q), "total": Course.query.count()})

@bp.route("/courses", methods=["POST"])
@require_auth(["admin"])
def add_course():
    course, error = CourseModel.create(request.get_json(force=True))
    if error: return err(error)
    return ok(course), 201

@bp.route("/courses/<code>", methods=["PUT"])
@require_auth(["admin"])
def update_course(code):
    course, error = CourseModel.update(_normalise_code(code), request.get_json(force=True))
    if error: return err(error, 404 if "not found" in error else 400)
    return ok(course)

@bp.route("/courses/<code>", methods=["DELETE"])
@require_auth(["admin"])
def delete_course(code):
    normalised = _normalise_code(code)
    if not CourseModel.delete(normalised): return err("Course not found.", 404)
    return ok({"message": f"Course {normalised} deleted."})

# ── Timetable ──────────────────────────────────────────────────────────────
@bp.route("/timetable", methods=["GET"])
@require_auth(["admin"])
def get_timetable():
    settings = {s.key: s.value for s in Settings.query.all()}
    return ok({
        "slots":    CourseModel.get_timetable_slots(),
        "events":   [e.to_dict() for e in TimetableEvent.query.all()],
        "semester": settings.get("current_semester", "2024/2025 Semester 1"),
    })

@bp.route("/timetable/<code>", methods=["PUT"])
@require_auth(["admin"])
def update_timetable(code):
    course, error = CourseModel.update_timetable_slot(
        _normalise_code(code), request.get_json(force=True))
    if error: return err(error, 404 if "not found" in error else 400)
    return ok(course)

# ── Attendance overview ────────────────────────────────────────────────────
@bp.route("/att-overview", methods=["GET"])
@require_auth(["admin"])
def att_overview():
    depts = Department.query.all()
    campus_avg = round(sum(d.avg_attendance for d in depts) / len(depts), 1) if depts else 0
    return ok({
        "campus_avg":    f"{campus_avg}%",
        "total_at_risk": sum(d.at_risk for d in depts),
        "departments":   [d.to_dict() for d in depts],
    })

# ── Department management ─────────────────────────────────────────────────
@bp.route("/departments", methods=["GET"])
@require_auth(["admin"])
def get_departments():
    from app.models.student import Student
    from app.models.lecturer import Lecturer
    from app.models.attendance import Attendance
    from app.models.settings import Settings

    settings = {s.key: s.value for s in Settings.query.all()}
    threshold = int(settings.get("attendance_threshold", 70))

    depts = Department.query.all()
    result = []
    for d in depts:
        # Auto-calculate counts from real data
        students  = Student.query.filter(
            db.func.lower(Student.dept).like(f"%{d.name.lower()}%")).all()
        lecturers = Lecturer.query.filter(
            db.func.lower(Lecturer.dept).like(f"%{d.name.lower()}%")).all()
        courses   = Course.query.filter(
            db.func.lower(Course.dept).like(f"%{d.name.lower()}%")).all()

        # Attendance stats
        att_records = []
        for s in students:
            att_records += Attendance.query.filter_by(matric=s.matric).all()

        avg_att  = round(sum(r.rate for r in att_records) / len(att_records), 1) if att_records else 0
        at_risk  = sum(1 for r in att_records if r.rate < threshold)

        # Update the department record with real counts
        d.students       = len(students)
        d.lecturers      = len(lecturers)
        d.courses        = len(courses)
        d.avg_attendance = avg_att
        d.at_risk        = at_risk

        result.append({
            "name":           d.name,
            "students":       len(students),
            "lecturers":      len(lecturers),
            "courses":        len(courses),
            "avg_attendance": avg_att,
            "at_risk":        at_risk,
            "avg_gpa":        d.avg_gpa,
            "pass_rate":      d.pass_rate,
            "trend":          d.trend,
        })

    db.session.commit()
    return ok({"departments": result, "total": len(result)})

@bp.route("/departments", methods=["POST"])
@require_auth(["admin"])
def add_department():
    body = request.get_json(force=True)
    name = (body.get("name") or "").strip()
    if not name:
        return err("Department name is required.")
    if Department.query.get(name):
        return err("Department already exists.")
    d = Department(
        name=name,
        students=0, lecturers=0, courses=0,
        avg_attendance=0, at_risk=0,
        avg_gpa=0.0, pass_rate=0, trend="flat"
    )
    db.session.add(d)
    db.session.commit()
    return ok(d.to_dict()), 201

@bp.route("/departments/<name>", methods=["PUT"])
@require_auth(["admin"])
def update_department(name):
    name = name.replace("-", " ")
    d = Department.query.get(name)
    if not d:
        return err("Department not found.", 404)
    body = request.get_json(force=True)
    for f in ["students","lecturers","courses","avg_attendance","at_risk","avg_gpa","pass_rate","trend"]:
        if f in body: setattr(d, f, body[f])
    db.session.commit()
    return ok(d.to_dict())

@bp.route("/departments/<name>", methods=["DELETE"])
@require_auth(["admin"])
def delete_department(name):
    name = name.replace("-", " ")
    d = Department.query.get(name)
    if not d:
        return err("Department not found.", 404)
    db.session.delete(d)
    db.session.commit()
    return ok({"message": f"{name} deleted."})

# ── Student level management ───────────────────────────────────────────────
@bp.route("/students/<matric>/level", methods=["PUT"])
@require_auth(["admin"])
def update_student_level(matric):
    from app.models.user import User
    matric = _normalise_matric(matric)
    s = Student.query.get(matric)
    if not s:
        return err("Student not found.", 404)
    body = request.get_json(force=True)
    level = body.get("level")
    if not level:
        return err("Level is required.")
    s.level = level
    # Also update user record
    u = User.query.filter_by(matric=matric).first()
    if u: u.level = level
    db.session.commit()
    return ok({"matric": s.matric, "level": s.level})

# ── Grades management ──────────────────────────────────────────────────────
@bp.route("/grades-mgmt", methods=["GET"])
@require_auth(["admin"])
def grades_mgmt():
    from app.models.grade import Grade
    courses = Course.query.all()
    result = []
    for c in courses:
        grades = Grade.query.filter_by(course_code=c.code).all()
        submitted = all(g.exam is not None for g in grades) if grades else False
        result.append({
            "code":      c.code,
            "name":      c.name,
            "students":  c.students or 0,
            "lecturer":  c.lecturer_id or "—",
            "submitted": submitted,
            "total_grades": len(grades),
            "status":    "completed" if submitted else "pending",
        })
    pending   = [r for r in result if not r["submitted"]]
    submitted = [r for r in result if r["submitted"]]
    return ok({"pending": pending, "submitted": submitted})

@bp.route("/grades-mgmt/<code>/approve", methods=["POST"])
@require_auth(["admin"])
def approve_grades(code):
    code = _normalise_code(code)
    c = Course.query.get(code)
    if not c:
        return err("Course not found.", 404)
    c.status = "completed"
    db.session.commit()
    return ok({"message": f"Grades for {code} approved."})

# ── Notifications ──────────────────────────────────────────────────────────
@bp.route("/notifications", methods=["GET"])
@require_auth(["admin"])
def notifications():
    return ok(NotificationModel.get_for_role("admin"))

@bp.route("/notifications/read-all", methods=["POST"])
@require_auth(["admin"])
def mark_all_read():
    NotificationModel.mark_all_read("admin")
    return ok({"message": "All marked as read."})

# ── Broadcasts ─────────────────────────────────────────────────────────────
@bp.route("/broadcasts", methods=["GET"])
@require_auth(["admin"])
def get_broadcasts():
    return ok({"broadcasts": BroadcastModel.list_all()})

@bp.route("/broadcast", methods=["POST"])
@require_auth(["admin"])
def send_broadcast():
    from app.utils.email import send_broadcast_emails
    from app.models.settings import Settings
    body = request.get_json(force=True)
    title    = body.get("title", "")
    msg_body = body.get("body", "")
    audience = body.get("audience", "Everyone")
    tag      = body.get("tag", "Admin")

    broadcast, error = BroadcastModel.send(
        title=title, body=msg_body,
        audience=audience, tag=tag,
    )
    if error: return err(error)

    # Send real emails
    try:
        sent, failed = send_broadcast_emails(audience, title, msg_body)
        return ok({**broadcast, "emails_sent": sent, "emails_failed": failed}), 201
    except Exception as e:
        return ok({**broadcast, "emails_sent": 0, "email_error": str(e)}), 201

# ── Settings ───────────────────────────────────────────────────────────────
@bp.route("/settings", methods=["GET"])
@require_auth(["admin"])
def get_settings():
    return ok({s.key: s.value for s in Settings.query.all()})

@bp.route("/settings", methods=["POST"])
@require_auth(["admin"])
def update_settings():
    body = request.get_json(force=True)
    allowed = ["institution_name","current_semester","current_week",
               "attendance_threshold","grade_deadline","registration_deadline",
               "email_notifications","sms_notifications",
               "auto_at_risk_alerts","maintenance_mode"]
    for key in allowed:
        if key in body:
            s = Settings.query.get(key)
            if s: s.value = str(body[key])
            else: db.session.add(Settings(key=key, value=str(body[key])))
    db.session.commit()
    return ok({s.key: s.value for s in Settings.query.all()})
