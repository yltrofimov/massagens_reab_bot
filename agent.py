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
GIST_ID = os.getenv("GIST_ID")
GIST_TOKEN = os.getenv("GIST_TOKEN")

def read_used_from_gist():
    try:
        response = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GIST_TOKEN}"},
            timeout=15
        )
        content = response.json()["files"]["used.json"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"Gist read error: {e}")
        return []

def write_used_to_gist(used):
    try:
        requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GIST_TOKEN}"},
            json={"files": {"used.json": {"content": json.dumps(used, ensure_ascii=False)}}},
            timeout=15
        )
    except Exception as e:
        print(f"Gist write error: {e}")

def get_next_topic():
    with open("topics.json", encoding="utf-8") as f:
        topics = json.load(f)
    used = read_used_from_gist()
    remaining = [t for t in topics if t not in used]
    if not remaining:
        used = []
        remaining = topics
    topic = remaining[0]
    used.append(topic)
    write_used_to_gist(used)
    return topic

def return_topic(topic):
    used = read_used_from_gist()
    if topic in used:
        used.remove(topic)
    write_used_to_gist(used)

def generate_post(topic):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    for attempt in range(5):
        try:
            print(f"Generating post, attempt {attempt + 1}/5...")
            msg = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1500,
                timeout=60.0,
                messages=[{
                    "role": "user",
                    "content": (
                        "Ты - опытный массажист и реабилитолог с 15-летним стажем, эксперт в анатомии "
                        "и кинезиологии. Ведёшь профессиональный Telegram-канал для людей которые хотят "
                        "заботиться о своём теле.\n\n"
                        f"Напиши пост на тему: {topic}\n\n"
                        "Структура поста:\n"
                        "1. Цепляющее начало - 1-2 предложения которые сразу захватывают внимание\n"
                        "2. Объяснение проблемы - используй точную анатомическую терминологию: называй конкретные "
                        "мышцы, связки и суставы которые относятся именно к ЭТОЙ теме поста, с латинским названием "
                        "в скобках (например для шеи - m. sternocleidomastoideus, для спины - m. erector spinae, "
                        "для стопы - m. flexor digitorum brevis и т.д. - используй ту анатомию которая уместна по теме)\n"
                        "3. Практическое решение - конкретные техники пошагово, с профессиональными терминами "
                        "(например 'триггерная точка', 'миофасциальный релиз', 'постизометрическая релаксация', "
                        "'фасциальное натяжение')\n"
                        "4. Важное предупреждение - когда стоит обратиться к специалисту\n"
                        "5. Хештеги - 5-6 штук по теме\n\n"
                        "Требования:\n"
                        "- Максимум 900 символов, не больше\n"
                        "- Пиши языком профессионала который общается с осведомлённой аудиторией - "
                        "используй корректную медицинскую и анатомическую терминологию, но объясняй сложные "
                        "термины простыми словами в той же фразе\n"
                        "- Конкретика: указывай точную локализацию (например 'у основания черепа, в зоне "
                        "затылочной кости') и точные техники воздействия\n"
                        "- 2-3 эмодзи уместно по тексту\n"
                        "- Тон уверенного эксперта, не учебника и не разговорного блога\n"
                        "- Читатель-профессионал должен оценить точность, а читатель-новичок все равно понять суть"
                    )
                }]
            )
            return msg.choices[0].message.content
        except Exception as e:
            print(f"Attempt {attempt + 1}/5 failed: {e}")
            if attempt < 4:
                print("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                raise

def get_image(topic):
    topic_lower = topic.lower()

    medical_topics = [
        "дцп", "церебральн", "инсульт", "постинсульт", "онколог", "рак",
        "невролог", "реабилитац", "восстановлени", "двигательн",
        "перелом", "травм", "мениск", "эндопротезирован", "сколиоз",
        "лимфедем", "варикоз", "радикулит", "защем", "седалищ",
        "нейропати", "паралич", "парез", "атрофи", "дистрофи",
        "контрактур", "тугоподвижн", "спастик", "гипертонус"
    ]

    query = None

    for keyword in medical_topics:
        if keyword in topic_lower:
            query = random.choice([
                "physical therapy rehabilitation",
                "medical rehabilitation",
                "physiotherapy treatment",
                "patient recovery",
                "rehabilitation exercises"
            ])
            break

    if not query:
        child_topics = ["детск", "ребенк", "груднич", "малыш", "ребёнок"]
        for keyword in child_topics:
            if keyword in topic_lower:
                query = random.choice([
                    "baby massage therapy",
                    "infant massage",
                    "baby care massage"
                ])
                break

    if not query:
        sport_topics = ["спорт", "бег", "тренировк", "фитнес", "упражнени"]
        for keyword in sport_topics:
            if keyword in topic_lower:
                query = random.choice([
                    "sports massage therapy",
                    "athlete recovery",
                    "fitness massage"
                ])
                break

    if not query:
        translations = {
            "стоун": "hot stone massage therapy",
            "камн": "hot stone massage",
            "соль": "sea salt body scrub spa",
            "скраб": "body scrub spa treatment",
            "обёртыван": "body wrap spa treatment",
            "португал": "portugal spa wellness",
            "лиссабон": "lisbon spa wellness",
            "алгарв": "algarve portugal spa",
            "алентеж": "alentejo portugal nature",
            "пробков": "cork natural wellness",
            "термальн": "thermal spa portugal",
            "миндальн": "almond oil massage",
            "оливков": "olive oil massage",
            "монои": "monoi oil spa",
            "арган": "argan oil massage",
            "лаванд": "lavender essential oil",
            "мёд": "honey massage spa",
            "шея": "neck massage",
            "шейн": "neck massage",
            "поясниц": "back pain massage",
            "стоп": "foot massage",
            "голеностоп": "ankle rehabilitation",
            "массаж": "massage therapy",
            "плеч": "shoulder massage",
            "спин": "back massage",
            "колен": "knee rehabilitation",
            "рук": "hand massage",
            "осанк": "posture correction",
            "мышц": "muscle massage",
            "триггер": "trigger point massage",
            "самомассаж": "self massage",
            "масл": "massage oil",
            "крем": "massage cream",
            "эфирн": "essential oils spa",
            "аромат": "aromatherapy oils",
            "аллерг": "skin allergy test",
            "гель": "cooling gel",
            "гряз": "spa mud treatment",
            "водоросл": "seaweed spa",
            "бальзам": "massage balm",
            "тейп": "kinesiology tape",
            "вакуумн": "cupping therapy",
            "беремен": "pregnancy massage",
            "глаз": "eye relaxation",
            "рубц": "scar tissue massage",
            "роллер": "foam roller exercise",
            "лимфедем": "lymphatic drainage",
            "невралг": "nerve pain therapy",
            "инструментальн": "IASTM tool massage",
            "обув": "footwear posture",
            "theragun": "massage gun device",
            "пистолет": "massage gun device",
            "миофасциальн": "myofascial release therapy",
            "головн": "headache relief massage",
            "судорог": "muscle cramp relief",
            "бессонниц": "insomnia relief massage",
            "стресс": "stress relief massage",
            "бруксизм": "jaw tension relief",
            "челюст": "jaw massage therapy",
            "тазобедрен": "hip joint therapy",
            "гуаша": "gua sha facial massage",
            "дренажн": "lymphatic drainage massage",
            "точечн": "acupressure massage",
            "кож": "skin care therapy",
            "гигиен": "massage hygiene",
            "растяжк": "stretching exercises",
            "гимнастик": "exercise therapy",
            "массажист": "professional massage therapist",
            "техник": "massage techniques",
            "сустав": "joint therapy massage",
            "позвоночник": "spine therapy",
            "бедр": "thigh muscle rehabilitation",
            "локт": "elbow injury therapy",
            "теннис": "tennis elbow therapy",
            "связк": "ligament injury rehabilitation",
            "лодыжк": "ankle injury rehabilitation"
        }
        for key, value in translations.items():
            if key in topic_lower:
                query = value
                break

    if not query:
        query = "massage therapy"

    print(f"Searching Pexels for: {query}")
    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}

    try:
        response = requests.get(
            f"https://api.pexels.com/v1/search?query={query}&per_page=10",
            headers=headers, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if data.get("photos"):
            return random.choice(data["photos"])["src"]["medium"]
    except Exception as e:
        print(f"Pexels error: {e}")

    for fallback in ["massage therapy", "physical therapy", "wellness spa"]:
        try:
            response = requests.get(
                f"https://api.pexels.com/v1/search?query={fallback}&per_page=1",
                headers=headers, timeout=30
            )
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["medium"]
        except:
            continue

    return "https://images.pexels.com/photos/3822141/pexels-photo-3822141.jpeg"

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
        params=params, timeout=35
    )
    return response.json().get("result", [])

def answer_callback(callback_id):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
        data={"callback_query_id": callback_id}
    )

if __name__ == "__main__":
    session_id = str(uuid.uuid4())[:8]
    print("Запуск агента...")

    topic = get_next_topic()
    print(f"Тема: {topic}")

    print("Генерирую пост...")
    try:
        post = generate_post(topic)
        print(f"Пост готов:\n{post}\n")
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        send_message(MODERATOR_ID, f"❌ Ошибка генерации поста: {e}")
        exit(1)

    print("Ищу картинку...")
    image_url = get_image(topic)
    print(f"Картинка: {image_url}")

    print("Отправляю на проверку...")
    send_preview(MODERATOR_ID, post, image_url, session_id)
    print("Жду решения (максимум 5 часов)...")

    offset = None
    waiting_for_edit = False
    start_time = time.time()
    TIMEOUT = 18000

    while True:
        if time.time() - start_time > TIMEOUT:
            send_message(MODERATOR_ID, "⏰ Время вышло (5 часов). Пост отклонён, тема возвращена в очередь.")
            return_topic(topic)
            print("Timeout - rejected")
            break

        try:
            updates = get_updates(offset)
        except Exception as e:
            print(f"Updates error: {e}")
            time.sleep(5)
            continue

        for update in updates:
            offset = update["update_id"] + 1

            if "callback_query" in update:
                cb = update["callback_query"]
                if str(cb["from"]["id"]) != str(MODERATOR_ID):
                    continue
                data = cb["data"]
                if not data.endswith(session_id):
                    answer_callback(cb["id"])
                    continue
                answer_callback(cb["id"])
                action = data.replace(f"_{session_id}", "")

                if action == "approve":
                    result = publish_to_channel(post, image_url)
                    if result.get("ok"):
                        send_message(MODERATOR_ID, "✅ Пост опубликован в канал!")
                        print("Опубликовано!")
                    else:
                        send_message(MODERATOR_ID, f"❌ Ошибка: {result}")
                    exit()

                elif action == "edit":
                    send_message(MODERATOR_ID,
                        "✏️ Вот текст поста — отредактируй и отправь мне исправленную версию:\n\n" + post)
                    waiting_for_edit = True

                elif action == "reject":
                    return_topic(topic)
                    send_message(MODERATOR_ID, "❌ Пост пропущен, тема возвращена в очередь.")
                    print("Отклонён.")
                    exit()

            elif "message" in update and waiting_for_edit:
                msg = update["message"]
                if str(msg["from"]["id"]) != str(MODERATOR_ID):
                    continue
                if "text" in msg:
                    post = msg["text"]
                    waiting_for_edit = False
                    send_message(MODERATOR_ID, "✅ Получил! Показываю обновлённый пост...")
                    send_preview(MODERATOR_ID, post, image_url, session_id)

        time.sleep(1)