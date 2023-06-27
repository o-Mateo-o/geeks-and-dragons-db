"""User-firendly connection object and the connection errors."""

import json
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Union

from mysql.connector import connect
from mysql.connector.cursor import MySQLCursor
from mysql.connector.errors import ProgrammingError


class SQLError(Exception):
    """An error related to connection, statement execution etc."""

    ...


class DBConnector:
    """Safe database connector which automatically reads the connection details
    form the configuration file and its input attributes.

    A SQLError is raised in case of initial connecting issues.

    Attributes:
        conn: A connection object.
        connection_settings: A connection configuration dictionary.

    Args:
        password: A password for the database and user given in the connection configuration file.
    """

    def __init__(self, password: str) -> None:
        self.conn = None
        with open(Path("config/database.connection.json"), "r") as f:
            self.connection_settings = json.load(f)
            self.connection_settings["password"] = password
        try:
            self.conn = connect(**self.connection_settings)
        except ProgrammingError as err:
            raise SQLError(f"DB Architect could not estabilish a connection:\n {err}.")

    @property
    def db_name(self) -> Union[str, None]:
        """Get the name of database the object is connected to.

        Returns:
            Union[str, None]: A database name.
        """
        if self.conn:
            return self.connection_settings["database"]
        else:
            return None

    def __del__(self) -> None:
        """Close the connection when the object is removed from memory."""
        if self.conn:
            self.conn.close()


class DBEngineer(ABC):
    """Abstract worker, exectuting operations on databases.

    Attributes:
        db_connector: A custom data base connector.

    Args:
        db_connector (DBConnector): A custom data base connector.
    """

    def __init__(self, db_connector: DBConnector) -> None:
        self.db_connector = db_connector

    @contextmanager
    def cursor(self, commit: bool = False) -> Generator[MySQLCursor, Any, None]:
        """Context to safely use the cursor, and close it after completing the operations.
        It can additionally do the commit action.

        Args:
            commit (bool, optional): If the commit action is expected. Defaults to False.

        Yields:
            Generator[MySQLCursor, Any, None]: A cursor.
        """
        crsr = self.db_connector.conn.cursor()
        try:
            yield crsr
        finally:
            crsr.close()
            if commit:
                self.db_connector.conn.commit()

    @abstractmethod
    def run(self) -> None:
        """Do all the core operations."""
        NotImplemented
