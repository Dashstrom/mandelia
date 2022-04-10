import sys

from .controller.controller import Controller


def main():
    if len(sys.argv) == 1:
        ctrl = Controller()
    elif len(sys.argv) == 2:
        ctrl = Controller(path=sys.argv[1])
    else:
        raise ValueError("Take only one optional argument")
    ctrl.run()


if __name__ == "__main__":
    main()
