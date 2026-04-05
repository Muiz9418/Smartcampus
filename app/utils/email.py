import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env'))

# Try loading from multiple locations
for env_path in [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env'),
    os.path.join(os.getcwd(), '.env'),
    '/Users/mac/Documents/my project/.env',
]:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        break

MAIL_EMAIL    = os.environ.get("MAIL_EMAIL")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

def send_email(to, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"]    = f"SmartCampus <{MAIL_EMAIL}>"
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_EMAIL, MAIL_PASSWORD)
        server.sendmail(MAIL_EMAIL, to, msg.as_bytes())
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)

def send_broadcast_emails(audience, title, body_text):
    from app.models.user import User
    role_map = {
        "Everyone":     None,
        "All Students": "student",
        "All Lecturers":"lecturer",
        "Admin":        "admin",
    }
    role_filter = role_map.get(audience)
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.all()
    sent, failed = 0, 0
    for u in users:
        if not u.email:
            continue
        ok, err = send_email(
            to=u.email,
            subject=f"[SmartCampus] {title}",
            body=f"Dear {u.name},\n\n{body_text}\n\n- SmartCampus Team"
        )
        if ok: sent += 1
        else:
            failed += 1
            print(f"Failed to send to {u.email}: {err}")
    return sent, failed
