import asyncio
import json
from asyncpg import create_pool
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application, ConversationHandler

# Database connection parameters
DB_USER = 'postgres'
DB_PASSWORD = '1234'
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'demo'

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7780146222:AAHHDd-M0mf1ly09tvXwoQ5tHsRtD5K8AOs'

# Создаем подключение к базе данных
async def create_db_pool():
    return await create_pool(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)

# Асинхронно добавляем новый самолет в базу данных
async def add_aircraft_to_db(aircraft_code: str, model: dict, range_: int):
    # Преобразуем словарь модели в строку JSON
    model_json = json.dumps(model)

    pool = await create_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO aircrafts_data(aircraft_code, model, range) VALUES($1, $2, $3)',
            aircraft_code, model_json, range_
        )
    await pool.close()

# Телеграм-бот, отправляющий приветственное сообщение и кнопки
async def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("Добавить новый самолет")]], one_time_keyboard=True
    )
    await update.message.reply_text("Привет! Нажми кнопку ниже, чтобы добавить новый самолет.", reply_markup=reply_markup)
    return WAITING_FOR_ACTION

# Обрабатываем запрос на добавление нового самолета
async def add_aircraft(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите код самолета (например, A320):")
    return WAITING_FOR_AIRCRAFT_CODE

# Получаем код самолета
async def waiting_for_aircraft_code(update: Update, context: CallbackContext):
    context.user_data["aircraft_code"] = update.message.text
    await update.message.reply_text("Теперь введите модель самолета (например, Airbus A320):")
    return WAITING_FOR_MODEL

# Получаем модель самолета
async def waiting_for_model(update: Update, context: CallbackContext):
    # Создаем словарь для модели на разных языках
    context.user_data["model"] = {"en": update.message.text, "ru": "непереведенная модель"}  # Вы можете добавить русскую модель здесь
    await update.message.reply_text("Теперь введите дальность полета (например, 4000 км):")
    return WAITING_FOR_RANGE

# Получаем дальность полета и добавляем данные в базу
async def waiting_for_range(update: Update, context: CallbackContext):
    try:
        range_ = int(update.message.text)
        aircraft_code = context.user_data["aircraft_code"]
        model = context.user_data["model"]

        # Добавляем самолет в базу данных
        await add_aircraft_to_db(aircraft_code, model, range_)

        await update.message.reply_text(f"Самолет {aircraft_code} ({model['en']}) с дальностью {range_} км успешно добавлен!")

        # Очищаем данные
        context.user_data.clear()

        # Отправляем пользователя на старт
        await start(update, context)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для дальности полета.")
        return WAITING_FOR_RANGE

# Обработчики команд и состояний
def main():
    # Вместо Updater, используем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Определяем состояния для ConversationHandler
    global WAITING_FOR_ACTION, WAITING_FOR_AIRCRAFT_CODE, WAITING_FOR_MODEL, WAITING_FOR_RANGE
    WAITING_FOR_ACTION, WAITING_FOR_AIRCRAFT_CODE, WAITING_FOR_MODEL, WAITING_FOR_RANGE = range(4)

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.TEXT & ~filters.COMMAND, add_aircraft)],
        states={
            WAITING_FOR_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_aircraft)],  # Это состояние для ожидания кнопки
            WAITING_FOR_AIRCRAFT_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, waiting_for_aircraft_code)],
            WAITING_FOR_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, waiting_for_model)],
            WAITING_FOR_RANGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, waiting_for_range)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conversation_handler)

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
