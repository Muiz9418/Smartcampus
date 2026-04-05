from extensions import db

class Broadcast(db.Model):
    __tablename__ = "broadcasts"
    id       = db.Column(db.String(20), primary_key=True)
    title    = db.Column(db.String(200))
    body     = db.Column(db.Text)
    audience = db.Column(db.String(50))
    tag      = db.Column(db.String(50))
    sent_at  = db.Column(db.String(30))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
