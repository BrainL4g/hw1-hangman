"""
Infrastructure Layer - Реализация инфраструктурных компонентов.

Этот модуль содержит:
- FileStorage: Файловое хранилище данных
- InteractiveCLI/NonInteractiveCLI: CLI интерфейсы
- STAGES: ASCII визуализации виселицы
"""

from src.infrastructure.storage import FileStorage
from src.infrastructure.cli_ui import InteractiveCLI, NonInteractiveCLI
from src.infrastructure.visuals import STAGES

__all__ = ["FileStorage", "InteractiveCLI", "NonInteractiveCLI", "STAGES"]
