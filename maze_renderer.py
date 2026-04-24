from maze_generator import Maze, Cell
from operator import sub

Pair = tuple[str, str]
Grid = tuple[tuple[Pair, Pair], tuple[Pair, Pair]]


class MazeRenderer:

    def __init__(self) -> None:
        self.tree: tuple[Grid, Grid] = (
            (((' ', '•'), ('•', '╗')), (('•', '═'), ('╔', '╦'))),
            ((('•', '╝'), ('║', '╣')), (('╚', '╩'), ('╠', '╬')))
        )
        self.show_path: bool = False
        self.entry_char: str = '▓'
        self.exit_char: str = '░'
        self.path_char: str = '▒'
        self.mask_char: str = '█'
        self.palette: list[str] = [
            "\033[34m", "\033[32m", "\033[33m",
            "\033[31m", "\033[35m", "\033[36m",
            "\033[37m"
        ]
        self.color_path: int = 1
        self.color_walls: int = 2
        self.color_entry: int = 3
        self.color_exit: int = 4
        self.color_mask: int = 5

    def render_maze(self, maze: Maze) -> None:

        self.maze: Maze = maze
        self.y_len: int = len(maze.grid)
        self.x_len: int = len(maze.grid[0])

        maze_render = self.__gen_grid()
        self.__apply_walls(maze_render)
        self.__apply_crossing(maze_render)
        self.__add_mask(maze_render)
        if self.show_path:
            self.__add_path(maze_render)
        self.__add_entry(maze_render)
        self.__add_exit(maze_render)

        display = "\n".join("".join(row) for row in maze_render)
        print(f"{display}\033[0m")

    def cycle_path_display(self) -> None:
        self.show_path ^= True

    def cycle_colors(self) -> None:

        nb_colors = len(self.palette)

        self.color_entry = (self.color_entry + 1) % nb_colors
        self.color_exit = (self.color_exit + 1) % nb_colors
        self.color_mask = (self.color_mask + 1) % nb_colors
        self.color_path = (self.color_path + 1) % nb_colors
        self.color_walls = (self.color_walls + 1) % nb_colors

    def render_menu(self) -> int:

        print()
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path fron entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")

        success = False
        error = ""

        while success is False:
            print(error)
            response = input("Choice? (1-4): ")

            try:
                nb = int(response)
                if not (0 < nb < 5):
                    raise ValueError("")
            except Exception:
                error = "\033[1;31mERROR UNKNOWN INPUT TRY AGAIN\033[0m"
                print("\033[1A\033[2K\033[1A\033[2K", end="")
            else:
                success = True
                return nb
        return 0

    def __add_entry(self, grid: list[list[str]]) -> None:

        entry = self.maze.entry
        entry_color = self.palette[self.color_entry]
        char = f"{entry_color}{self.entry_char}\033[0m"
        grid[entry[1] * 2 + 1][entry[0] * 2 + 1] = char * 3

    def __add_exit(self, grid: list[list[str]]) -> None:

        exit = self.maze.exit
        exit_color = self.palette[self.color_exit]
        char = f"{exit_color}{self.exit_char}\033[0m"
        grid[exit[1] * 2 + 1][exit[0] * 2 + 1] = char * 3

    def __add_path(self, grid: list[list[str]]) -> None:

        prev = None
        path_color = self.palette[self.color_path]
        char = f"{path_color}{self.path_char}\033[0m"

        for pos in self.maze.path:
            grid[pos[1] * 2 + 1][pos[0] * 2 + 1] = char * 3
            if prev is not None:
                direction = tuple(map(sub, pos, prev))
                y = (pos[1] * 2 + 1) - direction[1]
                x = (pos[0] * 2 + 1) - direction[0]
                grid[y][x] = char * 3 if x % 2 else char
            prev = pos

    def __add_mask(self, grid: list[list[str]]) -> None:

        mask_color = self.palette[self.color_mask]
        char = f"{mask_color}{self.mask_char}\033[0m"

        for pos in self.maze.mask:
            grid[pos[1] * 2 + 1][pos[0] * 2 + 1] = char * 3

    def __gen_grid(self) -> list[list[str]]:

        wall_color = self.palette[self.color_walls]

        y_len = self.y_len * 2 + 1
        x_len = self.x_len * 2 + 1

        display: list[list[str]] = [[""] * x_len for _ in range(y_len)]

        for y in range(y_len):

            for x in range(x_len):

                if y == 0 and x == 0:
                    char = self.tree[0][1][1][0]
                elif y == 0 and x == x_len - 1:
                    char = self.tree[0][0][1][1]
                elif y == y_len - 1 and x == 0:
                    char = self.tree[1][1][0][0]
                elif y == y_len - 1 and x == x_len - 1:
                    char = self.tree[1][0][0][1]
                elif y == 0 and not x % 2:
                    char = self.tree[0][1][1][1]
                elif not y % 2 and x == 0:
                    char = self.tree[1][1][1][0]
                elif y == y_len - 1 and not x % 2:
                    char = self.tree[1][1][0][1]
                elif not y % 2 and x == x_len - 1:
                    char = self.tree[1][0][1][1]
                elif y % 2 and not x % 2:
                    char = self.tree[1][0][1][0]
                elif not y % 2 and x % 2:
                    char = self.tree[0][1][0][1]
                elif y % 2 and x % 2:
                    char = self.tree[0][0][0][0]
                elif not y % 2 and not x % 2:
                    char = self.tree[1][1][1][1]
                else:
                    char = '0'
                char = f"{wall_color}{char}\033[0m"
                display[y][x] = char * 3 if x % 2 else char

        return display

    def __apply_walls(self, grid: list[list[str]]) -> None:

        wall_color = self.palette[self.color_walls]
        char = f"{wall_color}{self.tree[0][0][0][0]}\033[0m"

        m_grid = self.maze.grid

        for y in range(self.y_len):

            for x in range(self.x_len):

                if (x < self.x_len - 1 and
                        not self.has_x_wall(m_grid[y][x], m_grid[y][x + 1])):
                    grid[y * 2 + 1][(x + 1) * 2] = char

                if (y < self.y_len - 1 and
                        not self.has_y_wall(m_grid[y][x], m_grid[y + 1][x])):
                    grid[(y + 1) * 2][x * 2 + 1] = char * 3

    def __apply_crossing(self, grid: list[list[str]]) -> None:

        y_len = self.y_len * 2 + 1
        x_len = self.x_len * 2 + 1

        wall_color = self.palette[self.color_walls]

        for y in range(y_len)[0:y_len:2]:
            for x in range(x_len)[0:x_len:2]:

                n = 1 if y != 0 and ' ' not in grid[y - 1][x] else 0
                s = 1 if y != y_len - 1 and ' ' not in grid[y + 1][x] else 0
                e = 1 if x != x_len - 1 and ' ' not in grid[y][x + 1] else 0
                w = 1 if x != 0 and ' ' not in grid[y][x - 1] else 0

                grid[y][x] = f"{wall_color}{self.tree[n][e][s][w]}\033[0m"

    @staticmethod
    def has_x_wall(west: Cell, east: Cell) -> bool:
        return bool(west & 2) and bool(east & 8)

    @staticmethod
    def has_y_wall(north: Cell, south: Cell) -> bool:
        return bool(north & 4) and bool(south & 1)
