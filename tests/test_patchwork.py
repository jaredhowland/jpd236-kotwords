import unittest

from kotwords_py.model.patchwork import Patchwork
from kotwords_py.model.puzzle import BorderDirection


class PatchworkTests(unittest.IsolatedAsyncioTestCase):
    def _build_patchwork(self, label_pieces: bool = True) -> Patchwork:
        return Patchwork(
            title="Test title",
            creator="Test creator",
            copyright="Test copyright",
            description="Test description",
            grid=[
                ["A", "B", "C", "D", "E"],
                ["F", "G", "H", "I", "J"],
                ["K", "L", "M", "N", "O"],
                ["P", "Q", "R", "S", "T"],
                ["U", "V", "W", "X", "Y"],
            ],
            row_clues=[
                ["Clue A1", "Clue A2"],
                ["Clue B1", "Clue B2"],
                ["Clue C1", "Clue C2"],
                ["Clue D1", "Clue D2"],
                ["Clue E1", "Clue E2"],
            ],
            piece_clues=["Piece 1", "Piece 2", "Piece 3", "Piece 4", "Piece 5"],
            piece_numbers=[
                [1, 1, 1, 2, 2],
                [1, 1, 2, 2, 3],
                [4, 4, 3, 3, 3],
                [4, 4, 4, 3, 5],
                [4, 5, 5, 5, 5],
            ],
            label_pieces=label_pieces,
        )

    async def test_patchwork_builds_rows_and_pieces(self) -> None:
        puzzle = await self._build_patchwork().as_puzzle()

        self.assertEqual("A", puzzle.grid[0][0].number)
        self.assertEqual("B", puzzle.grid[1][0].number)
        self.assertEqual("1", puzzle.grid[0][0].top_right_number)
        self.assertEqual("2", puzzle.grid[0][3].top_right_number)
        self.assertEqual(
            frozenset({BorderDirection.RIGHT, BorderDirection.BOTTOM}),
            puzzle.grid[0][2].border_directions,
        )
        self.assertEqual(
            ["A", "B", "C", "D", "E"],
            [clue.number for clue in puzzle.clues[0].clues],
        )
        self.assertEqual("Clue A1 / Clue A2", puzzle.clues[0].clues[0].text)
        self.assertEqual(
            ["1", "2", "3", "4", "5"],
            [clue.number for clue in puzzle.clues[1].clues],
        )
        self.assertEqual(10, len(puzzle.words))
        self.assertEqual(
            [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
            [(coordinate.x, coordinate.y) for coordinate in puzzle.words[5].cells],
        )

    async def test_patchwork_unlabeled_pieces_omits_piece_words(self) -> None:
        puzzle = await self._build_patchwork(label_pieces=False).as_puzzle()
        self.assertEqual(5, len(puzzle.words))
        self.assertEqual("", puzzle.clues[1].clues[0].number)
        self.assertEqual(
            sorted(clue.text for clue in puzzle.clues[1].clues),
            [clue.text for clue in puzzle.clues[1].clues],
        )

    def test_patchwork_validates_piece_coverage(self) -> None:
        with self.assertRaisesRegex(ValueError, "Piece numbers do not cover range"):
            Patchwork(
                title="Test title",
                creator="Test creator",
                copyright="Test copyright",
                description="Test description",
                grid=[["A"]],
                row_clues=[["Clue A1"]],
                piece_clues=["Piece 1"],
                piece_numbers=[[99]],
                label_pieces=True,
            )


if __name__ == "__main__":
    unittest.main()
