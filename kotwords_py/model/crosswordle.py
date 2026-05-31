"""Crosswordle puzzle model."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.crossword import Crossword
from kotwords_py.model.puzzle import BorderDirection, Cell, Clue, ClueList, Coordinate, Puzzle, Word


class _CellStatus(Enum):
    WHITE = ""
    YELLOW = "#c9b458"
    GREEN = "#6aaa64"


@dataclass
class Crosswordle(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    grid: list[list[str]]
    answer: str
    across_clues: list[str]
    down_clues: list[str]

    def __post_init__(self) -> None:
        super().__init__()
        if not self.grid or any(len(row) != len(self.grid[0]) for row in self.grid):
            raise ValueError("All rows of the grid must have the same length")
        if len(self.grid[0]) != len(self.answer):
            raise ValueError("Answer must have the same length as the grids")
        if len(self.grid) != len(self.across_clues):
            raise ValueError(f"Have {len(self.grid)} rows but {len(self.across_clues)} across clues")
        if len(self.grid[0]) != len(self.down_clues):
            raise ValueError(f"Have {len(self.grid[0])} columns but {len(self.down_clues)} down clues")

    async def create_puzzle(self) -> Puzzle:
        cell_statuses: list[list[_CellStatus]] = []
        for row in self.grid:
            is_used = [self.answer[x] == ch for x, ch in enumerate(row)]
            row_statuses: list[_CellStatus] = []
            for x, ch in enumerate(row):
                if self.answer[x] == ch:
                    row_statuses.append(_CellStatus.GREEN)
                    continue
                first_match = next(
                    (
                        i
                        for i, used in enumerate(is_used)
                        if self.answer[i] == ch and not used
                    ),
                    -1,
                )
                if first_match != -1:
                    is_used[first_match] = True
                    row_statuses.append(_CellStatus.YELLOW)
                else:
                    row_statuses.append(_CellStatus.WHITE)
            cell_statuses.append(row_statuses)

        puzzle_grid = [
            [
                Cell(solution=ch, background_color=cell_statuses[y][x].value)
                for x, ch in enumerate(row)
            ]
            for y, row in enumerate(self.grid)
        ] + [
            [
                Cell(
                    solution=ch,
                    background_color=_CellStatus.GREEN.value,
                    border_directions=frozenset({BorderDirection.TOP}),
                )
                for ch in self.answer
            ]
        ]

        for x, y, clue_number, _, _ in Crossword.for_each_cell(puzzle_grid):
            if clue_number is not None:
                puzzle_grid[y][x] = replace(puzzle_grid[y][x], number=str(clue_number))

        clues = [
            ClueList(
                title="Across",
                clues=tuple(
                    Clue(
                        word_id=y + 1,
                        number=str(1 if y == 0 else y + len(self.grid[0])),
                        text=self.across_clues[y] if y < len(self.across_clues) else "-",
                    )
                    for y in range(len(puzzle_grid))
                ),
            ),
            ClueList(
                title="Down",
                clues=tuple(
                    Clue(
                        word_id=1000 + x + 1,
                        number=str(x + 1),
                        text=self.down_clues[x],
                    )
                    for x in range(len(puzzle_grid[0]))
                ),
            ),
        ]

        words = [
            Word(id=y + 1, cells=tuple(Coordinate(x, y) for x in range(len(row))))
            for y, row in enumerate(puzzle_grid)
        ] + [
            Word(
                id=1000 + x + 1,
                cells=tuple(Coordinate(x, y) for y in range(len(puzzle_grid) - 1)),
            )
            for x in range(len(puzzle_grid[0]))
        ]

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=puzzle_grid,
            clues=clues,
            words=words,
        )
