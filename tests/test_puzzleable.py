import asyncio
import unittest

from kotwords_py.formats.puzzleable import DelegatingPuzzleable, Puzzleable
from kotwords_py.model.puzzle import Cell, ClueList, Puzzle, Word


def make_puzzle() -> Puzzle:
    return Puzzle(
        title="Title",
        creator="Creator",
        copyright="Copyright",
        description="Description",
        grid=[[Cell(solution="A")]],
        clues=[ClueList(title="Across", clues=tuple())],
        words=[Word(id=1, cells=tuple())],
    )


class CountingPuzzleable(Puzzleable):
    def __init__(self) -> None:
        super().__init__()
        self.create_count = 0

    async def create_puzzle(self) -> Puzzle:
        self.create_count += 1
        await asyncio.sleep(0)
        return make_puzzle()


class CountingDelegatingPuzzleable(DelegatingPuzzleable):
    def __init__(self, delegate: Puzzleable) -> None:
        super().__init__()
        self.delegate = delegate
        self.get_count = 0

    async def get_puzzleable(self) -> Puzzleable:
        self.get_count += 1
        return self.delegate


class PuzzleableTests(unittest.IsolatedAsyncioTestCase):
    async def test_as_puzzle_caches_single_result(self) -> None:
        puzzleable = CountingPuzzleable()

        first = await puzzleable.as_puzzle()
        second = await puzzleable.as_puzzle()

        self.assertIs(first, second)
        self.assertEqual(1, puzzleable.create_count)

    async def test_as_puzzle_caches_under_concurrency(self) -> None:
        puzzleable = CountingPuzzleable()

        first, second, third = await asyncio.gather(
            puzzleable.as_puzzle(),
            puzzleable.as_puzzle(),
            puzzleable.as_puzzle(),
        )

        self.assertIs(first, second)
        self.assertIs(second, third)
        self.assertEqual(1, puzzleable.create_count)

    async def test_delegating_puzzleable_delegates_and_caches(self) -> None:
        delegate = CountingPuzzleable()
        wrapper = CountingDelegatingPuzzleable(delegate)

        first = await wrapper.as_puzzle()
        second = await wrapper.as_puzzle()

        self.assertIs(first, second)
        self.assertEqual(1, wrapper.get_count)
        self.assertEqual(1, delegate.create_count)


if __name__ == "__main__":
    unittest.main()
