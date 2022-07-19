import sys
from .constants import *
import logging


def init_logger():
    with open(debug_log_file, 'w') as _:
        pass


    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(debug_log_file),
            logging.StreamHandler(sys.stderr),
        ]
    )
