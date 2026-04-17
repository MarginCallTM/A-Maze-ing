from maze_generator import MazeGenerator

maze = MazeGenerator(4, 4, 42)
maze.generate()

for row in maze.grid:
    print(row)
