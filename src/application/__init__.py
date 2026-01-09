"""
Application Layer - Сервисный слой и конфигурация игры.

Этот модуль содержит:
- GameConfig: Конфигурация игры с категориями и уровнями сложности
- GameService: Основной сервис управления игровой логикой
"""

from src.application.config import GameConfig
from src.application.game_service import GameService

__all__ = ["GameConfig", "GameService"]
