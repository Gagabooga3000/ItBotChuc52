"""
Конфигурационный файл для Telegram бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# ID канала для уведомлений (можно использовать @channel_username или ID)
NOTIFICATION_CHANNEL_ID = os.getenv('NOTIFICATION_CHANNEL_ID', '')

# ID админов (список через запятую)
admin_ids_str = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip() and id.strip().isdigit()]

# Настройки базы данных
DATABASE_PATH = 'feedback.db'

# Настройки логирования
LOG_FILE = 'bot.log'
LOG_LEVEL = 'INFO'

# Настройки напоминаний (в часах)
REMINDER_INTERVAL_HOURS = 24  # Напоминать о необработанных отзывах каждые 24 часа

