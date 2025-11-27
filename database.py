"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Получить соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица для фидбека
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                device_info TEXT,
                app_version TEXT,
                os_version TEXT,
                steps_to_reproduce TEXT,
                problem_solved TEXT,
                advantages TEXT,
                rating INTEGER,
                screenshot_file_id TEXT,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица для статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_feedback INTEGER DEFAULT 0,
                bugs_count INTEGER DEFAULT 0,
                ideas_count INTEGER DEFAULT 0,
                feedback_count INTEGER DEFAULT 0,
                avg_rating REAL DEFAULT 0,
                UNIQUE(date)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")

    def add_feedback(self, user_id: int, username: str, feedback_type: str, 
                    description: str, **kwargs) -> int:
        """Добавить новый фидбек"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Определение приоритета для багов
        priority = kwargs.get('priority', 'normal')
        if feedback_type == 'bug':
            # Автоматическое определение приоритета
            critical_keywords = ['критично', 'критическая', 'не работает', 'не запускается', 
                                'вылетает', 'crash', 'critical']
            description_lower = description.lower()
            if any(keyword in description_lower for keyword in critical_keywords):
                priority = 'high'
            elif 'медленно' in description_lower or 'slow' in description_lower:
                priority = 'medium'

        cursor.execute('''
            INSERT INTO feedback 
            (user_id, username, type, description, device_info, app_version, 
             os_version, steps_to_reproduce, problem_solved, advantages, 
             rating, screenshot_file_id, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, username, feedback_type, description,
            kwargs.get('device_info'), kwargs.get('app_version'),
            kwargs.get('os_version'), kwargs.get('steps_to_reproduce'),
            kwargs.get('problem_solved'), kwargs.get('advantages'),
            kwargs.get('rating'), kwargs.get('screenshot_file_id'),
            priority, 'new'
        ))

        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Добавлен фидбек ID {feedback_id} от пользователя {user_id}")
        return feedback_id

    def get_feedback(self, feedback_id: int) -> Optional[Dict]:
        """Получить фидбек по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_feedback(self, feedback_type: Optional[str] = None, 
                        status: Optional[str] = None, 
                        limit: int = 50) -> List[Dict]:
        """Получить все фидбеки с фильтрацией"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM feedback WHERE 1=1'
        params = []

        if feedback_type:
            query += ' AND type = ?'
            params.append(feedback_type)

        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_feedback_status(self, feedback_id: int, status: str) -> bool:
        """Обновить статус фидбека"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE feedback 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, feedback_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        if success:
            logger.info(f"Статус фидбека {feedback_id} обновлен на {status}")
        return success

    def get_statistics(self) -> Dict:
        """Получить статистику"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Общая статистика
        cursor.execute('SELECT COUNT(*) as total FROM feedback')
        total = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE type = ?', ('bug',))
        bugs = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE type = ?', ('idea',))
        ideas = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE type = ?', ('feedback',))
        feedback = cursor.fetchone()['count']

        cursor.execute('SELECT AVG(rating) as avg FROM feedback WHERE rating IS NOT NULL')
        avg_rating = cursor.fetchone()['avg'] or 0

        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE status = ?', ('new',))
        new_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE status = ?', ('in_progress',))
        in_progress_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE status = ?', ('resolved',))
        resolved_count = cursor.fetchone()['count']

        conn.close()

        return {
            'total': total,
            'bugs': bugs,
            'ideas': ideas,
            'feedback': feedback,
            'avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'new': new_count,
            'in_progress': in_progress_count,
            'resolved': resolved_count
        }

    def get_unprocessed_feedback(self, hours: int = 24) -> List[Dict]:
        """Получить необработанные фидбеки за последние N часов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM feedback 
            WHERE status = 'new' 
            AND datetime(created_at) <= datetime('now', '-' || ? || ' hours')
            ORDER BY priority DESC, created_at ASC
        ''', (hours,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_top_issues(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Получить топ проблем по ключевым словам"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT description, COUNT(*) as count 
            FROM feedback 
            WHERE type = 'bug'
            GROUP BY description
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [(row['description'], row['count']) for row in rows]

    def export_to_csv_data(self) -> List[Dict]:
        """Получить все данные для экспорта в CSV"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

