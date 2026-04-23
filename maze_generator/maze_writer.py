from .maze import Maze


def write_maze(maze: Maze, output_file: str) -> None:
    with open(output_file, "w") as f:
        for row in maze.grid:
            line = "".join(f"{cell:X}" for cell in row)
            f.write(line + "\n")
        f.write("\n")
        f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
        f.write(f"{maze.exit[0]},{maze.exit[1]}\n")
        f.write(f"{maze.path_directions}\n")
