"""Main app class. Setup and all the launch events handled."""

import logging
from getpass import getpass
from os import chdir
from pathlib import Path

from colorlog import ColoredFormatter

from src import connection, drandom, fillup, reader, report


class NoActionsError(Exception):
    """When no options were selected by the user but he still runs the app."""

    ...


class DBManagerApp:
    """Main database manager app."""

    @staticmethod
    def _log_setup() -> None:
        """Set up the logger. Add the colors and info level for the terminal display."""
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
        """Ask for the password and establish the connection.
        Inform the user about the success.

        Returns:
            DBConnector: A database connector object.
        """
        password = getpass("Enter the connection password:")
        db_connector = connection.DBConnector(password)
        print(":)")
        return db_connector

    def _run(self, f: bool, r: bool, o: bool) -> None:
        """With the options provided establish the connection if needed,
        then check if any of the options was selected and perform the
        operations selected by the user.

        Args:
            f (bool): New database fill-up flag.
            r (bool): New report generation flag.
            o (bool): Open report flag.

        Raises:
            NoActionsError: If none of the options is selected.
        """
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
        """Set up the app (current working directory and the logger), launch it with the
        given options and handle the errors by logging them the right way (and stopping the execution).

        Args:
            f (bool): New database fill-up flag.
            r (bool): New report generation flag.
            o (bool): Open report flag.

        """
        chdir(Path(".").parent)
        self._log_setup()
        try:
            self._run(f, r, o)
        except (connection.SQLError, NoActionsError, report.AssetsMissingError) as err:
            logging.error(err)
        except reader.ReportOpenError as err:
            logging.warning(err)
        print("All the steps have been completed successfully.")
