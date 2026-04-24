from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Self, Union


Cell = Annotated[int, Field(ge=0, le=15)]
PositiveInt = Annotated[int, Field(ge=0)]
Coords = tuple[PositiveInt, PositiveInt]
Seed = Union[int, float, str, bytes, None]


class Maze(BaseModel):

    grid: list[list[Cell]]
    entry: Coords
    exit: Coords
    path: list[Coords]
    mask: list[Coords]
    path_directions: str


class MazeError(Exception):
    pass


class MazeOptions(BaseModel):

    width: int = Field(ge=2)
    height: int = Field(ge=2)
    entry: Coords
    exit: Coords
    output_file: str
    perfect: bool = Field(default=False)
    seed: Seed = Field(default=None)
    has_forty_two: bool = True

    @model_validator(mode='after')
    def entry_validator(self) -> Self:
        if self.entry[0] >= self.width or self.entry[1] >= self.height:
            raise ValueError("Maze entrance out of bound")
        return self

    @model_validator(mode='after')
    def exit_validator(self) -> Self:
        if self.exit[0] >= self.width or self.exit[1] >= self.height:
            raise ValueError("Maze exit out of bound")
        return self

    @model_validator(mode='after')
    def forty_two_validator(self) -> Self:
        if self.width < 9 or self.height < 7:
            self.has_forty_two = False
        return self
