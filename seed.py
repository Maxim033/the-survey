import random
from faker import Faker
from survey_app import create_app, db
from survey_app.models import Survey, Question, Choice, Response

fake = Faker("ru_RU")

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Создаем 10 опросов
    for _ in range(10):
        survey = Survey(
            title=fake.sentence(nb_words=4),
            description=fake.text(max_nb_chars=120),
            is_active=True
        )
        db.session.add(survey)
        db.session.commit()

        # Каждый опрос: 3-5 вопросов
        for _ in range(random.randint(3, 5)):
            q_type = random.choice(["single", "multiple"])
            question = Question(
                text=fake.sentence(nb_words=6),
                q_type=q_type,
                survey_id=survey.id
            )
            db.session.add(question)
            db.session.commit()

            # Каждый вопрос: 3-6 вариантов
            choices = []
            for _ in range(random.randint(3, 6)):
                choice = Choice(text=fake.word(), question_id=question.id)
                db.session.add(choice)
                db.session.commit()
                choices.append(choice)

            # Создаём ответы (100 пользователей случайно отвечают)
            for _ in range(100):
                if q_type == "single":
                    selected = [random.choice(choices)]
                else:
                    selected = random.sample(choices, random.randint(1, len(choices)))
                for ch in selected:
                    resp = Response(question_id=question.id, choice_id=ch.id)
                    db.session.add(resp)

    db.session.commit()
    print("✅ База заполнена тестовыми данными (около 1000+ записей).")
