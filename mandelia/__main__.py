"""File call when module is called as script."""
import sys

from .controller.controller import Controller


def main() -> None:
    """Run Controller from sys.argv."""
    if len(sys.argv) == 1:
        Controller()
    elif len(sys.argv) == 2:
        Controller(path=sys.argv[1])
    else:
        raise ValueError("Take only one optional argument")


if __name__ == "__main__":
    main()
