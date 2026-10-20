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

    # Определяем тип поста по теме
    type_rules = {
        "мышц": "МЫШЦА",
        "muscul": "МЫШЦА",
        "техник": "ТЕХНИКА",
        "ломи": "ТЕХНИКА",
        "испанск": "ТЕХНИКА",
        "медов": "ТЕХНИКА",
        "криол": "ТЕХНИКА",
        "лимфодренаж": "ТЕХНИКА",
        "стоун": "ТЕХНИКА",
        "гуаша": "ИНСТРУМЕНТ",
        "роллер": "ИНСТРУМЕНТ",
        "тейп": "ИНСТРУМЕНТ",
        "пистолет": "ИНСТРУМЕНТ",
        "theragun": "ИНСТРУМЕНТ",
        "банк": "ИНСТРУМЕНТ",
        "скребок": "ИНСТРУМЕНТ",
        "камн": "ИНСТРУМЕНТ",
        "миф": "МИФ",
        "правда": "МИФ",
        "токсин": "МИФ",
        "противопоказан": "ПРОТИВОПОКАЗАНИЕ",
        "нельзя": "ПРОТИВОПОКАЗАНИЕ",
        "запрет": "ПРОТИВОПОКАЗАНИЕ",
        "варикоз": "ПРОТИВОПОКАЗАНИЕ",
        "онколог": "ПРОТИВОПОКАЗАНИЕ",
        "истори": "КЕЙС",
        "практик": "КЕЙС",
        "случа": "КЕЙС",
    }

    post_type = "СОВЕТ"  # по умолчанию
    topic_lower = topic.lower()
    for key, ptype in type_rules.items():
        if key in topic_lower:
            post_type = ptype
            break

    # Структура для каждого типа
    structures = {
        "МЫШЦА": """
Напиши профессиональный пост-разбор мышцы на тему: {topic}

Структура:
1. Цепляющее начало — зачем читателю знать эту мышцу (1-2 предложения)
2. Полное название мышцы на русском и латыни (например: многораздельная мышца — musculus multifidus)
3. Расположение — где находится, от куда до куда идёт, простыми словами
4. Функция — за какое движение отвечает, пример биомеханики
5. Триггерные точки — где искать, как проявляются (боль, онемение)
6. Как работать с этой мышцей — техника самомассажа или работы специалиста
7. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- Полные названия мышц всегда
- Для профессионала точно, для новичка понятно
- 2-3 эмодзи
""",
        "ТЕХНИКА": """
Напиши профессиональный пост про технику массажа на тему: {topic}

Структура:
1. Цепляющее начало — интригующий факт или вопрос (1-2 предложения)
2. История и происхождение техники — откуда, когда появилась
3. На чём основана — физиологический принцип действия
4. Для кого подходит и в каких случаях применяется
5. Важные противопоказания именно для этой техники
6. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- Никакой фантастики — только реальные свойства техники
- Для профессионала точно, для новичка понятно
- 2-3 эмодзи
""",
        "ИНСТРУМЕНТ": """
Напиши профессиональный пост про инструмент или гаджет на тему: {topic}

Структура:
1. Цепляющее начало — что это и почему это интересно (1-2 предложения)
2. История и происхождение — откуда появился инструмент, философия
3. Из чего делают — материалы, виды (например гуаша бывает из нефрита, розового кварца)
4. Для чего реально используется — честно и точно (не преувеличивать эффект)
5. Для кого подходит — возраст, тип кожи, ситуации
6. Чего нельзя делать с этим инструментом
7. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- ВАЖНО: гуаша и МФР роллер — разные инструменты для разных задач, никогда не смешивать
- Никакой фантастики — только реальные свойства
- Для профессионала точно, для новичка понятно
- 2-3 эмодзи
""",
        "МИФ": """
Напиши профессиональный пост-разбор мифа на тему: {topic}

Структура:
1. Цепляющее начало — озвучь миф провокационно (1-2 предложения)
2. Почему люди в это верят — откуда взялось заблуждение
3. Что говорит наука и практика — факты, физиология
4. Как есть на самом деле — правда без прикрас
5. Практический вывод для читателя
6. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- Только доказанные факты, никакой фантастики
- Уверенный тон эксперта
- 2-3 эмодзи
""",
        "ПРОТИВОПОКАЗАНИЕ": """
Напиши профессиональный пост про противопоказания на тему: {topic}

Структура:
1. Цепляющее начало — почему это важно знать (1-2 предложения)
2. Суть противопоказания — что именно и почему нельзя, физиологическое объяснение
3. Какие виды массажа под запретом, а какие допустимы в этом случае
4. Что можно делать вместо массажа
5. Когда всё-таки можно — условия и ограничения
6. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- Медицински точно и ответственно
- Для профессионала точно, для новичка понятно
- 2-3 эмодзи
""",
        "КЕЙС": """
Напиши профессиональный пост-кейс из практики на тему: {topic}

Структура:
1. Цепляющее начало — интригующая ситуация (1-2 предложения)
2. Ситуация клиента — симптомы, жалобы (анонимно)
3. Что обнаружил специалист — диагностика, находки
4. Что было сделано — техники, курс, подход
5. Результат — что изменилось и почему
6. Вывод для читателя
7. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- Реалистично и правдоподобно
- Для профессионала точно, для новичка понятно
- 2-3 эмодзи
""",
        "СОВЕТ": """
Напиши профессиональный пост-совет на тему: {topic}

Структура:
1. Цепляющее начало — боль, проблема или вопрос (1-2 предложения)
2. Объяснение причины — анатомия строго по теме поста
   ПРАВИЛО: упоминай ТОЛЬКО мышцы/суставы относящиеся к данной теме
   Давай полное название мышцы: русское + латинское + где находится
   Пост про масло/косметику — анатомию не упоминай вообще
3. Практическое решение — конкретные техники пошагово
4. Предупреждение — когда идти к специалисту
5. Хештеги 5-6 штук

Требования:
- 850-900 символов строго
- Конкретика: точная локализация, конкретные движения
- Для профессионала точно, для новичка понятно
- 2-3 эмодзи
"""
    }

    prompt = structures[post_type].format(topic=topic)

    for attempt in range(5):
        try:
            print(f"Generating post ({post_type}), attempt {attempt + 1}/5...")
            msg = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                max_tokens=1500,
                timeout=60.0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — опытный массажист и реабилитолог с 15-летним стажем, "
                            "эксперт в анатомии и кинезиологии. Ведёшь профессиональный "
                            "Telegram-канал для двух аудиторий: клиентов (обычные люди) и "
                            "коллег-массажистов. Пишешь точно, честно, без фантастики. "
                            "Никогда не преувеличиваешь эффект процедур. "
                            "Всегда даёшь полные названия мышц: русское + латинское + расположение."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return msg.choices[0].message.content
        except Exception as e:
            print(f"Attempt {attempt + 1}/5 failed: {e}")
            if attempt < 4:
                print("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                raise
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    for attempt in range(5):
        try:
            print(f"Generating post, attempt {attempt + 1}/5...")
            msg = client.chat.completions.create(
                model="openai/gpt-oss-20b",
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
                        "2. Объяснение проблемы - используй ТОЛЬКО анатомию которая прямо относится к теме поста. "
                        "Правило: если тема про стопу - пиши про мышцы стопы, про колено - про колено, про масло - "
                        "вообще не упоминай мышцы. Никогда не вставляй анатомию ради анатомии. "
                        "Латинские названия только для мышц которые реально задействованы в теме.\n"
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
                        "- ВАЖНО: выбирай анатомические термины строго по теме поста. "
                        "Пост про масло или косметику - без названий мышц. "
                        "Пост про стопу - только мышцы стопы. Пост про шею - только мышцы шеи. "
                        "Никаких универсальных мышц которые вставляются в любой пост.\n"
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