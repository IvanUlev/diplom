def validate(data: dict) -> dict:
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    priority = str(data.get("priority", "medium")).strip().lower()

    if not title:
        return {
            "is_task": False,
            "error": "empty_title"
        }

    if len(title) < 3:
        return {
            "is_task": False,
            "error": "title_too_short"
        }

    if priority not in {"high", "medium", "low"}:
        priority = "уточните срок"
    print(priority)
    return {
        "is_task": True,
        "title": title,
        "description": description,
        "priority": priority,
    }