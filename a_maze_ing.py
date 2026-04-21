import sys


def main() -> None:
    if not len(sys.argv) == 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]
    print(f"{config_file}")


if __name__ == "__main__":
    main()
