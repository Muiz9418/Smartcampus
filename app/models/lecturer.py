from extensions import db

class Lecturer(db.Model):
    __tablename__ = "lecturers"
    id      = db.Column(db.String(20), primary_key=True)
    name    = db.Column(db.String(100))
    dept    = db.Column(db.String(100))
    email   = db.Column(db.String(120))
    status  = db.Column(db.String(20), default="active")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class LecturerModel:
    @staticmethod
    def get_dashboard_stats(staff_id):
        from app.models.course import Course
        courses = Course.query.filter_by(lecturer_id=staff_id).all()
        total_students = sum(c.students for c in courses)
        return {
            "stats": {
                "total_courses": len(courses),
                "total_students": total_students,
                "classes_today": 0,
            },
            "today": [],
            "courses": [{"code": c.code, "name": c.name,
                         "students": c.students, "avg_attendance": "N/A"} for c in courses],
        }

    @staticmethod
    def get_schedule(staff_id):
        from app.models.course import Course
        courses = Course.query.filter_by(lecturer_id=staff_id).all()
        return {"courses": [c.to_dict() for c in courses], "today": []}

    @staticmethod
    def get_mark_att_session(code):
        from app.models.student import Student
        from app.models.attendance import Attendance
        students = Student.query.all()
        return {"course": code, "students": [
            {"id": s.matric, "name": s.name, "status": None} for s in students
        ]}

    @staticmethod
    def save_attendance(code, records):
        from app.models.attendance import Attendance
        for rec in records:
            row = Attendance.query.filter_by(
                matric=rec.get("id"), course_code=code).first()
            if row and rec.get("status") == "present":
                row.attended += 1
                row.total += 1
            elif row:
                row.total += 1
        db.session.commit()
        return len(records)

    @staticmethod
    def get_att_report(code):
        from app.models.attendance import Attendance
        from app.models.student import Student
        records = Attendance.query.filter_by(course_code=code).all()
        if not records:
            return None
        students = []
        for r in records:
            s = Student.query.get(r.matric)
            absent = r.total - r.attended
            students.append({
                "id": r.matric, "name": s.name if s else r.matric,
                "attended": r.attended, "absent": absent,
                "rate": r.rate, "risk": r.rate < 70,
            })
        return {"total_classes": records[0].total if records else 0, "students": students}

    @staticmethod
    def get_grade_upload(code):
        from app.models.grade import Grade
        from app.models.student import Student
        grades = Grade.query.filter_by(course_code=code).all()
        result = []
        for g in grades:
            s = Student.query.get(g.matric)
            result.append({
                "id": g.matric, "name": s.name if s else g.matric,
                "ca": g.ca, "exam": g.exam,
                "total": g.total if g.exam is not None else None,
                "grade": g.letter if g.exam is not None else None,
            })
        return {"course": code, "students": result}

    @staticmethod
    def save_grades(code, updates, action):
        from app.models.grade import Grade
        for upd in updates:
            g = Grade.query.filter_by(matric=upd.get("id"), course_code=code).first()
            if g:
                if "ca" in upd: g.ca = upd["ca"]
                if "exam" in upd: g.exam = upd["exam"]
        db.session.commit()
        return f"Grades {'submitted' if action == 'submit' else 'saved'} for {code}."

    @staticmethod
    def list_all(q=""):
        query = Lecturer.query
        if q:
            q = f"%{q}%"
            query = query.filter(
                db.or_(Lecturer.name.ilike(q), Lecturer.dept.ilike(q))
            )
        return [l.to_dict() for l in query.all()]

    @staticmethod
    def create(data):
        if not data.get("name") or not data.get("email"):
            return None, "Missing required fields."
        import uuid
        new_id = "STF-" + str(uuid.uuid4())[:4].upper()
        l = Lecturer(id=new_id, name=data["name"], dept=data.get("dept",""),
                     email=data["email"], status=data.get("status","active"))
        db.session.add(l)
        db.session.commit()
        return l.to_dict(), None

    @staticmethod
    def update(staff_id, data):
        l = Lecturer.query.get(staff_id)
        if not l: return None, "Lecturer not found."
        for f in ["name","dept","email","status"]:
            if f in data: setattr(l, f, data[f])
        db.session.commit()
        return l.to_dict(), None

    @staticmethod
    def delete(staff_id):
        l = Lecturer.query.get(staff_id)
        if not l: return False
        db.session.delete(l)
        db.session.commit()
        return True
