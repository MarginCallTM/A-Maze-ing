from maze_renderer import MazeRenderer
from maze_generator import Maze, MazeGenerator
import sys

a, b, c, d, e, f = [10, 11, 12, 13, 14, 15]


def main() -> None:
    if not len(sys.argv) == 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]
    print(f"{config_file}")
    MazeGenerator.from_config_file(config_file)


    # renderer = MazeRenderer(maze)
    # renderer.render_maze()


if __name__ == "__main__":
    main()
