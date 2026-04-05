from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = "notifications"
    id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role   = db.Column(db.String(20))
    icon   = db.Column(db.String(10))
    title  = db.Column(db.String(200))
    desc   = db.Column(db.Text)
    time   = db.Column(db.String(50))
    tag    = db.Column(db.String(50))
    unread = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class NotificationModel:
    @staticmethod
    def get_for_role(role):
        notes = Notification.query.filter_by(role=role).all()
        return {
            "notifications": [n.to_dict() for n in notes],
            "unread_count": sum(1 for n in notes if n.unread),
        }

    @staticmethod
    def mark_all_read(role):
        Notification.query.filter_by(role=role).update({"unread": False})
        db.session.commit()

class BroadcastModel:
    @staticmethod
    def list_all():
        from app.models.broadcast import Broadcast
        return [b.to_dict() for b in Broadcast.query.order_by(Broadcast.sent_at.desc()).all()]

    @staticmethod
    def send(title, body, audience, tag="Admin"):
        from app.models.broadcast import Broadcast
        if not title or not body:
            return None, "Title and body are required."
        import uuid
        b = Broadcast(
            id=str(uuid.uuid4())[:8], title=title, body=body,
            audience=audience, tag=tag,
            sent_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        db.session.add(b)
        role_map = {
            "Everyone": ["student","lecturer","admin"],
            "All Students": ["student"],
            "All Lecturers": ["lecturer"],
            "Admin": ["admin"],
        }
        for role in role_map.get(audience, ["student","lecturer","admin"]):
            db.session.add(Notification(
                role=role, icon="📣", title=title,
                desc=body, time="Just now", tag=tag, unread=True
            ))
        db.session.commit()
        return b.to_dict(), None
