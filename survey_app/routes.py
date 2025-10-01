from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from .models import Survey, Question, Choice, Response

bp = Blueprint("main", __name__)

# Главная
@bp.route("/")
def index():
    surveys = Survey.query.all()
    return render_template("index.html", surveys=surveys)


# Новый опрос
@bp.route("/survey/new", methods=["GET", "POST"])
def new_survey():
    if request.method == "POST":
        survey = Survey(
            title=request.form["title"],
            description=request.form.get("description")
        )
        db.session.add(survey)
        db.session.commit()
        return redirect(url_for("main.manage_survey", survey_id=survey.id))
    return render_template("survey_new.html")

# Управление опросом (добавление вопросов)
@bp.route("/survey/<int:survey_id>/manage", methods=["GET", "POST"])
def manage_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if survey.is_active:  # нельзя редактировать завершённый опрос
        return redirect(url_for("main.index"))

    if request.method == "POST":
        q_text = request.form["question_text"]
        q_type = request.form["q_type"]
        question = Question(text=q_text, q_type=q_type, survey_id=survey.id)
        db.session.add(question)
        db.session.commit()

        # варианты ответа
        choices = request.form.getlist("choice_text")
        for ch in choices:
            if ch.strip():
                db.session.add(Choice(text=ch.strip(), question_id=question.id))
        db.session.commit()
        return redirect(url_for("main.manage_survey", survey_id=survey.id))

    return render_template("survey_manage.html", survey=survey)

# Завершение опроса
@bp.route("/survey/<int:survey_id>/finish", methods=["POST"])
def finish_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    survey.is_active = True
    db.session.commit()
    return redirect(url_for("main.index"))


# Удаление опроса
@bp.route("/survey/<int:survey_id>/delete", methods=["POST"])
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    return redirect(url_for("main.index"))

@bp.route("/survey/<int:survey_id>/take", methods=["GET", "POST"])
def take_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if not survey.is_active:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        for q in survey.questions:
            answers = request.form.getlist(str(q.id))
            for choice_id in answers:
                resp = Response(question_id=q.id, choice_id=int(choice_id))
                db.session.add(resp)
        db.session.commit()
        return render_template("survey_thanks.html", survey=survey)

    return render_template("survey_take.html", survey=survey)



# Просмотр результатов
@bp.route("/survey/<int:survey_id>/results")
def results(survey_id):
    survey = Survey.query.get_or_404(survey_id)

    # Считаем количество голосов по вариантам
    stats = {}
    for q in survey.questions:
        q_stats = {}
        for c in q.choices:
            count = Response.query.filter_by(choice_id=c.id).count()
            q_stats[c.text] = count
        stats[q.text] = q_stats

    return render_template("survey_results.html", survey=survey, stats=stats)
