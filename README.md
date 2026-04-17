*This project has been created as part of the 42 curriculum by acombier, *

# A-Maze-ing

Maze generator in Python with visual display and reusable module.

> Work in progress — this README will be updated as the project evolves.

## Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
make install
```

## Makefile commands

| Command | Description |
|---|---|
| `make install` | Install project dependencies |
| `make run` | Run the program with `config.txt` |
| `make debug` | Run in debug mode (pdb) |
| `make clean` | Remove cache files (`__pycache__`, `.mypy_cache`, etc.) |
| `make lint` | Run flake8 + mypy with mandatory flags |
| `make lint-strict` | Run flake8 + mypy in strict mode |
