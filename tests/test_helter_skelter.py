import unittest

from kotwords_py.model.helter_skelter import AnswerVector, Direction, HelterSkelter


class HelterSkelterTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_puzzle_with_explicit_vectors(self) -> None:
        helter_skelter = HelterSkelter(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[
                ["A", "B", "C"],
                ["D", "E", "F"],
                ["G", "H", "I"],
            ],
            answers=["ADG", "CFI"],
            clues=["Clue 1", "Clue 2"],
            answer_vectors=[
                AnswerVector(start=(0, 0), direction=Direction.SOUTH),
                AnswerVector(start=(2, 0), direction=Direction.SOUTH),
            ],
        )

        puzzle = await helter_skelter.as_puzzle()

        self.assertEqual("1", puzzle.grid[0][0].number)
        self.assertEqual("2", puzzle.grid[0][2].number)
        self.assertEqual("", puzzle.grid[1][1].number)
        self.assertEqual([(0, 0), (0, 1), (0, 2)], [(c.x, c.y) for c in puzzle.words[0].cells])
        self.assertEqual([(2, 0), (2, 1), (2, 2)], [(c.x, c.y) for c in puzzle.words[1].cells])

    async def test_create_puzzle_autodetects_vectors(self) -> None:
        helter_skelter = HelterSkelter(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[
                ["A", "B", "C"],
                ["D", "E", "F"],
                ["G", "H", "I"],
            ],
            answers=["ABC", "BEH"],
            clues=["Clue 1", "Clue 2"],
        )

        puzzle = await helter_skelter.as_puzzle()

        self.assertEqual([(0, 0), (1, 0), (2, 0)], [(c.x, c.y) for c in puzzle.words[0].cells])
        self.assertEqual([(1, 0), (1, 1), (1, 2)], [(c.x, c.y) for c in puzzle.words[1].cells])

    async def test_extend_to_edges_ignores_answer_length(self) -> None:
        helter_skelter = HelterSkelter(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[
                ["A", "B", "C"],
                ["D", "E", "F"],
                ["G", "H", "I"],
            ],
            answers=["AD"],
            clues=["Clue 1"],
            answer_vectors=[AnswerVector(start=(0, 0), direction=Direction.SOUTH)],
            extend_to_edges=True,
        )

        puzzle = await helter_skelter.as_puzzle()

        self.assertEqual([(0, 0), (0, 1), (0, 2)], [(c.x, c.y) for c in puzzle.words[0].cells])

    async def test_rejects_ambiguous_autodetected_vectors(self) -> None:
        helter_skelter = HelterSkelter(
            title="Title",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            grid=[
                ["A", "A"],
                ["A", "A"],
            ],
            answers=["A"],
            clues=["Clue 1"],
        )

        with self.assertRaisesRegex(ValueError, "Found two possible vectors for answer A in grid"):
            await helter_skelter.as_puzzle()

    async def test_validates_grid_shape_and_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "Have 1 answers but 0 clues"):
            HelterSkelter(
                title="Title",
                creator="Creator",
                copyright="Copyright",
                description="Description",
                grid=[["A"]],
                answers=["A"],
                clues=[],
            )

        with self.assertRaisesRegex(ValueError, "Grid must be square"):
            HelterSkelter(
                title="Title",
                creator="Creator",
                copyright="Copyright",
                description="Description",
                grid=[["A"], ["B", "C"]],
                answers=["A"],
                clues=["Clue 1"],
            )


if __name__ == "__main__":
    unittest.main()
