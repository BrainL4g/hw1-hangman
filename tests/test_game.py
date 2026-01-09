import pytest

from src.core.entities import Word
from src.core.exceptions import (
    GameAlreadyFinishedError,
    HintAlreadyUsedError,
    InvalidGuessError,
)
from src.core.game import HangmanGame


@pytest.fixture
def word():
    return Word("кот", "маленькое домашнее животное")


def test_initialization_valid(word):
    game = HangmanGame(word, 7)
    state = game.state()
    assert state.word == word
    assert state.max_attempts == 7
    assert state.errors == 0
    assert state.guessed_letters == set()
    assert not state.game_finished


def test_initialization_word_too_short():
    with pytest.raises(ValueError, match="Слово должно содержать минимум 2 символа"):
        Word("а", "")


def test_initialization_word_nonalpha():
    with pytest.raises(ValueError, match="Слово должно содержать только буквы"):
        Word("кот1", "")


def test_initialization_word_empty():
    with pytest.raises(ValueError, match="Слово не может быть пустым"):
        Word("", "")


def test_guess_valid_letter_correct(word):
    game = HangmanGame(word, 7)
    result = game.guess("к")
    assert result.is_correct
    assert "к" in result.guessed_letters
    assert result.errors == 0
    assert result.current_state == "к**"


def test_guess_valid_letter_incorrect(word):
    game = HangmanGame(word, 7)
    result = game.guess("а")
    assert not result.is_correct
    assert "а" in result.guessed_letters
    assert result.errors == 1
    assert result.current_state == "***"


def test_guess_empty_string(word):
    game = HangmanGame(word, 7)
    with pytest.raises(InvalidGuessError, match="Неверный ввод: требуется одна буква"):
        game.guess("")


def test_guess_multiple_chars(word):
    game = HangmanGame(word, 7)
    with pytest.raises(InvalidGuessError, match="Неверный ввод: требуется одна буква"):
        game.guess("ка")


def test_guess_nonalpha(word):
    game = HangmanGame(word, 7)
    with pytest.raises(InvalidGuessError, match="Неверный ввод: требуется одна буква"):
        game.guess("1")


def test_guess_duplicate(word):
    game = HangmanGame(word, 7)
    game.guess("к")
    with pytest.raises(InvalidGuessError, match="Буква уже была угадана"):
        game.guess("к")


def test_guess_uppercase_converted_to_lower(word):
    game = HangmanGame(word, 7)
    result = game.guess("К")
    assert result.is_correct
    assert "к" in result.guessed_letters
    assert result.current_state == "к**"


def test_guess_after_win(word):
    game = HangmanGame(word, 7)
    game.guess("к")
    game.guess("о")
    game.guess("т")
    with pytest.raises(GameAlreadyFinishedError, match="Игра уже завершена"):
        game.guess("а")


def test_guess_after_loss(word):
    game = HangmanGame(word, 2)
    game.guess("а")
    game.guess("б")
    with pytest.raises(GameAlreadyFinishedError, match="Игра уже завершена"):
        game.guess("в")


def test_get_hint_once(word):
    game = HangmanGame(word, 7)
    hint = game.get_hint()
    assert hint == "маленькое домашнее животное"


def test_get_hint_twice_raises_error(word):
    game = HangmanGame(word, 7)
    game.get_hint()
    with pytest.raises(HintAlreadyUsedError, match="Подсказка уже использована"):
        game.get_hint()


def test_get_hint_after_finish(word):
    game = HangmanGame(word, 7)
    game.guess("к")
    game.guess("о")
    game.guess("т")
    with pytest.raises(GameAlreadyFinishedError, match="Игра уже завершена"):
        game.get_hint()


def test_is_won_true(word):
    game = HangmanGame(word, 7)
    game.guess("к")
    game.guess("о")
    game.guess("т")
    assert game.state().is_won


def test_is_won_false(word):
    game = HangmanGame(word, 7)
    game.guess("к")
    game.guess("о")
    assert not game.state().is_won


def test_is_lost_true(word):
    game = HangmanGame(word, 2)
    game.guess("а")
    game.guess("б")
    assert game.state().is_lost


def test_is_lost_false(word):
    game = HangmanGame(word, 7)
    game.guess("а")
    assert not game.state().is_lost


def test_long_word():
    word = Word("гиппопотам", "крупное водное млекопитающее")
    game = HangmanGame(word, 7)
    result = game.guess("г")
    assert result.current_state == "г*********"
