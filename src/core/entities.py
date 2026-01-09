from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(frozen=True)
class Word:
    value: str
    description: str = ""

    def __post_init__(self):
        if not self.value:
            raise ValueError("Слово не может быть пустым")
        if len(self.value) < 2:
            raise ValueError("Слово должно содержать минимум 2 символа")
        if not all(ch.isalpha() for ch in self.value):
            raise ValueError("Слово должно содержать только буквы")


@dataclass(frozen=True)
class GameState:
    word: Word
    guessed_letters: Set[str] = field(default_factory=set)
    errors: int = 0
    max_attempts: int = 6
    game_finished: bool = False

    @property
    def is_won(self) -> bool:
        """Проверяет, выиграна ли игра."""
        return (
            all(letter in self.guessed_letters for letter in self.word.value)
            and not self.game_finished
        )

    @property
    def is_lost(self) -> bool:
        """Проверяет, проиграна ли игра."""
        return self.errors >= self.max_attempts and not self.game_finished


@dataclass(frozen=True)
class GuessResult:
    current_state: str
    is_correct: bool
    is_won: bool
    is_lost: bool
    errors: int
    guessed_letters: Set[str]


@dataclass
class Achievement:
    name: str
    description: str


@dataclass
class PlayerStatistics:
    games_played: int = 0
    wins: int = 0
    total_score: int = 0
    match_history: List[Dict] = field(default_factory=list)
    unlocked_achievements: List[str] = field(default_factory=list)

    @property
    def win_percentage(self) -> float:
        return (self.wins / self.games_played * 100) if self.games_played > 0 else 0.0


@dataclass
class MatchStatistics:
    match_id: str
    score: int
    hint_used: bool
    errors: int
    result: str
