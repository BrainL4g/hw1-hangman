import pytest

from src.application.config import GameConfig
from src.application.game_service import GameService
from src.core.entities import Word
from src.core.exceptions import CategoryNotFoundError, NoWordsError
from src.infrastructure.cli_ui import NonInteractiveCLI
from src.infrastructure.storage import FileStorage


@pytest.fixture
def config():
    return GameConfig()


@pytest.fixture
def storage(config):
    return FileStorage(config)


@pytest.fixture
def service(storage, config):
    return GameService(storage, None, config)


def test_determine_category_level_attempts_found(storage):
    cat, lvl, attempts = storage.determine_category_level_attempts("кот")
    assert cat == "животные"
    assert lvl == "лёгкий"
    assert attempts == 7


def test_determine_category_level_attempts_not_found(storage):
    cat, lvl, attempts = storage.determine_category_level_attempts("абракадабра")
    assert cat == "внешнее"
    assert lvl == "внешнее"
    assert attempts == 6


def test_determine_category_level_attempts_empty_word(storage):
    cat, lvl, attempts = storage.determine_category_level_attempts("")
    assert cat == "внешнее"
    assert lvl == "внешнее"
    assert attempts == 6


def test_run_valid_game_win():
    cli = NonInteractiveCLI("кот", "кот")
    output = cli.run()
    assert output == "кот;POS"


def test_run_valid_game_loss():
    cli = NonInteractiveCLI("кот", "абвгдеё")
    output = cli.run()
    assert output == "***;NEG"


def test_run_duplicate_guesses_ignored():
    cli = NonInteractiveCLI("кот", "кккот")
    output = cli.run()
    assert output == "кот;POS"


def test_run_with_invalid_guesses_and_duplicates():
    cli = NonInteractiveCLI("кот", "к11от")
    output = cli.run()
    assert output == "кот;POS"


def test_run_with_empty_guesses():
    cli = NonInteractiveCLI("кот", "")
    output = cli.run()
    assert output == "***;NEG"


def test_list_categories(service):
    categories = service.list_categories()
    assert "животные" in categories


def test_list_levels(service):
    levels = service.list_levels()
    assert "лёгкий" in levels


def test_list_levels_empty(mocker, service):
    mocker.patch.object(service, "list_levels", return_value=[])
    levels = service.list_levels()
    assert not levels


def test_list_words_valid_category(service):
    words_by_level = service.list_words("животные")
    assert any(
        word.value == "кот" for level, word_list in words_by_level for word in word_list
    )


def test_list_words_invalid_category(service):
    with pytest.raises(
        CategoryNotFoundError, match="Категория 'несуществующая_категория' не найдена"
    ):
        service.list_words("несуществующая_категория")


def test_show_hint_found(service):
    hint = service.show_hint("кот")
    assert "маленькое домашнее животное" in hint


def test_show_hint_not_found(service):
    hint = service.show_hint("абракадабра")
    assert hint == "Подсказка недоступна"


def test_check_word_found(service):
    category, level = service.check_word("кот")
    assert "животные" == category


def test_check_word_not_found(service):
    with pytest.raises(NoWordsError, match="Слово 'абракадабра' отсутствует в базе"):
        service.check_word("абракадабра")


def test_run_with_spaces_in_guesses():
    cli = NonInteractiveCLI("кот", "к о т")
    output = cli.run()
    assert output == "кот;POS"
