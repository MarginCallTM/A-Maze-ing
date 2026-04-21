from maze import Maze, Cell
from operator import add
from functools import reduce


class MazeRenderer:

    def __init__(self, maze: Maze):
        self.maze: Maze = maze
        self.tree = (
            (((' ', '•'), ('•', '╗')), (('•', '═'), ('╔', '╦'))),
            ((('•', '╝'), ('║', '╣')), (('╚', '╩'), ('╠', '╬')))
        )
        self.y_len = len(maze.grid)
        self.x_len = len(maze.grid[0])

    def render_maze(self) -> None:

        display = self.__gen_grid()
        display = self.__apply_walls(display)
        display = self.__apply_crossing(display)
        for row in display:
            print(reduce(add, row))

    def __gen_grid(self,) -> list[list[str]]:

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

    def __apply_walls(self, grid: list[list[str]]) -> list[list[str]]:

        m_grid = self.maze.grid

        for y in range(self.y_len):

            for x in range(self.x_len):

                if (x < self.x_len - 1 and
                        not self.has_x_wall(m_grid[y][x], m_grid[y][x + 1])):
                    grid[y * 2 + 1][(x + 1) * 2] = " "

                if (y < self.y_len - 1 and
                        not self.has_y_wall(m_grid[y][x], m_grid[y + 1][x])):
                    grid[(y + 1) * 2][x * 2 + 1] = "   "

        return grid

    def __apply_crossing(self, grid: list[list[str]]) -> list[list[str]]:

        for y in range(self.y_len * 2 + 1)[2:self.y_len * 2 - 1:2]:

            for x in range(self.x_len * 2 + 1)[2:self.x_len * 2 - 1:2]:

                north = 1 if ' ' not in grid[y - 1][x] else 0
                south = 1 if ' ' not in grid[y + 1][x] else 0
                east = 1 if ' ' not in grid[y][x + 1] else 0
                west = 1 if ' ' not in grid[y][x - 1] else 0

                grid[y][x] = self.tree[north][east][south][west]

        return grid

    @staticmethod
    def has_x_wall(west: Cell, east: Cell) -> bool:
        return bool(west & 2) and bool(east & 8)

    @staticmethod
    def has_y_wall(north: Cell, south: Cell) -> bool:
        return bool(north & 4) and bool(south & 1)
