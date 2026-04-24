from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Self, Union


Cell = Annotated[int, Field(ge=0, le=15)]
PositiveInt = Annotated[int, Field(ge=0)]
Coords = tuple[PositiveInt, PositiveInt]
Seed = Union[int, float, str, bytes, None]


class Maze(BaseModel):
    """Result of a maze generation, ready to be rendered or serialized."""

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
    """Validated configuration for a maze generation."""

    width: int = Field(ge=2, le=200)
    height: int = Field(ge=2, le=200)
    entry: Coords
    exit: Coords
    output_file: str
    perfect: bool = Field(default=False)
    seed: Seed = Field(default=None)
    has_forty_two: bool = True

    @model_validator(mode='after')
    def end_point_validation(self) -> Self:
        """Ensure the entry and exit cells don't overlap."""
        if self.entry == self.exit:
            raise ValueError("Entry and exit cells overlap")
        return self

    @model_validator(mode='after')
    def entry_validator(self) -> Self:
        """Ensure the entry cell stays within the maze bounds."""
        if self.entry[0] >= self.width or self.entry[1] >= self.height:
            raise ValueError("Maze entrance out of bound")
        return self

    @model_validator(mode='after')
    def exit_validator(self) -> Self:
        """Ensure the exit cell stays within the maze bounds."""
        if self.exit[0] >= self.width or self.exit[1] >= self.height:
            raise ValueError("Maze exit out of bound")
        return self

    @model_validator(mode='after')
    def forty_two_validator(self) -> Self:
        """Flag mazes too small to host the centered "42" pattern."""
        if self.width < 9 or self.height < 7:
            self.has_forty_two = False
        return self

    @model_validator(mode='after')
    def out_file_vlidator(self) -> Self:
        """Check if the output file is a txt file"""
        if not self.output_file.endswith(".txt"):
            raise ValueError("Output file must be a txt file")
        return self
