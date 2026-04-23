from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Self, Union


Cell = Annotated[int, Field(ge=0, le=15)]
PositiveInt = Annotated[int, Field(ge=0)]
Coords = tuple[PositiveInt, PositiveInt]
Seed = Union[int, float, str, bytes, None]


class Maze(BaseModel):
    """Result of a maze generation, ready to be rendered or serialized.

    Attributes:
        grid: 2D grid of cells. Each cell is an integer in [0, 15] whose bits
            encode closed walls (bit 0 North, bit 1 East, bit 2 South,
            bit 3 West; 1 means closed).
        entry: (x, y) coordinates of the entry cell.
        exit: (x, y) coordinates of the exit cell.
        path: Ordered list of (x, y) cells from entry to exit (shortest path).
        mask: Cells forming the "42" pattern (fully closed, excluded from DFS).
        path_directions: Shortest path encoded as a string of N/E/S/W letters.
    """

    grid: list[list[Cell]]
    entry: Coords
    exit: Coords
    path: list[Coords]
    mask: list[Coords]
    path_directions: str


class MazeError(Exception):
    """Raised when maze generation or configuration fails."""
    pass


class MazeOptions(BaseModel):
    """Validated configuration for a maze generation.

    Attributes:
        width: Maze width in cells (>= 2).
        height: Maze height in cells (>= 2).
        entry: (x, y) coordinates of the entry, inside the maze bounds.
        exit: (x, y) coordinates of the exit, inside the maze bounds.
        output_file: Path of the file where the maze will be written.
        perfect: If True, the maze has exactly one path between entry and exit.
        seed: Seed passed to ``random.seed`` for reproducible generation.
    """

    width: int = Field(ge=2)
    height: int = Field(ge=2)
    entry: Coords
    exit: Coords
    output_file: str
    perfect: bool = Field(default=False)
    seed: Seed = Field(default=None)

    @model_validator(mode='after')
    def entry_validator(self) -> Self:
        """Ensure the entry cell stays within the maze bounds.

        Raises:
            ValueError: If the entry is outside ``[0, width) x [0, height)``.
        """
        if self.entry[0] >= self.width or self.entry[1] >= self.height:
            raise ValueError("Maze entrance out of bound")
        return self

    @model_validator(mode='after')
    def exit_validator(self) -> Self:
        """Ensure the exit cell stays within the maze bounds.

        Raises:
            ValueError: If the exit is outside ``[0, width) x [0, height)``.
        """
        if self.exit[0] >= self.width or self.exit[1] >= self.height:
            raise ValueError("Maze exit out of bound")
        return self

    @model_validator(mode='after')
    def forty_two_validator(self) -> Self:
        """Flag mazes too small to host the centered "42" pattern."""
        if self.width < 9 or self.height < 7:
            self.has_forty_two = False
        return self
