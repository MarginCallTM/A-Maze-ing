*This project has been created as part of the 42 curriculum by acombier, qdescomb.*

# A-Maze-ing

> Work in progress — this README will be updated as the project evolves.

## Description

A-Maze-ing is a maze generator written in Python. Given a configuration
file, the program generates a random maze (optionally *perfect*), solves
it to find the shortest path between the entry and the exit, and writes
the result to an output file in a hexadecimal wall representation.

The maze also contains a visible `42` pattern drawn with fully closed
cells, as required by the 42 curriculum.

A visual representation (terminal ASCII) is provided to display the maze,
the solution path, and the `42` pattern, with basic user interactions.

The generation logic is encapsulated in a standalone, reusable Python
module (`mazegen`), designed to be importable in future projects.

## Instructions

### Installation

```bash
# Clone the repository
git clone <repo_url> A-Maze-ing && cd A-Maze-ing

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dev dependencies
make install
```

### Execution

```bash
# Run the program with the default config file
make run
# equivalent to: python3 a_maze_ing.py config.txt

# Run in debug mode (pdb)
make debug

# Run the test suite
python3 -m pytest test_generator.py -v
```

### Quality checks

```bash
make lint         # flake8 + mypy with mandatory flags
make lint-strict  # flake8 + mypy --strict
make clean        # remove caches (__pycache__, .mypy_cache, etc.)
```

## Resources

### References

- Jamis Buck, *Mazes for Programmers* — comprehensive reference on maze
  generation and solving algorithms.
- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Wikipedia — Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Pydantic documentation](https://docs.pydantic.dev/) — used for
  configuration validation.

### AI usage

AI (Claude) was used as a collaborative pair-programmer on the following
tasks, always with a human review-and-rewrite loop:

- Brainstorming algorithm choices and trade-offs (DFS vs. Prim vs.
  Kruskal).
- Reviewing code for norm compliance (flake8, mypy) and suggesting
  refactors (e.g., factoring out dead code in the `42` pattern
  implementation).
- Drafting test cases (boundary tests, connectivity, pattern invariants).
- Explaining Python-specific idioms (set comprehensions, type hints,
  Pydantic validators) to support live-evaluation readiness.

All AI-generated code was reviewed, understood, and rewritten by hand
before being committed — following the learner rules described in the
subject.

## Configuration file format

The configuration file uses `KEY=VALUE` pairs, one per line. Lines
starting with `#` are comments and are ignored.

### Mandatory keys

| Key           | Description                      | Example                  |
|---------------|----------------------------------|--------------------------|
| `WIDTH`       | Maze width (number of cells)     | `WIDTH=20`               |
| `HEIGHT`      | Maze height (number of cells)    | `HEIGHT=15`              |
| `ENTRY`       | Entry coordinates `(x, y)`       | `ENTRY=0,0`              |
| `EXIT`        | Exit coordinates `(x, y)`        | `EXIT=19,14`             |
| `OUTPUT_FILE` | Path of the output file          | `OUTPUT_FILE=maze.txt`   |
| `PERFECT`     | Whether the maze is perfect      | `PERFECT=True`           |

### Optional keys

| Key            | Description                               | Example          |
|----------------|-------------------------------------------|------------------|
| `SEED`         | Seed for random generation (reproducible) | `SEED=42`        |
| `ALGORITHM`    | Generation algorithm to use               | `ALGORITHM=DFS`  |
| `DISPLAY_MODE` | Visual display mode                       | `DISPLAY_MODE=ascii` |

A default `config.txt` is provided at the root of the repository.

### Constraints

- `WIDTH` and `HEIGHT` must be at least `3`.
- `ENTRY` and `EXIT` must be distinct, within maze bounds, and lie on
  valid cells (not inside the `42` pattern).
- If the maze size is too small to fit the `42` pattern (currently
  `WIDTH >= 9` and `HEIGHT >= 7`), the pattern is omitted and a warning
  is printed on `stderr`.

## Algorithm

### Generation — DFS Recursive Backtracker

The maze is generated using the **DFS Recursive Backtracker** algorithm
(iterative implementation with an explicit stack).

**Why this algorithm?**

- **Perfect mazes by construction.** The DFS explores every cell exactly
  once and only removes the wall between a visited cell and its unvisited
  neighbor. The resulting structure is a spanning tree over the cells,
  guaranteeing exactly one path between any two cells — which directly
  satisfies the `PERFECT=True` requirement.
- **No large open areas.** Because the output is a tree (no cycles),
  there is no way to have a `3x3` open area — cycles are required for
  that. The `2x3` / `3x2` maximum corridor constraint is therefore
  respected by construction.
- **Simple and deterministic.** Seeding `random` with `SEED` makes the
  generation fully reproducible, which is required by the subject and
  essential for debugging and testing.
- **Naturally integrates the `42` pattern.** Pattern cells are marked
  `visited=True` before the DFS starts, so the algorithm simply skips
  them. They remain fully closed (walls value `15`), and the rest of the
  maze forms a connected spanning tree around the pattern.

### Solving — Breadth-First Search

The shortest path between the entry and the exit is computed with a
classic BFS. BFS is guaranteed to find the shortest path in an unweighted
graph, which is exactly what we have (each cell connects to its open
neighbors with uniform cost). The path is encoded as a string of `N`,
`E`, `S`, `W` letters, as required by the subject.

### The `42` pattern

The pattern is a `7x5` binary matrix (`PATTERN_42`) where `1` marks a
cell that must be fully closed. It is centered in the maze at
`((width - 7) // 2, (height - 5) // 2)`. The `MazeGenerator` exposes
`self.pattern_cells: set[tuple[int, int]]` — the absolute coordinates
of the pattern cells — so that the visual display code can colour them
distinctively.

## Reusable module

The maze generation logic is encapsulated in the `MazeGenerator` class
inside `maze_generator.py`. It is designed to be built and distributed
as a standalone, pip-installable package named `mazegen-*` (`.whl` or
`.tar.gz`), placed at the root of this Git repository.

### Minimal usage example

```python
from maze_generator import MazeGenerator
from Maze import MazeOptions

options = MazeOptions(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    output_file="maze.txt",
    perfect=True,
    seed="42",
)

gen = MazeGenerator(options)
gen.generate()                              # builds the maze
path, directions = gen.solve((0, 0), (19, 14))

# Public attributes:
gen.grid            # list[list[int]] — walls encoded in hex
gen.pattern_cells   # set[tuple[int, int]] — '42' pattern cells
gen.has_forty_two   # bool — whether the pattern was applied
```

### Package build

*Section to be completed once the package build is implemented
(Phase 3).*

## Team & Project management

### Roles

- **Adrien Combier (`acombier`)** — maze generation algorithm (DFS),
  solver (BFS), `42` pattern integration, test suite for the generator.
- **Quentin Descombes (`qdescomb`)** — configuration file parsing,
  output file writer (hexadecimal format), visual representation
  (terminal ASCII).

### Planning and how it evolved

- **Initial plan.** Follow the order suggested by the subject:
  Phase 0 → 1.1 → 1.2 → 1.4 → 1.5 → 2 → 1.3 → 3 → 4 → 5 → 6.
- **Actual evolution.** We started with Phase 0 (setup) and immediately
  split the work along a clear interface: one team member builds the
  `MazeGenerator` class (grid, solver, pattern), the other builds the
  user-facing pipeline (parsing, output, display). This let us work in
  parallel without stepping on each other.
- **Scope adjustment.** The output file step (Phase 1.5) was initially
  a shared task; we reassigned it to the parsing/display team member
  to consolidate the "I/O side" of the project in one place.
- **Pattern `42`.** Initially developed as an experimental feature with
  a pre- and post-DFS cleanup. A code review revealed the post-DFS step
  was a no-op; we rewrote the implementation cleanly (pattern cells
  marked visited before the DFS, single source of truth via
  `pattern_cells`).

### What worked well

- Splitting the work around a clear class interface (`MazeGenerator`
  exposing `grid`, `pattern_cells`, `solve()`) allowed the two team
  members to progress in parallel without merge conflicts.
- Writing the test suite alongside the generator caught the `42`
  pattern mis-implementation early.
- Static analysis (flake8 + mypy) enforced from Phase 0 avoided
  accumulating debt.

### What could be improved

- The main entry point (`a_maze_ing.py`) remained a skeleton too long;
  wiring it end-to-end earlier would have surfaced integration issues
  sooner.
- The `42` pattern was rewritten once due to an over-engineered first
  draft — a whiteboard of the invariants before coding would have
  avoided the detour.

### Tools used

- **Language.** Python 3.10+
- **Validation.** Pydantic (configuration and data models)
- **Testing.** pytest (17 tests covering dimensions, borders, wall
  coherence, connectivity, solver, `42` pattern)
- **Linting.** flake8, mypy (mandatory flags + `--strict` available)
- **Environment.** venv
- **AI.** Claude (collaborative pair-programming, always with human
  review — see *AI usage* section above)
- **Version control.** Git / GitHub
