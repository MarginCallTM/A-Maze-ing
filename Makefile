.PHONY: install run debug clean lint lint-strict

run:
	python3 a_maze_ing.py config.txt

install:
	pip install -r requirements-dev.txt


debug:
	python3 -m pdb a_maze_ing.py config.txt

build:
	python3 -m pip install --upgrade build setuptools wheel; python3 -m build

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
