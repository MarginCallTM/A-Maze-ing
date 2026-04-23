from maze_renderer import MazeRenderer
from maze_generator import MazeGenerator
import sys


def main() -> None:
    if not len(sys.argv) == 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]
    maze_generator = MazeGenerator.from_config_file(config_file)
    maze = maze_generator.build()
    maze_generator.write_maze(maze, maze_generator.output_file)
    renderer = MazeRenderer(maze)
    renderer.render_maze()

    while True:
        choice = renderer.render_menu()
        if choice == 1:
            maze = maze_generator.build()
            maze_generator.write_maze(maze, maze_generator.output_file)
            renderer = MazeRenderer(maze)
            renderer.render_maze()
        elif choice == 2:
            renderer.cycle_path_display()
            renderer.render_maze()
        elif choice == 3:
            renderer.cycle_colors()
            renderer.render_maze()
        elif choice == 4:
            sys.exit(0)


if __name__ == "__main__":
    main()
