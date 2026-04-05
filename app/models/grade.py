from extensions import db

class Grade(db.Model):
    __tablename__ = "grades"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matric      = db.Column(db.String(20), db.ForeignKey("students.matric"))
    course_code = db.Column(db.String(20), db.ForeignKey("courses.code"))
    course_name = db.Column(db.String(100))
    ca          = db.Column(db.Integer, default=0)
    exam        = db.Column(db.Integer, nullable=True)
    units       = db.Column(db.Integer, default=3)

    @property
    def total(self):
        return (self.ca or 0) + (self.exam or 0)

    @property
    def letter(self):
        t = self.total
        if t >= 70: return "A"
        if t >= 60: return "B"
        if t >= 50: return "C"
        if t >= 45: return "D"
        return "F"

    @property
    def points(self):
        return {"A":5,"B":4,"C":3,"D":2,"F":0}.get(self.letter, 0)

    def to_dict(self):
        return {"code": self.course_code, "name": self.course_name,
                "ca": self.ca, "exam": self.exam, "total": self.total,
                "grade": self.letter, "units": self.units}
