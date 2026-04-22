from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import asyncio
import os
import random


# =========================
# Настройки и данные
# =========================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN не найден. Проверь файл .env")


USERS = ["Молодой", "Славик", "Саня", "Алик"]

WHO_PHRASES = [
    "проиграет катку",
    "красавчик дня",
    "самый ленивый",
    "король доты",
    "лоханётся",
    "тащит игру",
    "идёт в зал (но не факт)",
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


# =========================
# Команды
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "😎 Я здесь.\n\n"
        "Что умею:\n"
        "/start — запуск\n"
        "/help — список команд\n"
        "/who — случайный прикол дня\n"
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
        "/who — кто сегодня кто\n"
        "/play — монетка: играем или не играем\n"
        "/rate <что-то> — оценка чего угодно\n"
        "/luck — твоя удача сегодня",
        do_quote=False,
    )


async def who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    person = random.choice(USERS)
    phrase = random.choice(WHO_PHRASES)

    await update.message.reply_text(
        f"🎯 Сегодня {phrase}: {person}",
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