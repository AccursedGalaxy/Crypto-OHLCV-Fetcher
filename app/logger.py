# logger.py
# logger setup for the project. Production quality logs.
import logging


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with the given name and log file.
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


# Initialize and set up the main logger for the application
logger = setup_logger("BitFetch")
