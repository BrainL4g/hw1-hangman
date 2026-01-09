import random
from typing import List, Optional, Tuple

from colorama import Fore

from src.application.config import GameConfig
from src.core.entities import (
    Achievement,
    GameState,
    GuessResult,
    MatchStatistics,
    PlayerStatistics,
    Word,
)
from src.core.exceptions import (
    CategoryNotFoundError,
    HintAlreadyUsedError,
    InvalidGuessError,
    InvalidInputError,
    LevelNotFoundError,
)
from src.core.game import HangmanGame
from src.core.interfaces import UI, Game, Storage


class GameService:
    """Сервис для управления игрой."""

    def __init__(self, storage: Storage, ui: UI, config: GameConfig):
        """Инициализация сервиса игры."""
        self.__storage = storage
        self.__ui = ui
        self.__config = config
        self.__game: Optional[Game] = None
        self.__category: Optional[str] = None
        self.__level: Optional[str] = None
        self.__last_result: Optional[GuessResult] = None
        self.__match_id: Optional[str] = None
        self.__errors_count: int = 0
        self.__hint_used: bool = False
        self.__wrong_letters: set = set()
        self.__consecutive_wins: int = 0

    @staticmethod
    def _generate_match_id() -> str:
        """Генерировать 9-значное число из уникальных цифр."""
        digits = list(range(10))
        random.shuffle(digits)
        return "".join(map(str, digits[:9]))

    def start_game(
        self, category: Optional[str] = None, level: Optional[str] = None
    ) -> None:
        """Запустить новую игру."""
        self.__match_id = self._generate_match_id()
        self.__errors_count = 0
        self.__hint_used = False
        self.__wrong_letters = set()

        categories = self.__storage.get_categories()
        self.__category = (
            category
            if category in categories
            else self.__ui.choose_category(categories)
        )
        if self.__category not in self.__config.categories:
            raise CategoryNotFoundError(f"Категория '{self.__category}' не найдена")

        levels = list(self.__config.level_attempts.keys())
        self.__level = level if level in levels else self.__ui.choose_level(levels)
        if self.__level not in self.__config.level_attempts:
            raise LevelNotFoundError(f"Уровень '{self.__level}' не найден")

        random.seed()
        word = self.__storage.get_word(self.__category, self.__level)
        max_attempts = self.__config.level_attempts[self.__level]
        self.__game = HangmanGame(word, max_attempts)

        self.__ui.display_message(
            f"Игра началась: {self.__category}, {self.__level} {self.__config.level_descriptions()[self.__level]}"
        )

    def play(self) -> None:
        """Основной игровой цикл."""
        if not self.__game:
            raise ValueError("Игра не началась")

        while not (
            self.__last_result
            and (self.__last_result.is_won or self.__last_result.is_lost)
        ):
            self.__ui.display_game(
                self.__game.state(), self.__category, self.__level, self.__wrong_letters
            )

            try:
                user_input = self.__ui.get_user_input()
            except InvalidInputError:
                continue

            if user_input.lower() == "hint":
                self.__handle_hint()
                continue

            self.__handle_guess(user_input)

        self.__ui.display_game(
            self.__game.state(), self.__category, self.__level, self.__wrong_letters
        )

        result_message = (
            f"{Fore.GREEN}Вы выиграли!{Fore.RESET}"
            if self.__last_result.is_won
            else f"{Fore.RED}Вы проиграли! Человек повешен!{Fore.RESET}"
        )
        self.__ui.display_message(result_message)
        self.__ui.display_message(
            f"Слово: {self.__game.state().word.value}", final=True
        )

        score = self.__calculate_score()
        self.__ui.display_message(f"Очки за игру: {score}")

        new_achievements = self.__check_achievements()
        if new_achievements:
            self.__ui.display_message("Новые достижения:")
            for ach in new_achievements:
                self.__ui.display_message(f"- {ach.name}: {ach.description}")

        self.__update_statistics(score, self.__last_result.is_won)

    def __handle_hint(self) -> None:
        """Обработать запрос подсказки."""
        try:
            if self.__hint_used:
                raise HintAlreadyUsedError("Подсказка уже использована")
            hint = self.__game.get_hint()
            self.__hint_used = True
            self.__ui.display_message(f"Подсказка: {hint}")
            self.__ui.update_hint(hint)
        except HintAlreadyUsedError as e:
            self.__ui.display_message(str(e), error=True)
            input("Нажмите Enter для продолжения...")
        except Exception as e:
            self.__ui.display_message(
                f"Ошибка при получении подсказки: {str(e)}", error=True
            )
            input("Нажмите Enter для продолжения...")

    def __handle_guess(self, letter: str) -> None:
        """Обработать угадывание буквы."""
        try:
            current_state = self.__game.state()
            if letter in current_state.guessed_letters:
                self.__ui.display_message("Буква уже вводилась.", error=True)
                input("Нажмите Enter для продолжения...")
                return

            self.__last_result = self.__game.guess(letter)
            if not self.__last_result.is_correct:
                self.__errors_count += 1
                self.__wrong_letters.add(letter)
        except InvalidGuessError as e:
            self.__ui.display_message(str(e), error=True)
            input("Нажмите Enter для продолжения...")

    def __calculate_score(self) -> int:
        """Рассчитать очки за игру."""
        if not self.__last_result or not self.__last_result.is_won:
            return 0

        base_score = len(self.__game.state().word.value) * 10
        penalty_errors = self.__errors_count * 5
        penalty_hint = 20 if self.__hint_used else 0
        bonus_perfect = 50 if self.__errors_count == 0 and not self.__hint_used else 0

        score = base_score - penalty_errors - penalty_hint + bonus_perfect
        return max(score, 0)

    def __check_achievements(self) -> List[Achievement]:
        """Проверить и разблокировать новые достижения."""
        achievements = []
        stats: PlayerStatistics = self.__storage.load_achievements()

        if self.__last_result.is_won:
            self.__consecutive_wins += 1
        else:
            self.__consecutive_wins = 0

        if self.__last_result.is_won and not self.__hint_used:
            ach_name = "Без подсказки"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(
                    Achievement(ach_name, "Выиграть без использования подсказки")
                )
                stats.unlocked_achievements.append(ach_name)

        if self.__last_result.is_won and self.__hint_used:
            ach_name = "С подсказкой"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(
                    Achievement(ach_name, "Выиграть используя подсказку")
                )
                stats.unlocked_achievements.append(ach_name)

        if self.__last_result.is_won and self.__errors_count == 0:
            ach_name = "Спидранер"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(Achievement(ach_name, "Выиграть без единой ошибки"))
                stats.unlocked_achievements.append(ach_name)

        if self.__last_result.is_won and stats.wins == 0:
            ach_name = "Новичок"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(Achievement(ach_name, "Первая победа"))
                stats.unlocked_achievements.append(ach_name)

        if self.__last_result.is_won and stats.wins + 1 == 10:
            ach_name = "Профи"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(Achievement(ach_name, "10 побед"))
                stats.unlocked_achievements.append(ach_name)

        if self.__last_result.is_won and stats.wins + 1 == 25:
            ach_name = "Мастер"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(Achievement(ach_name, "25 побед"))
                stats.unlocked_achievements.append(ach_name)

        if self.__consecutive_wins >= 5:
            ach_name = "Серия побед"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(Achievement(ach_name, "5 побед подряд"))
                stats.unlocked_achievements.append(ach_name)

        if self.__consecutive_wins >= 10:
            ach_name = "Упорство"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(Achievement(ach_name, "10 побед подряд"))
                stats.unlocked_achievements.append(ach_name)

        score = self.__calculate_score()
        if score > 100:
            ach_name = "Высокий счёт"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(
                    Achievement(ach_name, "Набрать более 100 очков в одной игре")
                )
                stats.unlocked_achievements.append(ach_name)

        max_attempts = self.__config.level_attempts[self.__level]
        if self.__last_result.is_won and self.__errors_count == max_attempts - 1:
            ach_name = "На грани"
            if ach_name not in stats.unlocked_achievements:
                achievements.append(
                    Achievement(ach_name, "Выиграть с одной оставшейся попыткой")
                )
                stats.unlocked_achievements.append(ach_name)

        self.__storage.save_achievements(stats)
        return achievements

    def __update_statistics(self, score: int, is_win: bool) -> None:
        """Обновить статистику игрока."""
        stats: PlayerStatistics = self.__storage.load_achievements()
        stats.games_played += 1
        if is_win:
            stats.wins += 1
        stats.total_score += score

        match_stats = MatchStatistics(
            match_id=self.__match_id,
            score=score,
            hint_used=self.__hint_used,
            errors=self.__errors_count,
            result="win" if is_win else "loss",
        )
        stats.match_history.append(match_stats.__dict__)

        self.__storage.save_achievements(stats)

    def view_statistics(self) -> None:
        """Отобразить статистику игрока."""
        stats: PlayerStatistics = self.__storage.load_achievements()
        self.__ui.view_statistics(stats)

    @property
    def current_category(self) -> Optional[str]:
        """Получить текущую категорию."""
        return self.__category

    @property
    def current_level(self) -> Optional[str]:
        """Получить текущий уровень."""
        return self.__level

    @property
    def game_state(self) -> Optional[GameState]:
        """Получить состояние текущей игры."""
        return self.__game.state() if self.__game else None

    def list_categories(self) -> List[str]:
        """Список доступных категорий."""
        return self.__storage.get_categories()

    def list_levels(self) -> List[str]:
        """Список доступных уровней."""
        return self.__storage.get_levels()

    def list_words(self, category: str) -> List[Tuple[str, List[Word]]]:
        """Список слов для категории."""
        return self.__storage.get_words_by_category(category)

    def show_hint(self, word: str) -> str:
        """Подсказка для слова."""
        return self.__storage.get_hint(word)

    def check_word(self, word: str) -> Tuple[str, str]:
        """Проверка наличия слова в базе."""
        return self.__storage.check_word(word)
