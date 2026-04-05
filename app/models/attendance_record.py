from extensions import db
from datetime import date

class AttendanceRecord(db.Model):
    """One row per student per class session."""
    __tablename__ = "attendance_records"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matric      = db.Column(db.String(20), db.ForeignKey("students.matric"))
    course_code = db.Column(db.String(20), db.ForeignKey("courses.code"))
    date        = db.Column(db.String(20))   # YYYY-MM-DD
    status      = db.Column(db.String(10))   # present | absent

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
