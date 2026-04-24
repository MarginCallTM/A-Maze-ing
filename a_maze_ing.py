"""Entry point of the A-Maze-ing CLI.

Reads a configuration file, generates a maze, writes it to disk in
the subject's hex format and displays it in the terminal.
"""

from maze_renderer import MazeRenderer
from maze_generator import MazeGenerator, MazeError
from pydantic import ValidationError
import sys


def main() -> None:
    """Run the full pipeline: parse config, build, write, render.

    Expects a single CLI argument pointing to the configuration file.
    Exits with status 1 on usage errors.
    """
    if not len(sys.argv) == 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]

    renderer = MazeRenderer()

    try:
        maze_generator = MazeGenerator.from_config_file(config_file)
        maze = maze_generator.build()
    except ValidationError as e:
        print(e.errors()[0]["msg"], file=sys.stderr)
        sys.exit(1)
    except MazeError as e:
        print(e)
        sys.exit(1)
    maze_generator.write_maze(maze, maze_generator.output_file)
    renderer.render_maze(maze)

    while True:
        choice = renderer.render_menu()
        if choice == 1:
            maze = maze_generator.build()
            maze_generator.write_maze(maze, maze_generator.output_file)
            renderer.render_maze(maze)
        elif choice == 2:
            renderer.cycle_path_display()
            renderer.render_maze(maze)
        elif choice == 3:
            renderer.cycle_colors()
            renderer.render_maze(maze)
        elif choice == 4:
            sys.exit(0)


if __name__ == "__main__":
    main()
