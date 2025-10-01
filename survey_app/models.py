from datetime import datetime
from . import db

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)  # 🔹 активный или завершён

    questions = db.relationship("Question", backref="survey", lazy=True, cascade="all, delete")



class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    q_type = db.Column(db.String(20), nullable=False)  # "single" | "multiple"
    survey_id = db.Column(db.Integer, db.ForeignKey("survey.id"), nullable=False)

    choices = db.relationship("Choice", backref="question", lazy=True, cascade="all, delete")


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
