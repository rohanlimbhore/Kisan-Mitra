from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class CommunityPost(db.Model):
    __tablename__ = "community_posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    media_path = db.Column(db.String(255), nullable=True)
    media_type = db.Column(db.String(20), nullable=True)
    likes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class DiagnosisReport(db.Model):
    __tablename__ = "diagnosis_reports"

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
