from maze_generator.maze_generator import MazeGenerator
from maze_generator.maze import MazeOptions
from maze_renderer import MazeRenderer


def main() -> None:
    options = MazeOptions(
        width=250,
        height=250,
        entry=(0, 0),
        exit=(249, 249),
        output_file="maze.txt",
        perfect=True,
        seed="50",
    )
    maze = MazeGenerator(options).build()
    MazeRenderer(maze).render_maze()


if __name__ == "__main__":
    main()
