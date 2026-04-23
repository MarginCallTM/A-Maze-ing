"""Terminal ASCII rendering of a :class:`Maze`."""

from maze_generator import Maze, Cell
from operator import add, sub
from functools import reduce


class MazeRenderer:
    """Render a :class:`Maze` as box-drawing characters in the terminal.

    The renderer turns each cell into a 3x1 character group and
    stitches the walls together using a lookup tree of 4-way
    junctions. Entry, exit, shortest path and "42" mask cells each
    have their own glyph, and the wall colour can be rotated through
    :attr:`palette`.

    Attributes:
        maze: The maze to display.
        palette: ANSI colour codes cycled by interaction ``3``.
        color_index: Index of the currently active colour in ``palette``.
        show_path: Whether the shortest path overlay is drawn.
    """

    def __init__(self, maze: Maze):
        """Prepare the glyph tree, palette and default display flags."""
        self.maze: Maze = maze
        self.tree = (
            (((' ', '•'), ('•', '╗')), (('•', '═'), ('╔', '╦'))),
            ((('•', '╝'), ('║', '╣')), (('╚', '╩'), ('╠', '╬')))
        )
        self.entry_char = '▓'
        self.exit_char = '░'
        self.path_char = '▒'
        self.mask_char = '█'
        self.y_len = len(maze.grid)
        self.x_len = len(maze.grid[0])
        self.palette: list[str] = [
            "\033[34m", "\033[32m", "\033[33m",
            "\033[31m", "\033[35m", "\033[36m",
        ]
        self.color_index: int = 0
        self.show_path: bool = False

    def render_maze(self) -> None:
        """Draw the maze on stdout with the active colour.

        Builds the full character grid (borders, walls, junctions,
        mask, path, entry, exit) and prints it row by row.
        """
        display = self.__gen_grid()
        self.__apply_walls(display)
        self.__apply_crossing(display)
        self.__add_mask(display)
        self.__add_path(display)
        self.__add_entry(display)
        self.__add_exit(display)
        for row in display:
            print(f"{self.palette[self.color_index]}{reduce(add, row)}\033[0m")

    def __add_entry(self, grid: list[list[str]]) -> None:
        """Overwrite the entry cell with the entry glyph."""
        entry = self.maze.entry

        grid[entry[1] * 2 + 1][entry[0] * 2 + 1] = self.entry_char * 3

    def __add_exit(self, grid: list[list[str]]) -> None:
        """Overwrite the exit cell with the exit glyph."""
        exit = self.maze.exit

        grid[exit[1] * 2 + 1][exit[0] * 2 + 1] = self.exit_char * 3

    def __add_path(self, grid: list[list[str]]) -> None:
        """Draw the shortest path, including links across opened walls."""
        prev = None

        for pos in self.maze.path:
            grid[pos[1] * 2 + 1][pos[0] * 2 + 1] = self.path_char * 3
            if prev is not None:
                direction = tuple(map(sub, pos, prev))
                y = (pos[1] * 2 + 1) - direction[1]
                x = (pos[0] * 2 + 1) - direction[0]
                grid[y][x] = self.path_char * 3 if x % 2 else self.path_char
            prev = pos

    def __add_mask(self, grid: list[list[str]]) -> None:
        """Fill every cell of the "42" pattern with the mask glyph."""
        for pos in self.maze.mask:
            grid[pos[1] * 2 + 1][pos[0] * 2 + 1] = self.mask_char * 3

    def __gen_grid(self) -> list[list[str]]:
        """Allocate the display grid and place external borders/junctions.

        Returns:
            A 2D list of strings sized ``(2H+1) x (2W+1)``, already
            filled with corner, border and inner junction glyphs.
        """
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

                display[y][x] = char * 3 if x % 2 else char

        return display

    def __apply_walls(self, grid: list[list[str]]) -> None:
        """Clear display cells where two neighbours share an open wall."""
        m_grid = self.maze.grid

        for y in range(self.y_len):

            for x in range(self.x_len):

                if (x < self.x_len - 1 and
                        not self.has_x_wall(m_grid[y][x], m_grid[y][x + 1])):
                    grid[y * 2 + 1][(x + 1) * 2] = self.tree[0][0][0][0]

                if (y < self.y_len - 1 and
                        not self.has_y_wall(m_grid[y][x], m_grid[y + 1][x])):
                    grid[(y + 1) * 2][x * 2 + 1] = self.tree[0][0][0][0] * 3

    def __apply_crossing(self, grid: list[list[str]]) -> None:
        """Pick the right junction glyph for each wall intersection.

        Uses the 4-bit N/E/S/W neighbour mask to index :attr:`tree`.
        """
        y_len = self.y_len * 2 + 1
        x_len = self.x_len * 2 + 1

        for y in range(y_len)[0:y_len:2]:
            for x in range(x_len)[0:x_len:2]:

                n = 1 if y != 0 and ' ' not in grid[y - 1][x] else 0
                s = 1 if y != y_len - 1 and ' ' not in grid[y + 1][x] else 0
                e = 1 if x != x_len - 1 and ' ' not in grid[y][x + 1] else 0
                w = 1 if x != 0 and ' ' not in grid[y][x - 1] else 0

                grid[y][x] = self.tree[n][e][s][w]

    @staticmethod
    def has_x_wall(west: Cell, east: Cell) -> bool:
        """Return True when two horizontally adjacent cells share a wall."""
        return bool(west & 2) and bool(east & 8)

    @staticmethod
    def has_y_wall(north: Cell, south: Cell) -> bool:
        """Return True when two vertically adjacent cells share a wall."""
        return bool(north & 4) and bool(south & 1)
