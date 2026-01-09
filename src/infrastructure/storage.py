import json
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.application.config import GameConfig
from src.core.entities import PlayerStatistics, Word
from src.core.exceptions import (
    CategoryNotFoundError,
    LevelNotFoundError,
    NoWordsError,
    StorageError,
)
from src.core.interfaces import Storage


@dataclass
class FileStorage(Storage):
    """Хранилище слов и достижений на основе файлов."""

    config: GameConfig

    def load_words(self) -> Dict[str, Dict[str, List[Word]]]:
        """Получить слова из конфигурации."""
        if not self.config.categories:
            raise StorageError("Конфигурация не содержит слов")
        return self.config.categories

    def load_achievements(self) -> PlayerStatistics:
        """Загрузить статистику и достижения игрока."""
        try:
            file_path = os.path.join(
                os.path.dirname(__file__), "player_statistics.json"
            )
            if not os.path.exists(file_path):
                default_stats = PlayerStatistics()
                self.save_achievements(default_stats)
                return default_stats
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PlayerStatistics(
                games_played=data.get("games_played", 0),
                wins=data.get("wins", 0),
                total_score=data.get("total_score", 0),
                unlocked_achievements=data.get("unlocked_achievements", []),
                match_history=data.get("match_history", []),
            )
        except (FileNotFoundError, json.JSONDecodeError):
            raise StorageError("Ошибка чтения статистики из 'player_statistics.json'")

    def save_achievements(self, stats: PlayerStatistics) -> None:
        """Сохранить статистику и достижения игрока."""
        try:
            file_path = os.path.join(
                os.path.dirname(__file__), "player_statistics.json"
            )
            data = {
                "games_played": stats.games_played,
                "wins": stats.wins,
                "total_score": stats.total_score,
                "unlocked_achievements": stats.unlocked_achievements,
                "match_history": stats.match_history,
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            raise StorageError("Ошибка записи статистики в 'player_statistics.json'")

    def get_categories(self) -> List[str]:
        """Получить список категорий."""
        return list(self.load_words().keys())

    def get_levels(self) -> List[str]:
        """Получить список доступных уровней."""
        words = self.load_words()
        levels = set()
        for category in words:
            levels.update(words[category].keys())
        return sorted(list(levels))

    def get_word(self, category: str, level: str) -> Word:
        """Получить случайное слово для категории и уровня."""
        words = self.load_words()
        if category not in words:
            raise CategoryNotFoundError(f"Категория '{category}' не найдена")
        if level not in words[category]:
            raise LevelNotFoundError(f"Уровень '{level}' не найден")
        word_list = words[category][level]
        if not word_list:
            raise NoWordsError(
                f"Нет слов для категории '{category}' и уровня '{level}'"
            )
        return random.choice(word_list)

    def get_words_by_category(self, category: str) -> List[Tuple[str, List[Word]]]:
        """Получить слова по категории."""
        words = self.load_words()
        if category not in words:
            raise CategoryNotFoundError(f"Категория '{category}' не найдена")
        return [(level, word_list) for level, word_list in words[category].items()]

    def get_words_for_category_level(self, category: str, level: str) -> List[Word]:
        """Получить все слова для категории и уровня."""
        words = self.load_words()
        if category not in words:
            raise CategoryNotFoundError(f"Категория '{category}' не найдена")
        if level not in words[category]:
            raise LevelNotFoundError(f"Уровень '{level}' не найден")
        return words[category][level]

    def get_hint(self, word: str) -> str:
        """Получить подсказку для слова."""
        return self.config.hints.get(word.lower(), "Подсказка недоступна")

    def check_word(self, word: str) -> Tuple[str, str]:
        """Проверить наличие слова в базе."""
        words = self.load_words()
        for category, levels in words.items():
            for level, word_list in levels.items():
                for w in word_list:
                    if w.value == word.lower():
                        return category, level
        raise NoWordsError(f"Слово '{word}' отсутствует в базе")

    def determine_category_level_attempts(self, word: str) -> Tuple[str, str, int]:
        """Определить категорию, уровень и попытки для слова."""
        try:
            category, level = self.check_word(word)
            return category, level, self.config.level_attempts.get(level, 6)
        except NoWordsError:
            return "внешнее", "внешнее", 6
