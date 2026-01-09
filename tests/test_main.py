import pytest
from io import StringIO

from src.main import main
from src.application.game_service import GameService
from src.application.config import GameConfig
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


def test_main_help(mocker):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--help"])
    with pytest.raises(SystemExit):
        main()
    output = mock_stdout.getvalue()
    assert "Игра Виселица" in output


def test_main_version(mocker):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--version"])
    with pytest.raises(SystemExit):
        main()
    output = mock_stdout.getvalue()
    assert "Виселица v2.0 (2025)" in output


def test_main_interactive(mocker, service):
    mock_start = mocker.patch("src.application.game_service.GameService.start_game")
    mock_play = mocker.patch("src.application.game_service.GameService.play")
    mock_run = mocker.patch(
        "src.infrastructure.cli_ui.InteractiveCLI.run", return_value=True
    )
    mocker.patch("sys.argv", ["main.py"])
    mocker.patch("builtins.input", side_effect=["3"])
    main()
    mock_start.assert_called_once()
    mock_play.assert_called_once()
    mock_run.assert_called_once()


def test_main_categories(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--categories"])
    main()
    output = mock_stdout.getvalue()
    assert "животные" in output


def test_main_levels(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--levels"])
    main()
    output = mock_stdout.getvalue()
    assert "лёгкий" in output


def test_main_words_valid(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--words", "животные"])
    main()
    output = mock_stdout.getvalue()
    assert "Слова в категории 'животные':" in output


def test_main_words_no_arg(mocker):
    mock_stderr = mocker.patch("sys.stderr", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--words"])
    with pytest.raises(SystemExit):
        main()
    assert "argument --words: expected one argument" in mock_stderr.getvalue()


def test_main_hint_valid(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--hint", "кот"])
    main()
    output = mock_stdout.getvalue()
    assert "маленькое домашнее животное" in output


def test_main_hint_no_arg(mocker):
    mock_stderr = mocker.patch("sys.stderr", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--hint"])
    with pytest.raises(SystemExit):
        main()
    assert "argument --hint: expected one argument" in mock_stderr.getvalue()


def test_main_check_valid(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--check", "кот"])
    main()
    output = mock_stdout.getvalue()
    assert "Слово 'кот' найдено" in output


def test_main_check_no_arg(mocker):
    mock_stderr = mocker.patch("sys.stderr", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--check"])
    with pytest.raises(SystemExit):
        main()
    assert "argument --check: expected one argument" in mock_stderr.getvalue()


def test_main_invalid_args(mocker):
    mock_stderr = mocker.patch("sys.stderr", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "invalid"])
    with pytest.raises(SystemExit):
        main()
    assert "Неверные аргументы для неинтерактивного режима" in mock_stderr.getvalue()


def test_main_unexpected_error(mocker):
    mock_stderr = mocker.patch("sys.stderr", new_callable=StringIO)
    mocker.patch(
        "src.infrastructure.cli_ui.InteractiveCLI.run",
        side_effect=Exception("Test error"),
    )
    mocker.patch("sys.argv", ["main.py"])
    mocker.patch("builtins.input", side_effect=["3"])
    with pytest.raises(SystemExit):
        main()
    assert "Ошибка в интерактивном режиме: Test error" in mock_stderr.getvalue()


def test_main_stats(mocker, service):
    mock_stdout = mocker.patch("sys.stdout", new_callable=StringIO)
    mocker.patch("sys.argv", ["main.py", "--stats"])
    main()
    assert mock_stdout.getvalue().strip()
