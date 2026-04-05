from extensions import db
from datetime import datetime

class Material(db.Model):
    __tablename__ = "materials"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), db.ForeignKey("courses.code"))
    title       = db.Column(db.String(200))
    description = db.Column(db.Text)
    type        = db.Column(db.String(20))  # file | link | note
    url         = db.Column(db.String(500)) # for links
    filename    = db.Column(db.String(200)) # original filename
    filedata    = db.Column(db.LargeBinary) # base64 decoded file bytes
    filetype    = db.Column(db.String(50))  # MIME type
    filesize    = db.Column(db.Integer)     # bytes
    uploaded_at = db.Column(db.String(30), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    uploaded_by = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id":          self.id,
            "course_code": self.course_code,
            "title":       self.title,
            "description": self.description,
            "type":        self.type,
            "url":         self.url,
            "filename":    self.filename,
            "filetype":    self.filetype,
            "filesize":    self.filesize,
            "uploaded_at": self.uploaded_at,
            "uploaded_by": self.uploaded_by,
            # Don't send file data in list — only on download
        }
