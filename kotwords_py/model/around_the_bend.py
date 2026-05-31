"""Around the Bend puzzle model."""

from __future__ import annotations

from dataclasses import dataclass

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import Cell, CellType, Clue, ClueList, Coordinate, Puzzle, Word


@dataclass
class AroundTheBend(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    rows: list[str]
    clues: list[str]

    def __post_init__(self) -> None:
        super().__init__()

    async def create_puzzle(self) -> Puzzle:
        max_width = max(len(row) for row in self.rows)
        grid: list[list[Cell]] = []
        for y, row in enumerate(self.rows):
            padding = max_width - len(row)
            padded_cells = [Cell(cell_type=CellType.BLOCK) for _ in range(padding)]
            row_cells = [
                Cell(solution=ch, number=str(y + 1) if i == 0 else "")
                for i, ch in enumerate(row)
            ]
            grid.append(padded_cells + row_cells)

        puzzle_clues: list[Clue] = []
        puzzle_words: list[Word] = []
        for y, clue in enumerate(self.clues):
            next_y = (y + 1) % len(grid)
            first_half = [
                Coordinate(x=x, y=y)
                for x, cell in enumerate(grid[y])
                if cell.cell_type != CellType.BLOCK
            ]
            second_half = [
                Coordinate(x=x, y=next_y)
                for x, cell in enumerate(grid[next_y])
                if cell.cell_type != CellType.BLOCK
            ]
            puzzle_clues.append(Clue(y, str(y + 1), clue))
            puzzle_words.append(Word(y, tuple(first_half + list(reversed(second_half)))))

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=grid,
            clues=[ClueList("Clues", tuple(puzzle_clues))],
            words=puzzle_words,
        )
