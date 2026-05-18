"""
Настройки только для локальной разработки (DEBUG).
Production-конфигурация намеренно не включена.
"""
from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
