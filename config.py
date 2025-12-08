import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'survey.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key_" + os.urandom(16).hex())
    # Отключаем CSRF
    WTF_CSRF_ENABLED = False
    # Лимиты для предотвращения DoS
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    # Настройки безопасности сессий
    SESSION_COOKIE_SECURE = False  # True в production с HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 час