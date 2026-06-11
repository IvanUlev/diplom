import json
from agents.detector_agent import detect_task

while True:
    text = input("Введи сообщение: ")

    if text.lower() in ["exit", "quit"]:
        break

    result = detect_task(text)

    print("Результат:", result)
    print("-" * 30)