"""Spiral puzzle model."""

from __future__ import annotations

from dataclasses import dataclass, field

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import Cell, CellType, Clue, ClueList, Coordinate, Puzzle, Word
from kotwords_py.model.spiral_grid import create_square_list, get_side_length


@dataclass
class Spiral(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    inward_answers: list[str]
    inward_clues: list[str]
    outward_answers: list[str]
    outward_clues: list[str]
    inward_cells_input: list[str] = field(default_factory=list)
    dimensions: tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        super().__init__()
        self._inward_cells = self.inward_cells_input or list("".join(self.inward_answers))
        self._outward_cells = list(reversed(self._inward_cells))

        if "".join(self.inward_answers) != "".join(self._inward_cells):
            raise ValueError("Inward cells do not match the inward answers")
        if "".join(self.outward_answers) != "".join(self._outward_cells):
            raise ValueError("Inward and outward answers/cells do not match")
        if len(self.inward_clues) != len(self.inward_answers):
            raise ValueError(
                f"Different number of inward clues ({len(self.inward_clues)}) than answers ({len(self.inward_answers)})"
            )
        if len(self.outward_clues) != len(self.outward_answers):
            raise ValueError(
                f"Different number of outward clues ({len(self.outward_clues)}) than answers ({len(self.outward_answers)})"
            )

        width, height = self.dimensions
        if width > 0 or height > 0:
            if width <= 0 or height <= 0:
                raise ValueError("Either neither or both of width and height must be specified")
            if width * height < len(self._inward_cells):
                raise ValueError("Grid size not large enough to fit all cells")

    async def create_puzzle(self) -> Puzzle:
        width, height = self.dimensions
        if width <= 0 or height <= 0:
            side_length = get_side_length(len(self._inward_cells))
            width = side_length
            height = side_length

        square_list = create_square_list(width, height)
        grid_map: dict[tuple[int, int], Cell] = {}
        for i, square in enumerate(square_list):
            if i < len(self._inward_cells):
                directions = frozenset([square.border_direction]) if square.border_direction else frozenset()
                grid_map[(square.x, square.y)] = Cell(
                    number=str(i + 1),
                    solution=self._inward_cells[i],
                    border_directions=directions,
                )
            else:
                grid_map[(square.x, square.y)] = Cell(cell_type=CellType.BLOCK)

        grid = [[grid_map[(x, y)] for x in range(width)] for y in range(height)]

        words: list[Word] = []
        inward_jpz_clues: list[Clue] = []
        i = 0
        for word_number, answer in enumerate(self.inward_answers):
            cells_consumed = 0
            partial_answer = ""
            while len(partial_answer) < len(answer):
                partial_answer += self._inward_cells[i + cells_consumed]
                cells_consumed += 1
            if len(partial_answer) != len(answer):
                raise ValueError("Answers must be split cleanly across answer chunks")
            end_cell = i + cells_consumed
            words.append(
                Word(
                    word_number + 1,
                    tuple(Coordinate(x=s.x, y=s.y) for s in square_list[i:end_cell]),
                )
            )
            inward_jpz_clues.append(
                Clue(word_number + 1, f"{i + 1}-{end_cell}", self.inward_clues[word_number])
            )
            i = end_cell

        outward_jpz_clues: list[Clue] = []
        i = len(self._outward_cells)
        for word_number, answer in enumerate(self.outward_answers):
            cells_consumed = 0
            partial_answer = ""
            while len(partial_answer) < len(answer):
                partial_answer += self._inward_cells[i - cells_consumed - 1]
                cells_consumed += 1
            if len(partial_answer) != len(answer):
                raise ValueError("Answers must be split cleanly across answer chunks")
            end_cell = i - cells_consumed
            words.append(
                Word(
                    word_number + 101,
                    tuple(
                        Coordinate(x=s.x, y=s.y)
                        for s in reversed(square_list[end_cell:i])
                    ),
                )
            )
            outward_jpz_clues.append(
                Clue(word_number + 101, f"{i}-{end_cell + 1}", self.outward_clues[word_number])
            )
            i = end_cell

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=grid,
            clues=[
                ClueList("Inward", tuple(inward_jpz_clues)),
                ClueList("Outward", tuple(outward_jpz_clues)),
            ],
            words=words,
        )
