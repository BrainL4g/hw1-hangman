class HangmanError(Exception):
    """Базовое исключение для игры Виселица."""

    pass


class InvalidWordError(HangmanError):
    """Вызывается при некорректном слове."""

    pass


class InvalidGuessError(HangmanError):
    """Вызывается при некорректном угадывании."""

    pass


class CategoryNotFoundError(HangmanError):
    """Вызывается, когда категория не найдена."""

    pass


class LevelNotFoundError(HangmanError):
    """Вызывается, когда уровень не найден."""

    pass


class NoWordsError(HangmanError):
    """Вызывается, когда нет слов для категории и уровня."""

    pass


class HintAlreadyUsedError(HangmanError):
    """Вызывается при попытке повторного использования подсказки."""

    pass


class StorageError(HangmanError):
    """Ошибки работы с хранилищем."""

    pass


class InvalidInputError(HangmanError):
    """Вызывается при некорректном пользовательском вводе."""

    pass


class GameAlreadyFinishedError(HangmanError):
    """Вызывается, если игра уже завершена."""

    pass


class StatisticsNotFoundError(HangmanError):
    """Вызывается, если статистика игрока не найдена."""

    pass


class InvalidAchievementError(HangmanError):
    """Вызывается при некорректной ачивке."""

    pass


class InvalidScoreError(HangmanError):
    """Вызывается при некорректных очках."""

    pass


class CLIArgumentError(HangmanError):
    """Вызывается при ошибках аргументов командной строки."""

    pass


class InteractiveModeError(HangmanError):
    """Вызывается при ошибках интерактивного режима."""

    pass


class NonInteractiveModeError(HangmanError):
    """Вызывается при ошибках неинтерактивного режима."""

    pass
