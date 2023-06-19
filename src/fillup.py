import logging
import mysql.connector
from pathlib import Path
import json

class DBArchitect:
    def __init__(self) -> None:
        self.con = None
        with open(Path("config/user.database.connection.json"), "r") as f:
            connection_settings = json.load(f)
        try:
            self.con = mysql.connector.connect(**connection_settings)
        except mysql.connector.errors.ProgrammingError:
            # logging.error("Cannot connect.")
            raise Exception("DB Architect could not estabilish a connection.")

    @staticmethod
    def read_queries(q_type: str) -> str:
        if q_type == "tables":
            file_path = Path("queries/tables.sql")
        elif q_type == "views":
            file_path = Path("queries/views.sql")
        else:
            raise ValueError("Unknown file type.")
        with open(file_path, "r") as f:
            content = f.read()
        return content.split(";")

    def _build(self, q_type: str) -> None:
        cursor = self.con.cursor()
        for query in self.read_queries(q_type):
            cursor.execute(query)
        cursor.close()

    def build(self, q_type: str) -> None:
        try:
            self._build(q_type)
        except mysql.connector.errors.ProgrammingError as err:
            # logging.error("asdasdasdasdasd.")
            raise Exception(f"Error in execution: {err}")

    def __del__(self) -> None:
        if self.con:
            self.con.close()

def push(random_data: dict) -> None:
    db_architect = DBArchitect()
    db_architect.build("tables")
    # db_architect.build("views")
    logging.info("New database tables has been filled with random values and new views have been added.")
