from abc import ABC, abstractmethod
from typing import Dict, List

from src.core.entities import GameState, GuessResult, Word


class Game(ABC):
    """Интерфейс игры."""

    @abstractmethod
    def guess(self, letter: str) -> GuessResult:
        """Сделать угадывание буквы."""
        pass

    @abstractmethod
    def get_hint(self) -> str:
        """Получить подсказку."""
        pass

    @abstractmethod
    def state(self) -> GameState:
        """Получить текущее состояние игры."""
        pass


class Storage(ABC):
    """Интерфейс хранилища данных."""

    @abstractmethod
    def get_word(self, category: str, level: str) -> Word:
        """Получить случайное слово для категории и уровня."""
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """Получить список категорий."""
        pass

    @abstractmethod
    def get_levels(self) -> List[str]:
        """Получить список уровней."""
        pass

    @abstractmethod
    def get_words_for_category_level(self, category: str, level: str) -> List[Word]:
        """Получить все слова для категории и уровня."""
        pass

    @abstractmethod
    def save_achievements(self, achievements: Dict) -> None:
        """Сохранить достижения."""
        pass

    @abstractmethod
    def load_achievements(self) -> Dict:
        """Загрузить достижения."""
        pass


class UI(ABC):
    """Интерфейс пользовательского интерфейса."""

    @abstractmethod
    def display_game(self, state: GameState, category: str, level: str) -> None:
        """Отобразить состояние игры."""
        pass

    @abstractmethod
    def get_user_input(self) -> str:
        """Получить ввод от пользователя."""
        pass

    @abstractmethod
    def display_message(self, message: str, error: bool = False) -> None:
        """Отобразить сообщение."""
        pass

    @abstractmethod
    def choose_category(self, categories: List[str]) -> str:
        """Выбрать категорию."""
        pass

    @abstractmethod
    def choose_level(self, levels: List[str]) -> str:
        """Выбрать уровень."""
        pass
