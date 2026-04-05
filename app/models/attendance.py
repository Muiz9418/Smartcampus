from extensions import db

class Attendance(db.Model):
    __tablename__ = "attendance"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matric      = db.Column(db.String(20), db.ForeignKey("students.matric"))
    course_code = db.Column(db.String(20), db.ForeignKey("courses.code"))
    course_name = db.Column(db.String(100))
    attended    = db.Column(db.Integer, default=0)
    total       = db.Column(db.Integer, default=0)

    @property
    def rate(self):
        return round((self.attended / self.total) * 100, 1) if self.total else 0

    @property
    def status(self):
        r = self.rate
        if r >= 80: return "good"
        if r >= 70: return "ok"
        return "bad"

    def to_dict(self):
        return {"code": self.course_code, "name": self.course_name,
                "attended": self.attended, "total": self.total,
                "rate": self.rate, "status": self.status}
