"""Helter Skelter puzzle model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import Cell, Clue, ClueList, Coordinate, Puzzle, Word


class Direction(Enum):
    NORTH = (0, -1)
    NORTHEAST = (1, -1)
    EAST = (1, 0)
    SOUTHEAST = (1, 1)
    SOUTH = (0, 1)
    SOUTHWEST = (-1, 1)
    WEST = (-1, 0)
    NORTHWEST = (-1, -1)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]


@dataclass(frozen=True)
class AnswerVector:
    start: tuple[int, int]
    direction: Direction


@dataclass
class HelterSkelter(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    grid: list[list[str]]
    answers: list[str]
    clues: list[str]
    answer_vectors: list[AnswerVector] | None = None
    extend_to_edges: bool = False

    def __post_init__(self) -> None:
        super().__init__()
        self.answer_vectors = self.answer_vectors or []

        if len(self.answers) != len(self.clues):
            raise ValueError(f"Have {len(self.answers)} answers but {len(self.clues)} clues")

        if self.answer_vectors and len(self.answer_vectors) != len(self.answers):
            raise ValueError(f"Have {len(self.answer_vectors)} answer vectors but {len(self.answers)} answers")

        if not self.grid or not all(len(row) == len(self.grid[0]) for row in self.grid):
            raise ValueError("Grid must be square")

    async def create_puzzle(self) -> Puzzle:
        vectors = self._get_or_calculate_answer_vectors()
        numbers = {vector.start: str(i + 1) for i, vector in enumerate(vectors)}

        puzzle_grid = [
            [
                Cell(solution=ch, number=numbers.get((x, y), ""))
                for x, ch in enumerate(row)
            ]
            for y, row in enumerate(self.grid)
        ]

        puzzle_clues = tuple(
            Clue(word_id=i + 1, number=str(i + 1), text=clue)
            for i, clue in enumerate(self.clues)
        )

        puzzle_words: list[Word] = []
        for i, vector in enumerate(vectors):
            cells: list[Coordinate] = []
            x, y = vector.start
            while True:
                cells.append(Coordinate(x, y))
                x += vector.direction.dx
                y += vector.direction.dy
                in_bounds = y in range(len(self.grid)) and x in range(len(self.grid[y]))
                if not in_bounds or (not self.extend_to_edges and len(cells) >= len(self.answers[i])):
                    break
            puzzle_words.append(Word(id=i + 1, cells=tuple(cells)))

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=puzzle_grid,
            clues=[ClueList("Clues", puzzle_clues)],
            words=puzzle_words,
        )

    def _get_or_calculate_answer_vectors(self) -> list[AnswerVector]:
        if self.answer_vectors:
            return self.answer_vectors

        found_vectors: list[AnswerVector] = []
        starting_points = [(x, y) for y, row in enumerate(self.grid) for x in range(len(row))]

        for answer in self.answers:
            found_vector: AnswerVector | None = None
            for start_x, start_y in starting_points:
                for direction in Direction:
                    vector = AnswerVector((start_x, start_y), direction)
                    if vector in found_vectors:
                        continue

                    vector_answer = ""
                    x, y = start_x, start_y
                    new_starting_points: list[tuple[int, int]] = []
                    while y in range(len(self.grid)) and x in range(len(self.grid[y])):
                        vector_answer += self.grid[y][x]
                        new_starting_points.append((x, y))
                        x += direction.dx
                        y += direction.dy

                    if vector_answer.startswith(answer):
                        if found_vector is not None:
                            raise ValueError(f"Found two possible vectors for answer {answer} in grid")
                        found_vector = vector
                        starting_points = new_starting_points

            if found_vector is None:
                raise ValueError(f"Could not find answer {answer} in grid")
            found_vectors.append(found_vector)

        return found_vectors
