from flask import Flask
from extensions import db, add_cors_headers, err
import os

def create_app():
    app = Flask(__name__, static_folder="../frontend")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smartcampus-dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smartcampus.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes.auth            import bp as auth_bp
    from app.routes.admin           import bp as admin_bp
    from app.routes.student_routes  import bp as student_bp
    from app.routes.lecturer_routes import bp as lecturer_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(lecturer_bp)

    app.after_request(add_cors_headers)

    @app.route("/api/<path:path>", methods=["OPTIONS"])
    def options_handler(path):
        from extensions import ok
        return ok()

    @app.errorhandler(404)
    def not_found(e):
        return err("Not found.", 404)

    @app.errorhandler(500)
    def server_error(e):
        return err("Internal server error.", 500)

    with app.app_context():
        db.create_all()

    return app
