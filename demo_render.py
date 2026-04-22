from maze_generator.maze_generator import MazeGenerator
from maze_generator.maze import MazeOptions
from maze_renderer import MazeRenderer


def main() -> None:
    options = MazeOptions(
        width=150,
        height=150,
        entry=(0, 0),
        exit=(149, 149),
        output_file="maze.txt",
        perfect=False,
        seed="50",
    )
    maze = MazeGenerator(options).build()
    MazeRenderer(maze).render_maze()


if __name__ == "__main__":
    main()
