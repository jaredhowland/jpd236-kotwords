"""Core puzzle model primitives in Python."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

from kotwords_py.formats.puzzleable import Puzzleable


class CellType(Enum):
    REGULAR = "REGULAR"
    BLOCK = "BLOCK"
    CLUE = "CLUE"
    VOID = "VOID"

    def is_black(self) -> bool:
        return self in {CellType.BLOCK, CellType.VOID}


class BackgroundShape(Enum):
    NONE = "NONE"
    CIRCLE = "CIRCLE"


class BorderDirection(Enum):
    TOP = "TOP"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTTOM = "BOTTOM"


class ImageFormat(Enum):
    GIF = "GIF"
    JPG = "JPG"
    PNG = "PNG"


@dataclass(frozen=True)
class ImageData:
    format: ImageFormat
    data: bytes


@dataclass(frozen=True)
class Cell:
    solution: str = ""
    entry: str = ""
    foreground_color: str = ""
    background_color: str = ""
    background_image: Optional[ImageData] = None
    number: str = ""
    top_right_number: str = ""
    cell_type: CellType = CellType.REGULAR
    background_shape: BackgroundShape = BackgroundShape.NONE
    border_directions: frozenset[BorderDirection] = field(default_factory=frozenset)
    more_answers: tuple[str, ...] = field(default_factory=tuple)
    hint: bool = False


@dataclass(frozen=True)
class Coordinate:
    """0-indexed (x, y) position on a grid."""

    x: int
    y: int


@dataclass(frozen=True)
class Word:
    id: int
    cells: tuple[Coordinate, ...]


@dataclass(frozen=True)
class Clue:
    word_id: int
    number: str
    text: str
    format: str = ""

    def text_and_format(self) -> str:
        return f"{self.text} ({self.format})" if self.format.strip() else self.text


@dataclass(frozen=True)
class ClueList:
    title: str
    clues: tuple[Clue, ...]
    direction: str = ""
    merged_title: str = ""


class PuzzleType(Enum):
    CROSSWORD = "CROSSWORD"
    ACROSTIC = "ACROSTIC"
    CODED = "CODED"


@dataclass
class Puzzle(Puzzleable):
    title: str
    creator: str
    copyright: str
    description: str
    grid: list[list[Cell]]
    clues: list[ClueList]
    words: list[Word]
    has_html_clues: bool = False
    completion_message: str = ""
    puzzle_type: PuzzleType = PuzzleType.CROSSWORD
    has_unsupported_features: bool = False
    diagramless: bool = False

    def __post_init__(self) -> None:
        super().__init__()

    async def create_puzzle(self) -> "Puzzle":
        return self

    def get_clues(self, title_text: str) -> Optional[ClueList]:
        title_text_lower = title_text.lower()
        for clue_list in self.clues:
            if title_text_lower in clue_list.title.lower():
                return clue_list
        return None

    def has_unclued_words(self) -> bool:
        any_clue_has_text = any(clue.text for clue in _all_clues(self.clues))
        if not any_clue_has_text:
            return False
        word_ids = {word.id for word in self.words}
        clue_word_ids = {clue.word_id for clue in _all_clues(self.clues)}
        return word_ids != clue_word_ids

    def has_solution(self) -> bool:
        return any(
            cell.cell_type == CellType.REGULAR and bool(cell.solution)
            for row in self.grid
            for cell in row
        )


def _all_clues(clue_lists: Iterable[ClueList]) -> Iterable[Clue]:
    for clue_list in clue_lists:
        for clue in clue_list.clues:
            yield clue
