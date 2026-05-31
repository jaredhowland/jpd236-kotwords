import unittest

from kotwords_py.model.around_the_bend import AroundTheBend
from kotwords_py.model.puzzle import CellType
from kotwords_py.model.snake_charmer import SnakeCharmer


class AdditionalVariantTests(unittest.IsolatedAsyncioTestCase):
    async def test_around_the_bend_builds_wrapping_words(self) -> None:
        puzzleable = AroundTheBend(
            title="Around",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            rows=["ABCD", "EF", "GHI", "JKL"],
            clues=["Clue 1", "Clue 2", "Clue 3", "Clue 4"],
        )

        puzzle = await puzzleable.as_puzzle()

        self.assertEqual(4, len(puzzle.grid))
        self.assertEqual("", puzzle.grid[0][1].number)
        self.assertEqual("2", puzzle.grid[1][2].number)
        self.assertEqual(CellType.BLOCK, puzzle.grid[1][0].cell_type)
        self.assertEqual(["1", "2", "3", "4"], [clue.number for clue in puzzle.clues[0].clues])
        self.assertEqual([(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (2, 1)], [(c.x, c.y) for c in puzzle.words[0].cells])
        self.assertEqual([(2, 1), (3, 1), (3, 2), (2, 2), (1, 2)], [(c.x, c.y) for c in puzzle.words[1].cells])

    async def test_snake_charmer_creates_double_numbered_cells(self) -> None:
        puzzleable = SnakeCharmer(
            title="Snake",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            answers=["ABCD", "EFG", "HABCD", "EFGH"],
            clues=["Clue 1", "Clue 2", "Clue 3", "Clue 4"],
            grid_coordinates=[(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)],
        )

        puzzle = await puzzleable.as_puzzle()

        self.assertEqual("1", puzzle.grid[0][0].number)
        self.assertEqual("", puzzle.grid[0][0].top_right_number)
        self.assertEqual("3", puzzle.grid[1][0].number)
        self.assertEqual("2", puzzle.grid[2][2].number)
        self.assertEqual("4", puzzle.grid[2][2].top_right_number)
        self.assertEqual(CellType.BLOCK, puzzle.grid[1][1].cell_type)
        self.assertEqual([1, 2, 3, 4], [word.id for word in puzzle.words])

    async def test_snake_charmer_rejects_conflicting_overlaps(self) -> None:
        puzzleable = SnakeCharmer(
                title="Snake",
                creator="Creator",
                copyright="Copyright",
                description="Description",
                answers=["AB", "CD", "AX", "CF"],
                clues=["Clue 1", "Clue 2", "Clue 3", "Clue 4"],
                grid_coordinates=[(0, 0), (1, 0), (1, 1), (0, 1)],
            )
        with self.assertRaisesRegex(ValueError, r"Conflict at cell \(1, 0\)"):
            await puzzleable.as_puzzle()


if __name__ == "__main__":
    unittest.main()
