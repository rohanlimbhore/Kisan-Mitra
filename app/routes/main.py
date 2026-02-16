from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from app.models import CommunityPost, DiagnosisReport, db
from app.services.ai_service import AIServiceError, ask_assistant, diagnose_crop_issue, explain_government_scheme

main_bp = Blueprint("main", __name__)

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
VIDEO_EXTENSIONS = {"mp4"}


def _allowed_file(filename: str, allowed: set[str]) -> bool:
    if "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in allowed


def _save_file(uploaded_file, target_dir: Path) -> str:
    filename = secure_filename(uploaded_file.filename)
    extension = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid4().hex}.{extension}"
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / unique_name
    uploaded_file.save(path)
    return f"uploads/{target_dir.name}/{unique_name}"


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/ai-assistant")
def ai_assistant_page():
    return render_template("ai_assistant.html")


@main_bp.route("/crop-diagnosis", methods=["GET", "POST"])
def crop_diagnosis_page():
    diagnosis_result = None
    error = None

    if request.method == "POST":
        image = request.files.get("image")
        if not image or image.filename == "":
            error = "Please upload an image file."
        elif not _allowed_file(image.filename, IMAGE_EXTENSIONS):
            error = "Only JPG, JPEG, and PNG files are allowed."
        else:
            image_bytes = image.read()
            image.seek(0)
            try:
                diagnosis_result = diagnose_crop_issue(image_bytes, image.filename)
                saved_path = _save_file(image, Path(current_app.config["DIAGNOSIS_UPLOAD_DIR"]))
                report = DiagnosisReport(image_path=saved_path, diagnosis=diagnosis_result)
                db.session.add(report)
                db.session.commit()
            except AIServiceError as exc:
                error = str(exc)
            except Exception:
                error = "Diagnosis failed. Please try again."

    return render_template("crop_diagnosis.html", diagnosis_result=diagnosis_result, error=error)


@main_bp.route("/community", methods=["GET", "POST"])
def community_page():
    error = None
    if request.method == "POST":
        content = (request.form.get("content") or "").strip()
        media = request.files.get("media")
        media_path = None
        media_type = None

        if not content:
            error = "Post text is required."
        elif media and media.filename:
            lower_name = media.filename.lower()
            if _allowed_file(lower_name, IMAGE_EXTENSIONS):
                media_type = "image"
            elif _allowed_file(lower_name, VIDEO_EXTENSIONS):
                media_type = "video"
            else:
                error = "Only JPG, JPEG, PNG, and MP4 files are allowed."

            if not error:
                media_path = _save_file(media, Path(current_app.config["COMMUNITY_UPLOAD_DIR"]))

        if not error:
            post = CommunityPost(content=content, media_path=media_path, media_type=media_type)
            db.session.add(post)
            db.session.commit()

    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return render_template("community.html", posts=posts, error=error)


@main_bp.route("/govt-schemes")
def govt_schemes_page():
    return render_template("govt_schemes.html")


@main_bp.post("/api/chat")
def api_chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Message is required."}), 400
    try:
        reply = ask_assistant(message)
        return jsonify({"reply": reply})
    except AIServiceError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Unable to process your request."}), 500


@main_bp.post("/api/schemes")
def api_schemes():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Search query is required."}), 400
    try:
        result = explain_government_scheme(query)
        return jsonify({"result": result})
    except AIServiceError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception:
        return jsonify({"error": "Unable to fetch scheme information."}), 500


@main_bp.post("/api/community/<int:post_id>/like")
def like_post(post_id: int):
    post = CommunityPost.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({"likes": post.likes})


@main_bp.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
    return send_from_directory(current_app.config["UPLOAD_FOLDER_ROOT"], filename)
