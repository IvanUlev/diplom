import json
from agents.detector_baseline import detect_task
from agents.extractor import extract_data
from agents.priority_baseline import get_priority
from agents.validator import validate


with open("data/dataset_detector.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)


def process(text: str) -> dict:
    is_task = detect_task(text)

    if not is_task:
        return {"is_task": False}

    data = extract_data(text)

    if "error" in data:
        return {
            "is_task": False,
            "error": data["error"],
            "details": data.get("details", ""),
        }

    data["priority"] = get_priority(text)

    return validate(data)


results = []

for item in dataset:
    pred = process(item["text"])
    results.append({
        "text": item["text"],
        "true": item["is_task"],
        "pred": pred
    })


tp = fp = fn = tn = 0
valid_count = 0
error_count = 0

for item in results:
    pred = item["pred"]

    if "error" in pred:
        error_count += 1
        continue

    valid_count += 1

    y_true = item["true"]
    y_pred = pred["is_task"]

    if y_true and y_pred:
        tp += 1
    elif not y_true and y_pred:
        fp += 1
    elif y_true and not y_pred:
        fn += 1
    else:
        tn += 1

accuracy = (tp + tn) / valid_count if valid_count else 0
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

print("\n=== МЕТРИКИ ===")
print("Valid samples:", valid_count)
print("Errors:", error_count)
print("Accuracy:", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1:", round(f1, 4))


tests = [
    "Сделать отчёт до завтра",
    "Пофиксить баг сегодня",
    "Подготовить презентацию к пятнице",
    "Отправить письмо клиенту",
    "Закончить диплом к 1 апреля",
    "Купить продукты завтра",
    "Сходить в зал сегодня вечером",
    "Позвонить маме в пятницу",
    "Сделать задачу срочно",
    "Оплатить аренду до завтра",
    "Сделать отчёт",
    "Пофиксить баг",
    "Подготовить презентацию",
    "Написать код",
    "Прочитать книгу",
    "Убраться в комнате",
    "Сходить в магазин",
    "Проверить почту",
    "Сделать домашку",
    "Разобраться с проектом",
    "Надо бы сделать отчёт",
    "Можно как-нибудь пофиксить баг",
    "Неплохо бы обновить документацию",
    "Стоит заняться этим",
    "Надо бы разобраться",
    "Когда-нибудь сделать это",
    "Если получится, сделай задачу",
    "Попробуй пофиксить баг",
    "Надо бы закончить проект",
    "Может стоит обновить код",
    "Пойдём гулять",
    "Давай созвонимся",
    "Может встретимся завтра",
    "Как дела?",
    "Что делаешь?",
    "Я устал",
    "Сегодня хорошая погода",
    "Это было сложно",
    "Мне не нравится этот код",
    "Ты видел это?",
    "Давай подумаем над архитектурой",
    "Стоит обсудить дизайн",
    "Нужно подумать над этим",
    "Интересно, как это работает",
    "Надо обсудить это позже",
    "Можно обсудить задачу",
    "Давай подумаем",
    "Нужно разобраться",
    "Интересная идея",
    "Надо поговорить об этом",
    "Посмотри задачу",
    "Разберись с этим",
    "Сделай это",
    "Сделай задачу",
    "Проверь это",
    "Посмотри код",
    "Сделай как у конкурентов",
    "Исправь это",
    "Займись этим",
    "Разберись позже",
    "Срочно сделать отчёт",
    "Очень важно закончить проект",
    "Нужно срочно оплатить",
    "Сделать прямо сейчас",
    "Немедленно отправить письмо",
    "Сделать отчёт до четверга",
    "Подготовить презентацию к понедельнику",
    "Пофиксить баг до завтра",
    "Закончить проект к пятнице",
    "Сдать работу сегодня",
    "фывафыва",
    "123456",
    "!!!???",
    "...",
    "///////",
]

print("\n=== ТЕСТЫ ===\n")

for t in tests:
    print("Вход:", t)
    print("Выход:", process(t))


with open("results_detector.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)