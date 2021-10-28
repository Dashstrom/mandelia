from .controller.controller import Controller
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        Controller()
    elif len(sys.argv) == 2:
        Controller(path=sys.argv[1])
    else:
        raise ValueError("Take only one optional argument")
