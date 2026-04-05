import os
from flask import send_from_directory
from app import create_app

app = create_app()

FRONTEND = os.path.join(os.path.dirname(__file__), "frontend")

@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND, filename)

if __name__ == "__main__":
    print("=" * 60)
    print("  SmartCampus — http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
