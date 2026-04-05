from extensions import db
from datetime import datetime

class Enrolment(db.Model):
    __tablename__ = "enrolments"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matric      = db.Column(db.String(20), db.ForeignKey("students.matric"), nullable=False)
    course_code = db.Column(db.String(20), db.ForeignKey("courses.code"),   nullable=False)
    enrolled_at = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d"))

    __table_args__ = (db.UniqueConstraint("matric", "course_code", name="uq_enrolment"),)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
