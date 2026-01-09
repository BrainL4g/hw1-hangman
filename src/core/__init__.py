"""
Core Layer - Основные доменные сущности и интерфейсы игры.

Этот модуль содержит:
- Сущности (Word, GameState, PlayerStatistics, etc.)
- Исключения для обработки ошибок
- Абстрактные интерфейсы (Game, Storage, UI)
- Логику игры (HangmanGame)
"""

from src.core.entities import (
    Word,
    GameState,
    GuessResult,
    Achievement,
    PlayerStatistics,
    MatchStatistics,
)
from src.core.exceptions import (
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
)
from src.core.interfaces import Game, Storage, UI
from src.core.game import HangmanGame

__all__ = [
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
]
