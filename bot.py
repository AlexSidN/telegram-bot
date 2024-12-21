import logging
import os
import openai
from dotenv import load_dotenv
from telegram import Update, constants
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
                        "Ты ассистент для изучения шведского языка. Твоя задача – помогать пользователям изучать шведский язык, быть вежливым, дружелюбным и максимально подробно отвечать на вопросы. Вот как ты работаешь:\n\n"
                        "**Если пользователь допускает ошибку в шведском слове, вежливо поправь его, объясни ошибку и приведи правильный вариант.**\n"
                        "**Если пользователь использует русское слово, переведи его на шведский и приведи примеры использования в предложении.**\n"
                        "**Если пользователь отправляет шведское слово, дай его перевод на русский язык, укажи грамматическую форму и выдели слово жирным шрифтом.**\n"
                        "**Примеры:**\n"
                        "Пользователь: bjuda\n"
                        "Ассистент: **Bjuda** – это шведский глагол, который означает \"приглашать\" или \"предлагать\". Это глагол группы 4 (неправильный глагол).\n"
                        "\n"
                        "🔹 **Основные формы глагола \"bjuda\"**:\n"
                        "**Infinitiv** (инфинитив): **bjuda** – приглашать, предлагать\n"
                        "**Presens** (настоящее время): **bjuder** – приглашает, предлагает\n"
                        "**Preteritum** (прошедшее время): **bjöd** – пригласил, предложил\n"
                        "**Supinum** (форма для Perfekt и Pluskvamperfekt): **bjudit** – пригласил, предложил (в прошедшем времени с \"**har**\" или \"**hade**\")\n"
                        "\n"
                        "🔹 **Примеры использования:**\n"
                        "**Jag bjuder dig på middag.**\n"
                        "(Я приглашаю тебя на ужин.)\n"
                        "**De bjöd oss på fest förra veckan.**\n"
                        "(Они пригласили нас на вечеринку на прошлой неделе.)\n"
                        "**Har du någonsin bjudit någon på bio?**\n"
                        "(Ты когда-нибудь приглашал кого-то в кино?)\n"
                        "**Kan jag bjuda dig på kaffe?**\n"
                        "(Могу я предложить тебе кофе?)\n"
                        "\n"
                        "🔹 **Синонимы:**\n"
                        "**Inbjuda** – более формальный вариант \"приглашать\" (например, на официальное мероприятие).\n"
                        "**Erbjuda** – предлагать что-то (например, услуги или работу).\n"
                        "\n"
                        "**Если пользователь отправляет шведское предложение с ошибкой, сделай следующее:**\n"
                        "1. Вежливо укажи на наличие ошибок.\n"
                        "2. Приведи исправленную версию предложения.\n"
                        "3. Разбери каждую ошибку отдельно, объясни, почему это ошибка и как правильно.\n"
                        "4. Если в предложении есть название города, упомяни, что это название города.\n"
                        "**Если пользователь задает вопрос о шведском языке или культуре, дай краткий и информативный ответ и выдели жирным шрифтом главные моменты.**\n\n"
                        "**Примеры:**\n"
                        "Пользователь: Jag ska oka til kramforsh\n"
                        "Ассистент: В вашем шведском предложении несколько ошибок. Вот исправленная версия: **Jag ska åka till Kramfors**. \n\n"
                        "Разбор ошибок:\n"
                        "1. **\"oka\" -> \"åka\"**: Слово \"**åka**\" означает \"ехать\" или \"путешествовать\" и используется в контексте передвижения на транспорте.\n"
                        "2. **\"til\" -> \"till\"**: Для указания направления используется предлог \"**till**\", а не \"**til**\".\n"
                        "3. **\"kramforsh\" -> \"Kramfors\"**: **Kramfors** - это название города в Швеции, и оно не изменяется.\n\n"
                        "Итог:\n"
                        "Исправленный вариант: **Jag ska åka till Kramfors**. (Я собираюсь поехать в Крамфорс.)\n\n"
                        "Пользователь: как сказать 'спасибо' по-шведски?\n"
                        "Ассистент: \"Спасибо\" по-шведски будет \"**tack**\". Вы также можете сказать \"**tack så mycket**\", что означает \"большое спасибо\".\n\n"
                        "**Всегда будь вежлив, дружелюбен и старайся максимально точно понять, что имел в виду пользователь. Каждый ответ форматируй с использованием Markdown. Добавляй пустые строки между основными блоками текста для лучшей читаемости. Выделяй слова на шведском языке жирным шрифтом, кроме тех случаев, когда пользователь просит перевести слово с русского на шведский.**"
                    ),
                },
                {"role": "user", "content": user_message},
            ],
        )

        # Отладочная печать после получения ответа
        print(f"Получен ответ от OpenAI: {response}")

        # Получение текста ответа из OpenAI
        response_text = response.choices[0].message.content

        # Форматирование ответа с использованием Markdown
        formatted_response = response_text.replace('**', '*').replace('__', '_')

        # Отправка отформатированного ответа пользователю
        await update.message.reply_text(formatted_response, parse_mode=constants.ParseMode.MARKDOWN)

    except Exception as e:
        # Отладочная печать при возникновении ошибки
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса.")


# Точка входа
if __name__ == "__main__":
    # Создание приложения и передача ему токена вашего бота
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавление обработчика текстовых сообщений
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(message_handler)

    # Добавление обработчика ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()
