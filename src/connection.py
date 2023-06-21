import json
from pathlib import Path
import logging
from mysql.connector.errors import ProgrammingError
from mysql.connector import connect

class SQLError(Exception):
    """An error related to connection, statement execution etc."""
    ...

class DBConnector:
    def __init__(self) -> None:
        self.conn = None
        with open(Path("config/user.database.connection.json"), "r") as f:
            self.connection_settings = json.load(f)
        try:
            self.conn = connect(**self.connection_settings)
        except ProgrammingError:
            raise SQLError("DB Architect could not estabilish a connection.")

    @property
    def db_name(self):
        if self.conn:
            return self.connection_settings["database"]
        else:
            return None

    def __del__(self) -> None:
        if self.conn:
            self.conn.close()


