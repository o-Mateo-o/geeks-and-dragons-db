import logging
from colorlog import ColoredFormatter


def setup() -> None:
    """Set up the logger."""
    LOG_LEVEL = logging.DEBUG
    LOGFORMAT = "  %(log_color)s%(levelname)s: %(message)s%(reset)s"

    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)
