from extensions import db

class TimetableEvent(db.Model):
    __tablename__ = "timetable_events"
    id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day   = db.Column(db.String(10))
    time  = db.Column(db.String(10))
    label = db.Column(db.String(20))
    color = db.Column(db.String(10))
    tc    = db.Column(db.String(10))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
