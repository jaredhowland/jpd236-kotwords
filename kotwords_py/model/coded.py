"""Coded puzzle model."""

from __future__ import annotations

import random
from dataclasses import dataclass

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.crossword import Crossword
from kotwords_py.model.puzzle import Cell, CellType, Puzzle, PuzzleType, Word, Coordinate


@dataclass
class Coded(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    grid: list[list[str | None]]
    assignments: list[str]
    givens: list[str]

    def __post_init__(self) -> None:
        super().__init__()
        grid_letters = {ch for row in self.grid for ch in row if ch is not None}
        if grid_letters != set(self.assignments):
            raise ValueError(
                "Set of characters in the grid does not match the set of characters in the assignments"
            )

    async def create_puzzle(self) -> Puzzle:
        assignment_map = {ch: i + 1 for i, ch in enumerate(self.assignments)}
        puzzle_grid = [
            [
                Cell(cell_type=CellType.BLOCK)
                if ch is None
                else Cell(
                    solution=ch,
                    number=str(assignment_map[ch]),
                    hint=ch in self.givens,
                    entry=ch if ch in self.givens else "",
                )
                for ch in row
            ]
            for row in self.grid
        ]

        words: list[Word] = []
        across_word_number = 1
        down_word_number = 1
        for x, y, _, is_across, is_down in Crossword.for_each_cell(puzzle_grid):
            if is_across:
                word: list[Coordinate] = []
                i = x
                while i < len(puzzle_grid[y]) and not puzzle_grid[y][i].cell_type.is_black():
                    word.append(Coordinate(x=i, y=y))
                    i += 1
                words.append(Word(across_word_number, tuple(word)))
                across_word_number += 1
            if is_down:
                word = []
                j = y
                while j < len(puzzle_grid) and not puzzle_grid[j][x].cell_type.is_black():
                    word.append(Coordinate(x=x, y=j))
                    j += 1
                words.append(Word(1000 + down_word_number, tuple(word)))
                down_word_number += 1

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            puzzle_type=PuzzleType.CODED,
            grid=puzzle_grid,
            clues=[],
            words=sorted(words, key=lambda word: word.id),
        )

    @classmethod
    def from_raw_input(
        cls,
        title: str,
        creator: str,
        copyright: str,
        description: str,
        grid: str,
        assignments: str,
        givens: str,
    ) -> "Coded":
        grid_chars = [
            [None if ch == "." else ch for ch in line]
            for line in (line.strip() for line in grid.upper().splitlines())
            if line
        ]
        assignment_list = cls.generate_assignments(grid_chars) if not assignments.strip() else list(assignments.upper())
        return cls(
            title=title,
            creator=creator,
            copyright=copyright,
            description=description,
            grid=grid_chars,
            assignments=assignment_list,
            givens=list(givens),
        )

    @staticmethod
    def generate_assignments(grid: list[list[str | None]]) -> list[str]:
        letters: list[str] = []
        for row in grid:
            for ch in row:
                if ch is not None and ch not in letters:
                    letters.append(ch)
        random.shuffle(letters)
        return letters
