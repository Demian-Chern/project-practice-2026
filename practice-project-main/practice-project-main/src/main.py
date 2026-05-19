import logging
import random
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# токен у нас в .env файле
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN или запустите: BOT_TOKEN='<token>' /usr/local/bin/python3 src/main.py"
    )

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

user_last_active = {}

quiz_questions = [
    {
        "question": "Какая формула описывает второй закон Ньютона?",
        "options": ["F = ma", "E = mc^2", "F = kx", "P = UI"],
        "correct": 0,
        "explanation": "F = ma — сила равна массе на ускорение."
    },
    {
        "question": "Какая единица измерения силы?",
        "options": ["Ватт", "Ньютон", "Джоуль", "Паскаль"],
        "correct": 1,
        "explanation": "Сила измеряется в ньютонах (Н)."
    },
    {
        "question": "Что такое инерция?",
        "options": ["Свойство тел сохранять скорость", "Падение тел", "Движение по окружности", "Притяжение Земли"],
        "correct": 0,
        "explanation": "Инерция — способность тела сохранять скорость при отсутствии внешних сил."
    }
]

PHYSICS_FACTS = [
    "Скорость света в вакууме — 299 792 458 м/с.",
    "Чёрные дыры испаряются — это открытие Стивена Хокинга.",
    "В холодной воде мы замерзаем быстрее, чем в воздухе при той же температуре.",
    "Квантовая запутанность работает быстрее скорости света (но информация не передаётся).",
    "Протон на 99,999999999999% состоит из пустоты.",
    "Если сжать кусок углерода под давлением 50 000 атмосфер, получится алмаз.",
    "Температура солнечного ядра — около 15 миллионов градусов Цельсия.",
    "Магнитное поле Земля создаёт жидкое железное ядро.",
    "Формула E=mc² означает, что масса и энергия — одно и то же.",
    "Молния может быть в 5 раз горячее поверхности Солнца."
]

async def main_menu(update_or_query, context, is_query=True):
    keyboard = [
        [InlineKeyboardButton("📚 Механика", callback_data="theme_mech")],
        [InlineKeyboardButton("⚡ Электричество", callback_data="theme_elec")],
        [InlineKeyboardButton("🌀 Термодинамика", callback_data="theme_thermo")],
        [InlineKeyboardButton("❓ Викторина", callback_data="quiz_start")],
        [InlineKeyboardButton("📖 Все материалы", callback_data="materials")],
        [InlineKeyboardButton("🔍 Интересный факт", callback_data="fact")],
        [InlineKeyboardButton("🎓 Вопрос из ЕГЭ", callback_data="exam")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Главное меню. Выбери действие:"

    if is_query:
        await update_or_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text(text=text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_last_active[user.id] = datetime.now()
    await main_menu(update, context, is_query=False)

#обработчик нажатий на кнопки - отвечает за навигацию и викторину
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # просто убираем часики, но никакой подсказки не показываем
    user_id = query.from_user.id
    user_last_active[user_id] = datetime.now()
    data = query.data

    back_button = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
    back_markup = InlineKeyboardMarkup(back_button)

    if data == "theme_mech":
        text = "📚 *Механика*\n\nОсновные законы: Ньютон, сохранение импульса, энергия.\nПолезные ссылки:\n- [Кинематика за 10 минут](https://www.youtube.com/watch?v=Eh_3RN7zYB0)\n- [Законы Ньютона — просто](https://www.youtube.com/watch?v=1jSAgHFawxM)\nПрактика: реши задачу про движение с ускорением."
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "theme_elec":
        text = "⚡ *Электричество*\n\nЗакон Ома, мощность, цепи постоянного тока.\nСсылки:\n- [Закон Ома для чайников](https://www.youtube.com/watch?v=57KUxXqyTNE)\n- [Схемы соединения](https://www.youtube.com/watch?v=p1ufHMDZoIY)\nСовет: нарисуй схему — половина дела."
        await query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_markup)

    elif data == "theme_thermo":
        text = "🌀 *Термодинамика*\n\nТемпература, давление, внутренняя энергия.\nПолезное:\n- [Первый закон термодинамики](https://www.youtube.com/watch?v=-ES4mpQk1XM)\n- [Изопроцессы на пальцах](https://www.youtube.com/watch?v=M6LZas6_ptQ)\nЗапомни: Q = ΔU + A"
        await query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_markup)

    elif data == "materials":
        text = "📖 *Все ресурсы проекта*:\n\n🔹 [VK сообщество](https://vk.com/simplephysicsmp)\n🔹 [YouTube](https://youtube.com/@Simplephysics-mpu?si=vUpu2Xtzsi1KuwgK)\n🔹 [РуТуб](https://rutube.ru/channel/43627801)\n🔹 [Telegram канал](https://t.me/simplephysics_polyteh)\n\nСледи за обновлениями!"
        await query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_markup)

    elif data == "fact":
        fact = random.choice(PHYSICS_FACTS)
        text = f"🔬 *Случайный факт о физике:*\n\n{fact}"
        await query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_markup)

    elif data == "exam":
        ege_questions = [
            "Автомобиль разгоняется от 0 до 72 км/ч за 5 с. Найдите ускорение.",
            "Сопротивление проводника 10 Ом, ток 2 А. Какое напряжение?",
            "Чему равна сила тяжести для тела массой 5 кг? (g=10 м/с²)"
        ]
        text = f"🎓 *Пример вопроса из ЕГЭ:*\n\n{random.choice(ege_questions)}\n\nПопробуй решить сам. Ответы и разбор — в нашем VK."
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=back_markup)

    elif data == "main_menu":
        await main_menu(query, context, is_query=True)

    #викторина
    elif data == "quiz_start":
        context.user_data["quiz_score"] = 0
        context.user_data["quiz_index"] = 0
        # отправляем первый вопрос (новым сообщением, чтобы не мешать навигацию)
        await send_quiz_question(query, context)

    elif data.startswith("quiz_answer_"):
        # получаем индекс ответа и текущий вопрос
        parts = data.split("_")
        selected = int(parts[2])
        index = context.user_data.get("quiz_index", 0)
        score = context.user_data.get("quiz_score", 0)

        if index < len(quiz_questions):
            q = quiz_questions[index]
            is_correct = (selected == q["correct"])
            if is_correct:
                score += 1
                context.user_data["quiz_score"] = score
                result_text = f"✅ *Верно!* {q['explanation']}"
            else:
                correct_text = q["options"][q["correct"]]
                result_text = f"❌ *Неверно.* Правильный ответ: {correct_text}. {q['explanation']}"

            # редактирование текста с вопросом
            try:
                await query.edit_message_text(
                    text=f"❓ *Вопрос {index+1}:* {q['question']}\n\n(Уже отвечен)",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass

            # новое сообщение с результатом
            await query.message.reply_text(result_text, parse_mode="Markdown")

            # переход к след вопросу или завершение
            context.user_data["quiz_index"] = index + 1

            if context.user_data["quiz_index"] < len(quiz_questions):
                # следующий вопрос новым сообщением
                await send_quiz_question(query, context)
            else:
                total = len(quiz_questions)
                final_score = context.user_data.get("quiz_score", 0)
                final_text = f"🎉 *Викторина окончена!*\nТвой результат: {final_score} из {total}\nМолодец! Продолжай изучать физику."
                await query.message.reply_text(final_text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_markup)
                # очищение данных викторины
                context.user_data.pop("quiz_index", None)
                context.user_data.pop("quiz_score", None)
        else:
            await query.message.reply_text("Ошибка: вопросы закончились. Начни заново /start")

    else:
        await query.edit_message_text("Неизвестная команда. Попробуй /start", reply_markup=back_markup)

# функция отправки вопроса викторины
async def send_quiz_question(query, context):
    index = context.user_data.get("quiz_index", 0)
    if index >= len(quiz_questions):
        return
    q = quiz_questions[index]
    keyboard = []
    for i, opt in enumerate(q["options"]):
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"quiz_answer_{i}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"❓ *Вопрос {index+1}:* {q['question']}"
    await query.message.reply_text(text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

# ------------------- КОМАНДЫ /materials, /exam -------------------
async def materials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📖 *Все ресурсы проекта*:\n\n🔹 [VK сообщество](https://vk.com/mospolyphysics)\n🔹 [Pinterest](https://pinterest.com/mospolyphysics)\n🔹 [Дзен](https://dzen.ru/mospolyphysics)\n🔹 [Telegram канал](https://t.me/mospolyphysics)"
    await update.message.reply_text(text=text, parse_mode=ParseMode.MARKDOWN)

async def exam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ege_questions = [
        "Автомобиль разгоняется от 0 до 72 км/ч за 5 с. Найдите ускорение.",
        "Сопротивление проводника 10 Ом, ток 2 А. Какое напряжение?",
        "Чему равна сила тяжести для тела массой 5 кг? (g=10 м/с²)"
    ]
    await update.message.reply_text(f"🎓 *Пример вопроса из ЕГЭ:*\n\n{random.choice(ege_questions)}\n\nПопробуй решить сам. Ответы и разбор — в нашем VK.", parse_mode=ParseMode.MARKDOWN)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я не понял команду. Напиши /start")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """команда для проверки, что бот отвечает"""
    await update.message.reply_text("pong")


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    """глобальный обработчик ошибок"""
    logging.exception("Ошибка при обработке обновления:")
    # Пытаемся уведомить пользователя, что произошла ошибка
    try:
        if hasattr(update, "message") and update.message:
            await update.message.reply_text("Произошла ошибка на сервере. Администратор уведомлен!")
    except Exception:
        logging.exception("не удалось отправить сообщение об ошибке пользователю")

# ------------------- ЗАПУСК -------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("materials", materials_command))
    app.add_handler(CommandHandler("exam", exam_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_error_handler(handle_error)

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()