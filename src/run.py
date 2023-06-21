import logging
import json
from getpass import getpass
from pathlib import Path

from colorlog import ColoredFormatter

from src import connection, drandom, fillup, reader, report


class NoActionsError(Exception):
    ...

class CError(Exception):
    ...

def validate_user():
    with open(Path("config/database.connection.json"), "r") as f:
        config = json.load(f)
    password = getpass("Enter the connection password:")
    config["password"] = password
    with open(Path("config/user.database.connection.json"), "w") as f:
        json.dump(config, f)

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
    db_connector = connection.DBConnector()
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
