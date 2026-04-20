from maze_generator import MazeGenerator, PATTERN_42
from Maze import MazeOptions


def make_generator(width=10, height=10, seed=42):
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


def test_grid_dimensions():
    gen = make_generator(10, 10, 42)
    gen.generate()
    assert len(gen.grid) == 10
    for row in gen.grid:
        assert len(row) == 10


def test_cell_values_in_range():
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        for x in range(gen.width):
            cell = gen.grid[y][x]
            assert 0 <= cell <= 15


def test_border_walls_north():
    gen = make_generator(10, 10, 42)
    gen.generate()
    for x in range(gen.width):
        assert gen.grid[0][x] & 1 != 0


def test_border_walls_south():
    gen = make_generator(10, 10, 42)
    gen.generate()
    for x in range(gen.width):
        assert gen.grid[gen.height - 1][x] & 4 != 0


def test_border_walls_west():
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        assert gen.grid[y][0] & 8 != 0


def test_border_walls_east():
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        assert gen.grid[y][gen.width - 1] & 2 != 0


def test_wall_coherence_horizontal():
    gen = make_generator(10, 10, 42)
    gen.generate()
    for y in range(gen.height):
        for x in range(gen.width - 1):
            cell_left = gen.grid[y][x]
            cell_right = gen.grid[y][x + 1]
            left_has_east = (cell_left & 2) != 0
            right_has_west = (cell_right & 8) != 0
            assert left_has_east == right_has_west


def test_full_connectivity():
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

    assert count == gen.width * gen.height


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


# === TESTS PATTERN 42 ===

class TestPattern42:

    def setup_method(self) -> None:
        self.gen = make_generator(20, 15, 42)
        self.gen.generate()
        self.gen.apply_pattern_42()
        self.start_x = (self.gen.width - 7) // 2
        self.start_y = (self.gen.height - 5) // 2

    def test_pattern_cells_are_closed(self) -> None:
        """Chaque cellule du pattern vaut 15 (tous les murs)."""
        for py in range(len(PATTERN_42)):
            for px in range(len(PATTERN_42[0])):
                if PATTERN_42[py][px] == 1:
                    gx = self.start_x + px
                    gy = self.start_y + py
                    assert self.gen.grid[gy][gx] == 15

    def test_pattern_wall_coherence_horizontal(self) -> None:
        """Coherence Est/Ouest respectee apres le pattern."""
        for y in range(self.gen.height):
            for x in range(self.gen.width - 1):
                left_has_east = (self.gen.grid[y][x] & 2) != 0
                right_has_west = (self.gen.grid[y][x + 1] & 8) != 0
                assert left_has_east == right_has_west

    def test_pattern_wall_coherence_vertical(self) -> None:
        """Coherence Sud/Nord respectee apres le pattern."""
        for y in range(self.gen.height - 1):
            for x in range(self.gen.width):
                top_has_south = (self.gen.grid[y][x] & 4) != 0
                bottom_has_north = (self.gen.grid[y + 1][x] & 1) != 0
                assert top_has_south == bottom_has_north

    def test_maze_solvable_after_pattern(self) -> None:
        """Le labyrinthe reste resolvable apres le pattern."""
        path, directions = self.gen.solve((0, 0), (19, 14))
        assert path[0] == (0, 0)
        assert path[-1] == (19, 14)
        assert len(directions) == len(path) - 1
