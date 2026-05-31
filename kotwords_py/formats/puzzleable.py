"""Base puzzle conversion abstraction for the Python migration scaffold."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from kotwords_py.model.puzzle import Puzzle


class InvalidFormatError(Exception):
    """Exception raised when puzzle input is in an invalid format."""


class Puzzleable(ABC):
    """Base class for data that can be parsed as a Puzzle."""

    def __init__(self) -> None:
        self._cached_puzzle: Optional["Puzzle"] = None
        self._cached_puzzle_lock = asyncio.Lock()

    async def as_puzzle(self) -> "Puzzle":
        """Parse and return data as a Puzzle, caching the result."""
        async with self._cached_puzzle_lock:
            if self._cached_puzzle is None:
                self._cached_puzzle = await self.create_puzzle()
            return self._cached_puzzle

    @abstractmethod
    async def create_puzzle(self) -> "Puzzle":
        """Parse and return data as a Puzzle."""
        raise NotImplementedError
