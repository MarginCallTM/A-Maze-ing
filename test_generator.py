import pytest
from maze_generator import MazeGenerator
from Maze import MazeOptions

maze = MazeGenerator(4, 4, 42)
maze.generate()

def make_generator(
    width: int = 10, height: int = 10, seed: int = 42
) -> MazeGenerator:
    options = MazeOptions(
        width=width,
        height=height,
        entry=(0, 0),
        exit=(width - 1, height - 1),
        output_file="test.txt",
        perfect=True,
        seed=str(seed),
    )
    return MazeGenerator(options)


def test_grid_dimensions() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    assert len(gen.grid) == 10
    for row in gen.grid:
        assert len(row) == 10


def test_cell_values_in_range() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        for x in range(gen.width):
            cell = gen.grid[y][x]
            assert 0 <= cell <= 15


def test_border_walls_north() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    for x in range(gen.width):
        assert gen.grid[0][x] & 1 != 0


def test_border_walls_south() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    for x in range(gen.width):
        assert gen.grid[gen.height - 1][x] & 4 != 0


def test_border_walls_west() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        assert gen.grid[y][0] & 8 != 0


def test_border_walls_east() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        assert gen.grid[y][gen.width - 1] & 2 != 0


def test_wall_coherence_horizontal() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        for x in range(gen.width - 1):
            cell_left = gen.grid[y][x]
            cell_right = gen.grid[y][x + 1]
            left_has_east = (cell_left & 2) != 0
            right_has_west = (cell_right & 8) != 0
            assert left_has_east == right_has_west


def test_full_connectivity() -> None:
    gen = make_generator(10, 10, 42)
    gen.generate()
    visited = [[False] * gen.width for _ in range(gen.height)]
    stack = [(0, 0)]
    visited[0][0] = True
    count = 0

    while stack:
        x, y = stack.pop()
        count += 1
        # Nord : pas de mur et pas hors grille
        if gen.grid[y][x] & 1 == 0 and y > 0:
            if not visited[y - 1][x]:
                visited[y - 1][x] = True
                stack.append((x, y - 1))
        # Est
        if gen.grid[y][x] & 2 == 0 and x < gen.width - 1:
            if not visited[y][x + 1]:
                visited[y][x + 1] = True
                stack.append((x + 1, y))
        # Sud
        if gen.grid[y][x] & 4 == 0 and y < gen.height - 1:
            if not visited[y + 1][x]:
                visited[y + 1][x] = True
                stack.append((x, y + 1))
        # Ouest
        if gen.grid[y][x] & 8 == 0 and x > 0:
            if not visited[y][x - 1]:
                visited[y][x - 1] = True
                stack.append((x - 1, y))

    assert count == gen.width * gen.height - len(gen.pattern_cells)


# === TESTS SOLVE ===

class TestSolve:

    def setup_method(self) -> None:
        self.gen = make_generator(10, 10, 42)
        self.gen.generate()
        self.entry = (0, 0)
        self.exit = (9, 9)
        self.path, self.directions = self.gen.solve(self.entry, self.exit)

    def test_path_starts_at_entry(self) -> None:
        assert self.path[0] == self.entry

    def test_path_ends_at_exit(self) -> None:
        assert self.path[-1] == self.exit

    def test_path_no_wall_crossing(self) -> None:
        """Le chemin ne traverse aucun mur."""
        direction_to_wall = {
            (0, -1): 1,   # Nord
            (1, 0): 2,    # Est
            (0, 1): 4,    # Sud
            (-1, 0): 8,   # Ouest
        }
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            dx, dy = x2 - x1, y2 - y1
            wall = direction_to_wall[(dx, dy)]
            assert self.gen.grid[y1][x1] & wall == 0

    def test_path_steps_are_adjacent(self) -> None:
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            dist = abs(x2 - x1) + abs(y2 - y1)
            assert dist == 1

    def test_directions_match_path(self) -> None:
        dir_map = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        assert len(self.directions) == len(self.path) - 1
        for i, letter in enumerate(self.directions):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            dx, dy = dir_map[letter]
            assert (x1 + dx, y1 + dy) == (x2, y2)

    def test_directions_only_valid_chars(self) -> None:
        valid = set("NESW")
        for char in self.directions:
            assert char in valid


# === Test 42 Pattern ===

class TestPattern42:

    def test_has_forty_two_true_when_large_enough(self) -> None:
        gen = make_generator(9, 7, 42)
        assert gen.has_forty_two is True
        assert len(gen.pattern_cells) > 0

    def test_has_forty_two_false_when_too_small(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        gen = make_generator(8, 6, 42)
        assert gen.has_forty_two is False
        assert gen.pattern_cells == set()
        captured = capsys.readouterr()
        assert "too small" in captured.err

    def test_pattern_cells_are_closed(self) -> None:
        gen = make_generator(20, 15, 42)
        gen.generate()
        path, directions = gen.solve((0, 0), (19, 14))
        assert path[0] == (0, 0)
        assert path[-1] == (19, 14)
        assert len(directions) == len(path) - 1
