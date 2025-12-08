# survey_app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, make_response
import time
from . import db
from .models import Survey, Question, Choice, Response

bp = Blueprint("main", __name__)


# Главная страница
@bp.route("/")
def index():
    surveys = Survey.query.order_by(Survey.created_at.desc()).all()
    return render_template("index.html", surveys=surveys)


# Создание нового опроса
@bp.route("/survey/new", methods=["GET", "POST"])
def new_survey():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Название опроса обязательно", "danger")
            return render_template("survey_new.html")

        if len(title) > 200:
            flash("Название слишком длинное (максимум 200 символов)", "danger")
            return render_template("survey_new.html")

        if len(description) > 5000:
            flash("Описание слишком длинное (максимум 5000 символов)", "danger")
            return render_template("survey_new.html")

        try:
            survey = Survey(title=title, description=description)
            db.session.add(survey)
            db.session.commit()

            flash("Опрос успешно создан", "success")
            return redirect(url_for("main.manage_survey", survey_id=survey.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при создании опроса: {str(e)}", "danger")
            return render_template("survey_new.html")

    return render_template("survey_new.html")


# Управление опросом
@bp.route("/survey/<int:survey_id>/manage", methods=["GET", "POST"])
def manage_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    if survey.is_active:
        flash("Нельзя редактировать активный опрос", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        question_text = request.form.get("question_text", "").strip()
        q_type = request.form.get("q_type", "single")

        if not question_text:
            flash("Текст вопроса обязателен", "danger")
            return redirect(url_for("main.manage_survey", survey_id=survey_id))

        if len(question_text) > 500:
            flash("Текст вопроса слишком длинный (максимум 500 символов)", "danger")
            return redirect(url_for("main.manage_survey", survey_id=survey_id))

        if q_type not in ['single', 'multiple']:
            q_type = 'single'

        # Валидация вариантов ответа
        choices = request.form.getlist("choice_text")
        valid_choices = []

        for i, ch in enumerate(choices):
            ch_clean = ch.strip()
            if ch_clean:
                if len(ch_clean) > 200:
                    flash(f"Вариант {i + 1} слишком длинный (максимум 200 символов)", "danger")
                    return redirect(url_for("main.manage_survey", survey_id=survey_id))
                valid_choices.append(ch_clean)

        if len(valid_choices) < 2:
            flash("Добавьте хотя бы два варианта ответа", "danger")
            return redirect(url_for("main.manage_survey", survey_id=survey_id))

        if len(valid_choices) > 10:
            flash("Максимальное количество вариантов - 10", "danger")
            return redirect(url_for("main.manage_survey", survey_id=survey_id))

        try:
            # Создаем вопрос
            question = Question(
                text=question_text,
                q_type=q_type,
                survey_id=survey.id
            )
            db.session.add(question)
            db.session.flush()

            # Создаем варианты ответа
            for ch_text in valid_choices:
                choice = Choice(
                    text=ch_text,
                    question_id=question.id
                )
                db.session.add(choice)

            db.session.commit()
            flash("Вопрос успешно добавлен", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при добавлении вопроса: {str(e)}", "danger")

        return redirect(url_for("main.manage_survey", survey_id=survey_id))

    return render_template("survey_manage.html", survey=survey)


# Добавление варианта ответа
@bp.route("/question/<int:question_id>/add_choice")
def add_choice(question_id):
    question = Question.query.get_or_404(question_id)

    if question.survey.is_active:
        flash("Нельзя изменять активный опрос", "danger")
        return redirect(url_for("main.index"))

    if len(question.choices) >= 10:
        flash("Максимальное количество вариантов - 10", "warning")
        return redirect(url_for("main.manage_survey", survey_id=question.survey_id))

    try:
        choice = Choice(
            text="Новый вариант",
            question_id=question.id
        )
        db.session.add(choice)
        db.session.commit()
        flash("Вариант добавлен", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при добавлении варианта: {str(e)}", "danger")

    return redirect(url_for("main.manage_survey", survey_id=question.survey_id))


# Удаление варианта
@bp.route("/choice/<int:choice_id>/delete/<int:survey_id>")
def delete_choice(choice_id, survey_id):
    choice = Choice.query.get_or_404(choice_id)

    if choice.question.survey.is_active:
        flash("Нельзя изменять активный опрос", "danger")
        return redirect(url_for("main.index"))

    if len(choice.question.choices) <= 2:
        flash("Вопрос должен содержать минимум 2 варианта", "danger")
        return redirect(url_for("main.manage_survey", survey_id=survey_id))

    try:
        db.session.delete(choice)
        db.session.commit()
        flash("Вариант удален", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении варианта: {str(e)}", "danger")

    return redirect(url_for("main.manage_survey", survey_id=survey_id))


# Удаление вопроса
@bp.route("/question/<int:question_id>/delete/<int:survey_id>")
def delete_question(question_id, survey_id):
    question = Question.query.get_or_404(question_id)

    if question.survey.is_active:
        flash("Нельзя изменять активный опрос", "danger")
        return redirect(url_for("main.index"))

    try:
        db.session.delete(question)
        db.session.commit()
        flash("Вопрос удален", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении вопроса: {str(e)}", "danger")

    return redirect(url_for("main.manage_survey", survey_id=survey_id))


# Завершение опроса
@bp.route("/survey/<int:survey_id>/finish", methods=["POST"])
def finish_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    if not survey.questions:
        flash("Добавьте хотя бы один вопрос", "danger")
        return redirect(url_for("main.manage_survey", survey_id=survey_id))

    # Проверяем вопросы
    for q in survey.questions:
        if len(q.choices) < 2:
            flash(f"У вопроса '{q.text[:50]}...' должно быть минимум 2 варианта", "danger")
            return redirect(url_for("main.manage_survey", survey_id=survey_id))

    try:
        survey.is_active = True
        db.session.commit()
        flash("Опрос опубликован", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при публикации опроса: {str(e)}", "danger")

    return redirect(url_for("main.index"))


# Удаление опроса
@bp.route("/survey/<int:survey_id>/delete", methods=["POST"])
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    try:
        db.session.delete(survey)
        db.session.commit()
        flash("Опрос удален", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении опроса: {str(e)}", "danger")

    return redirect(url_for("main.index"))


# Прохождение опроса
@bp.route("/survey/<int:survey_id>/take", methods=["GET", "POST"])
def take_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    if not survey.is_active:
        flash("Опрос недоступен для прохождения", "danger")
        return redirect(url_for("main.index"))

    # Проверка куки, чтобы предотвратить повторное прохождение
    survey_cookie = f"survey_{survey_id}_completed"
    if request.cookies.get(survey_cookie):
        flash("Вы уже проходили этот опрос", "info")
        return redirect(url_for("main.results", survey_id=survey_id))

    if request.method == "POST":
        valid_responses = []
        ip_address = request.remote_addr
        user_agent = request.user_agent.string[:500] if request.user_agent.string else ""

        # Проверяем ответы на каждый вопрос
        for q in survey.questions:
            answers = request.form.getlist(str(q.id))

            if not answers:
                # Для обязательных вопросов
                if q.is_required:
                    flash(f"Пожалуйста, ответьте на вопрос: {q.text[:50]}...", "danger")
                    return redirect(url_for("main.take_survey", survey_id=survey_id))
                continue

            # Преобразуем и валидируем ID вариантов
            for choice_id in answers:
                try:
                    choice_id_int = int(choice_id)
                    # Проверяем, что вариант принадлежит вопросу
                    choice = Choice.query.filter_by(
                        id=choice_id_int,
                        question_id=q.id
                    ).first()
                    if choice:
                        resp = Response(
                            question_id=q.id,
                            choice_id=choice_id_int,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                        valid_responses.append(resp)
                except (ValueError, TypeError):
                    continue

        if not valid_responses:
            flash("Пожалуйста, ответьте хотя бы на один вопрос", "danger")
            return redirect(url_for("main.take_survey", survey_id=survey_id))

        try:
            # Сохраняем ответы
            db.session.add_all(valid_responses)
            db.session.commit()

            # Устанавливаем куку, чтобы помнить о прохождении опроса
            response = make_response(render_template("survey_thanks.html", survey=survey))
            response.set_cookie(
                survey_cookie,
                'true',
                max_age=30 * 24 * 60 * 60,  # 30 дней
                httponly=True,
                samesite='Lax'
            )

            return response

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при сохранении ответов: {str(e)}", "danger")
            return redirect(url_for("main.take_survey", survey_id=survey_id))

    return render_template("survey_take.html", survey=survey)


# Просмотр результатов
@bp.route("/survey/<int:survey_id>/results")
def results(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    # Собираем статистику
    stats = {}
    for q in survey.questions:
        q_stats = {}
        total_responses = Response.query.filter_by(question_id=q.id).count()

        for c in q.choices:
            count = Response.query.filter_by(choice_id=c.id).count()
            percentage = (count / total_responses * 100) if total_responses > 0 else 0
            q_stats[c.text] = {
                'count': count,
                'percentage': round(percentage, 1)
            }

        stats[q.id] = {
            'text': q.text,
            'type': q.q_type,
            'total': total_responses,
            'data': q_stats
        }

    return render_template("survey_results.html", survey=survey, stats=stats)


# Обработчики ошибок
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html',
                           message="Страница не найдена",
                           code=404), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html',
                           message="Внутренняя ошибка сервера",
                           code=500), 500