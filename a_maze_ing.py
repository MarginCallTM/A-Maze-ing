import sys
from maze_renderer import MazeRenderer
from maze import Maze


a, b, c, d, e, f = [10, 11, 12, 13, 14, 15]


def main():
    maze = Maze(
        maze=[
            [9, 1, 5, 1, 5, 5, 5, 1, 5, 5, 5, 3, d, 1, 5, 1, 5, 1, 5, 3],
            [e, a, d, 0, 5, 5, 7, a, b, d, 3, c, 7, 8, 7, c, 7, c, 7, a],
            [9, 0, 1, 4, 7, 9, 5, 0, 4, 1, 4, 1, 7, a, 9, 1, 1, 3, d, 2],
            [a, e, e, d, 3, c, 7, c, 7, c, 3, e, d, 0, 0, 6, e, c, 7, a],
            [8, 5, 5, 1, 4, 1, 5, 5, 1, 3, 8, 1, 3, a, 8, 7, 9, 5, 5, 2],
            [8, 5, 7, c, 7, c, 7, b, a, e, e, e, e, a, a, 9, 2, b, 9, 2],
            [8, 5, 5, 1, 5, 3, b, a, a, b, b, 9, 1, 2, e, a, e, a, a, a],
            [8, 7, b, a, d, 4, 4, 2, a, c, 4, 6, e, a, 9, 4, 1, 2, e, a],
            [8, 5, 6, 8, 1, 7, f, a, c, 7, f, f, f, a, c, 7, a, e, 9, 2],
            [a, b, b, e, a, b, f, c, 5, 1, 5, 7, f, a, b, 9, 4, 3, e, a],
            [8, 0, 4, 3, a, a, f, f, f, e, f, f, f, 8, 2, c, 7, e, d, 2],
            [e, a, d, 6, e, a, b, b, f, b, f, d, 5, 2, 8, 7, 9, 3, 9, 2],
            [9, 2, b, d, 1, 0, 0, 6, f, a, f, f, f, e, e, b, a, e, 8, 6],
            [e, 8, 0, 5, 2, a, 8, 7, 9, 0, 7, b, 9, 1, 7, 8, 0, 5, 6, b],
            [b, e, c, 7, e, e, a, d, 0, 0, 5, 0, 2, c, 7, a, c, 7, d, 2],
            [c, 1, 1, 1, 1, 5, 4, 3, a, 8, 3, e, 8, 5, 1, 0, 5, 1, 5, 2],
            [d, 2, a, 8, 4, 1, 3, a, a, a, e, 9, 0, 3, e, a, d, 0, 7, a],
            [b, a, e, a, b, a, a, a, e, 8, 3, e, e, e, d, 6, b, e, 9, 2],
            [8, 4, 3, e, a, e, e, 8, 7, a, e, b, b, 9, 1, 1, 4, 3, e, a],
            [c, 7, c, 5, 4, 5, 5, 4, 5, 4, 5, 4, 4, 4, 4, 4, 7, e, d, 6],
             ],
        entry=(0, 0),
        exit=(20, 20),
        path=[]
    )

    renderer = MazeRenderer(maze)
    renderer.render_maze()


    # if not len(sys.argv) == 2:
    #     print("Usage: python3 a_maze_ing.py <config_file>")
    #     sys.exit(1)
    # config_file = sys.argv[1]
    # print(f"{config_file}")


if __name__ == "__main__":
    main()
