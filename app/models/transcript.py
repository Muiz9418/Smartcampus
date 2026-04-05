from extensions import db

class TranscriptSemester(db.Model):
    __tablename__ = "transcript_semesters"
    id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matric = db.Column(db.String(20), db.ForeignKey("students.matric"))
    label  = db.Column(db.String(50))
    gpa    = db.Column(db.Float)
    units  = db.Column(db.Integer)

class TranscriptCourse(db.Model):
    __tablename__ = "transcript_courses"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    semester_id = db.Column(db.Integer, db.ForeignKey("transcript_semesters.id"))
    code        = db.Column(db.String(20))
    name        = db.Column(db.String(100))
    grade       = db.Column(db.String(5))
    units       = db.Column(db.Integer)
