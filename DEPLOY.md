# Развертывание бота на сервере

## 🚀 Варианты развертывания

### 1. Railway.app (Рекомендуется - бесплатный тариф)

1. Зарегистрируйтесь на [Railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите GitHub репозиторий или загрузите файлы
4. Добавьте переменные окружения:
   - `BOT_TOKEN` - токен бота
   - `NOTIFICATION_CHANNEL_ID` - ID канала
   - `ADMIN_IDS` - ID админов через запятую
5. Railway автоматически определит Python проект и запустит бота

**Команда запуска:** `python bot.py`

### 2. Render.com (Бесплатный тариф)

1. Зарегистрируйтесь на [Render.com](https://render.com)
2. Создайте новый "Web Service"
3. Подключите репозиторий
4. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Добавьте переменные окружения в разделе Environment

### 3. PythonAnywhere

1. Зарегистрируйтесь на [PythonAnywhere](https://www.pythonanywhere.com)
2. Загрузите файлы через Files
3. Создайте задачу (Task) для запуска бота
4. Настройте переменные окружения

### 4. VPS (Virtual Private Server)

#### Настройка на Linux VPS:

1. Подключитесь к серверу по SSH
2. Установите Python и зависимости:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

3. Клонируйте или загрузите проект:
   ```bash
   git clone <ваш_репозиторий>
   cd TG_BOT
   ```

4. Установите зависимости:
   ```bash
   pip3 install -r requirements.txt
   ```

5. Создайте файл `.env`:
   ```bash
   nano .env
   ```
   Добавьте переменные окружения

6. Используйте `screen` или `tmux` для запуска в фоне:
   ```bash
   # Установка screen
   sudo apt install screen
   
   # Создание сессии
   screen -S telegram_bot
   
   # Запуск бота
   python3 bot.py
   
   # Отключение: Ctrl+A, затем D
   # Подключение обратно: screen -r telegram_bot
   ```

7. Или используйте systemd для автозапуска (см. ниже)

#### Автозапуск через systemd (Linux)

Создайте файл `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Feedback Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/TG_BOT
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/TG_BOT/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активация:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

Проверка статуса:
```bash
sudo systemctl status telegram-bot
```

### 5. Windows Server / ПК (если всегда включен)

#### Автозапуск через планировщик задач:

1. Откройте "Планировщик заданий"
2. Создайте новую задачу:
   - **Триггер:** При входе в систему
   - **Действие:** Запустить программу
   - **Программа:** `python`
   - **Аргументы:** `E:\Все проекты заебательские\TG_BOT\bot.py`
   - **Рабочая папка:** `E:\Все проекты заебательские\TG_BOT`

#### Запуск как служба Windows (требует дополнительных настроек)

Можно использовать NSSM (Non-Sucking Service Manager) для запуска Python скрипта как службы Windows.

## 📝 Важные замечания

1. **Безопасность:**
   - Никогда не коммитьте файл `.env` в Git
   - Используйте переменные окружения на сервере
   - Ограничьте доступ к серверу

2. **Мониторинг:**
   - Настройте логирование
   - Используйте мониторинг процессов (pm2, supervisor)
   - Настройте уведомления об ошибках

3. **Резервное копирование:**
   - Регулярно делайте бэкап базы данных `feedback.db`
   - Храните копии конфигурации

4. **Производительность:**
   - Для большого количества пользователей используйте VPS
   - Бесплатные платформы могут иметь ограничения

## 🔧 Быстрый старт на VPS

```bash
# 1. Подключение к серверу
ssh user@your-server.com

# 2. Установка зависимостей
sudo apt update && sudo apt install -y python3 python3-pip git

# 3. Клонирование проекта
git clone <your-repo-url>
cd TG_BOT

# 4. Установка Python пакетов
pip3 install -r requirements.txt

# 5. Создание .env файла
nano .env
# Добавьте переменные окружения

# 6. Запуск в screen
screen -S bot
python3 bot.py
# Ctrl+A, затем D для отключения

# 7. Проверка работы
screen -r bot
```

## 📊 Рекомендации по выбору

- **Для тестирования:** Railway.app или Render.com (бесплатно)
- **Для продакшена:** VPS (DigitalOcean, Vultr) от $5/месяц
- **Для домашнего использования:** Если ПК всегда включен, используйте автозапуск

