import json
import time
from agents.detector import detect_task
from agents.extractor_new import extract_data
from agents.validator_new import validate_task



def load_dataset(path):
    with open("data/dataset2.json", "r", encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(dataset):
    y_true = []
    y_pred = []

    total_latency = 0
    total_tokens = 0

    deadline_correct = 0
    priority_correct = 0
    total_tasks = 0

    results = []

    for item in dataset:
        text = item["text"]
        true_label = item["is_task"]

        start = time.time()

        #DETECTOR
        det = detect_task(text)

        y_true.append(true_label)
        y_pred.append(det["is_task"])

        total_latency += det["latency"]
        if det["tokens"]:
            total_tokens += det["tokens"].get("total_tokens", 0)

        #Не задача
        if not det["is_task"]:
            results.append({
                "text": text,
                "is_task": False
            })
            continue

        #EXTRACTOR
        ext = extract_data(text)

        total_latency += ext.get("latency", 0)

        if ext.get("tokens"):
            total_tokens += ext["tokens"].get("total_tokens", 0)

        if "error" in ext:
            results.append({
                "text": text,
                "is_task": True,
                "output": ext
            })
            continue

        #VALIDATOR
        val = validate_task(ext, extract_data, text)

        total_latency += val.get("latency", 0)
        total_tokens += val.get("tokens", 0)

        final_task = val["task"]

        #Сравнение с эталоном
        if "expected" in item:
            total_tasks += 1

            if final_task.get("priority") == item["expected"].get("priority"):
                priority_correct += 1

            if final_task.get("deadline") == item["expected"].get("deadline"):
                deadline_correct += 1

        results.append({
            "text": text,
            "is_task": True,
            "output": final_task
        })

    #Классификация
    tp = fp = fn = tn = 0

    for t, p in zip(y_true, y_pred):
        if t and p:
            tp += 1
        elif not t and p:
            fp += 1
        elif t and not p:
            fn += 1
        else:
            tn += 1

    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    #Доп метрики
    deadline_acc = deadline_correct / total_tasks if total_tasks else 0
    priority_acc = priority_correct / total_tasks if total_tasks else 0

    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "deadline_accuracy": deadline_acc,
        "priority_accuracy": priority_acc,
        "total_latency": total_latency,
        "total_tokens": total_tokens
    }

    return metrics, results


if __name__ == "__main__":
    dataset = load_dataset("dataset_full.json")

    metrics, results = run_pipeline(dataset)

    print("\n=== METRICS ===")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))

    with open("results_pipeline.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)