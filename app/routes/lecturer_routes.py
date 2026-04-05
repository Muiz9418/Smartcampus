from flask import Blueprint, request
from extensions import ok, err, require_auth, current_user, db
from app.models.course import Course
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.attendance_record import AttendanceRecord
from app.models.enrolment import Enrolment
from app.models.grade import Grade
from app.models.notification import Notification, NotificationModel
from app.models.material import Material
from datetime import date

bp = Blueprint("lecturer", __name__, url_prefix="/api/lecturer")


def _my_courses(staff_id):
    return Course.query.filter_by(lecturer_id=staff_id).all()


@bp.route("/dashboard", methods=["GET"])
@require_auth(["lecturer"])
def dashboard():
    from datetime import date
    u = current_user()
    courses = _my_courses(u.staff_id)
    total_students = sum(c.students or 0 for c in courses)
    notifs = NotificationModel.get_for_role("lecturer")

    # Today's day name
    day_map = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
    today_day = day_map[date.today().weekday()].upper()

    # Today's classes — match course days against today
    today = []
    for c in courses:
        if not c.days: continue
        course_days = [d.strip().upper()[:3] for d in c.days.replace("/"," ").split()]
        if today_day[:3] in course_days:
            today.append({
                "time":    c.time.split("-")[0] if c.time else "—",
                "course":  f"{c.code} — {c.name}",
                "venue":   c.venue or "—",
                "students": c.students or 0,
                "code":    c.code,
            })

    # Real avg attendance per course
    course_list = []
    for c in courses:
        records = Attendance.query.filter_by(course_code=c.code).all()
        avg = round(sum(r.rate for r in records)/len(records),1) if records else None
        course_list.append({
            "code":           c.code,
            "name":           c.name,
            "students":       c.students or 0,
            "avg_attendance": f"{avg}%" if avg is not None else "No data",
        })

    # Overall avg attendance across all courses
    all_records = []
    for c in courses:
        all_records += Attendance.query.filter_by(course_code=c.code).all()
    avg_att = round(sum(r.rate for r in all_records)/len(all_records),1) if all_records else None

    return ok({
        "user": u.to_dict(),
        "stats": {
            "total_courses":  len(courses),
            "total_students": total_students,
            "classes_today":  len(today),
            "avg_attendance": f"{avg_att}%" if avg_att is not None else "No data",
        },
        "today":   today,
        "courses": course_list,
        "recent_notifications": [n for n in notifs["notifications"] if n["unread"]][:3],
    })


@bp.route("/schedule", methods=["GET"])
@require_auth(["lecturer"])
def schedule():
    u = current_user()
    courses = _my_courses(u.staff_id)
    return ok({
        "courses": [c.to_dict() for c in courses],
        "today":   [],
    })


@bp.route("/mark-att/<code>", methods=["GET"])
@require_auth(["lecturer"])
def get_mark_att(code):
    code = code.replace("-", " ").upper()
    date_str = request.args.get("date") or date.today().strftime("%Y-%m-%d")

    # Only enrolled students
    enrolments = Enrolment.query.filter_by(course_code=code).all()
    matrics = [e.matric for e in enrolments]
    students = Student.query.filter(Student.matric.in_(matrics)).all()

    # Check if already marked for this date
    existing = {
        r.matric: r.status
        for r in AttendanceRecord.query.filter_by(
            course_code=code, date=date_str).all()
    }

    course = Course.query.get(code)
    return ok({
        "course":         code,
        "course_name":    f"{code} — {course.name}" if course else code,
        "date":           date_str,
        "already_marked": len(existing) > 0,
        "students": [
            {"id": s.matric, "name": s.name,
             "status": existing.get(s.matric, None)}
            for s in students
        ]
    })


@bp.route("/mark-att/<code>", methods=["POST"])
@require_auth(["lecturer"])
def post_mark_att(code):
    code = code.replace("-", " ").upper()
    body     = request.get_json(force=True)
    records  = body.get("records", [])
    date_str = body.get("date") or date.today().strftime("%Y-%m-%d")

    for rec in records:
        matric = rec.get("id")
        status = rec.get("status", "absent")

        existing = AttendanceRecord.query.filter_by(
            matric=matric, course_code=code, date=date_str).first()

        if existing:
            old_status = existing.status
            existing.status = status
            row = Attendance.query.filter_by(matric=matric, course_code=code).first()
            if row:
                if old_status == "present" and status == "absent":
                    row.attended = max(0, row.attended - 1)
                elif old_status == "absent" and status == "present":
                    row.attended += 1
        else:
            db.session.add(AttendanceRecord(
                matric=matric, course_code=code,
                date=date_str, status=status
            ))
            row = Attendance.query.filter_by(matric=matric, course_code=code).first()
            if row:
                row.total += 1
                if status == "present":
                    row.attended += 1

    db.session.commit()
    return ok({"message": f"Attendance saved for {code}.", "saved": len(records)})


@bp.route("/att-reports/<code>", methods=["GET"])
@require_auth(["lecturer"])
def att_reports(code):
    code = code.replace("-", " ").upper()
    course  = Course.query.get(code)
    records = Attendance.query.filter_by(course_code=code).all()

    # Count distinct class dates
    total_classes = db.session.query(AttendanceRecord.date).filter_by(
        course_code=code).distinct().count()

    students = []
    for r in records:
        s = Student.query.get(r.matric)
        absent = r.total - r.attended
        students.append({
            "id":       r.matric,
            "name":     s.name if s else r.matric,
            "attended": r.attended,
            "absent":   absent,
            "rate":     r.rate,
            "risk":     r.rate < 70,
        })

    avg = round(sum(r["rate"] for r in students) / len(students), 1) if students else 0
    at_risk = sum(1 for r in students if r["risk"])
    perfect = sum(1 for r in students if r["rate"] == 100)
    return ok({
        "course_name":   f"{code} — {course.name}" if course else code,
        "total_classes": total_classes,
        "avg_rate":      avg,
        "at_risk":       at_risk,
        "perfect":       perfect,
        "students":      students,
    })


@bp.route("/grades", methods=["GET"])
@require_auth(["lecturer"])
def get_grades_default():
    u = current_user()
    courses = _my_courses(u.staff_id)
    if not courses:
        return ok({"course_name": "No courses assigned", "students": []})
    course = courses[0]
    grades = Grade.query.filter_by(course_code=course.code).all()
    return ok({
        "course_name": f"{course.code} — {course.name}",
        "students": [g.to_dict() for g in grades],
    })

@bp.route("/grades/<code>", methods=["GET"])
@require_auth(["lecturer"])
def get_grades(code):
    code = code.replace("-", " ").upper()
    grades = Grade.query.filter_by(course_code=code).all()
    result = []
    for g in grades:
        s = Student.query.get(g.matric)
        result.append({
            "id":    g.matric,
            "name":  s.name if s else g.matric,
            "ca":    g.ca,
            "exam":  g.exam,
            "total": g.total if g.exam is not None else None,
            "grade": g.letter if g.exam is not None else None,
        })
    return ok({"course": code, "students": result})


@bp.route("/grades/<code>", methods=["POST"])
@require_auth(["lecturer"])
def post_grades(code):
    code    = code.replace("-", " ").upper()
    body    = request.get_json(force=True)
    updates = body.get("updates", [])
    action  = body.get("action", "save")
    for upd in updates:
        g = Grade.query.filter_by(matric=upd.get("id"), course_code=code).first()
        if g:
            if "ca"   in upd: g.ca   = upd["ca"]
            if "exam" in upd: g.exam = upd["exam"]
    db.session.commit()
    return ok({"message": f"Grades {'submitted' if action == 'submit' else 'saved'} for {code}."})


@bp.route("/materials/<code>", methods=["GET"])
@require_auth(["lecturer"])
def get_materials(code):
    code = code.replace("-", " ").upper()
    materials = Material.query.filter_by(course_code=code).order_by(Material.id.desc()).all()
    return ok({"materials": [m.to_dict() for m in materials]})

@bp.route("/materials/<code>", methods=["POST"])
@require_auth(["lecturer"])
def add_material(code):
    import base64
    code = code.replace("-", " ").upper()
    body = request.get_json(force=True)
    title = (body.get("title") or "").strip()
    if not title:
        return err("Title is required.")

    mat_type = body.get("type", "note")
    filedata = None
    filename = None
    filetype = None
    filesize = None

    if mat_type == "file" and body.get("filedata"):
        try:
            raw = base64.b64decode(body["filedata"])
            filedata = raw
            filename = body.get("filename", "file")
            filetype = body.get("filetype", "application/octet-stream")
            filesize = len(raw)
            # Limit to 10MB
            if filesize > 10 * 1024 * 1024:
                return err("File too large. Maximum size is 10MB.")
        except Exception as e:
            return err(f"Invalid file data: {str(e)}")

    m = Material(
        course_code = code,
        title       = title,
        description = body.get("description", ""),
        type        = mat_type,
        url         = body.get("url", ""),
        filename    = filename,
        filedata    = filedata,
        filetype    = filetype,
        filesize    = filesize,
        uploaded_by = current_user().staff_id,
    )
    db.session.add(m)
    db.session.commit()
    return ok(m.to_dict()), 201

@bp.route("/materials/download/<int:material_id>", methods=["GET"])
@require_auth(["lecturer", "student"])
def download_material(material_id):
    from flask import send_file
    import io
    m = Material.query.get(material_id)
    if not m or not m.filedata:
        return err("File not found.", 404)
    return send_file(
        io.BytesIO(m.filedata),
        mimetype=m.filetype or "application/octet-stream",
        as_attachment=True,
        download_name=m.filename or "download"
    )

@bp.route("/materials/delete/<int:material_id>", methods=["DELETE"])
@require_auth(["lecturer"])
def delete_material(material_id):
    m = Material.query.get(material_id)
    if not m:
        return err("Material not found.", 404)
    db.session.delete(m)
    db.session.commit()
    return ok({"message": "Deleted."})

@bp.route("/notifications", methods=["GET"])
@require_auth(["lecturer"])
def notifications():
    return ok(NotificationModel.get_for_role("lecturer"))


@bp.route("/notifications/read-all", methods=["POST"])
@require_auth(["lecturer"])
def mark_all_read():
    NotificationModel.mark_all_read("lecturer")
    return ok({"message": "All marked as read."})
