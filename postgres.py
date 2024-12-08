import asyncio
from asyncpg import create_pool
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application, ConversationHandler
import json

# Параметры подключения к базе данных
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'demo'

# Токен Telegram-бота
TELEGRAM_BOT_TOKEN = '7780146222:AAHHDd-M0mf1ly09tvXwoQ5tHsRtD5K8AOs'

# Создание подключения к базе данных
async def create_db_pool():
    return await create_pool(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)

# Добавление самолета в базу данных
async def add_aircraft_to_db(aircraft_code: str, model: str, range_: int):
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        # Преобразуем model в валидный JSON
        model_json = json.dumps({"model": model})

        # Вставляем в базу данных
        await conn.execute(
            'INSERT INTO aircrafts_data(aircraft_code, model, range) VALUES($1, $2::jsonb, $3)',
            aircraft_code, model_json, range_
        )
    await pool.close()

# Получение всех самолетов из базы данных
async def fetch_all_aircrafts():
    pool = await create_db_pool()
    async with pool.acquire() as conn:
        result = await conn.fetch('SELECT aircraft_code, model, range FROM aircrafts_data')
    await pool.close()
    return result

# Начальное приветственное сообщение
async def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Добавить новый самолет")],
            [KeyboardButton("Показать все самолеты")]
        ], one_time_keyboard=True
    )
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=reply_markup)
    return 1  # Переходим к следующему шагу

# Обработка нажатия кнопки "Добавить новый самолет"
async def add_aircraft(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите код самолета (например, A320):")
    return 2  # Переходим к ожиданию кода самолета

# Получение и сохранение кода самолета
async def waiting_for_aircraft_code(update: Update, context: CallbackContext):
    context.user_data["aircraft_code"] = update.message.text
    await update.message.reply_text("Введите модель самолета:")
    return 3  # Переходим к ожиданию модели

# Получение и сохранение модели самолета
async def waiting_for_model(update: Update, context: CallbackContext):
    context.user_data["model"] = update.message.text
    await update.message.reply_text("Введите дальность полета (км):")
    return 4  # Переходим к ожиданию дальности полета

# Получение дальности полета и добавление самолета в базу данных
async def waiting_for_range(update: Update, context: CallbackContext):
    try:
        range_ = int(update.message.text)
        aircraft_code = context.user_data["aircraft_code"]
        model = context.user_data["model"]

        await add_aircraft_to_db(aircraft_code, model, range_)
        await update.message.reply_text(f"Самолет {aircraft_code} ({model}) с дальностью {range_} км добавлен!")

        context.user_data.clear()  # Очищаем данные
        return await start(update, context)  # Возвращаемся на старт

    except ValueError:
        await update.message.reply_text("Введите корректную дальность (число).")
        return 4  # Если ошибка, снова ждем дальность

# Вывод всех самолетов из базы
async def show_all_aircrafts(update: Update, context: CallbackContext):
    aircrafts = await fetch_all_aircrafts()
    if aircrafts:
        message = '\n'.join([f"Код: {row['aircraft_code']}, Модель: {row['model']}, Дальность: {row['range']} км" for row in aircrafts])
    else:
        message = "Самолеты не найдены."
    await update.message.reply_text(message)

# Обработка кнопок (добавить или показать)
async def handle_button_press(update: Update, context: CallbackContext):
    if update.message.text == "Добавить новый самолет":
        return await add_aircraft(update, context)
    elif update.message.text == "Показать все самолеты":
        return await show_all_aircrafts(update, context)

# Основная функция
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT, handle_button_press)],
            2: [MessageHandler(filters.TEXT, waiting_for_aircraft_code)],
            3: [MessageHandler(filters.TEXT, waiting_for_model)],
            4: [MessageHandler(filters.TEXT, waiting_for_range)],
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
