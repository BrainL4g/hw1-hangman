from dataclasses import dataclass
from typing import Set

from src.core.entities import Word
from src.core.exceptions import (
    GameAlreadyFinishedError,
    HintAlreadyUsedError,
    InvalidGuessError,
)


@dataclass
class GuessResult:
    current_state: str
    is_correct: bool
    is_won: bool
    is_lost: bool
    errors: int
    guessed_letters: Set[str]


@dataclass
class GameState:
    word: Word
    guessed_letters: Set[str]
    errors: int
    max_attempts: int
    game_finished: bool

    @property
    def is_won(self) -> bool:
        return self.game_finished and self.current_state == self.word.value

    @property
    def is_lost(self) -> bool:
        return self.game_finished and self.errors >= self.max_attempts

    @property
    def current_state(self) -> str:
        return "".join(
            letter if letter.lower() in self.guessed_letters else "*"
            for letter in self.word.value
        )


class HangmanGame:
    def __init__(self, word: Word, max_attempts: int):
        if not word.value:
            raise ValueError("Слово не может быть пустым")
        if len(word.value) < 2:
            raise ValueError("Слово должно содержать минимум 2 символа")
        if not word.value.isalpha():
            raise ValueError("Слово должно содержать только буквы")
        if max_attempts < 1:
            raise ValueError("Количество попыток должно быть больше 0")
        self.word = word
        self.max_attempts = max_attempts
        self.guessed_letters: Set[str] = set()
        self.errors = 0
        self.game_finished = False
        self.hint_used = False

    def guess(self, letter: str) -> GuessResult:
        if self.game_finished:
            raise GameAlreadyFinishedError("Игра уже завершена")
        if not letter:
            raise InvalidGuessError("Неверный ввод: требуется одна буква")
        if len(letter) > 1:
            raise InvalidGuessError("Неверный ввод: требуется одна буква")
        if not letter.isalpha():
            raise InvalidGuessError("Неверный ввод: требуется одна буква")
        letter = letter.lower()
        if letter in self.guessed_letters:
            raise InvalidGuessError("Буква уже была угадана")
        self.guessed_letters.add(letter)
        is_correct = letter in self.word.value.lower()
        if not is_correct:
            self.errors += 1
        current_state = self.state().current_state
        if current_state == self.word.value:
            self.game_finished = True
        elif self.errors >= self.max_attempts:
            self.game_finished = True
        return GuessResult(
            current_state=current_state,
            is_correct=is_correct,
            is_won=self.state().is_won,
            is_lost=self.state().is_lost,
            errors=self.errors,
            guessed_letters=self.guessed_letters.copy(),
        )

    def get_hint(self) -> str:
        if self.game_finished:
            raise GameAlreadyFinishedError("Игра уже завершена")
        if self.hint_used:
            raise HintAlreadyUsedError("Подсказка уже использована")
        self.hint_used = True
        return self.word.description

    def state(self) -> GameState:
        return GameState(
            word=self.word,
            guessed_letters=self.guessed_letters.copy(),
            errors=self.errors,
            max_attempts=self.max_attempts,
            game_finished=self.game_finished,
        )
