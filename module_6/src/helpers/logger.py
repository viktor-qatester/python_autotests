"""Шаблон логирования проекта.

Формат записи:
[2022-07-19 16:32:46,476] INFO - request: Request was sended,
где request — имя логгера и файла, в который пишется лог.
"""
import logging
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = MODULE_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE_NAME = "request"
LOG_PATH = LOG_DIR / f"{LOG_FILE_NAME}.log"
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s: %(message)s"

logger = logging.getLogger(LOG_FILE_NAME)
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
