import unittest

from kotwords_py.model.jelly_roll import JellyRoll
from kotwords_py.model.spiral import Spiral
from kotwords_py.model.two_tone import TwoTone


class SpiralVariantTests(unittest.IsolatedAsyncioTestCase):
    async def test_spiral_generates_inward_and_outward_clues(self) -> None:
        spiral = Spiral(
            title="Spiral",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            inward_answers=["AB", "CD"],
            inward_clues=["Inward 1", "Inward 2"],
            outward_answers=["DC", "BA"],
            outward_clues=["Outward 1", "Outward 2"],
            dimensions=(2, 2),
        )

        puzzle = await spiral.as_puzzle()

        self.assertEqual(["Inward", "Outward"], [cl.title for cl in puzzle.clues])
        self.assertEqual(["1-2", "3-4"], [cl.number for cl in puzzle.clues[0].clues])
        self.assertEqual(["4-3", "2-1"], [cl.number for cl in puzzle.clues[1].clues])
        self.assertEqual([1, 2, 101, 102], [word.id for word in puzzle.words])

    async def test_two_tone_generates_expected_word_groups(self) -> None:
        two_tone = TwoTone(
            title="TwoTone",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            all_squares_answers=["AB", "CD"],
            all_squares_clues=["All 1", "All 2"],
            odd_squares_answers=["AC"],
            odd_squares_clues=["Odd"],
            even_squares_answers=["BD"],
            even_squares_clues=["Even"],
            odd_square_background_color="#111111",
            even_square_background_color="#222222",
            dimensions=(2, 2),
        )

        puzzle = await two_tone.as_puzzle()

        self.assertEqual(["All Squares", "Odd Squares", "Even Squares"], [cl.title for cl in puzzle.clues])
        self.assertEqual("Every Other", puzzle.clues[1].merged_title)
        self.assertEqual("Every Other", puzzle.clues[2].merged_title)
        self.assertEqual([1, 2, 101, 201], [word.id for word in puzzle.words])

    async def test_jelly_roll_supports_combined_clues(self) -> None:
        jelly_roll = JellyRoll(
            title="Jelly",
            creator="Creator",
            copyright="Copyright",
            description="Description",
            jelly_roll_answers=["AB", "CD", "EF", "GH"],
            jelly_roll_clues=["J1", "J2", "J3", "J4"],
            light_squares_answers=["AD", "EH"],
            light_squares_clues=["L1", "L2"],
            dark_squares_answers=["BC", "FG"],
            dark_squares_clues=["D1", "D2"],
            light_square_background_color="#eeeeee",
            dark_square_background_color="#aaaaaa",
            combine_jelly_roll_clues=True,
            dimensions=(3, 3),
        )

        puzzle = await jelly_roll.as_puzzle()

        self.assertEqual(["Jelly Rolls", "Light Squares", "Dark Squares"], [cl.title for cl in puzzle.clues])
        self.assertEqual(1, len(puzzle.clues[0].clues))
        self.assertEqual("J1 / J2 / J3 / J4", puzzle.clues[0].clues[0].text)
        self.assertEqual([1, 101, 102, 201, 202], [word.id for word in puzzle.words])


if __name__ == "__main__":
    unittest.main()
