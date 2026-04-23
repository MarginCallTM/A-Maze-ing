"""Entry point of the A-Maze-ing CLI.

Reads a configuration file, generates a maze, writes it to disk in
the subject's hex format and displays it in the terminal.
"""

from maze_renderer import MazeRenderer
from maze_generator import MazeGenerator
import sys

a, b, c, d, e, f = [10, 11, 12, 13, 14, 15]


def main() -> None:
    """Run the full pipeline: parse config, build, write, render.

    Expects a single CLI argument pointing to the configuration file.
    Exits with status 1 on usage errors.
    """
    if not len(sys.argv) == 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]
    print(f"{config_file}")
    maze_generator = MazeGenerator.from_config_file(config_file)
    maze = maze_generator.build()
    maze_generator.write_maze(maze, maze_generator.output_file)
    renderer = MazeRenderer(maze)
    renderer.render_maze()


if __name__ == "__main__":
    main()
