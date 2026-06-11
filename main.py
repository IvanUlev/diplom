import json
from agents.detector import detect_task
from agents.extractor import extract_data
from agents.priority_baseline2 import get_priority, evaluate_priority_dataset
from agents.validator import validate


with open("data/dataset_detector.json", "r", encoding="utf-8") as f:
    detector_dataset = json.load(f)

with open("data/dataset_priority_v2.json", "r", encoding="utf-8") as f:
    priority_dataset = json.load(f)



def process(text: str) -> dict:
    if not detect_task(text):
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
for item in detector_dataset:
    pred = process(item["text"])
    results.append({
        "text": item["text"],
        "true": item["is_task"],
        "pred": pred,
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

print("\n=== DETECTOR PIPELINE METRICS ===")
print("Valid samples:", valid_count)
print("Errors:", error_count)
print("Accuracy:", round(accuracy, 4))
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1:", round(f1, 4))

priority_metrics = evaluate_priority_dataset(priority_dataset)
print("\n=== PRIORITY METRICS ===")
print("Total:", priority_metrics["total"])
print("Correct:", priority_metrics["correct"])
print("Accuracy:", round(priority_metrics["accuracy"], 4))

with open("results_detector.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("results_priority.json", "w", encoding="utf-8") as f:
    json.dump(priority_metrics["details"], f, ensure_ascii=False, indent=2)
