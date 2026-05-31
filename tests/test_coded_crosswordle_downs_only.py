import unittest

from kotwords_py.model.coded import Coded
from kotwords_py.model.crossword import Crossword
from kotwords_py.model.crosswordle import Crosswordle
from kotwords_py.model.downs_only import ClueDirection, DownsOnly
from kotwords_py.model.puzzle import Cell, CellType, Clue, ClueList, Puzzle, PuzzleType


class CodedCrosswordleDownsOnlyTests(unittest.IsolatedAsyncioTestCase):
    async def test_coded_builds_grid_and_words(self) -> None:
        coded = Coded(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[["A", "B"], ["C", None]],
            assignments=["C", "A", "B"],
            givens=["B"],
        )

        puzzle = await coded.as_puzzle()

        self.assertEqual(PuzzleType.CODED, puzzle.puzzle_type)
        self.assertEqual("2", puzzle.grid[0][0].number)
        self.assertTrue(puzzle.grid[0][1].hint)
        self.assertEqual("B", puzzle.grid[0][1].entry)
        self.assertEqual(CellType.BLOCK, puzzle.grid[1][1].cell_type)
        self.assertEqual([1, 1001], [word.id for word in puzzle.words])

    async def test_coded_from_raw_input_generates_assignments(self) -> None:
        coded = Coded.from_raw_input(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid="AB\nC.",
            assignments="",
            givens="A",
        )

        self.assertEqual({"A", "B", "C"}, set(coded.assignments))
        self.assertEqual([["A", "B"], ["C", None]], coded.grid)

    async def test_crosswordle_generates_colored_grid_and_clues(self) -> None:
        crosswordle = Crosswordle(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[["B", "A"], ["A", "B"]],
            answer="AB",
            across_clues=["Across 1", "Across 2"],
            down_clues=["Down 1", "Down 2"],
        )

        puzzle = await crosswordle.as_puzzle()

        self.assertEqual("#c9b458", puzzle.grid[0][0].background_color)
        self.assertEqual("#c9b458", puzzle.grid[0][1].background_color)
        self.assertEqual("#6aaa64", puzzle.grid[2][0].background_color)
        self.assertEqual("1", puzzle.grid[0][0].number)
        self.assertEqual("4", puzzle.grid[2][0].number)
        self.assertEqual("-", puzzle.clues[0].clues[2].text)
        self.assertEqual([1, 2, 3, 1001, 1002], [word.id for word in puzzle.words])

    async def test_downs_only_clears_direction_by_length_heuristic(self) -> None:
        crossword = Crossword(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[
                [Cell(solution="A"), Cell(solution="B"), Cell(solution="C")],
                [Cell(cell_type=CellType.BLOCK), Cell(solution="D"), Cell(cell_type=CellType.BLOCK)],
                [Cell(solution="E"), Cell(solution="F"), Cell(solution="G")],
            ],
            across_clues={1: "Across 1", 3: "Across 3"},
            down_clues={1: "Down 1", 2: "Down 2", 4: "Down 4"},
        )
        puzzle = await crossword.as_puzzle()

        self.assertEqual(
            ClueDirection.ACROSS,
            DownsOnly.get_direction_to_clear_for_downs_only(puzzle),
        )

        downs_only = DownsOnly.with_downs_only(puzzle)
        self.assertEqual(["-", "-"], [clue.text for clue in downs_only.clues[0].clues])
        self.assertEqual(["Down 2"], [clue.text for clue in downs_only.clues[1].clues])

    async def test_downs_only_rejects_nonstandard_clue_lists(self) -> None:
        puzzle = Puzzle(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[[Cell(solution="A")]],
            clues=[ClueList(title="Clues", clues=(Clue(1, "1", "Only"),))],
            words=[],
        )

        with self.assertRaisesRegex(ValueError, "Cannot convert puzzle with non-standard clue lists"):
            DownsOnly.with_downs_only(puzzle)


if __name__ == "__main__":
    unittest.main()
