#
#   Simple console UI for Digi-Salama Assemblin project.
#
import sys
from core import Core
import logging


def main():
    # setup logging
    logging.basicConfig(\
        format="%(asctime)s:%(levelname)s:%(message)s", \
        datefmt='%d/%m/%Y %H:%M:%S',  \
        filename="general.log", \
        filemode="w", \
        level=logging.INFO)

    # errors go to both general and error log
    logger = logging.getLogger('')
    error_handler = logging.FileHandler('error.log', 'w')
    error_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s", datefmt='%d/%m/%Y %H:%M:%S'))
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    # on screen logging, also known as spam
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s:%(message)s", datefmt='%d/%m/%Y %H:%M:%S'))
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    core = None
    _print_info()

    while True:
        user_input = input("\n>")

        if (user_input == "exit"):
            print("\nExiting soon...\n")
            if (core is not None):
                core.stop()
            sys.exit()
        elif (user_input == 'start'):
            core = Core()
            print("Starting process.")
            core.start()
        elif (user_input == 'stop'):
            print("Stopping process.")
            core.stop()
        else:
            _print_info()

def _print_info():
        print("Digi-Salama Assemblin project software")
        print("Available commands:")
        print("   start - start the process")
        print("   stop  - stop the process")
        print("   exit  - exit the program")


if __name__ == "__main__":
    main()

