import random


class MazeGenerator():
    def __init__(self, width: int, height: int, seed: int) -> None:
        self.width = width
        self.height = height
        self.seed = seed
        random.seed(seed)
        self.grid = [[15 for i in range(width)] for i in range(height)]

    def _get_unvisited_neighbors(
            self, x: int, y: int, visited: list[list[bool]]) -> list[tuple[int, int]]:
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not visited[ny][nx]:
                    neighbors.append((nx, ny))
        return neighbors

    def _remove_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        if y2 < y1:  # North
            self.grid[y1][x1] &= ~1
            self.grid[y2][x2] &= ~4
        elif x2 > x1:  # East
            self.grid[y1][x1] &= ~2
            self.grid[y2][x2] &= ~8
        elif y2 > y1:  # South
            self.grid[y1][x1] &= ~4
            self.grid[y2][x2] &= ~1
        elif x2 < x1:  # West
            self.grid[y1][x1] &= ~8
            self.grid[y2][x2] &= ~2

    def generate(self) -> list[list[int]]:
        visited = [[False for i in range(self.width)]
                   for i in range(self.height)]
        stack = []
        start_x, start_y = 0, 0
        visited[start_y][start_x] = True
        stack.append((start_x, start_y))

        while stack:
            x, y = stack[-1]
            neighbors = self._get_unvisited_neighbors(x, y, visited)
            if neighbors:
                nx, ny = random.choice(neighbors)
                self._remove_wall(x, y, nx, ny)
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        return self.grid
