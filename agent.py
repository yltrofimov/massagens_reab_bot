import requests
import json
import os
import random
import time
import uuid
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
MODERATOR_ID = os.getenv("MODERATOR_ID")
CHANNEL_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_next_topic():
    with open("topics.json", encoding="utf-8") as f:
        topics = json.load(f)
    try:
        with open("used.json", encoding="utf-8") as f:
            used = json.load(f)
    except:
        used = []
    remaining = [t for t in topics if t not in used]
    if not remaining:
        used = []
        remaining = topics
    topic = remaining[0]
    used.append(topic)
    with open("used.json", "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False)
    return topic

def return_topic(topic):
    try:
        with open("used.json", encoding="utf-8") as f:
            used = json.load(f)
    except:
        used = []
    if topic in used:
        used.remove(topic)
    with open("used.json", "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False)

def generate_post(topic):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    msg = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": (
                "Ты - опытный массажист и реабилитолог с 15-летним стажем. "
                "Ведёшь Telegram-канал для людей которые хотят заботиться о своём теле.\n\n"
                f"Напиши пост на тему: {topic}\n\n"
                "Структура поста:\n"
                "1. Цепляющее начало - 1-2 предложения которые сразу захватывают внимание\n"
                "2. Объяснение проблемы - почему это происходит, что происходит в теле\n"
                "3. Практическое решение - конкретные техники пошагово\n"
                "4. Важное предупреждение - когда стоит обратиться к специалисту\n"
                "5. Хештеги - 5-6 штук по теме\n\n"
                "Требования:\n"
                "- Максимум 900 символов, не больше\n"
                "- Пиши как живой человек, не как учебник\n"
                "- Конкретика: не просто 'делайте упражнения' а 'надавите большим пальцем на точку под лопаткой и держите 30 секунд'\n"
                "- 2-3 эмодзи уместно по тексту\n"
                "- Читатель должен узнать что-то новое и сразу захотеть попробовать"
            )
        }]
    )
    return msg.choices[0].message.content

def get_image(topic):
    translations = {
        "шея": "neck massage",
        "поясница": "back pain massage",
        "стопы": "foot massage",
        "стоп": "foot massage",
        "голеностоп": "ankle rehabilitation",
        "реабилитация": "physical rehabilitation",
        "массаж": "massage therapy",
        "плечо": "shoulder massage",
        "спина": "back massage",
        "колено": "knee rehabilitation",
        "руки": "hand massage",
        "головная боль": "head massage",
        "осанка": "posture correction",
        "мышцы": "muscle massage",
        "триггер": "trigger point massage",
        "противопоказан": "massage therapy",
        "самомассаж": "self massage"
    }
    query = "massage therapy"
    for key, value in translations.items():
        if key in topic.lower():
            query = value
            break

    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}
    response = requests.get(
        f"https://api.pexels.com/v1/search?query={query}&per_page=5",
        headers=headers
    )
    data = response.json()
    if data.get("photos"):
        photo = random.choice(data["photos"])
        return photo["src"]["medium"]

    response = requests.get(
        "https://api.pexels.com/v1/search?query=massage therapy&per_page=1",
        headers=headers
    )
    return response.json()["photos"][0]["src"]["medium"]

def send_message(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": chat_id, "text": text}
    )

def send_preview(chat_id, text, image_url, session_id):
    caption = text[:1020] + "..." if len(text) > 1024 else text
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        data={
            "chat_id": chat_id,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": json.dumps({
                "inline_keyboard": [[
                    {"text": "✅ Опубликовать", "callback_data": f"approve_{session_id}"},
                    {"text": "✏️ Редактировать", "callback_data": f"edit_{session_id}"},
                    {"text": "❌ Пропустить", "callback_data": f"reject_{session_id}"}
                ]]
            })
        }
    )

def publish_to_channel(text, image_url):
    caption = text[:1020] + "..." if len(text) > 1024 else text
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
        data={
            "chat_id": CHANNEL_ID,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML"
        }
    )
    return response.json()

def get_updates(offset=None):
    params = {"timeout": 30, "allowed_updates": ["callback_query", "message"]}
    if offset:
        params["offset"] = offset
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getUpdates",
        params=params
    )
    return response.json().get("result", [])

def answer_callback(callback_id):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
        data={"callback_query_id": callback_id}
    )

if __name__ == "__main__":
    # Уникальный ID этой сессии - кнопки от прошлых запусков не сработают
    session_id = str(uuid.uuid4())[:8]

    print("Запуск агента...")

    topic = get_next_topic()
    print(f"Тема: {topic}")

    print("Генерирую пост...")
    post = generate_post(topic)
    print(f"Пост готов:\n{post}\n")

    print("Ищу картинку...")
    image_url = get_image(topic)

    print("Отправляю на проверку...")
    send_preview(MODERATOR_ID, post, image_url, session_id)
    print("Жду твоего решения (без ограничения времени)...")

    offset = None
    waiting_for_edit = False

    while True:
        updates = get_updates(offset)

        for update in updates:
            offset = update["update_id"] + 1

            # Нажата кнопка
            if "callback_query" in update:
                cb = update["callback_query"]
                if str(cb["from"]["id"]) != str(MODERATOR_ID):
                    continue

                data = cb["data"]

                # Проверяем что кнопка от текущей сессии
                if not data.endswith(session_id):
                    answer_callback(cb["id"])
                    continue

                answer_callback(cb["id"])
                action = data.replace(f"_{session_id}", "")

                if action == "approve":
                    result = publish_to_channel(post, image_url)
                    if result.get("ok"):
                        send_message(MODERATOR_ID, "Пост опубликован в канал!")
                        print("Опубликовано!")
                    else:
                        send_message(MODERATOR_ID, f"Ошибка публикации: {result}")
                    exit()

                elif action == "edit":
                    send_message(MODERATOR_ID,
                        "Вот текст поста — отредактируй и отправь мне исправленную версию:\n\n" + post)
                    waiting_for_edit = True

                elif action == "reject":
                    return_topic(topic)
                    send_message(MODERATOR_ID, "Пост пропущен, тема возвращена в очередь.")
                    print("Пост отклонён.")
                    exit()

            # Пришёл отредактированный текст
            elif "message" in update and waiting_for_edit:
                msg = update["message"]
                if str(msg["from"]["id"]) != str(MODERATOR_ID):
                    continue
                if "text" in msg:
                    post = msg["text"]
                    waiting_for_edit = False
                    send_message(MODERATOR_ID, "Получил! Показываю обновлённый пост...")
                    send_preview(MODERATOR_ID, post, image_url, session_id)