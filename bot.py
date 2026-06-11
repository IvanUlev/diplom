import logging
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import json

# Подключаем твои файлы с функциями
from agents.detector import detect_task  # Импортируем из detector.py
from agents.extractor import extract_data  # Импортируем из extractor.py
from agents.priority import get_priority  # Импортируем из priority.py
from agents.validator import validate  # Импортируем из validator.py

# Загрузка датасетов
def load_dataset(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Загрузка датасетов 
#detector_dataset = load_dataset('data/dataset_detector.json')  # Путь к датасету детектора
priority_dataset = load_dataset('data/dataset_priority_v2.json')  # Путь к датасету приоритетов

API_TOKEN = "vk1.a.CPJ37Dy2xgZW-anurhHqvyT--mFT5P8_UHqLO0Y7Cpt6y5EwkGLqe31RHlwIIEkPCH-UiBMnQpmsLbNrJEsqc84uT2WzQK6OaFGfumKQfUnVTPNhJPHNJXJgcNvjdwP7aNQ14-1LhUFSyPSXXty3pUzc8u-0HLHYNXBZfO3XP_OhgJAF8gztR72VmaGFEkmA8RsR2QisUmiUjC71_XtlZg"  # Токен ВКонтакте

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция для обработки сообщений от пользователей ВКонтакте
def handle_message(event, vk):
    text = event.text  # Получаем текст от пользователя

    # Проверка, является ли сообщение задачей с использованием detect_task
    if not detect_task(text):  # Если это не задача
        task_info = "Это не задача."  # Отправляем сообщение, что это не задача
        vk.messages.send(user_id=event.user_id, message=task_info, random_id=random.randint(1, 1e6))  # Добавляем random_id
        return
    
    # Извлекаем данные задачи с помощью extract_data
    data = extract_data(text)
    if "error" in data:
        task_info = f"Ошибка: {data['error']}\nДетали: {data.get('details', '')}"
        vk.messages.send(user_id=event.user_id, message=task_info, random_id=random.randint(1, 1e6))  # Добавляем random_id
        return
    
    # Если это задача, вычисляем приоритет с помощью get_priority
    data["priority"] = get_priority(text)

    # Валидация данных с помощью validate
    validated_data = validate(data)
    
    # Формируем ответ с задачей
    if validated_data["is_task"]:
        task_info = f"Задача: {validated_data['title']}\nОписание: {validated_data['description']}\nПриоритет: {validated_data['priority']}"
    else:
        task_info = "Это не задача."
    
    # Ответ пользователю
    vk.messages.send(user_id=event.user_id, message=task_info, random_id=random.randint(1, 1e6))  # Добавляем random_id

# Основная функция для создания и запуска бота
def main():
    # Авторизация с использованием API токена
    vk_session = vk_api.VkApi(token=API_TOKEN)
    vk = vk_session.get_api()

    # Долгий опрос для получения сообщений
    longpoll = VkLongPoll(vk_session)

    # Обрабатываем новые сообщения
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk)

if __name__ == '__main__':
    main()  # Запуск бота