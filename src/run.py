import logging
from getpass import getpass

from colorlog import ColoredFormatter

from src import connection, drandom, fillup, reader, report


class NoActionsError(Exception):
    ...


class CError(Exception):
    ...


def setup() -> None:
    """Set up the logger."""
    LOG_LEVEL = logging.INFO
    LOGFORMAT = "  %(log_color)s%(levelname)s: %(message)s%(reset)s"

    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)
    print("Database Manager has been launched.")


def run(f: bool, r: bool, o: bool) -> None:
    password = getpass("Enter the connection password:")
    db_connector = connection.DBConnector(password)
    print(":)")
    if f:
        data = drandom.generate_data()
        fillup.push(data, db_connector)
    if r:
        report.generate(db_connector)
    if o:
        reader.open_report()
    if not any([f, r, o]):
        raise NoActionsError("No actions selected")
    print("All the steps have been completed successfully.")
