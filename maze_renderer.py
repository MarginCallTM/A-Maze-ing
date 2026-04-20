from maze import Maze, Cell, PositiveInt


class MazeRenderer:

    def __init__(self, maze: Maze):
        self.maze: Maze = maze
        self.tree = (
            (((' ', '•'), ('•', '┐')), (('•', '─'), ('┌', '┬'))),
            ((('•', '┘'), ('│', '├')), (('└', '┴'), ('┤', '┼')))
        )

    def render_maze(self) -> None:

        m = self.maze.maze

        y_len = len(m)
        x_len = len(m[0])
        wall_line = ""
        for x in range(x_len):
            corner = self.__get_extern_corner(x, 0)
            x_wall = " "
            wall_line += x_wall + corner

        print(wall_line)

        for y in range(y_len):
            cell_line = ""
            wall_line = ""
            for x in range(x_len):
                if 0 <= x < (x_len - 1) and 0 <= y < (y_len - 1):
                    corner = self.__get_corner(m[y][x], m[y][x + 1],
                                               m[y + 1][x], m[y + 1][x + 1])
                else:
                    corner = self.__get_extern_corner(x, y)

                if 0 < x < (x_len - 1) and y < y_len - 1:
                    x_wall = self.__get_x_wall(m[y][x], m[y + 1][x])
                else:
                    x_wall = " "

                if 0 < y < (y_len - 1) and x < x_len - 1:
                    y_wall = self.__get_y_wall(m[y][x], m[y + 1][x])
                else:
                    y_wall = " "

                cell_line += "0" + y_wall
                wall_line += x_wall + corner
            print(cell_line)
            print(wall_line)

    def __get_corner(self, top_left: Cell, top_right: Cell, bottom_left: Cell,
                     bottom_right: Cell) -> str:
        top = int(self.is_x_connected(top_left, top_right))
        right = int(self.is_y_connected(top_right, bottom_right))
        bottom = int(self.is_x_connected(bottom_left, bottom_right))
        left = int(self.is_y_connected(top_left, bottom_left))

        return self.tree[top][right][bottom][left]

    def __get_extern_corner(self, x: PositiveInt, y: PositiveInt) -> str:

        m = self.maze.maze

        y_len = len(m)
        x_len = len(m[0])

        if x == 0 and y == 0:
            return self.__get_corner(0, 15, 15, m[y][x])
        elif x == 0 and y == y_len - 1:
            return self.__get_corner(15, m[y][x], 15, 0)
        elif y == 0 and x == x_len - 1:
            return self.__get_corner(15, 15, m[y][x], 0)
        elif x == x_len - 1 and y == y_len - 1:
            return self.__get_corner(m[y][x], 15, 15, 0)
        elif x == x_len - 1:
            return self.__get_corner(m[y][x], 8, m[y + 1][x], 8)
        elif y == y_len - 1:
            return self.__get_corner(m[y][x], m[y][x + 1], 1, 1)
        elif x == 0:
            return self.__get_corner(2, m[y][x], 2, m[y + 1][x])
        elif y == 0:
            return self.__get_corner(4, 4, m[y][x], m[y][x + 1])
        else:
            return "8"

    def __get_x_wall(self, top: Cell, bottom: Cell) -> str:
        if self.is_y_connected(top, bottom):
            return self.tree[0][1][0][1]
        else:
            return self.tree[0][0][0][0]

    def __get_y_wall(self, left: Cell, right: Cell) -> str:
        if self.is_x_connected(left, right):
            return self.tree[1][0][1][0]
        else:
            return self.tree[0][0][0][0]

    @staticmethod
    def is_x_connected(west: Cell, east: Cell) -> bool:
        return bool(west & 8) and bool(east & 2)

    @staticmethod
    def is_y_connected(north: Cell, south: Cell) -> bool:
        return bool(north & 4) and bool(south & 1)

