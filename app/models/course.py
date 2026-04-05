from extensions import db

class Course(db.Model):
    __tablename__ = "courses"
    code        = db.Column(db.String(20), primary_key=True)
    name        = db.Column(db.String(100))
    dept        = db.Column(db.String(100))
    units       = db.Column(db.Integer)
    lecturer_id = db.Column(db.String(20), db.ForeignKey("lecturers.id"))
    students    = db.Column(db.Integer, default=0)
    status      = db.Column(db.String(20), default="active")
    venue       = db.Column(db.String(50))
    days        = db.Column(db.String(30))
    time        = db.Column(db.String(20))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class CourseModel:
    @staticmethod
    def list_all(q=""):
        query = Course.query
        if q:
            q = f"%{q}%"
            query = query.filter(
                db.or_(Course.code.ilike(q), Course.name.ilike(q), Course.dept.ilike(q))
            )
        return [c.to_dict() for c in query.all()]

    @staticmethod
    def _sync_timetable(course):
        """Create timetable events for a course based on its days field."""
        from app.models.timetable import TimetableEvent
        # Remove old events for this course
        TimetableEvent.query.filter_by(label=course.code).delete()
        if not course.days or not course.time:
            return
        # Parse start time
        start_time = course.time.split("-")[0].strip()
        # Parse days (e.g. MON/WED or Mon/Wed)
        day_map = {
            "MON":"Mon","TUE":"Tue","WED":"Wed","THU":"Thu","FRI":"Fri",
            "Mon":"Mon","Tue":"Tue","Wed":"Wed","Thu":"Thu","Fri":"Fri",
        }
        colors = ["#dbeafe","#dcf5e8","#fef3c7","#ede9fe","#fce7f3","#fee2e2"]
        tcs    = ["#1d4ed8","#15803d","#92400e","#6d28d9","#be185d","#b91c1c"]
        import hashlib
        idx = int(hashlib.md5(course.code.encode()).hexdigest(), 16) % len(colors)
        for part in course.days.replace(" ","").split("/"):
            day = day_map.get(part.strip()[:3].upper()[:1]+part.strip()[1:3].lower(),
                              part.strip()[:3])
            day = day_map.get(part.strip().upper()[:3], part.strip()[:3])
            if day:
                db.session.add(TimetableEvent(
                    day=day, time=start_time,
                    label=course.code,
                    color=colors[idx], tc=tcs[idx]
                ))

    @staticmethod
    def create(data):
        if not data.get("code") or not data.get("name"):
            return None, "Missing required fields."
        if Course.query.get(data["code"]):
            return None, "Course code already exists."
        c = Course(
            code=data["code"], name=data["name"], dept=data.get("dept",""),
            units=data.get("units",3), lecturer_id=data.get("lecturer_id"),
            students=data.get("students",0), status=data.get("status","active"),
            venue=data.get("venue",""), days=data.get("days",""), time=data.get("time","")
        )
        db.session.add(c)
        db.session.flush()
        CourseModel._sync_timetable(c)
        db.session.commit()
        return c.to_dict(), None

    @staticmethod
    def update(code, data):
        c = Course.query.get(code)
        if not c: return None, "Course not found."
        for f in ["name","dept","units","lecturer_id","students","status","venue","days","time"]:
            if f in data: setattr(c, f, data[f])
        CourseModel._sync_timetable(c)
        db.session.commit()
        return c.to_dict(), None

    @staticmethod
    def delete(code):
        c = Course.query.get(code)
        if not c: return False
        db.session.delete(c)
        db.session.commit()
        return True

    @staticmethod
    def get_timetable_slots():
        return [{"code": c.code, "name": c.name, "venue": c.venue,
                 "days": c.days, "time": c.time} for c in Course.query.all()]

    @staticmethod
    def update_timetable_slot(code, data):
        return CourseModel.update(code, {k: data[k] for k in ["venue","days","time"] if k in data})

    @staticmethod
    def get_grades_mgmt_overview():
        courses = Course.query.all()
        return {"courses": [{"code": c.code, "name": c.name, "status": c.status,
                              "submitted": c.status == "completed"} for c in courses]}
