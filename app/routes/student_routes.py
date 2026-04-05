from flask import Blueprint
from extensions import ok, err, require_auth, current_user
from app.models.student import StudentModel
from app.models.notification import NotificationModel
from app.models.enrolment import Enrolment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.course import Course

bp = Blueprint("student", __name__, url_prefix="/api/student")

def get_settings():
    from app.models.settings import Settings
    return {s.key: s.value for s in Settings.query.all()}

@bp.route("/dashboard", methods=["GET"])
@require_auth(["student"])
def dashboard():
    from datetime import date
    u = current_user()
    s = get_settings()
    data = StudentModel.get_dashboard_stats(u.matric)
    notifs = NotificationModel.get_for_role("student")
    day_map = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
    today_day = day_map[date.today().weekday()]
    today_schedule = [e for e in data.get("schedule",[]) if e.get("day") == today_day]
    return ok({
        "user":                 u.to_dict(),
        "stats":                data["stats"],
        "today_schedule":       today_schedule,
        "semester":             s.get("current_semester", ""),
        "academic_year":        s.get("academic_year", s.get("institution_name", "")),
        "week":                 s.get("current_week", ""),
        "recent_notifications": [n for n in notifs["notifications"] if n["unread"]][:3],
    })


@bp.route("/attendance", methods=["GET"])
@require_auth(["student"])
def attendance():
    u = current_user()
    data = StudentModel.get_attendance(u.matric)
    records = data["records"]
    total_att = sum(r.get("attended", 0) for r in records)
    total_cls = sum(r.get("total", 0) for r in records)
    at_risk   = [r for r in records if r.get("rate", 100) < 70]
    return ok({
        "semester": get_settings().get("current_semester", ""),
        "summary": {
            "overall_rate":     data["overall_rate"],
            "classes_attended": total_att,
            "total_classes":    total_cls,
            "absent":           total_cls - total_att,
            "at_risk_count":    len(at_risk),
        },
        "courses": records,
    })

@bp.route("/grades", methods=["GET"])
@require_auth(["student"])
def grades():
    u = current_user()
    data = StudentModel.get_grades(u.matric)
    grades = data["grades"]
    distinctions = sum(1 for g in grades if g.get("grade") == "A")
    return ok({
        "semester": get_settings().get("current_semester", ""),
        "summary": {
            "semester_gpa":    data["gpa"],
            "cumulative_gpa":  data["gpa"],
            "credits_earned":  data["total_units"],
            "distinctions":    distinctions,
        },
        "courses": grades,
    })

@bp.route("/transcript", methods=["GET"])
@require_auth(["student"])
def transcript():
    from app.models.grade import Grade
    from app.models.course import Course
    from app.models.transcript import TranscriptSemester, TranscriptCourse

    u = current_user()
    s = get_settings()

    # Get stored transcript semesters
    semesters = []
    stored = TranscriptSemester.query.filter_by(matric=u.matric).all()
    total_units, total_points = 0, 0

    for sem in stored:
        courses = TranscriptCourse.query.filter_by(semester_id=sem.id).all()
        semesters.append({
            "label": sem.label, "gpa": sem.gpa, "units": sem.units,
            "courses": [{"code": c.code, "name": c.name,
                         "grade": c.grade, "units": c.units} for c in courses]
        })
        total_units  += sem.units
        total_points += sem.gpa * sem.units

    # Add current semester from real grades if not already stored
    current_sem = s.get("current_semester", "Current Semester")
    stored_labels = [s.label for s in stored]
    if current_sem not in stored_labels:
        grades = Grade.query.filter_by(matric=u.matric).all()
        if grades:
            sem_units  = sum(g.units for g in grades if g.exam is not None)
            sem_points = sum(g.points * g.units for g in grades if g.exam is not None)
            sem_gpa    = round(sem_points / sem_units, 2) if sem_units else 0
            semesters.append({
                "label": f"{current_sem} (Current)",
                "gpa": sem_gpa,
                "units": sum(g.units for g in grades),
                "courses": [{
                    "code":  g.course_code,
                    "name":  g.course_name,
                    "grade": g.letter if g.exam is not None else "—",
                    "units": g.units,
                } for g in grades]
            })
            total_units  += sem_units
            total_points += sem_points

    cgpa = round(total_points / total_units, 2) if total_units else 0

    return ok({
        "student": {
            "name":           u.name,
            "matric":         u.matric,
            "department":     u.department or "—",
            "faculty":        u.faculty or "—",
            "level":          u.level or "—",
            "mode_of_entry":  "—",
            "admission_date": "—",
            "cumulative_gpa": cgpa,
        },
        "semesters": semesters,
    })

@bp.route("/courses", methods=["GET"])
@require_auth(["student"])
def courses():
    from app.models.enrolment import Enrolment
    u = current_user()
    data = StudentModel.get_enrolled_courses(u.matric)
    # All available courses for enrolment
    enrolled_codes = [e.course_code for e in Enrolment.query.filter_by(matric=u.matric).all()]
    all_courses = Course.query.all()
    available = [c for c in all_courses if c.code not in enrolled_codes]
    return ok({
        "courses":          data["courses"],
        "timetable_events": data["timetable"],
        "available":        [c.to_dict() for c in available],
    })

@bp.route("/course/<code>", methods=["GET"])
@require_auth(["student"])
def course_detail(code):
    normalised = code.replace("-", " ").upper()
    detail = StudentModel.get_course_detail(normalised, current_user().matric)
    if not detail:
        return err("Course not found.", 404)
    return ok(detail)

@bp.route("/materials/<code>", methods=["GET"])
@require_auth(["student"])
def get_materials(code):
    from app.models.material import Material
    code = code.replace("-", " ").upper()
    materials = Material.query.filter_by(course_code=code).order_by(Material.id.desc()).all()
    return ok({"materials": [m.to_dict() for m in materials]})

@bp.route("/materials/download/<int:material_id>", methods=["GET"])
@require_auth(["student"])
def download_material(material_id):
    from app.models.material import Material
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

@bp.route("/notifications", methods=["GET"])
@require_auth(["student"])
def notifications():
    return ok(NotificationModel.get_for_role("student"))

@bp.route("/notifications/read-all", methods=["POST"])
@require_auth(["student"])
def mark_all_read():
    NotificationModel.mark_all_read("student")
    return ok({"message": "All marked as read."})


@bp.route("/enrol/<code>", methods=["POST"])
@require_auth(["student"])
def enrol(code):
    """Enrol the current student in a course."""
    from extensions import db
    u = current_user()
    matric = u.matric
    code = code.replace("-", " ").upper()

    # Check course exists
    course = Course.query.get(code)
    if not course:
        return err("Course not found.", 404)

    # Check not already enrolled
    existing = Enrolment.query.filter_by(matric=matric, course_code=code).first()
    if existing:
        return err("You are already enrolled in this course.", 409)

    # Create enrolment
    enrolment = Enrolment(matric=matric, course_code=code)
    db.session.add(enrolment)

    # Create empty Grade record
    grade = Grade(matric=matric, course_code=code,
                  course_name=course.name, units=course.units or 3)
    db.session.add(grade)

    # Create empty Attendance record
    att = Attendance(matric=matric, course_code=code,
                     course_name=course.name, attended=0, total=0)
    db.session.add(att)

    # Update course student count
    course.students = (course.students or 0) + 1

    db.session.commit()
    return ok({"message": f"Successfully enrolled in {code}."})


@bp.route("/enrol/<code>", methods=["DELETE"])
@require_auth(["student"])
def unenrol(code):
    """Unenrol the current student from a course."""
    from extensions import db
    u = current_user()
    code = code.replace("-", " ").upper()

    enrolment = Enrolment.query.filter_by(matric=u.matric, course_code=code).first()
    if not enrolment:
        return err("You are not enrolled in this course.", 404)

    db.session.delete(enrolment)

    # Update course student count
    course = Course.query.get(code)
    if course and course.students:
        course.students = max(0, course.students - 1)

    db.session.commit()
    return ok({"message": f"Unenrolled from {code}."})
