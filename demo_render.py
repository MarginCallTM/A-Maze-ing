from maze_generator.maze_generator import MazeGenerator
from maze_generator.maze import MazeOptions
from maze_renderer import MazeRenderer
from maze_generator.maze_writer import write_maze


def main() -> None:
    options = MazeOptions(
        width=20,
        height=20,
        entry=(0, 0),
        exit=(19, 19),
        output_file="maze.txt",
        perfect=True,
        seed="50",
    )
    maze = MazeGenerator(options).build()
    write_maze(maze, options.output_file)
    MazeRenderer(maze).render_maze()


if __name__ == "__main__":
    main()
