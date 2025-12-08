# reset_database.py
from survey_app import create_app, db
from survey_app.models import Survey, Question, Choice

app = create_app()

with app.app_context():
    print("Удаляем старую базу данных...")

    # Удаляем все таблицы
    db.drop_all()

    # Создаем новые таблицы
    db.create_all()

    print("Создаем тестовые данные...")

    # Создаем тестовый опрос
    survey1 = Survey(
        title="Оценка качества обслуживания",
        description="Пожалуйста, оцените качество нашего обслуживания",
        is_active=True
    )

    survey2 = Survey(
        title="Предпочтения в еде",
        description="Опрос о пищевых предпочтениях",
        is_active=True
    )

    db.session.add(survey1)
    db.session.add(survey2)
    db.session.commit()

    # Вопросы для первого опроса
    q1 = Question(
        text="Как вы оцениваете качество обслуживания?",
        q_type="single",
        survey_id=survey1.id
    )

    q2 = Question(
        text="Что вам понравилось больше всего?",
        q_type="multiple",
        survey_id=survey1.id
    )

    db.session.add(q1)
    db.session.add(q2)
    db.session.commit()

    # Варианты для первого вопроса
    choices1 = ["Отлично", "Хорошо", "Удовлетворительно", "Плохо"]
    for text in choices1:
        choice = Choice(text=text, question_id=q1.id)
        db.session.add(choice)

    # Варианты для второго вопроса
    choices2 = ["Вежливость персонала", "Скорость обслуживания", "Качество продукции", "Чистота помещения"]
    for text in choices2:
        choice = Choice(text=text, question_id=q2.id)
        db.session.add(choice)

    # Вопросы для второго опроса
    q3 = Question(
        text="Какую кухню вы предпочитаете?",
        q_type="single",
        survey_id=survey2.id
    )

    q4 = Question(
        text="Какие продукты вы употребляете регулярно?",
        q_type="multiple",
        survey_id=survey2.id
    )

    db.session.add(q3)
    db.session.add(q4)
    db.session.commit()

    # Варианты для третьего вопроса
    choices3 = ["Русская", "Итальянская", "Японская", "Китайская", "Американская"]
    for text in choices3:
        choice = Choice(text=text, question_id=q3.id)
        db.session.add(choice)

    # Варианты для четвертого вопроса
    choices4 = ["Овощи", "Фрукты", "Мясо", "Рыба", "Молочные продукты", "Зерновые"]
    for text in choices4:
        choice = Choice(text=text, question_id=q4.id)
        db.session.add(choice)

    db.session.commit()

    print("✅ База данных успешно создана!")
    print(f"Создано опросов: 2")
    print(f"Создано вопросов: 4")
    print(f"Создано вариантов ответов: {len(choices1) + len(choices2) + len(choices3) + len(choices4)}")
    print("\nДоступные URL:")
    print(f"Главная страница: http://127.0.0.1:5002/")
    print(f"Пройти опрос 1: http://127.0.0.1:5002/survey/{survey1.id}/take")
    print(f"Пройти опрос 2: http://127.0.0.1:5002/survey/{survey2.id}/take")