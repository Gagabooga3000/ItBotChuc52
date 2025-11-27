"""
Обработчики команд и сообщений бота
"""
import logging
from typing import Dict
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Database

logger = logging.getLogger(__name__)
db = Database()

# Состояния для ConversationHandler
WAITING_FOR_TYPE, WAITING_FOR_DESCRIPTION, WAITING_FOR_STEPS, WAITING_FOR_DEVICE, \
WAITING_FOR_OS, WAITING_FOR_SCREENSHOT, WAITING_FOR_PROBLEM, WAITING_FOR_ADVANTAGES, \
WAITING_FOR_RATING = range(9)

# Типы фидбека
FEEDBACK_TYPES = {
    'bug': 'Сообщить об ошибке',
    'idea': 'Предложить идею',
    'feedback': 'Общий отзыв'
}


def get_main_keyboard():
    """Главная клавиатура"""
    keyboard = [
        ['Сообщить об ошибке', 'Предложить идею'],
        ['Общий отзыв'],
        ['Отмена']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = [['Отмена']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_rating_keyboard():
    """Клавиатура для оценки"""
    keyboard = [
        ['⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
👋 Добро пожаловать в бота для сбора обратной связи о мобильном приложении колледжа!

📱 Этот бот поможет вам:
• Сообщить об ошибках в приложении
• Предложить идеи для улучшения
• Оставить общий отзыв

🔹 Используйте команды:
/feedback - оставить отзыв
/bug - сообщить об ошибке
/idea - предложить идею
/help - помощь по командам

Или используйте кнопки ниже ⬇️
    """
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 Справка по командам:

/start - приветствие и инструкция
/feedback - оставить общий отзыв
/bug - сообщить об ошибке в приложении
/idea - предложить идею для улучшения
/help - эта справка

💡 Процесс отправки фидбека:
1. Выберите тип фидбека
2. Ответьте на вопросы бота
3. Ваш фидбек будет отправлен разработчикам

🔄 В любой момент можно отменить процесс командой /cancel или кнопкой "Отмена"
    """
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /feedback"""
    context.user_data['feedback_type'] = 'feedback'
    await update.message.reply_text(
        "📝 Вы хотите оставить общий отзыв.\n\n"
        "Пожалуйста, опишите ваш отзыв о приложении:",
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_DESCRIPTION


async def bug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /bug"""
    context.user_data['feedback_type'] = 'bug'
    await update.message.reply_text(
        "🐛 Вы хотите сообщить об ошибке.\n\n"
        "Пожалуйста, опишите проблему подробно:",
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_DESCRIPTION


async def idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /idea"""
    context.user_data['feedback_type'] = 'idea'
    await update.message.reply_text(
        "💡 Вы хотите предложить идею.\n\n"
        "Пожалуйста, опишите вашу идею:",
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_DESCRIPTION


async def handle_feedback_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора типа фидбека через кнопки"""
    text = update.message.text

    if text == 'Сообщить об ошибке':
        context.user_data['feedback_type'] = 'bug'
        await update.message.reply_text(
            "🐛 Вы хотите сообщить об ошибке.\n\n"
            "Пожалуйста, опишите проблему подробно:",
            reply_markup=get_cancel_keyboard()
        )
        return WAITING_FOR_DESCRIPTION

    elif text == 'Предложить идею':
        context.user_data['feedback_type'] = 'idea'
        await update.message.reply_text(
            "💡 Вы хотите предложить идею.\n\n"
            "Пожалуйста, опишите вашу идею:",
            reply_markup=get_cancel_keyboard()
        )
        return WAITING_FOR_DESCRIPTION

    elif text == 'Общий отзыв':
        context.user_data['feedback_type'] = 'feedback'
        await update.message.reply_text(
            "📝 Вы хотите оставить общий отзыв.\n\n"
            "Пожалуйста, опишите ваш отзыв о приложении:",
            reply_markup=get_cancel_keyboard()
        )
        return WAITING_FOR_DESCRIPTION

    elif text == 'Отмена':
        await cancel(update, context)
        return ConversationHandler.END


async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик описания"""
    context.user_data['description'] = update.message.text
    feedback_type = context.user_data.get('feedback_type', 'feedback')

    if feedback_type == 'bug':
        await update.message.reply_text(
            "📋 Опишите шаги для воспроизведения ошибки:",
            reply_markup=get_cancel_keyboard()
        )
        return WAITING_FOR_STEPS

    elif feedback_type == 'idea':
        await update.message.reply_text(
            "❓ Какую проблему решает ваша идея?",
            reply_markup=get_cancel_keyboard()
        )
        return WAITING_FOR_PROBLEM

    else:  # feedback
        await update.message.reply_text(
            "⭐ Оцените приложение от 1 до 5 звезд:",
            reply_markup=get_rating_keyboard()
        )
        return WAITING_FOR_RATING


async def handle_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик шагов воспроизведения"""
    context.user_data['steps_to_reproduce'] = update.message.text
    await update.message.reply_text(
        "📱 На каком устройстве возникла проблема?\n"
        "(Например: iPhone 12, Samsung Galaxy S21, Xiaomi Redmi Note 10)",
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_DEVICE


async def handle_device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик информации об устройстве"""
    context.user_data['device_info'] = update.message.text
    await update.message.reply_text(
        "💻 Какая версия операционной системы?\n"
        "(Например: iOS 15.0, Android 12)",
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_OS


async def handle_os(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик версии ОС"""
    context.user_data['os_version'] = update.message.text
    await update.message.reply_text(
        "📸 Можете прикрепить скриншот ошибки? (Отправьте фото или нажмите 'Пропустить')",
        reply_markup=ReplyKeyboardMarkup([['Пропустить', 'Отмена']], resize_keyboard=True)
    )
    return WAITING_FOR_SCREENSHOT


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик скриншота"""
    if update.message.photo:
        # Сохраняем file_id самого большого фото
        photo = update.message.photo[-1]
        context.user_data['screenshot_file_id'] = photo.file_id
        await save_feedback(update, context)
        return ConversationHandler.END
    elif update.message.text == 'Пропустить':
        await save_feedback(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте фото или нажмите 'Пропустить'",
            reply_markup=ReplyKeyboardMarkup([['Пропустить', 'Отмена']], resize_keyboard=True)
        )
        return WAITING_FOR_SCREENSHOT


async def handle_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проблемы для идеи"""
    context.user_data['problem_solved'] = update.message.text
    await update.message.reply_text(
        "✨ Какие преимущества даст реализация этой идеи?",
        reply_markup=get_cancel_keyboard()
    )
    return WAITING_FOR_ADVANTAGES


async def handle_advantages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик преимуществ идеи"""
    context.user_data['advantages'] = update.message.text
    await save_feedback(update, context)
    return ConversationHandler.END


async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик оценки"""
    text = update.message.text
    rating = text.count('⭐')
    
    if 1 <= rating <= 5:
        context.user_data['rating'] = rating
        await save_feedback(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите оценку от 1 до 5 звезд:",
            reply_markup=get_rating_keyboard()
        )
        return WAITING_FOR_RATING


async def save_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение фидбека в базу данных"""
    user_data = context.user_data
    user = update.effective_user

    feedback_type = user_data.get('feedback_type', 'feedback')
    
    feedback_id = db.add_feedback(
        user_id=user.id,
        username=user.username or f"user_{user.id}",
        feedback_type=feedback_type,
        description=user_data.get('description', ''),
        device_info=user_data.get('device_info'),
        app_version=user_data.get('app_version'),
        os_version=user_data.get('os_version'),
        steps_to_reproduce=user_data.get('steps_to_reproduce'),
        problem_solved=user_data.get('problem_solved'),
        advantages=user_data.get('advantages'),
        rating=user_data.get('rating'),
        screenshot_file_id=user_data.get('screenshot_file_id')
    )

    # Отправка уведомления в канал
    from notifications import send_feedback_notification
    await send_feedback_notification(context.bot, feedback_id, user_data)

    # Очистка данных пользователя
    context.user_data.clear()

    # Сообщение пользователю
    await update.message.reply_text(
        "✅ Спасибо! Ваш фидбек успешно отправлен разработчикам.\n\n"
        "Мы обязательно рассмотрим ваше обращение!",
        reply_markup=get_main_keyboard()
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена процесса"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Процесс отменен.",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

