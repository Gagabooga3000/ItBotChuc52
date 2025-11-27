"""
Модуль для напоминаний о необработанных отзывах
"""
import logging
import asyncio
from datetime import datetime
from telegram import Bot
from database import Database
from config import ADMIN_IDS, REMINDER_INTERVAL_HOURS, NOTIFICATION_CHANNEL_ID

logger = logging.getLogger(__name__)
db = Database()


async def send_reminders(bot: Bot):
    """Отправить напоминания о необработанных отзывах"""
    unprocessed = db.get_unprocessed_feedback(hours=REMINDER_INTERVAL_HOURS)

    if not unprocessed:
        logger.info("Нет необработанных отзывов для напоминания")
        return

    high_priority = [fb for fb in unprocessed if fb['priority'] == 'high']
    medium_priority = [fb for fb in unprocessed if fb['priority'] == 'medium']
    normal_priority = [fb for fb in unprocessed if fb['priority'] == 'normal']

    text = "⏰ **Напоминание о необработанных отзывах**\n\n"

    if high_priority:
        text += f"🔴 **Высокий приоритет:** {len(high_priority)}\n"
        for fb in high_priority[:5]:
            text += f"• #{fb['id']} - {fb['description'][:50]}...\n"

    if medium_priority:
        text += f"\n🟡 **Средний приоритет:** {len(medium_priority)}\n"
        for fb in medium_priority[:5]:
            text += f"• #{fb['id']} - {fb['description'][:50]}...\n"

    if normal_priority:
        text += f"\n🟢 **Низкий приоритет:** {len(normal_priority)}\n"
        for fb in normal_priority[:5]:
            text += f"• #{fb['id']} - {fb['description'][:50]}...\n"

    text += f"\nВсего необработанных: {len(unprocessed)}"

    # Отправка админам
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания админу {admin_id}: {e}")

    # Отправка в канал, если настроен
    if NOTIFICATION_CHANNEL_ID:
        try:
            await bot.send_message(
                chat_id=NOTIFICATION_CHANNEL_ID,
                text=text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания в канал: {e}")

    logger.info(f"Отправлены напоминания о {len(unprocessed)} необработанных отзывах")


async def reminder_loop(bot: Bot):
    """Цикл напоминаний"""
    while True:
        try:
            await send_reminders(bot)
            # Ждем указанное количество часов
            await asyncio.sleep(REMINDER_INTERVAL_HOURS * 3600)
        except Exception as e:
            logger.error(f"Ошибка в цикле напоминаний: {e}")
            await asyncio.sleep(3600)  # Ждем час перед повтором

