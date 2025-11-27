#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тестовый скрипт для проверки конфигурации"""
from config import BOT_TOKEN, ADMIN_IDS, NOTIFICATION_CHANNEL_ID

print("=" * 50)
print("Проверка конфигурации:")
print("=" * 50)
print(f"BOT_TOKEN: {'✅ Установлен' if BOT_TOKEN else '❌ Не установлен'}")
if BOT_TOKEN:
    print(f"  Длина токена: {len(BOT_TOKEN)} символов")
    print(f"  Начало токена: {BOT_TOKEN[:10]}...")
print(f"ADMIN_IDS: {ADMIN_IDS}")
print(f"NOTIFICATION_CHANNEL_ID: {NOTIFICATION_CHANNEL_ID if NOTIFICATION_CHANNEL_ID else 'Не установлен (можно оставить пустым)'}")
print("=" * 50)

