"""
Hangman Game - Игра "Виселица" с многоуровневой архитектурой.

Пакет реализует игру "Виселица" с поддержкой:
- Интерактивного и неинтерактивного режимов
- Различных категорий и уровней сложности
- Системы статистики и достижений
- Файлового хранения данных

Структура пакета:
    application/   - Сервисный слой и конфигурация
    core/          - Доменные сущности и бизнес-логика
    infrastructure/ - Реализация инфраструктуры (хранилище, UI)
    main.py        - Точка входа приложения
"""

from src.application import GameConfig, GameService
from .core import (
    Word,
    GameState,
    GuessResult,
    Achievement,
    PlayerStatistics,
    MatchStatistics,
    HangmanError,
    InvalidWordError,
    InvalidGuessError,
    CategoryNotFoundError,
    LevelNotFoundError,
    NoWordsError,
    HintAlreadyUsedError,
    StorageError,
    InvalidInputError,
    GameAlreadyFinishedError,
    StatisticsNotFoundError,
    InvalidAchievementError,
    InvalidScoreError,
    CLIArgumentError,
    InteractiveModeError,
    NonInteractiveModeError,
    Game,
    Storage,
    UI,
    HangmanGame,
)
from .infrastructure import FileStorage, InteractiveCLI, NonInteractiveCLI, STAGES

__all__ = [
    "GameConfig",
    "GameService",
    "Word",
    "GameState",
    "GuessResult",
    "Achievement",
    "PlayerStatistics",
    "MatchStatistics",
    "HangmanError",
    "InvalidWordError",
    "InvalidGuessError",
    "CategoryNotFoundError",
    "LevelNotFoundError",
    "NoWordsError",
    "HintAlreadyUsedError",
    "StorageError",
    "InvalidInputError",
    "GameAlreadyFinishedError",
    "StatisticsNotFoundError",
    "InvalidAchievementError",
    "InvalidScoreError",
    "CLIArgumentError",
    "InteractiveModeError",
    "NonInteractiveModeError",
    "Game",
    "Storage",
    "UI",
    "HangmanGame",
    "FileStorage",
    "InteractiveCLI",
    "NonInteractiveCLI",
    "STAGES",
]

__version__ = "0.2.0"
__author__ = "Egor"
__description__ = "Игра 'Виселица' с многоуровневой архитектурой"
