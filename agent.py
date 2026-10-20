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
        "масл": "ИНСТРУМЕНТ",
        "экстракт": "ИНСТРУМЕНТ",
        "пробков": "ИНСТРУМЕНТ",
        "крем": "ИНСТРУМЕНТ",
        "бальзам": "ИНСТРУМЕНТ",
        "соль": "ИНСТРУМЕНТ",
        "скраб": "ИНСТРУМЕНТ",
        "аромат": "ИНСТРУМЕНТ",
        "эфирн": "ИНСТРУМЕНТ",
        "лаванд": "ИНСТРУМЕНТ",
        "оливков": "ИНСТРУМЕНТ",
        "миндальн": "ИНСТРУМЕНТ",
        "арган": "ИНСТРУМЕНТ",
        "мёд": "ИНСТРУМЕНТ",
        "водоросл": "ИНСТРУМЕНТ",
        "грязи": "ИНСТРУМЕНТ",
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

    post_type = "СОВЕТ"
    topic_lower = topic.lower()
    for key, ptype in type_rules.items():
        if key in topic_lower:
            post_type = ptype
            break

    structures = {
        "МЫШЦА": (
            f"Напиши профессиональный пост-разбор мышцы на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — зачем читателю знать эту мышцу (1-2 предложения)\n"
            "2. Полное название мышцы на русском и латыни\n"
            "3. Расположение — где находится, от куда до куда идёт, простыми словами\n"
            "4. Функция — за какое движение отвечает, пример биомеханики\n"
            "5. Триггерные точки — где искать, как проявляются (боль, онемение)\n"
            "6. Как работать с этой мышцей — техника самомассажа или работы специалиста\n"
            "7. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- Полные названия мышц всегда: русское + латинское + где находится\n"
            "- Для профессионала точно, для новичка понятно\n"
            "- 2-3 эмодзи\n"
            "- Никакой фантастики, только факты\n"
        ),
        "ТЕХНИКА": (
            f"Напиши профессиональный пост про технику массажа на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — интригующий факт или вопрос (1-2 предложения)\n"
            "2. История и происхождение техники — откуда, когда появилась\n"
            "3. На чём основана — физиологический принцип действия\n"
            "4. Для кого подходит и в каких случаях применяется\n"
            "5. Важные противопоказания именно для этой техники\n"
            "6. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- Никакой фантастики — только реальные свойства техники\n"
            "- Для профессионала точно, для новичка понятно\n"
            "- 2-3 эмодзи\n"
        ),
        "ИНСТРУМЕНТ": (
            f"Напиши профессиональный пост про инструмент, косметику или ингредиент на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — что это и почему интересно (1-2 предложения)\n"
            "2. История и происхождение — откуда появился, философия\n"
            "3. Из чего делают или состав — материалы, виды\n"
            "4. Для чего реально используется — честно и точно, без преувеличений\n"
            "5. Для кого подходит — возраст, тип кожи, ситуации\n"
            "6. Чего нельзя делать с этим инструментом или ингредиентом\n"
            "7. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- ВАЖНО: гуаша и МФР роллер — разные инструменты для разных задач, никогда не смешивать\n"
            "- Гуаша и скребки — для лица и шеи, МФР роллер — для крупных мышц тела\n"
            "- Никакой фантастики — только реальные свойства\n"
            "- Для профессионала точно, для новичка понятно\n"
            "- 2-3 эмодзи\n"
        ),
        "МИФ": (
            f"Напиши профессиональный пост-разбор мифа на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — озвучь миф провокационно (1-2 предложения)\n"
            "2. Почему люди в это верят — откуда взялось заблуждение\n"
            "3. Что говорит наука и практика — факты, физиология\n"
            "4. Как есть на самом деле — правда без прикрас\n"
            "5. Практический вывод для читателя\n"
            "6. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- Только доказанные факты, никакой фантастики\n"
            "- Уверенный тон эксперта\n"
            "- 2-3 эмодзи\n"
        ),
        "ПРОТИВОПОКАЗАНИЕ": (
            f"Напиши профессиональный пост про противопоказания на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — почему это важно знать (1-2 предложения)\n"
            "2. Суть противопоказания — что именно и почему нельзя, физиологическое объяснение\n"
            "3. Какие виды массажа под запретом, а какие допустимы в этом случае\n"
            "4. Что можно делать вместо массажа\n"
            "5. Когда всё-таки можно — условия и ограничения\n"
            "6. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- Медицински точно и ответственно\n"
            "- Для профессионала точно, для новичка понятно\n"
            "- 2-3 эмодзи\n"
        ),
        "КЕЙС": (
            f"Напиши профессиональный пост-кейс из практики на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — интригующая ситуация (1-2 предложения)\n"
            "2. Ситуация клиента — симптомы, жалобы (анонимно)\n"
            "3. Что обнаружил специалист — диагностика, находки\n"
            "4. Что было сделано — техники, курс, подход\n"
            "5. Результат — что изменилось и почему\n"
            "6. Вывод для читателя\n"
            "7. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- Реалистично и правдоподобно\n"
            "- Для профессионала точно, для новичка понятно\n"
            "- 2-3 эмодзи\n"
        ),
        "СОВЕТ": (
            f"Напиши профессиональный пост-совет на тему: {topic}\n\n"
            "Структура:\n"
            "1. Цепляющее начало — боль, проблема или вопрос (1-2 предложения)\n"
            "2. Объяснение причины — ТОЛЬКО анатомия относящаяся к теме поста\n"
            "   Давай полное название мышцы: русское + латинское + где находится\n"
            "   Пост про масло или косметику — анатомию не упоминай вообще\n"
            "3. Практическое решение — конкретные техники пошагово\n"
            "4. Предупреждение — когда идти к специалисту\n"
            "5. Хештеги 5-6 штук\n\n"
            "Требования:\n"
            "- 850-900 символов строго\n"
            "- Конкретика: точная локализация, конкретные движения\n"
            "- Для профессионала точно, для новичка понятно\n"
            "- 2-3 эмодзи\n"
            "- ВАЖНО: называй разные мышцы в разных постах, не привязывайся к шее и спине\n"
        ),
    }

    prompt = structures[post_type]

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
                            "Всегда даёшь полные названия мышц: русское + латинское + расположение. "
                            "Гуаша и скребки — инструменты для лица и шеи. "
                            "МФР роллер — для крупных мышц тела до и после тренировок. "
                            "Это разные инструменты — никогда не смешивай их."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            result = msg.choices[0].message.content.strip()
            if not result:
                raise Exception("Модель вернула пустой ответ")
            return result
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
            "пробков": "cork natural product",
            "термальн": "thermal spa portugal",
            "миндальн": "almond oil massage",
            "оливков": "olive oil massage",
            "монои": "monoi oil spa",
            "арган": "argan oil massage",
            "лаванд": "lavender essential oil",
            "мёд": "honey massage spa",
            "гуаша": "gua sha facial tool",
            "роллер": "foam roller muscle",
            "тейп": "kinesiology tape",
            "пистолет": "massage gun device",
            "theragun": "massage gun device",
            "шея": "neck massage",
            "поясниц": "back pain massage",
            "стоп": "foot massage",
            "голеностоп": "ankle rehabilitation",
            "массаж": "massage therapy",
            "плеч": "shoulder massage",
            "спин": "back massage",
            "колен": "knee rehabilitation",
            "рук": "hand massage",
            "осанк": "posture correction",
            "мышц": "muscle anatomy",
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
            "беремен": "pregnancy massage",
            "глаз": "eye relaxation",
            "рубц": "scar tissue massage",
            "лимфедем": "lymphatic drainage",
            "невралг": "nerve pain therapy",
            "обув": "footwear posture",
            "миофасциальн": "myofascial release therapy",
            "головн": "headache relief massage",
            "судорог": "muscle cramp relief",
            "бессонниц": "insomnia relief massage",
            "стресс": "stress relief massage",
            "бруксизм": "jaw tension relief",
            "челюст": "jaw massage therapy",
            "тазобедрен": "hip joint therapy",
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
            "лодыжк": "ankle injury rehabilitation",
            "миф": "massage myths facts",
            "истори": "massage therapy success",
            "кейс": "massage therapy case",
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