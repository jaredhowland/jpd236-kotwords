"""Crossword model with standard numbering conversion."""

from __future__ import annotations

from dataclasses import dataclass, replace

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import BorderDirection, Cell, Clue, ClueList, Coordinate, Puzzle, Word

DOWN_CLUE_ID_OFFSET = 1000


@dataclass
class Crossword(Puzzleable):
    title: str
    creator: str
    copyright: str
    grid: list[list[Cell]]
    across_clues: dict[int, str]
    down_clues: dict[int, str]
    description: str = ""
    has_html_clues: bool = False
    diagramless: bool = False

    def __post_init__(self) -> None:
        super().__init__()
        if not self.grid:
            raise ValueError("Invalid grid - grid must contain at least one row")
        width = len(self.grid[0])
        for index, row in enumerate(self.grid):
            if len(row) != width:
                raise ValueError(
                    f"Invalid grid - row {index} has width {len(row)} but should be {width}"
                )

    async def create_puzzle(self) -> Puzzle:
        across_puzzle_clues: list[Clue] = []
        down_puzzle_clues: list[Clue] = []
        words: list[Word] = []

        grid_numbers: dict[tuple[int, int], int] = {}
        for x, y, clue_number, _, _ in self.for_each_numbered_cell(self.grid):
            grid_numbers[(x, y)] = clue_number

        for is_across, clue_number, clue, cells in self.for_each_clue(
            self.grid, self.across_clues, self.down_clues
        ):
            clue_list = across_puzzle_clues if is_across else down_puzzle_clues
            word_id = clue_number if is_across else clue_number + DOWN_CLUE_ID_OFFSET
            clue_list.append(Clue(word_id=word_id, number=str(clue_number), text=clue))
            words.append(Word(id=word_id, cells=tuple(cells)))

        across_title = "<b>Across</b>" if self.has_html_clues else "Across"
        down_title = "<b>Down</b>" if self.has_html_clues else "Down"

        numbered_grid = [
            [
                replace(cell, number=str(grid_numbers[(x, y)])) if (x, y) in grid_numbers else cell
                for x, cell in enumerate(row)
            ]
            for y, row in enumerate(self.grid)
        ]

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=numbered_grid,
            clues=[
                ClueList(title=across_title, clues=tuple(across_puzzle_clues)),
                ClueList(title=down_title, clues=tuple(down_puzzle_clues)),
            ],
            words=sorted(words, key=lambda word: word.id),
            has_html_clues=self.has_html_clues,
            diagramless=self.diagramless,
        )

    @classmethod
    def for_each_clue(
        cls,
        grid: list[list[Cell]],
        across_clues: dict[int, str],
        down_clues: dict[int, str],
        use_borders: bool = True,
    ) -> list[tuple[bool, int, str, list[Coordinate]]]:
        clues: list[tuple[bool, int, str, list[Coordinate]]] = []
        for x, y, clue_number, is_across, is_down in cls.for_each_cell(grid, use_borders):
            if is_across:
                word: list[Coordinate] = []
                i = x
                while True:
                    word.append(Coordinate(x=i, y=y))
                    if cls.has_border(grid, i, y, BorderDirection.RIGHT, True):
                        break
                    i += 1
                if clue_number is not None:
                    clues.append((True, clue_number, across_clues.get(clue_number, ""), word))
            if is_down:
                word = []
                j = y
                while True:
                    word.append(Coordinate(x=x, y=j))
                    if cls.has_border(grid, x, j, BorderDirection.BOTTOM, True):
                        break
                    j += 1
                if clue_number is not None:
                    clues.append((False, clue_number, down_clues.get(clue_number, ""), word))
        return clues

    @classmethod
    def for_each_cell(
        cls,
        grid: list[list[Cell]],
        use_borders: bool = True,
    ) -> list[tuple[int, int, int | None, bool, bool]]:
        cells: list[tuple[int, int, int | None, bool, bool]] = []
        current_clue_number = 1
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell.cell_type.is_black():
                    cells.append((x, y, None, False, False))
                    continue
                is_across = cls.needs_across_number(grid, x, y, use_borders)
                is_down = cls.needs_down_number(grid, x, y, use_borders)
                clue_number = None
                if is_across or is_down:
                    clue_number = current_clue_number
                    current_clue_number += 1
                cells.append((x, y, clue_number, is_across, is_down))
        return cells

    @classmethod
    def for_each_numbered_cell(
        cls,
        grid: list[list[Cell]],
        use_borders: bool = True,
    ) -> list[tuple[int, int, int, bool, bool]]:
        numbered_cells: list[tuple[int, int, int, bool, bool]] = []
        for x, y, clue_number, is_across, is_down in cls.for_each_cell(grid, use_borders):
            if clue_number is not None:
                numbered_cells.append((x, y, clue_number, is_across, is_down))
        return numbered_cells

    @classmethod
    def needs_across_number(cls, grid: list[list[Cell]], x: int, y: int, use_borders: bool) -> bool:
        return (
            not grid[y][x].cell_type.is_black()
            and cls.has_border(grid, x, y, BorderDirection.LEFT, use_borders)
            and not cls.has_border(grid, x, y, BorderDirection.RIGHT, use_borders)
        )

    @classmethod
    def needs_down_number(cls, grid: list[list[Cell]], x: int, y: int, use_borders: bool) -> bool:
        return (
            not grid[y][x].cell_type.is_black()
            and cls.has_border(grid, x, y, BorderDirection.TOP, use_borders)
            and not cls.has_border(grid, x, y, BorderDirection.BOTTOM, use_borders)
        )

    @classmethod
    def has_border(
        cls,
        grid: list[list[Cell]],
        x: int,
        y: int,
        direction: BorderDirection,
        use_borders: bool,
    ) -> bool:
        if use_borders and direction in grid[y][x].border_directions:
            return True

        if direction is BorderDirection.TOP:
            border_x, border_y = x, y - 1
            opposite = BorderDirection.BOTTOM
        elif direction is BorderDirection.BOTTOM:
            border_x, border_y = x, y + 1
            opposite = BorderDirection.TOP
        elif direction is BorderDirection.LEFT:
            border_x, border_y = x - 1, y
            opposite = BorderDirection.RIGHT
        else:
            border_x, border_y = x + 1, y
            opposite = BorderDirection.LEFT

        if border_y < 0 or border_y >= len(grid) or border_x < 0 or border_x >= len(grid[border_y]):
            return True

        border_cell = grid[border_y][border_x]
        return border_cell.cell_type.is_black() or (
            use_borders and opposite in border_cell.border_directions
        )
