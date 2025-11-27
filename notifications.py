"""
Модуль для отправки уведомлений в канал
"""
import logging
import html
from telegram import Bot
from database import Database
from config import NOTIFICATION_CHANNEL_ID

logger = logging.getLogger(__name__)
db = Database()


async def send_feedback_notification(bot: Bot, feedback_id: int, user_data: dict):
    """Отправить уведомление о новом фидбеке в канал"""
    if not NOTIFICATION_CHANNEL_ID:
        logger.warning("NOTIFICATION_CHANNEL_ID не настроен, уведомления не отправляются")
        return

    feedback = db.get_feedback(feedback_id)
    if not feedback:
        logger.error(f"Фидбек {feedback_id} не найден")
        return

    feedback_type = feedback['type']
    priority_emoji = {
        'high': '🔴',
        'medium': '🟡',
        'normal': '🟢'
    }
    priority = priority_emoji.get(feedback['priority'], '⚪')

    # Функция для экранирования текста для HTML
    def escape_html(text):
        if text is None:
            return 'Не указано'
        text_str = str(text).strip()
        if not text_str:
            return 'Не указано'
        return html.escape(text_str)

    # Формирование сообщения
    if feedback_type == 'bug':
        steps = escape_html(feedback['steps_to_reproduce']) if feedback['steps_to_reproduce'] else 'Не указано'
        device = escape_html(feedback['device_info']) if feedback['device_info'] else 'Не указано'
        os_ver = escape_html(feedback['os_version']) if feedback['os_version'] else 'Не указано'
        
        text = f"""{priority} <b>НОВАЯ ОШИБКА</b> #{feedback_id}

<b>Описание:</b>
{escape_html(feedback['description'])}

<b>Шаги воспроизведения:</b>
{steps}

<b>Устройство:</b> {device}
<b>ОС:</b> {os_ver}

<b>Приоритет:</b> {escape_html(feedback['priority'])}
<b>Пользователь:</b> @{escape_html(feedback['username'])} (ID: {feedback['user_id']})
<b>Дата:</b> {escape_html(feedback['created_at'])}"""

    elif feedback_type == 'idea':
        problem = escape_html(feedback['problem_solved']) if feedback['problem_solved'] else 'Не указано'
        advantages = escape_html(feedback['advantages']) if feedback['advantages'] else 'Не указано'
        
        text = f"""💡 <b>НОВАЯ ИДЕЯ</b> #{feedback_id}

<b>Описание:</b>
{escape_html(feedback['description'])}

<b>Проблема, которую решает:</b>
{problem}

<b>Преимущества:</b>
{advantages}

<b>Пользователь:</b> @{escape_html(feedback['username'])} (ID: {feedback['user_id']})
<b>Дата:</b> {escape_html(feedback['created_at'])}"""

    else:  # feedback
        rating_stars = '⭐' * feedback['rating'] if feedback['rating'] else 'Не указано'
        text = f"""📝 <b>НОВЫЙ ОТЗЫВ</b> #{feedback_id}

<b>Отзыв:</b>
{escape_html(feedback['description'])}

<b>Оценка:</b> {rating_stars}

<b>Пользователь:</b> @{escape_html(feedback['username'])} (ID: {feedback['user_id']})
<b>Дата:</b> {escape_html(feedback['created_at'])}"""

    try:
        message = await bot.send_message(
            chat_id=NOTIFICATION_CHANNEL_ID,
            text=text,
            parse_mode='HTML'
        )

        # Отправка скриншота, если есть
        if feedback['screenshot_file_id']:
            try:
                await bot.send_photo(
                    chat_id=NOTIFICATION_CHANNEL_ID,
                    photo=feedback['screenshot_file_id'],
                    caption=f"Скриншот для фидбека #{feedback_id}",
                    reply_to_message_id=message.message_id
                )
            except Exception as e:
                logger.error(f"Ошибка отправки скриншота: {e}")

        logger.info(f"Уведомление о фидбеке {feedback_id} отправлено в канал")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления в канал: {e}")

