from pydantic import BaseModel, Field
from typing import Annotated


Cell = Annotated[int, Field(ge=0, le=15)]
PositiveInt = Annotated[int, Field(ge=0)]
Coords = tuple[PositiveInt, PositiveInt]


class Maze(BaseModel):

    maze: list[list[Cell]]
    entry: Coords
    exit: Coords
    path: list[Coords]


class MazeOptions(BaseModel):

    width: int = Field(ge=2)
    height: int = Field(ge=2)
    entry: Coords
    exit: Coords
    output_file: str
    perfect: bool = Field(default=False)
