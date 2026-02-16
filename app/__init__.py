from flask import Flask

from app.config import COMMUNITY_UPLOAD_DIR, Config, DIAGNOSIS_UPLOAD_DIR, UPLOAD_DIR
from app.models import db
from app.routes.main import main_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    app.config["DIAGNOSIS_UPLOAD_DIR"] = DIAGNOSIS_UPLOAD_DIR
    app.config["COMMUNITY_UPLOAD_DIR"] = COMMUNITY_UPLOAD_DIR
    app.config["UPLOAD_FOLDER_ROOT"] = UPLOAD_DIR

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)

    @app.errorhandler(413)
    def payload_too_large(_):
        return {"error": "File too large. Maximum allowed size is 200MB."}, 413

    return app
