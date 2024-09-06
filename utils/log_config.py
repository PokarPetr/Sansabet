import logging
import sys


logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)-8s %(filename)-20s - str#%(lineno)d - %(message)s',
    level=logging.DEBUG
)


log_methods = {
    "debug": logging.debug,
    "info": logging.info,
    "warning": logging.warning,
    "error": logging.error,
    "critical": logging.critical
}


def log_message(level: str, message: str):
    """
    Логирует сообщение с заданным уровнем логирования.

    :param level: Уровень логирования (например, 'info', 'warning').
    :param message: Сообщение для логирования.
    """

    log_func = log_methods.get(level.lower(), logging.info)

    log_func(message)

