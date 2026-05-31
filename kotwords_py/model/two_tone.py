"""Two-Tone puzzle model."""

from __future__ import annotations

from dataclasses import dataclass

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import Cell, CellType, Clue, ClueList, Coordinate, Puzzle, Word
from kotwords_py.model.spiral_grid import Square, create_square_list, get_side_length


@dataclass
class TwoTone(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    all_squares_answers: list[str]
    all_squares_clues: list[str]
    odd_squares_answers: list[str]
    odd_squares_clues: list[str]
    even_squares_answers: list[str]
    even_squares_clues: list[str]
    odd_square_background_color: str
    even_square_background_color: str
    dimensions: tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        super().__init__()
        split_answers = "".join(ch for i, ch in enumerate("".join(self.all_squares_answers)) if i % 2 == 0), "".join(
            ch for i, ch in enumerate("".join(self.all_squares_answers)) if i % 2 == 1
        )

        if len(self.all_squares_clues) != len(self.all_squares_answers):
            raise ValueError(
                f"Different number of all square clues ({len(self.all_squares_clues)}) than answers ({len(self.all_squares_answers)})"
            )
        if len(self.odd_squares_clues) != len(self.odd_squares_answers):
            raise ValueError(
                f"Different number of odd square clues ({len(self.odd_squares_clues)}) than answers ({len(self.odd_squares_answers)})"
            )
        if len(self.even_squares_clues) != len(self.even_squares_answers):
            raise ValueError(
                f"Different number of even square clues ({len(self.even_squares_clues)}) than answers ({len(self.even_squares_answers)})"
            )
        if "".join(self.odd_squares_answers) != split_answers[0]:
            raise ValueError("Odd square answers do not match the odd squares of the all squares answers")
        if "".join(self.even_squares_answers) != split_answers[1]:
            raise ValueError("Even square answers do not match the even squares of the all squares answers")

        width, height = self.dimensions
        if width > 0 or height > 0:
            if width <= 0 or height <= 0:
                raise ValueError("Either neither or both of width and height must be specified")
            if width * height < sum(len(answer) for answer in self.all_squares_answers):
                raise ValueError("Grid size not large enough to fit all cells")

    async def create_puzzle(self) -> Puzzle:
        numbered_squares: set[int] = set()

        def add_numbered_squares(answers: list[str], start_index: int, is_every_other: bool) -> None:
            i = start_index
            for answer in answers:
                numbered_squares.add(i)
                i += len(answer) * (2 if is_every_other else 1)

        add_numbered_squares(self.all_squares_answers, 0, False)
        add_numbered_squares(self.odd_squares_answers, 0, True)
        add_numbered_squares(self.even_squares_answers, 1, True)

        width, height = self.dimensions
        if width <= 0 or height <= 0:
            side_length = get_side_length(sum(len(answer) for answer in self.all_squares_answers))
            width = side_length
            height = side_length

        square_list = create_square_list(width, height)
        letters = "".join(self.all_squares_answers)
        current_number = 1
        grid_map: dict[tuple[int, int], Cell] = {}
        for i, square in enumerate(square_list):
            if i < len(letters):
                directions = frozenset([square.border_direction]) if square.border_direction else frozenset()
                grid_map[(square.x, square.y)] = Cell(
                    number=str(current_number) if i in numbered_squares else "",
                    solution=letters[i],
                    background_color=(
                        self.odd_square_background_color if i % 2 == 0 else self.even_square_background_color
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
            jpz_clues: list[Clue] = []
            jpz_words: list[Word] = []
            i = 0
            for word_number, answer in enumerate(answers):
                first_cell = squares[i]
                jpz_words.append(
                    Word(
                        first_word_id + word_number,
                        tuple(Coordinate(x=s.x, y=s.y) for s in squares[i : i + len(answer)]),
                    )
                )
                jpz_clues.append(
                    Clue(
                        first_word_id + word_number,
                        grid[first_cell.y][first_cell.x].number,
                        clues[word_number],
                    )
                )
                i += len(answer)
            return jpz_clues, jpz_words

        all_squares_jpz_clues, all_squares_jpz_words = create_clues(
            self.all_squares_answers, self.all_squares_clues, square_list, 1
        )
        partitioned_squares = (
            [square for i, square in enumerate(square_list) if i % 2 == 0],
            [square for i, square in enumerate(square_list) if i % 2 == 1],
        )
        odd_squares_jpz_clues, odd_squares_jpz_words = create_clues(
            self.odd_squares_answers,
            self.odd_squares_clues,
            partitioned_squares[0],
            101,
        )
        even_squares_jpz_clues, even_squares_jpz_words = create_clues(
            self.even_squares_answers,
            self.even_squares_clues,
            partitioned_squares[1],
            201,
        )

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=grid,
            clues=[
                ClueList("All Squares", tuple(all_squares_jpz_clues)),
                ClueList("Odd Squares", tuple(odd_squares_jpz_clues), merged_title="Every Other"),
                ClueList("Even Squares", tuple(even_squares_jpz_clues), merged_title="Every Other"),
            ],
            words=all_squares_jpz_words + odd_squares_jpz_words + even_squares_jpz_words,
        )
