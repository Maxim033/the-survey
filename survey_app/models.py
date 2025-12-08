# survey_app/models.py
from datetime import datetime
import re
import html
from . import db


def sanitize_input(text, max_length=None):
    """Очистка и проверка ввода от опасного контента"""
    if not text:
        return text

    # Экранируем HTML символы
    text = html.escape(text)

    # Удаляем опасные конструкции
    dangerous_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'<script',
        r'</script>',
        r'on\w+\s*=',
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Ограничение длины
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text.strip()


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)

    questions = db.relationship("Question", backref="survey", lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        # Санитизируем входные данные
        if 'title' in kwargs:
            kwargs['title'] = sanitize_input(kwargs['title'], 200)
        if 'description' in kwargs:
            kwargs['description'] = sanitize_input(kwargs['description'], 5000)
        super().__init__(**kwargs)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    q_type = db.Column(db.String(20), nullable=False)  # "single" | "multiple"
    survey_id = db.Column(db.Integer, db.ForeignKey("survey.id"), nullable=False)
    is_required = db.Column(db.Boolean, default=True)

    choices = db.relationship("Choice", backref="question", lazy=True, cascade="all, delete-orphan")
    responses = db.relationship("Response", backref="question", lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        # Санитизируем входные данные
        if 'text' in kwargs:
            kwargs['text'] = sanitize_input(kwargs['text'], 500)
        # Проверяем тип вопроса
        if 'q_type' in kwargs and kwargs['q_type'] not in ['single', 'multiple']:
            kwargs['q_type'] = 'single'
        super().__init__(**kwargs)


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)

    responses = db.relationship("Response", backref="choice", lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        # Санитизируем входные данные
        if 'text' in kwargs:
            kwargs['text'] = sanitize_input(kwargs['text'], 200)
        super().__init__(**kwargs)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    def __init__(self, **kwargs):
        # Валидация данных
        if 'choice_id' in kwargs and kwargs['choice_id']:
            try:
                kwargs['choice_id'] = int(kwargs['choice_id'])
            except (ValueError, TypeError):
                raise ValueError("Неверный ID варианта ответа")

        super().__init__(**kwargs)