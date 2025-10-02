import random
from faker import Faker
from survey_app import create_app, db
from survey_app.models import Survey, Question, Choice, Response

fake = Faker("ru_RU")

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Создаем 1000 опросов
    surveys = []
    for i in range(1000):
        survey = Survey(
            title=f"{fake.sentence(nb_words=4)} #{i + 1}",
            description=fake.text(max_nb_chars=120),
            is_active=True
        )
        surveys.append(survey)

    db.session.add_all(surveys)
    db.session.commit()

    # Создаем вопросы для всех опросов
    all_questions = []
    for survey in surveys:
        for _ in range(random.randint(3, 5)):
            question = Question(
                text=fake.sentence(nb_words=6),
                q_type=random.choice(["single", "multiple"]),
                survey_id=survey.id
            )
            all_questions.append(question)

    db.session.add_all(all_questions)
    db.session.commit()

    # Создаем варианты ответов для всех вопросов
    all_choices = []
    for question in all_questions:
        for _ in range(random.randint(3, 6)):
            choice = Choice(text=fake.word(), question_id=question.id)
            all_choices.append(choice)

    db.session.add_all(all_choices)
    db.session.commit()

    # Создаем ответы для всех вопросов
    all_responses = []
    for question in all_questions:
        # Получаем варианты для этого вопроса
        question_choices = [c for c in all_choices if c.question_id == question.id]

        for _ in range(100):  # 100 ответов на вопрос
            if question.q_type == "single":
                selected = [random.choice(question_choices)]
            else:
                selected = random.sample(
                    question_choices,
                    random.randint(1, len(question_choices))
                )

            for ch in selected:
                resp = Response(question_id=question.id, choice_id=ch.id)
                all_responses.append(resp)

    db.session.add_all(all_responses)
    db.session.commit()

    print(f"✅ База заполнена: {len(surveys)} опросов, {len(all_questions)} вопросов, "
          f"{len(all_choices)} вариантов, {len(all_responses)} ответов")