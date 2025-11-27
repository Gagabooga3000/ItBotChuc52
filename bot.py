"""
Главный файл для запуска Telegram бота
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
from config import BOT_TOKEN, LOG_FILE, LOG_LEVEL
from handlers import (
    start_command, help_command, feedback_command, bug_command, idea_command,
    handle_feedback_type, handle_description, handle_steps, handle_device,
    handle_os, handle_screenshot, handle_problem, handle_advantages,
    handle_rating, cancel, get_main_keyboard,
    WAITING_FOR_TYPE, WAITING_FOR_DESCRIPTION, WAITING_FOR_STEPS,
    WAITING_FOR_DEVICE, WAITING_FOR_OS, WAITING_FOR_SCREENSHOT,
    WAITING_FOR_PROBLEM, WAITING_FOR_ADVANTAGES, WAITING_FOR_RATING
)
from admin import admin_command, admin_callback_handler
from reminders import reminder_loop

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Глобальная переменная для application (нужна для отправки уведомлений)
application = None


def main():
    """Главная функция для запуска бота"""
    global application

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте файл .env")
        return

    # Создание приложения без post_init (из-за проблем с Python 3.14)
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для сбора фидбека
    feedback_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('feedback', feedback_command),
            CommandHandler('bug', bug_command),
            CommandHandler('idea', idea_command),
            MessageHandler(filters.Regex('^(Сообщить об ошибке|Предложить идею|Общий отзыв)$'), handle_feedback_type)
        ],
        states={
            WAITING_FOR_TYPE: [
                MessageHandler(filters.Regex('^(Сообщить об ошибке|Предложить идею|Общий отзыв|Отмена)$'), handle_feedback_type)
            ],
            WAITING_FOR_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description)
            ],
            WAITING_FOR_STEPS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_steps)
            ],
            WAITING_FOR_DEVICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_device)
            ],
            WAITING_FOR_OS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_os)
            ],
            WAITING_FOR_SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_screenshot)
            ],
            WAITING_FOR_PROBLEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_problem)
            ],
            WAITING_FOR_ADVANTAGES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_advantages)
            ],
            WAITING_FOR_RATING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rating)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            MessageHandler(filters.Regex('^Отмена$'), cancel)
        ],
    )

    # Регистрация обработчиков (важно: порядок имеет значение!)
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('admin', admin_command))
    application.add_handler(CallbackQueryHandler(admin_callback_handler))
    application.add_handler(feedback_conv_handler)

    # Обработчик неизвестных команд (должен быть последним)
    async def unknown_command(update: Update, context):
        await update.message.reply_text(
            "❓ Неизвестная команда. Используйте /help для справки.",
            reply_markup=get_main_keyboard()
        )

    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Запуск бота
    logger.info("Бот запущен")
    # Временное отключение напоминаний из-за проблем с Python 3.14
    # Напоминания можно включить позже через другой механизм
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

