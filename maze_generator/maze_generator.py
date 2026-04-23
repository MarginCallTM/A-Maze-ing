import random
import sys
from collections import deque
from .maze import MazeOptions, Maze
from typing import Self


PATTERN_42 = [
    [1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],
]
"""Bitmap of the '42' logo. 1 = cell stays fully closed (wall=15)."""


class MazeGenerator():
    """Build, solve and serialize a maze from a :class:`MazeOptions`.

    The generator uses an iterative depth-first search (recursive
    backtracker) to carve a spanning tree, optionally breaks some
    extra walls when ``perfect`` is False, then finds the shortest
    path between entry and exit with a BFS."""

    def __init__(self, options: MazeOptions) -> None:
        """Initialize the generator state from validated options.

        Seeds the RNG, allocates a grid of fully-closed cells (value
        15) and computes the centered "42" pattern cells when the
        maze is large enough. Prints a warning on stderr otherwise.
        """
        self.width = options.width
        self.height = options.height
        self.entry = options.entry
        self.exit = options.exit
        self.perfect = options.perfect
        random.seed(options.seed)
        self.grid = [[15 for i in range(self.width)]
                     for i in range(self.height)]
        pattern_h = len(PATTERN_42)
        pattern_w = len(PATTERN_42[0])
        self.has_forty_two: bool = (
            self.width >= pattern_w + 2 and self.height >= pattern_h + 2
        )
        self.pattern_cells: set[tuple[int, int]] = set()
        self.output_file = options.output_file

        if self.has_forty_two:
            start_x = (self.width - pattern_w) // 2
            start_y = (self.height - pattern_h) // 2
            self.pattern_cells = {
                (start_x + px, start_y + py)
                for py in range(pattern_h)
                for px in range(pattern_w)
                if PATTERN_42[py][px] == 1
            }
        else:
            print(
                f"Warning: maze size ({self.width}x{self.height})"
                f"too small for '42' pattern, logo",
                file=sys.stderr
            )

        # Raise avec MazeError

    @classmethod
    def from_config_file(cls, config_file: str) -> Self:
        """Build a generator from a ``KEY=VALUE`` configuration file.

        Parses the file, coerces values (``True``/``False``, tuples,
        ints) and delegates final validation to :class:`MazeOptions`.
        Lines starting with ``#`` and blank lines are ignored.
        """
        MANDATORY_KEYS = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE',
                          'PERFECT']
        OPTIONAL_KEYS = ['SEED']

        config = {}

        with open(config_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)

                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif ',' in value:
                        try:
                            value = tuple(int(v) for v in value.split(','))
                        except ValueError:
                            pass
                    else:
                        try:
                            value = int(value)
                        except ValueError:
                            pass

                    config[key.lower()] = value

        missing = [key for key in MANDATORY_KEYS if key.lower() not in config]
        if missing:
            raise ValueError(f"Missing mandatory config keys: {missing}")

        known_keys = set(MANDATORY_KEYS + OPTIONAL_KEYS)

        for key in [key for key in config if key.upper() not in known_keys]:
            del config[key]

        print(config)

        options = MazeOptions(**config)

        return cls(options)

    def _get_unvisited_neighbors(
        self, x: int, y: int, visited: list[list[bool]]
    ) -> list[tuple[int, int]]:
        """Return the in-bounds, not-yet-visited neighbors of ``(x, y)``.
        Returns:
            List of ``(x, y)`` neighbor coordinates, in N/E/S/W order.
        """
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not visited[ny][nx]:
                    neighbors.append((nx, ny))
        return neighbors

    def _remove_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Open the wall shared by two adjacent cells.

        Updates both cells to keep the grid coherent (the two sides
        of a wall must always agree).
        """
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

    def _add_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Close the wall shared by two adjacent cells.

        Inverse operation of :meth:`_remove_wall`, kept coherent on
        both sides of the wall.
        """
        if y2 < y1:
            self.grid[y1][x1] |= 1
            self.grid[y2][x2] |= 4
        elif x2 > x1:
            self.grid[y1][x1] |= 2
            self.grid[y2][x2] |= 8
        elif y2 > y1:
            self.grid[y1][x1] |= 4
            self.grid[y2][x2] |= 1
        elif x2 < x1:
            self.grid[y1][x1] |= 8
            self.grid[y2][x2] |= 2

    def _would_create_3x3_open(
            self, x1: int, y1: int, x2: int, y2: int
    ) -> bool:
        """
        Temporarily opens the wall, scans the few 3x3 regions that
        could become open, then restores the wall. The subject forbids
        any 3x3 open area in the final maze.
        """
        self._remove_wall(x1, y1, x2, y2)
        xmin, xmax = min(x1, x2), max(x1, x2)
        ymin, ymax = min(y1, y2), max(y1, y2)
        result = False
        for X in range(max(0, xmax - 2), min(self.width - 3, xmin) + 1):
            for Y in range(max(0, ymax - 2), min(self.height - 3, ymin) + 1):
                if self._is_3x3_open(X, Y):
                    result = True
        self._add_wall(x1, y1, x2, y2)
        return result

    def _is_3x3_open(self, X: int, Y: int) -> bool:
        """Test whether the 3x3 block with top-left ``(X, Y)`` is fully open.

        A 3x3 block is open when none of its internal vertical or
        horizontal walls are closed.

        Returns:
            True if all internal walls of the block are open.
        """
        for dx in range(2):
            for dy in range(3):
                if self.grid[Y + dy][X + dx] & 2:
                    return False
        for dx in range(3):
            for dy in range(2):
                if self.grid[Y + dy][X + dx] & 4:
                    return False
        return True

    def _imperfect(self) -> None:
        """Break roughly 10% of internal walls to create multiple paths.

        Only walls whose removal does not create a 3x3 open area and
        whose two cells are outside the "42" pattern are eligible.
        Must be called after :meth:`generate`.
        """
        candidates = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                if (x + 1 < self.width
                        and (x + 1, y) not in self.pattern_cells
                        and self.grid[y][x] & 2):
                    candidates.append((x, y, x + 1, y))
                if (y + 1 < self.height
                        and (x, y + 1) not in self.pattern_cells
                        and self.grid[y][x] & 4):
                    candidates.append((x, y, x, y + 1))
        random.shuffle(candidates)
        target = max(1, len(candidates) // 10)
        removed = 0
        for x1, y1, x2, y2 in candidates:
            if removed >= target:
                break
            if not self._would_create_3x3_open(x1, y1, x2, y2):
                self._remove_wall(x1, y1, x2, y2)
                removed += 1

    def generate(self) -> list[list[int]]:
        """Carve the maze with an iterative DFS (recursive backtracker).

        Starts at ``(0, 0)``, treats "42" pattern cells as pre-visited
        so they stay fully closed, and carves a spanning tree over the
        remaining cells. Mutates ``self.grid`` in place.

        Returns:
            The resulting grid (same reference as ``self.grid``).
        """
        visited = [[False for i in range(self.width)]
                   for i in range(self.height)]
        for (x, y) in self.pattern_cells:
            visited[y][x] = True

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

    def solve(self, entry: tuple[int, int], exit_pos: tuple[int,
              int]) -> tuple[list[tuple[int, int]], str]:
        """Compute the shortest path between two cells using BFS.

        Returns:
            A tuple ``(path, directions)`` where ``path`` is the
            ordered list of cells from entry to exit and
            ``directions`` is the corresponding ``N``/``E``/``S``/``W``
            string.
        """
        visited = [[False for i in range(self.width)]
                   for i in range(self.height)]
        came_from = {}
        queue: deque[tuple[int, int]] = deque()

        start_x, start_y = entry
        visited[start_y][start_x] = True
        queue.append((start_x, start_y))

        directions = {
            (0, -1): ("N", 1),
            (1, 0): ("E", 2),
            (0, 1): ("S", 4),
            (-1, 0): ("W", 8),
        }

        while queue:
            x, y = queue.popleft()
            if (x, y) == exit_pos:
                break
            for (dx, dy), (direction, wall_bit) in directions.items():
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not visited[ny][nx] and self.grid[y][x] & wall_bit == 0:
                        visited[ny][nx] = True
                        came_from[(nx, ny)] = (x, y)
                        queue.append((nx, ny))

        path_coords = []
        current = exit_pos
        while current != entry:
            path_coords.append(current)
            current = came_from[current]
        path_coords.append(entry)
        path_coords.reverse()

        path_directions = ""
        for i in range(len(path_coords) - 1):
            x1, y1 = path_coords[i]
            x2, y2 = path_coords[i + 1]
            dx, dy = x2 - x1, y2 - y1
            for (ddx, ddy), (direction, _) in directions.items():
                if dx == ddx and dy == ddy:
                    path_directions += direction
                    break
        return path_coords, path_directions

    def build(self) -> Maze:
        """Run the full pipeline and return a :class:`Maze` instance.

        Generates the maze, optionally breaks walls when
        ``perfect=False``, solves it, and packages everything into a
        :class:`Maze`. Not idempotent: a second call on the same
        instance will solve the already-generated grid without
        re-carving it.

        Returns:
            A fully populated :class:`Maze`.
        """
        self.generate()
        if not self.perfect:
            self._imperfect()
        path_coords, path_directions = self.solve(self.entry, self.exit)
        return Maze(
            grid=self.grid,
            entry=self.entry,
            exit=self.exit,
            path=path_coords,
            mask=list(self.pattern_cells),
            path_directions=path_directions,
        )

    @staticmethod
    def write_maze(maze: Maze, output_file: str) -> None:
        """Serialize a :class:`Maze` to the subject's output format.

        Writes one hex digit per cell (bit 0 N, bit 1 E, bit 2 S,
        bit 3 W; 1 = wall closed), one row per line, then an empty
        line followed by the entry coordinates, the exit coordinates
        and the N/E/S/W path string. Every line ends with ``\\n``.
        """
        with open(output_file, "w") as f:
            for row in maze.grid:
                line = "".join(f"{cell:X}" for cell in row)
                f.write(line + "\n")
            f.write("\n")
            f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
            f.write(f"{maze.exit[0]},{maze.exit[1]}\n")
            f.write(f"{maze.path_directions}\n")