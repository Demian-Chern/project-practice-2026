"""скрипт для локальной проверки окружения перед запуском бота

проверка:
- наличие переменной окружения ТОКЕНА
- наличие файла .env в корне (и чтение оттуда)
- возможность импортировать python-telegram-bot и его версию
"""
import os
from pathlib import Path
import importlib
import importlib.util
import sys


def load_dotenv_if_present(root: Path):
    p = root / ".env"
    if not p.exists():
        return
    print(f"Найден .env: {p}")
    try:
        with p.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)
        print("Загружены переменные из .env (не перезаписываем существующие)")
    except Exception as e:
        print("Ошибка при чтении .env:", e)


def check_bot_token():
    token = os.getenv("BOT_TOKEN")
    if token:
        print("BOT_TOKEN: найден (скрыт)")
    else:
        print("BOT_TOKEN: не найден в окружении. Можно создать файл .env в корне с строкой BOT_TOKEN=<токен> или экспортировать переменную.")


def check_telegram_pkg():
    spec = None
    if hasattr(importlib, "util"):
        spec = importlib.util.find_spec("telegram")
    else:
        spec = None
    if not spec:
        print("python-telegram-bot: НЕ УСТАНОВЛЕН")
        print("Установите: pip install -r requirements.txt")
        return
    try:
        import telegram
        v = getattr(telegram, "__version__", None)
        if not v:
            try:
                from telegram import __version__ as ver
                v = ver
            except Exception:
                v = "?"
        print(f"python-telegram-bot: установлен (версия: {v})")
    except Exception as e:
        print("python-telegram-bot импортируется с ошибкой:", e)


def main():
    root = Path(__file__).resolve().parents[1]
    print("Рабочая директория проекта:", root)
    load_dotenv_if_present(root)
    check_bot_token()
    check_telegram_pkg()

    print("\nЕсли всё в порядке, запустите бота так:\n")
    print("BOT_TOKEN=\"<your-bot-token>\" /usr/local/bin/python3 src/main.py")


if __name__ == "__main__":
    main()
