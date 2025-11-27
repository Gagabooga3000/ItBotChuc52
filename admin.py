"""
Админ-панель бота
"""
import logging
import csv
import io
import html
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
db = Database()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id in ADMIN_IDS


async def show_admin_panel(query):
    """Показать админ-панель через callback query"""
    stats = db.get_statistics()

    stats_text = f"""
📊 <b>Статистика фидбека</b>

📈 <b>Общая статистика:</b>
• Всего отзывов: {stats['total']}
• Ошибок: {stats['bugs']}
• Идей: {stats['ideas']}
• Общих отзывов: {stats['feedback']}
• Средняя оценка: {stats['avg_rating']}/5

📋 <b>По статусам:</b>
• Новых: {stats['new']}
• В работе: {stats['in_progress']}
• Решено: {stats['resolved']}

🔹 Используйте кнопки ниже для управления
    """

    keyboard = [
        [
            InlineKeyboardButton("🐛 Ошибки", callback_data="admin_bugs"),
            InlineKeyboardButton("💡 Идеи", callback_data="admin_ideas")
        ],
        [
            InlineKeyboardButton("📝 Отзывы", callback_data="admin_feedback"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("📤 Экспорт CSV", callback_data="admin_export"),
            InlineKeyboardButton("⏰ Необработанные", callback_data="admin_unprocessed")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        stats_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /admin"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
        return

    stats = db.get_statistics()

    stats_text = f"""
📊 <b>Статистика фидбека</b>

📈 <b>Общая статистика:</b>
• Всего отзывов: {stats['total']}
• Ошибок: {stats['bugs']}
• Идей: {stats['ideas']}
• Общих отзывов: {stats['feedback']}
• Средняя оценка: {stats['avg_rating']}/5

📋 <b>По статусам:</b>
• Новых: {stats['new']}
• В работе: {stats['in_progress']}
• Решено: {stats['resolved']}

🔹 Используйте кнопки ниже для управления
    """

    keyboard = [
        [
            InlineKeyboardButton("🐛 Ошибки", callback_data="admin_bugs"),
            InlineKeyboardButton("💡 Идеи", callback_data="admin_ideas")
        ],
        [
            InlineKeyboardButton("📝 Отзывы", callback_data="admin_feedback"),
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("📤 Экспорт CSV", callback_data="admin_export"),
            InlineKeyboardButton("⏰ Необработанные", callback_data="admin_unprocessed")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        stats_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback от админ-кнопок"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
        return

    data = query.data

    if data == "admin_bugs":
        await show_feedback_list(query, 'bug', "🐛 <b>Ошибки:</b>\n\n")

    elif data == "admin_ideas":
        await show_feedback_list(query, 'idea', "💡 <b>Идеи:</b>\n\n")

    elif data == "admin_feedback":
        await show_feedback_list(query, 'feedback', "📝 <b>Отзывы:</b>\n\n")

    elif data == "admin_stats":
        await show_detailed_stats(query)

    elif data == "admin_export":
        await export_to_csv(query, context)

    elif data == "admin_unprocessed":
        await show_unprocessed(query)

    elif data.startswith("view_"):
        feedback_id = int(data.split("_")[1])
        await show_feedback_details(query, feedback_id)

    elif data.startswith("status_"):
        parts = data.split("_")
        feedback_id = int(parts[1])
        new_status = parts[2]
        await change_status(query, feedback_id, new_status)

    elif data == "back_to_admin":
        # Показываем админ-панель через edit_message_text
        await show_admin_panel(query)


async def show_feedback_list(query, feedback_type: str, header: str):
    """Показать список фидбеков определенного типа"""
    feedbacks = db.get_all_feedback(feedback_type=feedback_type, limit=20)

    if not feedbacks:
        await query.edit_message_text(f"{header}Нет отзывов этого типа.")
        return

    def escape_html(text):
        if text is None:
            return 'Не указано'
        return html.escape(str(text))

    text = header
    keyboard = []

    for fb in feedbacks[:10]:  # Показываем первые 10
        status_emoji = {
            'new': '🆕',
            'in_progress': '🔄',
            'resolved': '✅'
        }
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'normal': '🟢'
        }
        emoji = status_emoji.get(fb['status'], '📌')
        priority = priority_emoji.get(fb['priority'], '⚪')
        
        text += f"{emoji} {priority} #{fb['id']} - {escape_html(fb['description'][:50])}...\n"
        keyboard.append([
            InlineKeyboardButton(
                f"#{fb['id']} - {fb['status']}",
                callback_data=f"view_{fb['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def show_feedback_details(query, feedback_id: int):
    """Показать детали фидбека"""
    feedback = db.get_feedback(feedback_id)

    if not feedback:
        await query.answer("Фидбек не найден", show_alert=True)
        return

    status_emoji = {
        'new': '🆕',
        'in_progress': '🔄',
        'resolved': '✅'
    }
    priority_emoji = {
        'high': '🔴 Высокий',
        'medium': '🟡 Средний',
        'normal': '🟢 Низкий'
    }

    def escape_html(text):
        if text is None:
            return 'Не указано'
        return html.escape(str(text))

    text = f"""
{status_emoji.get(feedback['status'], '📌')} <b>Фидбек #{feedback['id']}</b>

<b>Тип:</b> {escape_html(feedback['type'])}
<b>Приоритет:</b> {priority_emoji.get(feedback['priority'], '⚪ Обычный')}
<b>Статус:</b> {escape_html(feedback['status'])}

<b>Описание:</b>
{escape_html(feedback['description'])}
"""

    if feedback['type'] == 'bug':
        if feedback['steps_to_reproduce']:
            text += f"\n<b>Шаги воспроизведения:</b>\n{escape_html(feedback['steps_to_reproduce'])}"
        if feedback['device_info']:
            text += f"\n<b>Устройство:</b> {escape_html(feedback['device_info'])}"
        if feedback['os_version']:
            text += f"\n<b>ОС:</b> {escape_html(feedback['os_version'])}"

    elif feedback['type'] == 'idea':
        if feedback['problem_solved']:
            text += f"\n<b>Проблема:</b> {escape_html(feedback['problem_solved'])}"
        if feedback['advantages']:
            text += f"\n<b>Преимущества:</b> {escape_html(feedback['advantages'])}"

    elif feedback['type'] == 'feedback':
        if feedback['rating']:
            text += f"\n<b>Оценка:</b> {'⭐' * feedback['rating']}"

    text += f"\n\n<b>Пользователь:</b> @{escape_html(feedback['username'])} (ID: {feedback['user_id']})"
    text += f"\n<b>Дата:</b> {escape_html(feedback['created_at'])}"

    keyboard = [
        [
            InlineKeyboardButton("🆕 Новый", callback_data=f"status_{feedback_id}_new"),
            InlineKeyboardButton("🔄 В работе", callback_data=f"status_{feedback_id}_in_progress"),
            InlineKeyboardButton("✅ Решено", callback_data=f"status_{feedback_id}_resolved")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    # Отправка скриншота, если есть
    if feedback['screenshot_file_id']:
        try:
            await query.message.reply_photo(
                feedback['screenshot_file_id'],
                caption=f"Скриншот для фидбека #{feedback_id}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки скриншота: {e}")


async def change_status(query, feedback_id: int, new_status: str):
    """Изменить статус фидбека"""
    success = db.update_feedback_status(feedback_id, new_status)

    if success:
        await query.answer(f"Статус изменен на {new_status}")
        # Уведомление пользователю
        feedback = db.get_feedback(feedback_id)
        if feedback:
            try:
                status_text = {
                    'new': 'новый',
                    'in_progress': 'в работе',
                    'resolved': 'решено'
                }
                await query.bot.send_message(
                    chat_id=feedback['user_id'],
                    text=f"📢 Статус вашего фидбека #{feedback_id} изменен на: {status_text.get(new_status, new_status)}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления пользователю: {e}")

        await show_feedback_details(query, feedback_id)
    else:
        await query.answer("Ошибка изменения статуса", show_alert=True)


async def show_detailed_stats(query):
    """Показать детальную статистику"""
    stats = db.get_statistics()
    top_issues = db.get_top_issues(limit=5)

    def escape_html(text):
        if text is None:
            return 'Не указано'
        return html.escape(str(text))

    text = f"""
📊 <b>Детальная статистика</b>

<b>Общая информация:</b>
• Всего отзывов: {stats['total']}
• Ошибок: {stats['bugs']}
• Идей: {stats['ideas']}
• Общих отзывов: {stats['feedback']}
• Средняя оценка: {stats['avg_rating']}/5

<b>По статусам:</b>
• Новых: {stats['new']}
• В работе: {stats['in_progress']}
• Решено: {stats['resolved']}
"""

    if top_issues:
        text += "\n<b>Топ проблем:</b>\n"
        for i, (issue, count) in enumerate(top_issues, 1):
            text += f"{i}. {escape_html(issue[:50])}... ({count})\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def export_to_csv(query, context: ContextTypes.DEFAULT_TYPE):
    """Экспорт данных в CSV"""
    feedbacks = db.export_to_csv_data()

    if not feedbacks:
        await query.answer("Нет данных для экспорта", show_alert=True)
        return

    # Создание CSV в памяти
    output = io.StringIO()
    fieldnames = ['id', 'user_id', 'username', 'type', 'description', 'device_info',
                  'app_version', 'os_version', 'steps_to_reproduce', 'problem_solved',
                  'advantages', 'rating', 'priority', 'status', 'created_at', 'updated_at']

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for fb in feedbacks:
        row = {field: fb.get(field, '') for field in fieldnames}
        writer.writerow(row)

    csv_data = output.getvalue()
    output.close()

    # Отправка файла
    csv_file = io.BytesIO(csv_data.encode('utf-8-sig'))  # UTF-8 BOM для Excel
    csv_file.name = f"feedback_export_{query.message.date.strftime('%Y%m%d_%H%M%S')}.csv"

    await query.message.reply_document(
        document=csv_file,
        caption="📤 Экспорт данных в CSV"
    )
    await query.answer("Файл отправлен")


async def show_unprocessed(query):
    """Показать необработанные отзывы"""
    feedbacks = db.get_unprocessed_feedback(hours=24)

    if not feedbacks:
        await query.edit_message_text("✅ Все отзывы обработаны!")
        return

    def escape_html(text):
        if text is None:
            return 'Не указано'
        return html.escape(str(text))

    text = f"⏰ <b>Необработанные отзывы (более 24 часов):</b>\n\n"
    keyboard = []

    for fb in feedbacks[:10]:
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'normal': '🟢'
        }
        emoji = priority_emoji.get(fb['priority'], '⚪')
        text += f"{emoji} #{fb['id']} - {escape_html(fb['description'][:50])}...\n"
        keyboard.append([
            InlineKeyboardButton(
                f"#{fb['id']}",
                callback_data=f"view_{fb['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

