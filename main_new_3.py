import json
from agents.detector import detect_task
from agents.extractor import extract_data
from agents.validator import validate_task  # новый валидатор


# =========================
# DATASET
# =========================
with open("data/dataset_detector.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)


# =========================
# PIPELINE
# =========================
def process(text: str):
    # 1. detector
    is_task = detect_task(text)

    if not is_task:
        return {
            "is_task": False,
            "final": None
        }

    # 2. extractor
    extracted = extract_data(text)

    if "error" in extracted:
        return {
            "is_task": False,
            "error": extracted
        }

    # 3. validator (с циклом)
    validated = validate_task(extracted, extract_data)

    return {
        "is_task": True,
        "validated": validated
    }


# =========================
# RUN
# =========================
results = []

for item in dataset:
    text = item["text"]
    true_label = item["is_task"]

    pred = process(text)

    results.append({
        "text": text,
        "true": true_label,
        "pred": pred
    })


# =========================
# METRICS
# =========================
tp = fp = fn = tn = 0
valid_count = 0

validator_success = 0
validator_scores = []
validator_iterations = []


for item in results:
    pred = item["pred"]

    # если детектор сказал не задача
    if not pred["is_task"]:
        y_pred = False
    else:
        y_pred = True

        val = pred["validated"]

        if val["status"] == "success":
            validator_success += 1
            validator_scores.append(val["score"])

        # считаем итерации
        # (если не сохранил — можно потом добавить в validator)
    
    y_true = item["true"]

    valid_count += 1

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


# =========================
# VALIDATOR METRICS
# =========================
validator_rate = validator_success / valid_count if valid_count else 0
avg_score = sum(validator_scores) / len(validator_scores) if validator_scores else 0


# =========================
# OUTPUT
# =========================
print("\n=== PIPELINE METRICS ===")
print("Samples:", valid_count)
print("Accuracy:", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1:", round(f1, 4))

print("\n=== VALIDATOR METRICS ===")
print("Success rate:", round(validator_rate, 4))
print("Avg score:", round(avg_score, 2))


# =========================
# SAVE
# =========================
with open("results_full_pipeline.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)