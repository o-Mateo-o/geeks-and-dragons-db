import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from mysql.connector.errors import ProgrammingError

from src.connection import DBConnector


class DBEngineer(ABC):
    def __init__(self, db_connector: DBConnector) -> None:
        self.db_connector = db_connector

    @contextmanager
    def cursor(self, commit: bool = False) -> Generator[MySQLCursor, Any, None]:
        crsr = self.db_connector.conn.cursor()
        try:
            yield crsr
        finally:
            crsr.close()
            if commit:
                self.db_connector.conn.commit()

    @abstractmethod
    def run(self) -> None:
        NotImplemented


def modify_safely(fun: callable) -> callable:
    def wrapper(*args):
        self: DBEngineer = args[0]
        with self.cursor() as crsr:
            crsr.execute("SET FOREIGN_KEY_CHECKS=0;")
            try:
                result = fun(*args)
            except ProgrammingError as err:
                # logging.error("asdasdasdasdasd.")
                raise Exception(f"Error in execution: {err}")
            else:
                crsr.execute("SET FOREIGN_KEY_CHECKS=1;")
                return result

    return wrapper


class DBArchitect(DBEngineer):
    @staticmethod
    def read_queries(q_type: str) -> str:
        if q_type == "tables":
            file_path = Path("queries/tables.sql")
        elif q_type == "views":
            file_path = Path("queries/views.sql")
        else:
            raise ValueError(f"Unknown object type '{q_type}'")
        with open(file_path, "r") as f:
            content = f.read()
        return content.split(";")

    @modify_safely
    def clear(self, q_type: str) -> None:
        if q_type not in {"tables", "views"}:
            raise ValueError(f"Unknown object type '{q_type}'")

        db_name = self.db_connector.db_name

        with self.cursor(commit=True) as crsr:
            crsr.execute(
                f"""SELECT table_name
                            FROM information_schema.{q_type}
                            WHERE table_schema = '{db_name}';"""
            )
            tables = [row[0] for row in crsr.fetchall()]
            for table in tables:
                crsr.execute(f"DROP TABLE IF EXISTS {table}")

    @modify_safely
    def create(self, q_type: str) -> None:
        with self.cursor(commit=True) as crsr:
            for query in self.read_queries(q_type):
                crsr.execute(query)

    def build(self, q_type: str) -> None:
        self.clear(q_type)
        self.create(q_type)

    def run(self) -> None:
        self.build("tables")
        self.build("views")


class DBFiller(DBEngineer):
    def run(self):
        pass


def push(random_data: dict, conn: MySQLConnection) -> None:
    DBArchitect(conn).run()
    DBFiller(conn).run()
    logging.info(
        "New database tables has been filled with random values and new views have been added."
    )
