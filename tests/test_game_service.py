import pytest
from io import StringIO
from typing import List, Tuple

from src.application.config import GameConfig
from src.application.game_service import GameService
from src.core.entities import Word
from src.core.exceptions import CategoryNotFoundError, LevelNotFoundError, NoWordsError
from src.infrastructure.storage import FileStorage
from src.infrastructure.cli_ui import InteractiveCLI


@pytest.fixture
def config():
    return GameConfig()


@pytest.fixture
def storage(config):
    return FileStorage(config)


@pytest.fixture
def ui(config):
    return InteractiveCLI(config)


@pytest.fixture
def service(storage, ui, config):
    return GameService(storage, ui, config)


def test_start_game_valid(mocker, service):
    mocker.patch(
        "random.choice", return_value=Word("кот", "маленькое домашнее животное")
    )
    service.start_game("животные", "лёгкий")
    assert service.game_state.word.value == "кот"
    assert service.game_state.max_attempts == 7


def test_start_game_no_words(mocker, service):
    mocker.patch.object(
        service._GameService__storage,
        "get_word",
        side_effect=NoWordsError("Нет слов для категории 'животные' и уровня 'лёгкий'"),
    )
    with pytest.raises(
        NoWordsError, match="Нет слов для категории 'животные' и уровня 'лёгкий'"
    ):
        service.start_game("животные", "лёгкий")


def test_list_categories(service):
    categories = service.list_categories()
    assert "животные" in categories


def test_list_levels(service):
    levels = service.list_levels()
    assert "лёгкий" in levels


def test_list_words_valid(service):
    words = service.list_words("животные")
    assert any(word.value == "кот" for level, word_list in words for word in word_list)


def test_list_words_invalid(service):
    with pytest.raises(CategoryNotFoundError, match="Категория 'bad' не найдена"):
        service.list_words("bad")


def test_show_hint_found(service):
    hint = service.show_hint("кот")
    assert hint == "маленькое домашнее животное"


def test_show_hint_not_found(service):
    hint = service.show_hint("абракадабра")
    assert hint == "Подсказка недоступна"


def test_check_word_found(service):
    category, level = service.check_word("кот")
    assert category == "животные"
    assert level == "лёгкий"


def test_check_word_not_found(service):
    with pytest.raises(NoWordsError, match="Слово 'абракадабра' отсутствует в базе"):
        service.check_word("абракадабра")


def test_view_statistics(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    service.view_statistics()
    assert mock_stdout.getvalue().strip()
