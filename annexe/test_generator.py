import pytest
from maze_generator.maze_generator import MazeGenerator
from maze_generator.maze import MazeOptions


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


# def main():
#     maze = Maze(
#         grid=[
#             [9, 1, 5, 1, 5, 5, 5, 1, 5, 5, 5, 3, d, 1, 5, 1, 5, 1, 5, 3],
#             [e, a, d, 0, 5, 5, 7, a, b, d, 3, c, 7, 8, 7, c, 7, c, 7, a],
#             [9, 0, 1, 4, 7, 9, 5, 0, 4, 1, 4, 1, 7, a, 9, 1, 1, 3, d, 2],
#             [a, e, e, d, 3, c, 7, c, 7, c, 3, e, d, 0, 0, 6, e, c, 7, a],
#             [8, 5, 5, 1, 4, 1, 5, 5, 1, 3, 8, 1, 3, a, 8, 7, 9, 5, 5, 2],
#             [8, 5, 7, c, 7, c, 7, b, a, e, e, e, e, a, a, 9, 2, b, 9, 2],
#             [8, 5, 5, 1, 5, 3, b, a, a, b, b, 9, 1, 2, e, a, e, a, a, a],
#             [8, 7, b, a, d, 4, 4, 2, a, c, 4, 6, e, a, 9, 4, 1, 2, e, a],
#             [8, 5, 6, 8, 1, 7, f, a, c, 7, f, f, f, a, c, 7, a, e, 9, 2],
#             [a, b, b, e, a, b, f, c, 5, 1, 5, 7, f, a, b, 9, 4, 3, e, a],
#             [8, 0, 4, 3, a, a, f, f, f, e, f, f, f, 8, 2, c, 7, e, d, 2],
#             [e, a, d, 6, e, a, b, b, f, b, f, d, 5, 2, 8, 7, 9, 3, 9, 2],
#             [9, 2, b, d, 1, 0, 0, 6, f, a, f, f, f, e, e, b, a, e, 8, 6],
#             [e, 8, 0, 5, 2, a, 8, 7, 9, 0, 7, b, 9, 1, 7, 8, 0, 5, 6, b],
#             [b, e, c, 7, e, e, a, d, 0, 0, 5, 0, 2, c, 7, a, c, 7, d, 2],
#             [c, 1, 1, 1, 1, 5, 4, 3, a, 8, 3, e, 8, 5, 1, 0, 5, 1, 5, 2],
#             [d, 2, a, 8, 4, 1, 3, a, a, a, e, 9, 0, 3, e, a, d, 0, 7, a],
#             [b, a, e, a, b, a, a, a, e, 8, 3, e, e, e, d, 6, b, e, 9, 2],
#             [8, 4, 3, e, a, e, e, 8, 7, a, e, b, b, 9, 1, 1, 4, 3, e, a],
#             [c, 7, c, 5, 4, 5, 5, 4, 5, 4, 5, 4, 4, 4, 4, 4, 7, e, d, 6],
#              ],
#         entry=(0, 0),
#         exit=(19, 19),
#         path=[
#               (0, 0), (1, 0), (1, 1), (1, 2), (0, 2), (0, 3), (0, 4), (0, 5),
#               (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (1, 10), (1, 11),
#               (1, 12), (1, 13), (2, 13), (3, 13), (4, 13), (4, 12), (5, 12),
#               (6, 12), (6, 13), (6, 14), (6, 15), (7, 15), (7, 16), (7, 17),
#               (7, 18), (7, 19), (8, 19), (9, 19), (9, 18), (9, 17), (9, 16),
#               (9, 15), (9, 14), (10, 14), (11, 14), (12, 14), (12, 15),
#               (13, 15), (14, 15), (15, 15), (16, 15), (17, 15), (18, 15),
#               (19, 15), (19, 16), (19, 17), (19, 18), (19, 19)
#             ],
#         mask=[
#             (6, 8), (6, 9), (6, 10), (7, 10), (8, 10), (8, 11), (8, 12),
#             (10, 8), (11, 8), (12, 8), (12, 9), (12, 10), (11, 10), (10, 10),
#             (10, 11), (10, 12), (11, 12), (12, 12)
#         ]
#     )
