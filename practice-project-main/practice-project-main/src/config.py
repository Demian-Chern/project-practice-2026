import os
from pathlib import Path
import logging


def _load_dotenv(dotenv_path: Path):
    try:
        with dotenv_path.open("r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # не перезаписывае уже заданные переменные окружения
                    os.environ.setdefault(key, val)
    except FileNotFoundError:
        return


def get_bot_token() -> str:
    root = Path(__file__).resolve().parents[1]
    dotenv = root / ".env"
    _load_dotenv(dotenv)

    token = os.getenv("BOT_TOKEN")
    if not token:
        logging.error("BOT_TOKEN не найден в окружении и в .env")
        raise RuntimeError(
            "BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN или создайте файл .env в корне с BOT_TOKEN=..."
        )
    return token
