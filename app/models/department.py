from extensions import db

class Department(db.Model):
    __tablename__ = "departments"
    name           = db.Column(db.String(100), primary_key=True)
    students       = db.Column(db.Integer, default=0)
    lecturers      = db.Column(db.Integer, default=0)
    courses        = db.Column(db.Integer, default=0)
    avg_attendance = db.Column(db.Integer, default=0)
    at_risk        = db.Column(db.Integer, default=0)
    avg_gpa        = db.Column(db.Float, default=0.0)
    pass_rate      = db.Column(db.Integer, default=0)
    trend          = db.Column(db.String(10), default="flat")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
