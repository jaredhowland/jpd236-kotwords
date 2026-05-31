"""Jelly Roll puzzle model."""

from __future__ import annotations

from dataclasses import dataclass

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import Cell, CellType, Clue, ClueList, Coordinate, Puzzle, Word
from kotwords_py.model.spiral_grid import Square, create_square_list, get_side_length

_LIGHT_SQUARE_MODULOS = (0, 3)
_DARK_SQUARE_MODULOS = (1, 2)


@dataclass
class JellyRoll(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    jelly_roll_answers: list[str]
    jelly_roll_clues: list[str]
    light_squares_answers: list[str]
    light_squares_clues: list[str]
    dark_squares_answers: list[str]
    dark_squares_clues: list[str]
    light_square_background_color: str
    dark_square_background_color: str
    combine_jelly_roll_clues: bool
    dimensions: tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        super().__init__()

        letters = "".join(self.jelly_roll_answers)
        split_answers = (
            "".join(ch for i, ch in enumerate(letters) if i % 4 in _LIGHT_SQUARE_MODULOS),
            "".join(ch for i, ch in enumerate(letters) if i % 4 in _DARK_SQUARE_MODULOS),
        )

        if "".join(self.light_squares_answers) != split_answers[0]:
            raise ValueError("Light square answers do not match the jelly roll answers")
        if "".join(self.dark_squares_answers) != split_answers[1]:
            raise ValueError("Dark square answers do not match the jelly roll answers")
        if len(self.jelly_roll_clues) != len(self.jelly_roll_answers):
            raise ValueError(
                f"Different number of jelly roll clues ({len(self.jelly_roll_clues)}) than answers ({len(self.jelly_roll_answers)})"
            )
        if len(self.light_squares_clues) != len(self.light_squares_answers):
            raise ValueError(
                "Different number of light square clues "
                f"({len(self.light_squares_clues)}) than answers ({len(self.light_squares_answers)})"
            )
        if len(self.dark_squares_clues) != len(self.dark_squares_answers):
            raise ValueError(
                f"Different number of dark square clues ({len(self.dark_squares_clues)}) than answers ({len(self.dark_squares_answers)})"
            )

        width, height = self.dimensions
        if width > 0 or height > 0:
            if width <= 0 or height <= 0:
                raise ValueError("Either neither or both of width and height must be specified")
            if width * height < sum(len(answer) for answer in self.jelly_roll_answers):
                raise ValueError("Grid size not large enough to fit all cells")

    async def create_puzzle(self) -> Puzzle:
        numbered_squares: set[int] = set()

        def add_numbered_squares(answers: list[str], start_index: int, included_modulos: tuple[int, ...]) -> None:
            i = start_index
            for answer in answers:
                numbered_squares.add(i)
                remaining_squares_to_skip = len(answer)
                position = i
                while remaining_squares_to_skip > 0 or position % 4 not in included_modulos:
                    if position % 4 in included_modulos:
                        remaining_squares_to_skip -= 1
                    position += 1
                i = position

        if not self.combine_jelly_roll_clues:
            add_numbered_squares(self.jelly_roll_answers, 0, (0, 1, 2, 3))
        add_numbered_squares(self.light_squares_answers, 0, _LIGHT_SQUARE_MODULOS)
        add_numbered_squares(self.dark_squares_answers, 1, _DARK_SQUARE_MODULOS)

        width, height = self.dimensions
        if width <= 0 or height <= 0:
            side_length = get_side_length(sum(len(answer) for answer in self.jelly_roll_answers))
            width = side_length
            height = side_length

        square_list = create_square_list(width, height)
        letters = "".join(self.jelly_roll_answers)
        current_number = 1
        grid_map: dict[tuple[int, int], Cell] = {}
        for i, square in enumerate(square_list):
            if i < len(letters):
                directions = frozenset([square.border_direction]) if square.border_direction else frozenset()
                grid_map[(square.x, square.y)] = Cell(
                    number=str(current_number) if i in numbered_squares else "",
                    solution=letters[i],
                    background_color=(
                        self.light_square_background_color
                        if i % 4 in _LIGHT_SQUARE_MODULOS
                        else self.dark_square_background_color
                    ),
                    border_directions=directions,
                )
                if i in numbered_squares:
                    current_number += 1
            else:
                grid_map[(square.x, square.y)] = Cell(cell_type=CellType.BLOCK)

        grid = [[grid_map[(x, y)] for x in range(width)] for y in range(height)]

        def create_clues(
            answers: list[str], clues: list[str], squares: list[Square], first_word_id: int
        ) -> tuple[list[Clue], list[Word]]:
            puzzle_clues: list[Clue] = []
            puzzle_words: list[Word] = []
            i = 0
            for word_number, answer in enumerate(answers):
                first_cell = squares[i]
                puzzle_words.append(
                    Word(
                        first_word_id + word_number,
                        tuple(Coordinate(x=s.x, y=s.y) for s in squares[i : i + len(answer)]),
                    )
                )
                puzzle_clues.append(
                    Clue(
                        first_word_id + word_number,
                        grid[first_cell.y][first_cell.x].number,
                        clues[word_number],
                    )
                )
                i += len(answer)
            return puzzle_clues, puzzle_words

        if self.combine_jelly_roll_clues:
            all_squares_puzzle_clues, all_squares_puzzle_words = create_clues(
                ["".join(self.jelly_roll_answers)],
                [" / ".join(self.jelly_roll_clues)],
                square_list,
                1,
            )
        else:
            all_squares_puzzle_clues, all_squares_puzzle_words = create_clues(
                self.jelly_roll_answers,
                self.jelly_roll_clues,
                square_list,
                1,
            )

        light_partition = [square for i, square in enumerate(square_list) if i % 4 in _LIGHT_SQUARE_MODULOS]
        dark_partition = [square for i, square in enumerate(square_list) if i % 4 in _DARK_SQUARE_MODULOS]

        light_squares_puzzle_clues, light_squares_puzzle_words = create_clues(
            self.light_squares_answers,
            self.light_squares_clues,
            light_partition,
            101,
        )
        dark_squares_puzzle_clues, dark_squares_puzzle_words = create_clues(
            self.dark_squares_answers,
            self.dark_squares_clues,
            dark_partition,
            201,
        )

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=grid,
            clues=[
                ClueList("Jelly Rolls", tuple(all_squares_puzzle_clues)),
                ClueList(
                    "Light Squares",
                    tuple(light_squares_puzzle_clues),
                    merged_title="Colored Paths",
                ),
                ClueList(
                    "Dark Squares",
                    tuple(dark_squares_puzzle_clues),
                    merged_title="Colored Paths",
                ),
            ],
            words=all_squares_puzzle_words + light_squares_puzzle_words + dark_squares_puzzle_words,
        )
