import requests
import json
import os
import random
import time
import uuid
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # работает и локально, и на GitHub (если .env нет - просто использует os.environ)

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
                        "2. Объяснение проблемы - используй точную анатомическую терминологию (названия мышц, "
                        "связок, суставов на русском с латинскими терминами в скобках где уместно, например "
                        "'трапециевидная мышца (m. trapezius)')\n"
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
    
    # === МЕДИЦИНСКИЕ/СЕРЬЁЗНЫЕ ТЕМЫ (абстрактные картинки) ===
    medical_topics = [
        "дцп", "церебральн", "инсульт", "постинсульт", "онколог", "рак",
        "невролог", "реабилитац", "восстановлени", "двигательн",
        "перелом", "травм", "мениск", "эндопротезирован", "сколиоз",
        "лимфедем", "варикоз", "радикулит", "защем", "седалищ",
        "нейропати", "паралич", "парез", "атрофи", "дистрофи",
        "контрактур", "тугоподвижн", "спастик", "гипертонус"
    ]
    
    for keyword in medical_topics:
        if keyword in topic_lower:
            medical_queries = [
                "physical therapy rehabilitation",
                "medical rehabilitation",
                "therapy session medical",
                "patient recovery",
                "rehabilitation exercises",
                "medical care professional",
                "healing process medical",
                "physiotherapy treatment",
                "medical support care",
                "rehabilitation center therapy"
            ]
            query = random.choice(medical_queries)
            print(f"Searching Pexels for (medical): {query}")
            break
    else:
        # === ДЕТСКИЕ ТЕМЫ ===
        child_topics = ["детск", "ребенк", "груднич", "малыш", "ребёнок"]
        for keyword in child_topics:
            if keyword in topic_lower:
                child_queries = [
                    "baby massage therapy",
                    "child massage",
                    "infant massage",
                    "baby care massage",
                    "children therapy"
                ]
                query = random.choice(child_queries)
                print(f"Searching Pexels for (child): {query}")
                break
            else:
                # === СПОРТИВНЫЕ ТЕМЫ ===
                sport_topics = ["спорт", "бег", "тренировк", "фитнес", "упражнени"]
                for keyword in sport_topics:
                    if keyword in topic_lower:
                        sport_queries = [
                            "sports massage therapy",
                            "athlete recovery",
                            "sports rehabilitation",
                            "fitness massage",
                            "post workout massage"
                        ]
                        query = random.choice(sport_queries)
                        print(f"Searching Pexels for (sport): {query}")
                        break
                    else:
                        # === ОБЫЧНЫЙ ПОИСК ПО СЛОВАРЮ ===
                        translations = {
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
                            "баночк": "spa bottles",
                            "тейп": "kinesiology tape",
                            "вакуумн": "cupping therapy",
                            "сумк": "massage therapist kit",
                            "беремен": "pregnancy massage",
                            "глаз": "eye relaxation",
                            "тейпирован": "kinesiology taping",
                            "рубц": "scar tissue massage",
                            "роллер": "foam roller exercise",
                            "программист": "office posture",
                            "лимфедем": "lymphatic drainage",
                            "невралг": "nerve pain therapy",
                            "инструментальн": "IASTM tool massage",
                            "радикулит": "lower back pain",
                            "обув": "footwear posture",
                            "theragun": "massage gun device",
                            "пистолет": "massage gun device",
                            "книжн": "anatomy book",
                            "квалификац": "physiotherapy training",
                            "ковид": "breathing exercise recovery",
                            "миофасциальн": "myofascial release therapy",
                            "постизометрическ": "post-isometric relaxation",
                            "фасциальн": "fascial massage therapy",
                            "релиз": "myofascial release",
                            "головн": "headache relief massage",
                            "судорог": "muscle cramp relief",
                            "бессонниц": "insomnia relief massage",
                            "стресс": "stress relief massage",
                            "бруксизм": "jaw tension relief",
                            "челюст": "jaw massage therapy",
                            "тазобедрен": "hip joint therapy",
                            "лопатк": "shoulder blade massage",
                            "крест": "lower back massage",
                            "гуаша": "gua sha facial massage",
                            "релаксац": "relaxation massage",
                            "дренажн": "lymphatic drainage massage",
                            "разогрев": "warming massage therapy",
                            "охлажда": "cooling gel therapy",
                            "точечн": "acupressure massage",
                            "кож": "skin care therapy",
                            "чистк": "cleaning massage tools",
                            "дезинфицир": "disinfecting massage tools",
                            "гигиен": "massage hygiene",
                            "растяжк": "stretching exercises",
                            "лфк": "physical therapy exercises",
                            "гимнастик": "exercise therapy",
                            "атлас": "anatomy atlas",
                            "учебник": "anatomy textbook",
                            "курс": "massage training course",
                            "тестировани": "muscle testing therapy",
                            "викторин": "anatomy quiz",
                            "диагноз": "medical diagnosis",
                            "разбор": "medical case study",
                            "кабинет": "massage therapy room",
                            "стол": "massage table",
                            "массажист": "professional massage therapist",
                            "инструмент": "massage tools",
                            "оборудовани": "massage equipment",
                            "чек-лист": "massage therapist checklist",
                            "гайд": "massage therapy guide",
                            "совет": "massage tips",
                            "ошибк": "massage mistakes",
                            "миф": "massage myths",
                            "противопоказан": "massage contraindications",
                            "безопасн": "safe massage practice",
                            "запрет": "massage restrictions",
                            "против": "massage contraindications",
                            "вопрос": "massage therapy Q&A",
                            "ответ": "massage therapy Q&A",
                            "истори": "massage therapy success story",
                            "практик": "massage therapy practice",
                            "эффект": "massage therapy benefits",
                            "польз": "massage therapy benefits",
                            "техник": "massage techniques",
                            "метод": "massage methods",
                            "зона": "massage therapy zones",
                            "тело": "human body massage",
                            "сустав": "joint therapy massage",
                            "позвоночник": "spine therapy",
                            "диск": "spinal disc therapy",
                            "бедр": "thigh muscle rehabilitation",
                            "пахов": "groin strain rehabilitation",
                            "локт": "elbow injury therapy",
                            "теннис": "tennis elbow therapy",
                            "хлыстов": "whiplash rehabilitation",
                            "гипс": "cast removal rehabilitation",
                            "связк": "ligament injury rehabilitation",
                            "растяжени": "muscle strain rehabilitation",
                            "лодыжк": "ankle injury rehabilitation"
                        }
                        
                        query = "massage therapy"
                        for key, value in translations.items():
                            if key in topic_lower:
                                query = value
                                print(f"Searching Pexels for (translation): {query}")
                                break
                        else:
                            print(f"Searching Pexels for (default): {query}")
    
    # === ПОИСК В PEXELS ===
    headers = {"Authorization": os.getenv("PEXELS_API_KEY")}
    
    try:
        response = requests.get(
            f"https://api.pexels.com/v1/search?query={query}&per_page=10",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if data.get("photos"):
            photo = random.choice(data["photos"])
            return photo["src"]["medium"]
    except Exception as e:
        print(f"Pexels error: {e}")
    
    # === FALLBACK (если ничего не нашлось) ===
    fallback_queries = [
        "massage therapy",
        "healthcare professional",
        "physical therapy",
        "wellness massage"
    ]
    
    for fallback_query in fallback_queries:
        try:
            response = requests.get(
                f"https://api.pexels.com/v1/search?query={fallback_query}&per_page=1",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["medium"]
        except:
            continue
    
    # Абсолютный fallback
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
        params=params,
        timeout=30
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
        print(f"Ошибка генерации поста: {e}")
        send_message(MODERATOR_ID, f"❌ Ошибка генерации поста: {e}")
        exit(1)

    print("Ищу картинку...")
    image_url = get_image(topic)
    print(f"Картинка: {image_url}")

    print("Отправляю на проверку...")
    send_preview(MODERATOR_ID, post, image_url, session_id)
    print("Жду твоего решения (максимум 5 часов)...")

    offset = None
    waiting_for_edit = False
    start_time = time.time()
    TIMEOUT = 18000  # 5 часов в секундах

    while True:
        # Проверка таймаута (5 часов)
        if time.time() - start_time > TIMEOUT:
            send_message(MODERATOR_ID, "⏰ Время ожидания истекло (5 часов). Пост автоматически отклонён.")
            return_topic(topic)
            print("Timeout 5h - post rejected")
            break

        try:
            updates = get_updates(offset)
        except Exception as e:
            print(f"Error getting updates: {e}")
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
                        send_message(MODERATOR_ID, f"❌ Ошибка публикации: {result}")
                    exit()

                elif action == "edit":
                    send_message(MODERATOR_ID,
                        "✏️ Вот текст поста — отредактируй и отправь мне исправленную версию:\n\n" + post)
                    waiting_for_edit = True

                elif action == "reject":
                    return_topic(topic)
                    send_message(MODERATOR_ID, "❌ Пост пропущен, тема возвращена в очередь.")
                    print("Пост отклонён.")
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