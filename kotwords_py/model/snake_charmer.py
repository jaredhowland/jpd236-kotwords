"""Snake Charmer puzzle model."""

from __future__ import annotations

from dataclasses import dataclass

from kotwords_py.formats.puzzleable import Puzzleable
from kotwords_py.model.puzzle import Cell, CellType, Clue, ClueList, Coordinate, Puzzle, Word


@dataclass
class SnakeCharmer(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    answers: list[str]
    clues: list[str]
    grid_coordinates: list[tuple[int, int]]

    def __post_init__(self) -> None:
        super().__init__()
        if not self.grid_coordinates:
            raise ValueError("Cannot have an empty grid")
        if len(self.grid_coordinates) * 2 != sum(len(answer) for answer in self.answers):
            raise ValueError("Grid size must be exactly half the length of all the answers")

    async def create_puzzle(self) -> Puzzle:
        cell_numbers_map: dict[tuple[int, int], list[int]] = {}
        solution_map: dict[tuple[int, int], str] = {}
        words: list[list[tuple[int, int]]] = []

        i = 0
        clue_number = 1
        for answer in self.answers:
            start_coordinate = self.grid_coordinates[i % len(self.grid_coordinates)]
            cell_numbers_map.setdefault(start_coordinate, []).append(clue_number)
            word: list[tuple[int, int]] = []
            for j, ch in enumerate(answer):
                coordinates = self.grid_coordinates[(i + j) % len(self.grid_coordinates)]
                existing = solution_map.setdefault(coordinates, ch)
                if existing != ch:
                    raise ValueError(
                        f"Conflict at cell ({coordinates[0]}, {coordinates[1]}) for answer {clue_number} "
                        f"({answer}): {existing} from previous answer does not match {ch} from this answer."
                    )
                word.append(coordinates)
            words.append(word)
            i += len(answer)
            clue_number += 1

        width = max(x for x, _ in self.grid_coordinates) + 1
        height = max(y for _, y in self.grid_coordinates) + 1
        grid: list[list[Cell]] = []
        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                if (x, y) not in solution_map:
                    row.append(Cell(cell_type=CellType.BLOCK))
                else:
                    cell_numbers = cell_numbers_map.get((x, y), [])
                    row.append(
                        Cell(
                            solution=solution_map[(x, y)],
                            number=str(cell_numbers[0]) if cell_numbers else "",
                            top_right_number=str(cell_numbers[1]) if len(cell_numbers) > 1 else "",
                        )
                    )
            grid.append(row)

        puzzle_clues: list[Clue] = []
        puzzle_words: list[Word] = []
        for i, clue in enumerate(self.clues):
            puzzle_clues.append(Clue(i + 1, str(i + 1), clue))
            puzzle_words.append(
                Word(
                    i + 1,
                    tuple(Coordinate(x=x, y=y) for x, y in words[i]),
                )
            )

        return Puzzle(
            title=self.title,
            creator=self.creator,
            copyright=self.copyright,
            description=self.description,
            grid=grid,
            clues=[ClueList("Clues", tuple(puzzle_clues))],
            words=puzzle_words,
        )
