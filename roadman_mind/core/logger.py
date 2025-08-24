import logging
import sys

def setup_logger():
    """
    Configures a basic console logger.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)-8s] --- %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

# You can get this logger instance from other modules
logger = logging.getLogger("roadman_mind")
