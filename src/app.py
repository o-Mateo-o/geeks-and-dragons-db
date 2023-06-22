import logging
from getpass import getpass
from os import chdir
from pathlib import Path

from colorlog import ColoredFormatter

from src import connection, drandom, fillup, reader, report


class NoActionsError(Exception):
    ...


class CError(Exception):
    ...


class DBManagerApp:
    @staticmethod
    def _log_setup() -> None:
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

    @staticmethod
    def _establish_connection() -> connection.DBConnector:
        password = getpass("Enter the connection password:")
        db_connector = connection.DBConnector(password)
        print(":)")
        return db_connector

    def _run(self, f: bool, r: bool, o: bool) -> None:
        # connection
        if any([f, r]):
            db_connector = self._establish_connection()
        if not any([f, r, o]):
            raise NoActionsError("No actions selected")
        # actions
        if f:
            data = drandom.generate_data()
            fillup.push(data, db_connector)
        if r:
            report.generate(db_connector)
        if o:
            reader.open_report()

    def run(self, f: bool, r: bool, o: bool):
        chdir(Path(".").parent)
        self._log_setup()
        try:
            self._run(f, r, o)
        except (connection.SQLError, NoActionsError, CError) as err:
            logging.error(err)
        except reader.ReportOpenError as err:
            logging.warning(err)
        print("All the steps have been completed successfully.")
