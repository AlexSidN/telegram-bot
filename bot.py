import logging
import os
import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токенов из переменных окружения
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Инициализация OpenAI API
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI(api_key=openai.api_key)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция-обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирует ошибки и отправляет сообщение об ошибке."""
    # Логирование ошибки
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Отправка сообщения об ошибке (необязательно)
    try:
        if update:
            await update.message.reply_text("Произошла ошибка при обработке вашего запроса.")
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {e}")

# Функция для обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения и отправляет их в OpenAI API."""
    user_message = update.message.text
    
    try:
        # Отладочная печать перед отправкой запроса
        print(f"Отправляю запрос в OpenAI: {user_message}")
        
        # Отправка запроса к OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты ассистент для изучения шведского языка. При ответах соблюдай следующие правила:\n\n"
                        
                        "1. При переводе с русского на шведский:\n"
                        "Перевод на шведский:\n\n"
                        "1. Официальный стиль:\n"
                        "**шведская фраза**\n"
                        "(русский перевод)\n"
                        "*пояснение о формальном использовании*\n\n"
                        
                        "2. Дружеский стиль:\n"
                        "**шведская фраза**\n"
                        "(русский перевод)\n"
                        "*пояснение о неформальном использовании*\n\n"
                        
                        "2. При исправлении ошибок в шведской фразе:\n"
                        "**неправильная шведская фраза**\n"
                        "(русский перевод)\n\n"
                        
                        "*Объяснение ошибки*\n\n"
                        
                        "Правильный вариант: **правильная шведская фраза**\n"
                        "(русский перевод)\n\n"
                        
                        "3. При ответе на вопросы о грамматике:\n"
                        "*Начни с краткого объяснения*\n\n"
                        "**примеры на шведском**\n"
                        "(переводы примеров)\n\n"
                        "*дополнительные пояснения*\n\n"
                        
                        "Всегда завершай ответ фразой:\n"
                        "*Если нужно больше пояснений, дайте знать!*"
                    )
                },
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )
        
        # Отладочная печать после получения ответа
        print(f"Получен ответ от OpenAI: {response}")
        
        # Отправка ответа пользователю с поддержкой Markdown
        await update.message.reply_text(
            response.choices[0].message.content,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        # Отладочная печать при возникновении ошибки
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса.")

# Точка входа
if __name__ == "__main__":
    try:
        print("Starting bot...")
        # Создание приложения и передача ему токена вашего бота
        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        print("Application built successfully")
        
        # Добавление обработчика текстовых сообщений
        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        application.add_handler(message_handler)
        
        # Добавление обработчика ошибок
        application.add_error_handler(error_handler)
        
        print("Handlers added, starting polling...")
        # Запуск бота
        application.run_polling()
        
    except Exception as e:
        print(f"Error during initialization: {e}")
