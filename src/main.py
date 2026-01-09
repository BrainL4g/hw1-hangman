"""
Точка входа в приложение Виселица.
"""

import argparse
import sys

from src.application.config import GameConfig
from src.application.game_service import GameService
from src.core.exceptions import (
    CLIArgumentError,
    HangmanError,
    InteractiveModeError,
    NonInteractiveModeError,
    StorageError,
)
from src.infrastructure.cli_ui import InteractiveCLI, NonInteractiveCLI
from src.infrastructure.storage import FileStorage


def create_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Игра Виселица - угадай слово по буквам!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python -m src.main
  python -m src.main кот абв
  python -m src.main --categories
  python -m src.main --levels
  python -m src.main --words животные
  python -m src.main --hint кот
  python -m src.main --stats
        """,
    )

    parser.add_argument("word", nargs="?", help="Слово для неинтерактивной игры")
    parser.add_argument(
        "guesses", nargs="?", help="Буквы для угадывания в неинтерактивной игры"
    )

    parser.add_argument(
        "--categories", action="store_true", help="Показать доступные категории"
    )
    parser.add_argument(
        "--levels", action="store_true", help="Показать уровни сложности"
    )
    parser.add_argument(
        "--words", type=str, metavar="CATEGORY", help="Показать слова в категории"
    )
    parser.add_argument(
        "--hint", type=str, metavar="WORD", help="Показать подсказку для слова"
    )
    parser.add_argument(
        "--check", type=str, metavar="WORD", help="Проверить наличие слова в базе"
    )
    parser.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Предустановленная категория для интерактивной игры",
    )
    parser.add_argument(
        "--level",
        type=str,
        metavar="LEVEL",
        help="Предустановленный уровень для интерактивной игры",
    )
    parser.add_argument(
        "--stats", action="store_true", help="Показать статистику игрока"
    )
    parser.add_argument("--version", action="version", version="Виселица v2.0 (2025)")

    return parser


def handle_non_interactive_mode(
    args: argparse.Namespace, storage: FileStorage, config: GameConfig
) -> None:
    """Обработать неинтерактивный режим."""
    try:
        if args.word and args.guesses:
            if not args.word.strip() or not args.guesses.strip():
                raise CLIArgumentError("Слово и буквы не могут быть пустыми")
            ui = NonInteractiveCLI(args.word, args.guesses)
            output = ui.run()
            print(output)
        elif args.categories:
            print("Доступные категории:")
            categories = storage.get_categories()
            if not categories:
                print("  (нет категорий)")
            for category in categories:
                print(f"  - {category}")
        elif args.levels:
            print("Уровни сложности:")
            if not config.level_attempts:
                print("  (нет уровней)")
            for level, attempts in config.level_attempts.items():
                print(f"  - {level} ({config.pluralize_attempts(attempts)})")
        elif args.words:
            if not args.words.strip():
                raise CLIArgumentError("Категория не может быть пустой")
            print(f"Слова в категории '{args.words}':")
            for level, words in storage.get_words_by_category(args.words):
                word_list = [word.value for word in words]
                print(
                    f"  {level}: {', '.join(word_list) if word_list else '(нет слов)'}"
                )
        elif args.hint:
            if not args.hint.strip():
                raise CLIArgumentError("Требуется слово для подсказки")
            hint = storage.get_hint(args.hint.lower())
            print(f"Подсказка для слова '{args.hint}': {hint}")
        elif args.check:
            if not args.check.strip():
                raise CLIArgumentError("Требуется слово для проверки")
            category, level = storage.check_word(args.check.lower())
            print(
                f"Слово '{args.check}' найдено: категория '{category}', уровень '{level}'"
            )
        else:
            raise CLIArgumentError("Неверные аргументы для неинтерактивного режима")
    except Exception as e:
        raise NonInteractiveModeError(f"Ошибка в неинтерактивном режиме: {e}")


def handle_interactive_mode(args: argparse.Namespace, config: GameConfig) -> None:
    """Обработать интерактивный режим."""
    try:
        storage = FileStorage(config)
        ui = InteractiveCLI(config, args.category, args.level)
        service = GameService(storage, ui, config)
        if ui.run(args.category, args.level):
            service.start_game(args.category, args.level)
            service.play()
    except KeyboardInterrupt:
        print("\nИгра прервана")
    except Exception as e:
        raise InteractiveModeError(f"Ошибка в интерактивном режиме: {e}")


def handle_statistics_mode(args: argparse.Namespace, config: GameConfig) -> None:
    """Обработать режим отображения статистики."""
    try:
        storage = FileStorage(config)
        ui = InteractiveCLI(config)
        service = GameService(storage, ui, config)
        service.view_statistics()
    except Exception as e:
        raise InteractiveModeError(f"Ошибка при отображении статистики: {e}")


def main() -> None:
    """Точка входа приложения."""
    parser = create_parser()
    args = parser.parse_args()
    config = GameConfig()

    try:
        import src
    except ImportError as e:
        print(
            f"Ошибка: Запустите скрипт из корневой папки проекта: {e}", file=sys.stderr
        )
        raise CLIArgumentError("Неверная структура проекта")

    try:
        storage = FileStorage(config)
    except Exception as e:
        raise StorageError(f"Ошибка инициализации хранилища: {e}")

    try:
        if args.stats:
            handle_statistics_mode(args, config)
        elif (
            args.word
            or args.guesses
            or any([args.categories, args.levels, args.words, args.hint, args.check])
        ):
            handle_non_interactive_mode(args, storage, config)
        else:
            handle_interactive_mode(args, config)
    except HangmanError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
