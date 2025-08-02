"""Простая запись событий в лог."""

import logging


logging.basicConfig(
    filename="poiskmore.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_event(event: str) -> None:
    """Логирует переданное событие."""
    logging.info(event)

