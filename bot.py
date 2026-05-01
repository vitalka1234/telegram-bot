from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from datetime import date
import asyncio
import os
import random
import json


# =========================
# Настройки и данные
# =========================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN не найден. Проверь файл .env")


USERS = ["Молодой", "Славик", "Саня"]

ROLES_FILE = "roles.json"


WHO_ROLES = [
    "👑 король дня",
    "😎 MVP",
    "🔥 главный тащер",
    "🤡 клоун дня",
    "💀 руинер",
    "🛌 AFK-мастер",
    "🎯 снайпер",
    "📉 минус ммр",
    "🧠 стратег, но только в голове",
    "🐒 играет как чувствует",
    "🧊 холодная голова",
    "🚀 надежда команды",
    "🧱 стена команды",
    "🕳 пропасть без вести",
    "🎮 легенда лобби",
]

WHO_EVENTS = [
    "проиграет первую катку",
    "затащит в соло",
    "скажет 'я только одну' и останется до ночи",
    "уйдёт в тильт после первой смерти",
    "будет ныть про тиммейтов",
    "сломает мораль всей команде",
    "включит режим бота",
    "будет играть на рандомном герое",
    "пойдёт не туда и не вернётся",
    "пропадёт на 30 минут без объяснений",
    "будет спорить, но окажется неправ",
    "случайно сделает лучший мув дня",
    "забудет, зачем зашёл в игру",
    "будет говорить 'я не потею', но будет потеть",
    "будет обвинять интернет",
    "выдаст фразу дня",
    "сделает вид, что всё под контролем",
    "начнёт катку уверенно, закончит философией",
    "будет играть так, будто завтра турнир",
    "получит минус мораль, но продолжит",
    "сделает странный билд и будет его защищать",
    "будет просить сейв, когда уже поздно",
    "внезапно станет полезным",
    "будет молчать, а потом резко начнёт командовать",
    "скажет 'последняя' минимум три раза",
]

RARE_WHO_EVENTS = [
    "💀 Сегодня никто не играет. Вселенная против.",
    "🎮 Сегодня все играют. Отмазки не принимаются.",
    "🤡 Сегодня день цирка. Каждый сам за себя.",
    "🧘 Сегодня лучше не играть. Мораль дороже ммр.",
    "🔥 Сегодня день побед. Но это не точно.",
]


RESPONSES = {
    "dota": {
        "triggers": ["дота", "доту", "дотка", "дотку"],
        "answers": [
            "-25 ммр 💀",
            "опять дота? 😭",
            "ну всё понятно...",
            "пошли, я готов 😎",
        ],
    },
    "work": {
        "triggers": ["работа", "работать", "работу", "работе"],
        "answers": [
            "не напоминай 😭",
            "работа не волк 🐺",
            "сегодня выходной",
        ],
    },
    "food": {
        "triggers": ["жрать", "есть", "кушать", "покушать"],
        "answers": [
            "опять? 🍔",
            "ты только что ел 🤨",
            "да сколько можно 😂",
        ],
    },
    "gym": {
        "triggers": ["зал", "тренировка", "качалка"],
        "answers": [
            "легенда 😎",
            "сегодня пропустишь как обычно?",
            "уважаю 💪",
        ],
    },
}


# =========================
# Вспомогательные функции
# =========================

def get_rate_emoji(score: int) -> str:
    if score <= 3:
        return "💀"
    if score <= 6:
        return "😐"
    if score <= 8:
        return "😎"
    return "🔥"


def get_luck_comment(percent: int) -> str:
    if percent <= 20:
        return "сегодня лучше не рисковать 💀"
    if percent <= 50:
        return "так себе, но жить можно 😐"
    if percent <= 80:
        return "день нормальный 😎"
    return "сегодня ты в ударе 🔥"


def load_roles() -> dict:
    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_roles(data: dict) -> None:
    with open(ROLES_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def generate_daily_roles() -> str:
    # редкое событие дня
    if random.randint(1, 100) <= 5:
        return random.choice(RARE_WHO_EVENTS)

    players = USERS.copy()
    roles = WHO_ROLES.copy()

    random.shuffle(players)
    random.shuffle(roles)

    lines = ["🎯 Роли на сегодня:\n"]

    for index, player in enumerate(players):
        role = roles[index % len(roles)]
        event = random.choice(WHO_EVENTS)

        # 30% шанс на второе событие
        if random.randint(1, 100) <= 30:
            second_event = random.choice(WHO_EVENTS)

            while second_event == event:
                second_event = random.choice(WHO_EVENTS)

            line = f"{player} — {role}\n   ↳ {event}\n   ↳ {second_event}"
        else:
            line = f"{player} — {role}\n   ↳ {event}"

        lines.append(line)

    return "\n\n".join(lines)


# =========================
# Команды
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "😎 Я здесь.\n\n"
        "Что умею:\n"
        "/start — запуск\n"
        "/help — список команд\n"
        "/who — роли дня\n"
        "/play — подкинуть монетку: играем или нет\n"
        "/rate <что-то> — оценить что угодно\n"
        "/luck — уровень удачи сегодня",
        do_quote=False,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📌 Команды:\n"
        "/start — запуск\n"
        "/help — помощь\n"
        "/who — роли дня\n"
        "/play — монетка: играем или не играем\n"
        "/rate <что-то> — оценка чего угодно\n"
        "/luck — твоя удача сегодня",
        do_quote=False,
    )


async def who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    today = str(date.today())
    data = load_roles()

    if data.get("date") == today and data.get("text"):
        await update.message.reply_text(
            data["text"],
            do_quote=False,
        )
        return

    text = generate_daily_roles()

    save_roles({
        "date": today,
        "text": text,
    })

    await update.message.reply_text(
        text,
        do_quote=False,
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text(
        "🎲 Ну давай... Подкидываю монетку",
        do_quote=False,
    )

    await asyncio.sleep(3)
    await msg.edit_text("🎲 Подкидываю.")

    await asyncio.sleep(1)
    await msg.edit_text("🎲 Подкидываю..")

    await asyncio.sleep(1)
    await msg.edit_text("🎲 Подкидываю...")

    await asyncio.sleep(1.5)

    result = random.choice(["🎮 ИГРАЕМ 😎", "💀 НЕ ИГРАЕМ 💀"])
    await msg.edit_text(result)


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Напиши, что оценить. Пример: /rate дота",
            do_quote=False,
        )
        return

    target = " ".join(context.args)
    score = random.randint(1, 10)
    emoji = get_rate_emoji(score)

    await update.message.reply_text(
        f"📊 {target} — {score}/10 {emoji}",
        do_quote=False,
    )


async def luck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    percent = random.randint(1, 100)
    comment = get_luck_comment(percent)

    await update.message.reply_text(
        f"🍀 Уровень удачи сегодня: {percent}%\n{comment}",
        do_quote=False,
    )


# =========================
# Автоответы
# =========================

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    if update.message.chat.type == "private":
        return

    text = update.message.text.lower()
    user_name = update.effective_user.first_name or "Брат"
    bot_username = (context.bot.username or "").lower()
    mentioned = f"@{bot_username}" in text if bot_username else False

    for category_data in RESPONSES.values():
        triggers = category_data["triggers"]
        answers = category_data["answers"]

        for trigger in triggers:
            if trigger in text:
                if not mentioned and random.randint(1, 100) > 30:
                    return

                answer = random.choice(answers)

                if mentioned:
                    answer = f"{user_name}, {answer}"

                await update.message.reply_text(
                    answer,
                    do_quote=False,
                )
                return


# =========================
# Запуск
# =========================

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("who", who))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("rate", rate))
    app.add_handler(CommandHandler("luck", luck))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
