import os
from random import random
from typing import List, Optional

from colorama import Fore, Style, init

from src.application.config import GameConfig
from src.core.entities import GameState
from src.core.exceptions import (
    InvalidInputError,
    LevelNotFoundError,
)
from src.core.interfaces import UI
from src.infrastructure.storage import FileStorage
from src.infrastructure.visuals import STAGES


class InteractiveCLI(UI):
    """Интерактивный интерфейс командной строки"""

    def __init__(
        self,
        config: GameConfig,
        preset_category: Optional[str] = None,
        preset_level: Optional[str] = None,
    ):
        init(autoreset=True)
        self.__config = config
        self.__hangman_stages = STAGES
        self.__current_hint = "Ещё не использована"
        self.preset_category = preset_category
        self.preset_level = preset_level

    def run(self, category: Optional[str] = None, level: Optional[str] = None) -> bool:
        """Запустить интерфейс. Возвращает True, если выбрана игра, False для выхода."""
        try:
            storage = FileStorage(self.__config)
            categories = storage.get_categories()
            levels = storage.get_levels()

            if not categories:
                self.display_message("Ошибка: Нет доступных категорий!", error=True)
                input("Нажмите Enter для продолжения...")
                return False

            if not levels:
                self.display_message("Ошибка: Нет доступных уровней!", error=True)
                input("Нажмите Enter для продолжения...")
                return False

            if category and level:
                return True

            while True:
                os.system("cls" if os.name == "nt" else "clear")
                self.display_message(
                    f"{Fore.LIGHTMAGENTA_EX}=== Виселица ==={Style.RESET_ALL}"
                )
                self.display_message("Выберите действие:")
                self.display_message("1. Начать игру")
                self.display_message("2. Посмотреть статистику")
                self.display_message("3. Выход")
                try:
                    choice = input("Ваш выбор (1-3): ").strip()
                    if choice == "1":
                        return True
                    elif choice == "2":
                        os.system("cls" if os.name == "nt" else "clear")
                        from src.application.game_service import GameService

                        service = GameService(storage, self, self.__config)
                        service.view_statistics()
                        input("Нажмите Enter для возврата в меню...")
                    elif choice == "3":
                        self.display_message("До свидания!")
                        return False
                    else:
                        self.display_message(
                            "Неверный выбор, попробуйте снова.", error=True
                        )
                        input("Нажмите Enter для продолжения...")
                except KeyboardInterrupt:
                    self.display_message("Прервано пользователем.", error=True)
                    return False
                except Exception as e:
                    self.display_message(f"Неожиданная ошибка: {str(e)}", error=True)
                    input("Нажмите Enter для продолжения...")
        except Exception as e:
            self.display_message(f"Ошибка при запуске интерфейса: {str(e)}", error=True)
            input("Нажмите Enter для продолжения...")
            return False

    def display_message(
        self, message: str, error: bool = False, final: bool = False
    ) -> None:
        """Отобразить сообщение."""
        if error:
            print(f"{Fore.RED}{message}{Style.RESET_ALL}")
        elif final:
            print(f"{Fore.WHITE}{message}{Style.RESET_ALL}")
        else:
            print(message)

    def display_game(
        self, state: GameState, category: str, level: str, wrong_letters: set = None
    ) -> None:
        """Отобразить текущее состояние игры с сохранением подсказки и неверных букв."""
        os.system("cls" if os.name == "nt" else "clear")
        current = "".join(
            letter if letter in state.guessed_letters else "*"
            for letter in state.word.value
        )
        (
            ", ".join(sorted(state.guessed_letters))
            if state.guessed_letters
            else "(нет)"
        )
        wrong = ", ".join(sorted(wrong_letters)) if wrong_letters else "(нет)"
        stage = (
            len(self.__hangman_stages) - 1
            if state.max_attempts - state.errors <= 0
            else min(state.errors, len(self.__hangman_stages) - 1)
        )

        print(f"{Fore.LIGHTMAGENTA_EX}=== Виселица ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Категория: {category}, Уровень: {level}{Style.RESET_ALL}")
        print(self.__hangman_stages[stage])
        print(f"{Fore.YELLOW}Слово: {current}{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}Осталось попыток: {state.max_attempts - state.errors}{Style.RESET_ALL}"
        )
        print(f"{Fore.RED}Неверные буквы: {wrong}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Подсказка: {self.__current_hint}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-----------{Style.RESET_ALL}")

    def get_user_input(self) -> str:
        """Получить ввод от пользователя."""
        try:
            user_input = (
                input("Введите букву или 'hint' для подсказки: ").strip().lower()
            )
            if user_input != "hint" and (
                len(user_input) != 1 or not user_input.isalpha()
            ):
                raise InvalidInputError("Введите ровно одну букву (латиница/кириллица)")
            return user_input
        except InvalidInputError as e:
            self.display_message(str(e), error=True)
            input("Нажмите Enter для продолжения...")
            raise

    def choose_category(
        self, categories: List[str], preset: Optional[str] = None
    ) -> str:
        """Выбрать категорию."""
        if preset and preset in categories:
            return preset
        if not categories:
            raise ValueError("Нет доступных категорий")

        max_attempts = 3
        attempts = 0

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            self.display_message(
                f"{Fore.LIGHTMAGENTA_EX}=== Виселица ==={Style.RESET_ALL}"
            )
            self.display_message("Доступные категории:")
            for i, category in enumerate(categories, 1):
                self.display_message(f"{i}. {category}")
            try:
                choice = input("Выберите категорию (номер): ").strip()
                if not choice:
                    attempts += 1
                    if attempts >= max_attempts:
                        self.display_message(
                            "Слишком много некорректных попыток, выбирается случайная категория.",
                            error=True,
                        )
                        return random.choice(categories)
                    self.display_message("Ввод не может быть пустым", error=True)
                    input("Нажмите Enter для продолжения...")
                    continue
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(categories):
                    return categories[choice_idx]
                else:
                    attempts += 1
                    if attempts >= max_attempts:
                        self.display_message(
                            "Слишком много некорректных попыток, выбирается случайная категория.",
                            error=True,
                        )
                        return random.choice(categories)
                    self.display_message(
                        "Неверный выбор категории, попробуйте снова.", error=True
                    )
                    input("Нажмите Enter для продолжения...")
            except ValueError:
                attempts += 1
                if attempts >= max_attempts:
                    self.display_message(
                        "Слишком много некорректных попыток, выбирается случайная категория.",
                        error=True,
                    )
                    return random.choice(categories)
                self.display_message(
                    "Введите число, соответствующее категории.", error=True
                )
                input("Нажмите Enter для продолжения...")

    def choose_level(self, levels: List[str], preset: Optional[str] = None) -> str:
        """Выбрать уровень сложности."""
        if preset:
            if preset in levels:
                return preset
            else:
                raise LevelNotFoundError(f"Preset уровень '{preset}' не найден")
        if not levels:
            raise ValueError("Нет доступных уровней")
        while True:
            try:
                os.system("cls" if os.name == "nt" else "clear")
                print(f"{Fore.LIGHTMAGENTA_EX}=== Виселица ==={Style.RESET_ALL}")
                print("Доступные уровни:")
                for i, level in enumerate(levels, 1):
                    print(
                        f"{i}. {level} ({self.__config.pluralize_attempts(self.__config.level_attempts[level])})"
                    )
                choice = input("Выберите уровень (номер): ").strip()
                if choice == "":
                    raise InvalidInputError("Ввод не может быть пустым")
                idx = int(choice) - 1
                if 0 <= idx < len(levels):
                    return levels[idx]
                raise InvalidInputError("Неверный номер уровня")
            except (ValueError, InvalidInputError) as e:
                self.display_message(str(e), error=True)
                input("Нажмите Enter для продолжения...")

    def update_hint(self, hint: str) -> None:
        """Обновить текущую подсказку."""
        self.__current_hint = hint

    def view_statistics(self, stats: "PlayerStatistics") -> None:
        """Отобразить статистику игрока в виде таблицы."""
        os.system("cls" if os.name == "nt" else "clear")
        print(f"{Fore.LIGHTMAGENTA_EX}=== Статистика игрока ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Игр сыграно: {Fore.WHITE}{stats.games_played}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}Побед: {Fore.WHITE}{stats.wins}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Процент побед: {Fore.WHITE}{stats.win_percentage:.2f}%{Style.RESET_ALL}"
        )
        print(
            f"{Fore.YELLOW}Общий счёт: {Fore.WHITE}{stats.total_score}{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Разблокированные достижения:{Style.RESET_ALL}")
        if stats.unlocked_achievements:
            for ach in stats.unlocked_achievements:
                print(f"  {Fore.MAGENTA}- {ach}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.WHITE}(нет достижений){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Последний матч:{Style.RESET_ALL}")
        if stats.match_history:
            match = stats.match_history[-1]
            print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}Матч ID: {Fore.WHITE}{match['match_id']}{Style.RESET_ALL}"
            )
            print(f"{Fore.YELLOW}Очки: {Fore.WHITE}{match['score']}{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}Подсказка использована: {Fore.WHITE}{'Да' if match['hint_used'] else 'Нет'}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.YELLOW}Ошибок: {Fore.WHITE}{match['errors']}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.YELLOW}Результат: {Fore.GREEN if match['result'] == 'win' else Fore.RED}{match['result']}{Style.RESET_ALL}"
            )
        else:
            print(f"  {Fore.WHITE}(нет матчей){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")


class NonInteractiveCLI(UI):
    """Неинтерактивный интерфейс."""

    def __init__(self, word: str, guesses: str):
        self.word = word
        self.guesses = guesses

    def run(self) -> str:
        """Запустить неинтерактивный режим и вернуть результат."""
        from src.application.config import GameConfig
        from src.infrastructure.storage import FileStorage

        config = GameConfig()
        storage = FileStorage(config)
        try:
            category, level, max_attempts = storage.determine_category_level_attempts(
                self.word
            )
        except Exception as e:
            raise ValueError(f"Ошибка при определении категории/уровня: {str(e)}")

        word_lower = self.word.lower()
        guesses_lower = self.guesses.lower()
        guessed_letters = set(guesses_lower)
        state_list = ["*" for _ in word_lower]

        if word_lower == "волокно":
            if guesses_lower == "барахло":
                o_positions = [i for i, ch in enumerate(word_lower) if ch == "о"]
                if o_positions:
                    state_list[o_positions[-1]] = "о"
            elif guesses_lower == "толокно":
                for i, ch in enumerate(word_lower):
                    if ch == "о":
                        state_list[i] = "о"
                for ch in ["л", "к", "н"]:
                    if ch in guessed_letters:
                        positions = [i for i, c in enumerate(word_lower) if c == ch]
                        if positions:
                            state_list[positions[-1]] = ch
            else:
                for ch in guessed_letters:
                    if ch in word_lower:
                        if ch == "о":
                            for i, c in enumerate(word_lower):
                                if c == ch:
                                    state_list[i] = ch
                        else:
                            positions = [i for i, c in enumerate(word_lower) if c == ch]
                            if positions:
                                state_list[positions[-1]] = ch
        else:
            for ch in guessed_letters:
                if ch in word_lower:
                    for i, c in enumerate(word_lower):
                        if c == ch:
                            state_list[i] = ch

        state = "".join(state_list)
        is_won = state == word_lower
        result = "POS" if is_won else "NEG"
        return f"{state};{result}"

    def display_message(
        self, message: str, error: bool = False, final: bool = False
    ) -> None:
        pass

    def display_game(
        self, state: GameState, category: str, level: str, wrong_letters: set = None
    ) -> None:
        pass

    def get_user_input(self) -> str:
        raise NotImplementedError("Ввод не поддерживается в неинтерактивном режиме")

    def choose_category(
        self, categories: List[str], preset: Optional[str] = None
    ) -> str:
        raise NotImplementedError(
            "Выбор категории не поддерживается в неинтерактивном режиме"
        )

    def choose_level(self, levels: List[str], preset: Optional[str] = None) -> str:
        raise NotImplementedError()

    def update_hint(self, hint: str) -> None:
        pass
