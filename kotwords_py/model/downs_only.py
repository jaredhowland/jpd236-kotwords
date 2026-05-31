"""Downs-only transformation helpers."""

from __future__ import annotations

from dataclasses import replace
from enum import Enum

from kotwords_py.model.puzzle import ClueList, Puzzle


class ClueDirection(Enum):
    ACROSS = "ACROSS"
    DOWN = "DOWN"


class DownsOnly:
    @staticmethod
    def with_downs_only(puzzle: Puzzle) -> Puzzle:
        across_clues = puzzle.get_clues("Across")
        down_clues = puzzle.get_clues("Down")
        if across_clues is None or down_clues is None or across_clues is down_clues or len(puzzle.clues) != 2:
            raise ValueError("Cannot convert puzzle with non-standard clue lists to Downs Only")

        direction_to_clear = DownsOnly.get_direction_to_clear_for_downs_only(puzzle)
        clues = (
            [DownsOnly.clear_clues(across_clues), down_clues]
            if direction_to_clear is ClueDirection.ACROSS
            else [across_clues, DownsOnly.clear_clues(down_clues)]
        )
        return replace(puzzle, clues=clues)

    @staticmethod
    def get_direction_to_clear_for_downs_only(puzzle: Puzzle) -> ClueDirection:
        def word_stats_for_rows() -> tuple[int, int]:
            max_word_length = 0
            words_at_max_length = 0
            for row in puzzle.grid:
                cur_word_length = 0
                for cell in row:
                    if cell.cell_type.is_black():
                        if cur_word_length > 0:
                            if cur_word_length > max_word_length:
                                max_word_length = cur_word_length
                                words_at_max_length = 1
                            elif cur_word_length == max_word_length:
                                words_at_max_length += 1
                            cur_word_length = 0
                    else:
                        cur_word_length += 1
                if cur_word_length > 0:
                    if cur_word_length > max_word_length:
                        max_word_length = cur_word_length
                        words_at_max_length = 1
                    elif cur_word_length == max_word_length:
                        words_at_max_length += 1
            return max_word_length, words_at_max_length

        def word_stats_for_columns() -> tuple[int, int]:
            max_word_length = 0
            words_at_max_length = 0
            for x in range(len(puzzle.grid[0])):
                cur_word_length = 0
                for y in range(len(puzzle.grid)):
                    if puzzle.grid[y][x].cell_type.is_black():
                        if cur_word_length > 0:
                            if cur_word_length > max_word_length:
                                max_word_length = cur_word_length
                                words_at_max_length = 1
                            elif cur_word_length == max_word_length:
                                words_at_max_length += 1
                            cur_word_length = 0
                    else:
                        cur_word_length += 1
                if cur_word_length > 0:
                    if cur_word_length > max_word_length:
                        max_word_length = cur_word_length
                        words_at_max_length = 1
                    elif cur_word_length == max_word_length:
                        words_at_max_length += 1
            return max_word_length, words_at_max_length

        across_max, across_count = word_stats_for_rows()
        down_max, down_count = word_stats_for_columns()

        if across_max > down_max:
            return ClueDirection.ACROSS
        if across_max < down_max or across_count < down_count:
            return ClueDirection.DOWN
        return ClueDirection.ACROSS

    @staticmethod
    def clear_clues(clue_list: ClueList) -> ClueList:
        return replace(
            clue_list,
            clues=tuple(replace(clue, text="-", format="") for clue in clue_list.clues),
        )
