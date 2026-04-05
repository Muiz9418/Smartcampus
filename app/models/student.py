from extensions import db
from app.models.attendance import Attendance
from app.models.grade import Grade
from app.models.timetable import TimetableEvent
from app.models.transcript import TranscriptSemester, TranscriptCourse

class Student(db.Model):
    __tablename__ = "students"
    matric  = db.Column(db.String(20), primary_key=True)
    name    = db.Column(db.String(100))
    dept    = db.Column(db.String(100))
    level   = db.Column(db.String(10))
    email   = db.Column(db.String(120))
    status  = db.Column(db.String(20), default="active")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class StudentModel:
    @staticmethod
    def get_dashboard_stats(matric):
        att = Attendance.query.filter_by(matric=matric).all()
        grades = Grade.query.filter_by(matric=matric).all()
        avg_att = round(sum(r.rate for r in att) / len(att), 1) if att else 0
        total_units = sum(g.units for g in grades)
        gpa = round(sum(g.points * g.units for g in grades) / total_units, 2) if total_units else 0
        events = TimetableEvent.query.all()
        return {
            "stats": {
                "enrolled_courses": len(att),
                "overall_attendance": f"{avg_att}%",
                "semester_gpa": gpa,
                "at_risk_courses": sum(1 for r in att if r.rate < 70),
            },
            "attendance": [r.to_dict() for r in att],
            "schedule": [e.to_dict() for e in events],
        }

    @staticmethod
    def get_attendance(matric):
        records = Attendance.query.filter_by(matric=matric).all()
        overall = round(sum(r.rate for r in records) / len(records), 1) if records else 0
        return {"records": [r.to_dict() for r in records], "overall_rate": f"{overall}%"}

    @staticmethod
    def get_grades(matric):
        grades = Grade.query.filter_by(matric=matric).all()
        total_units = sum(g.units for g in grades)
        gpa = round(sum(g.points * g.units for g in grades) / total_units, 2) if total_units else 0
        return {"grades": [g.to_dict() for g in grades], "gpa": gpa, "total_units": total_units}

    @staticmethod
    def get_transcript(user):
        matric = user.matric
        semesters = TranscriptSemester.query.filter_by(matric=matric).all()
        result = []
        cumulative_units, cumulative_points = 0, 0
        for sem in semesters:
            courses = TranscriptCourse.query.filter_by(semester_id=sem.id).all()
            result.append({
                "label": sem.label, "gpa": sem.gpa, "units": sem.units,
                "courses": [{"code": c.code, "name": c.name,
                             "grade": c.grade, "units": c.units} for c in courses]
            })
            cumulative_units += sem.units
            cumulative_points += sem.gpa * sem.units
        cgpa = round(cumulative_points / cumulative_units, 2) if cumulative_units else 0
        return {"cumulative_gpa": cgpa, "semesters": result}

    @staticmethod
    def get_enrolled_courses(matric=None):
        from app.models.course import Course
        from app.models.enrolment import Enrolment
        events = TimetableEvent.query.all()
        if matric:
            enrolments = Enrolment.query.filter_by(matric=matric).all()
            codes = [e.course_code for e in enrolments]
            courses = Course.query.filter(Course.code.in_(codes)).all()
        else:
            courses = Course.query.all()
        return {"courses": [c.to_dict() for c in courses],
                "timetable": [e.to_dict() for e in events]}

    @staticmethod
    def get_course_detail(code, matric):
        from app.models.course import Course
        from app.models.grade import Grade
        from app.models.enrolment import Enrolment
        course = Course.query.get(code)
        if not course:
            return None
        # Check enrolled
        enrolled = Enrolment.query.filter_by(matric=matric, course_code=code).first()
        if not enrolled:
            return None
        att = Attendance.query.filter_by(matric=matric, course_code=code).first()
        grade = Grade.query.filter_by(matric=matric, course_code=code).first()
        return {
            "course": course.to_dict(),
            "attendance": att.to_dict() if att else {},
            "grade": grade.to_dict() if grade else {},
            "materials": [],
        }

    @staticmethod
    def list_all(q=""):
        query = Student.query
        if q:
            q = f"%{q}%"
            query = query.filter(
                db.or_(Student.name.ilike(q), Student.matric.ilike(q), Student.dept.ilike(q))
            )
        return [s.to_dict() for s in query.all()]

    @staticmethod
    def create(data):
        for f in ["matric","name","dept","level","email"]:
            if not data.get(f):
                return None, f"Missing field: {f}"
        if Student.query.get(data["matric"]):
            return None, "Matric number already exists."
        s = Student(matric=data["matric"], name=data["name"], dept=data["dept"],
                    level=data["level"], email=data["email"],
                    status=data.get("status","active"))
        db.session.add(s)
        db.session.commit()
        return s.to_dict(), None

    @staticmethod
    def update(matric, data):
        s = Student.query.get(matric)
        if not s:
            return None, "Student not found."
        for f in ["name","dept","level","email","status"]:
            if f in data: setattr(s, f, data[f])
        db.session.commit()
        return s.to_dict(), None

    @staticmethod
    def delete(matric):
        s = Student.query.get(matric)
        if not s: return False
        db.session.delete(s)
        db.session.commit()
        return True
