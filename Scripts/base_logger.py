from .constants import *
import logging


def init_logger():
    """Initializes the `logging` module"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[
            logging.FileHandler(debug_log_file),
            logging.StreamHandler(),
        ]
    )
