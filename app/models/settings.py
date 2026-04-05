from extensions import db

class Settings(db.Model):
    __tablename__ = "settings"
    key   = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(200))
