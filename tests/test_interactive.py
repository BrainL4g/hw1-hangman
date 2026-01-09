import pytest
from src.application.game_service import GameService
from src.core.exceptions import CategoryNotFoundError, LevelNotFoundError, NoWordsError
from src.core.entities import GameState, Word
from src.infrastructure.cli_ui import InteractiveCLI, STAGES
from src.infrastructure.storage import FileStorage
from src.application.config import GameConfig


@pytest.fixture
def config():
    return GameConfig()


@pytest.fixture
def storage(config):
    return FileStorage(config)


@pytest.fixture
def service(storage, config):
    ui = InteractiveCLI(config)
    return GameService(storage, ui, config)


@pytest.fixture
def cli(config):
    return InteractiveCLI(config)


@pytest.mark.parametrize(
    "category, level, expected",
    [
        ("животные", "лёгкий", ["кот", "собака", "мышь"]),
        ("invalid", "лёгкий", []),
        ("животные", "invalid", []),
    ],
)
def test_get_words_for_category_level(storage, category, level, expected):
    try:
        words = [
            word.value for word in storage.get_words_for_category_level(category, level)
        ]
        assert words == expected
    except (CategoryNotFoundError, LevelNotFoundError):
        assert expected == []


def test_choose_category_empty_items(cli):
    with pytest.raises(ValueError, match="Нет доступных категорий"):
        cli.choose_category([])


def test_choose_level_empty_items(cli):
    with pytest.raises(ValueError, match="Нет доступных уровней"):
        cli.choose_level([])


@pytest.mark.parametrize(
    "errors, max_attempts, category, level, expected_contains",
    [
        (0, 7, "животные", "лёгкий", "Категория: животные"),
        (3, 7, "животные", "лёгкий", "Неверные буквы: (нет)"),
        (10, 7, "животные", "лёгкий", "Подсказка: Ещё не использована"),
    ],
)
def test_display_game(
    mocker, cli, errors, max_attempts, category, level, expected_contains, capsys
):
    state = GameState(
        word=Word("кот", "маленькое домашнее животное"),
        errors=errors,
        max_attempts=max_attempts,
        guessed_letters=set(),
        game_finished=False,
    )
    cli.display_game(state, category, level, set())
    captured = capsys.readouterr()
    assert expected_contains in captured.out
    assert STAGES[min(errors, len(STAGES) - 1)].strip() in captured.out
