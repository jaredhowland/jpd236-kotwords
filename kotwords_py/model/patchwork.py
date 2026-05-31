"""Patchwork puzzle model."""

from __future__ import annotations

from dataclasses import dataclass

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import (
    BorderDirection,
    Cell,
    Clue,
    ClueList,
    Coordinate,
    Puzzle,
    Word,
)


@dataclass
class Patchwork(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    grid: list[list[str]]
    row_clues: list[list[str]]
    piece_clues: list[str]
    piece_numbers: list[list[int]]
    label_pieces: bool

    def __post_init__(self) -> None:
        super().__init__()
        if len(self.row_clues) != len(self.grid):
            raise ValueError(
                f"Grid has height {len(self.grid)} but has {len(self.row_clues)} row clue sets"
            )
        piece_number_set = {number for row in self.piece_numbers for number in row}
        if piece_number_set != set(range(1, len(self.piece_clues) + 1)):
            raise ValueError(
                f"Piece numbers do not cover range from 1 to {len(self.piece_clues)} piece clues"
            )
        if len(self.grid) != len(self.piece_numbers):
            raise ValueError(
                f"Have {len(self.grid)} rows in grid but {len(self.piece_numbers)} rows of piece numbers"
            )
        if any(
            len(grid_row) != len(piece_row)
            for grid_row, piece_row in zip(self.grid, self.piece_numbers)
        ):
            raise ValueError("Width of grid and piece numbers do not match")

    async def create_puzzle(self) -> Puzzle:
        words: dict[int, list[Coordinate]] = {}
        puzzle_grid: list[list[Cell]] = []
        for y, row in enumerate(self.grid):
            puzzle_row: list[Cell] = []
            for x, ch in enumerate(row):
                piece_number = self.piece_numbers[y][x]
                word = words.setdefault(piece_number, [])
                word.append(Coordinate(x=x, y=y))
                borders: set[BorderDirection] = set()
                for (neighbor_x, neighbor_y), border_direction in (
                    ((x, y - 1), BorderDirection.TOP),
                    ((x + 1, y), BorderDirection.RIGHT),
                    ((x, y + 1), BorderDirection.BOTTOM),
                    ((x - 1, y), BorderDirection.LEFT),
                ):
                    if (
                        0 <= neighbor_y < len(self.piece_numbers)
                        and 0 <= neighbor_x < len(self.piece_numbers[neighbor_y])
                        and piece_number != self.piece_numbers[neighbor_y][neighbor_x]
                    ):
                        borders.add(border_direction)
                puzzle_row.append(
                    Cell(
                        solution=ch,
                        number=chr(ord("A") + y) if x == 0 else "",
                        top_right_number=str(piece_number) if len(word) == 1 else "",
                        border_directions=frozenset(borders),
                    )
                )
            puzzle_grid.append(puzzle_row)

        row_clue_list: list[Clue] = []
        row_word_list: list[Word] = []
        for y, clues in enumerate(self.row_clues):
            cells = tuple(Coordinate(x=x, y=y) for x in range(len(puzzle_grid[y])))
            row_clue_list.append(Clue(word_id=y + 1, number=chr(ord("A") + y), text=" / ".join(clues)))
            row_word_list.append(Word(id=y + 1, cells=cells))

        piece_clue_list: list[Clue] = []
        piece_word_list: list[Word] = []
        for i, clue in enumerate(self.piece_clues, start=1):
            word_id = 1000 + i
            piece_clue_list.append(
                Clue(word_id=word_id, number=str(i) if self.label_pieces else "", text=clue)
            )
            piece_word_list.append(Word(id=word_id, cells=tuple(words[i])))

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=puzzle_grid,
            clues=[
                ClueList(title="Rows", clues=tuple(row_clue_list)),
                ClueList(
                    title="Pieces",
                    clues=tuple(
                        piece_clue_list
                        if self.label_pieces
                        else sorted(piece_clue_list, key=lambda clue: clue.text)
                    ),
                ),
            ],
            words=row_word_list + (piece_word_list if self.label_pieces else []),
        )
