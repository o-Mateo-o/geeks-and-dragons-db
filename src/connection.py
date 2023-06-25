"""User-firendly connection object and the connection errors."""

import json
from pathlib import Path
from typing import Union

from mysql.connector import connect
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
