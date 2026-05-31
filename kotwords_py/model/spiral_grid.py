"""Spiral grid traversal helpers shared by spiral-style puzzle models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import ceil, sqrt
from typing import Optional

from kotwords_py.model.puzzle import BorderDirection


@dataclass(frozen=True)
class Square:
    x: int
    y: int
    border_direction: Optional[BorderDirection]


class _Direction(Enum):
    EAST = ((1, 0), BorderDirection.BOTTOM)
    SOUTH = ((0, 1), BorderDirection.LEFT)
    WEST = ((-1, 0), BorderDirection.TOP)
    NORTH = ((0, -1), BorderDirection.RIGHT)

    @property
    def offset(self) -> tuple[int, int]:
        return self.value[0]

    @property
    def border_direction(self) -> BorderDirection:
        return self.value[1]

    def move(self, point: tuple[int, int]) -> tuple[int, int]:
        return point[0] + self.offset[0], point[1] + self.offset[1]

    def rotate(self) -> "_Direction":
        if self is _Direction.EAST:
            return _Direction.SOUTH
        if self is _Direction.SOUTH:
            return _Direction.WEST
        if self is _Direction.WEST:
            return _Direction.NORTH
        return _Direction.EAST


def get_side_length(letter_count: int) -> int:
    return int(ceil(sqrt(float(letter_count))))


def create_square_list(width: int, height: int) -> list[Square]:
    total_size = width * height
    used_points: set[tuple[int, int]] = set()
    square_list: list[Square] = []

    direction = _Direction.EAST
    current_point = (0, 0)

    while len(used_points) < total_size:
        next_point = direction.move(current_point)
        include_border = True
        if (
            next_point in used_points
            or next_point[0] < 0
            or next_point[0] >= width
            or next_point[1] < 0
            or next_point[1] >= height
        ):
            direction = direction.rotate()
            next_point = direction.move(current_point)
            include_border = False

        square_list.append(
            Square(
                x=current_point[0],
                y=current_point[1],
                border_direction=direction.border_direction if include_border else None,
            )
        )
        used_points.add(current_point)
        current_point = next_point

    return square_list
