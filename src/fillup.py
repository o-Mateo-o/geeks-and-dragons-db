"""Features related to the database creation and inserting the entire data set."""

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

import pandas as pd
from mysql.connector.cursor import MySQLCursor
from mysql.connector.errors import ProgrammingError
from tqdm import tqdm

from src.connection import DBConnector, SQLError


class DBEngineer(ABC):

    """Abstract worker, exectuting operations on databases.

    Attributes:
        db_connector: Custom data base connector.

    Args:
        db_connector: Custom data base connector.
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


def modify_safely(fun: callable) -> callable:
    """Decorate the db-related function to disable the unnecessary checks
    during the time of function call. Catch also the incoming db-related errors
    and handle them by passing them properly formatted.

    Args:
        fun (callable): Some db-related function.

    Returns:
        callable: A decorated function.
    """

    def wrapper(*args):
        self: DBEngineer = args[0]
        with self.cursor() as crsr:
            crsr.execute("SET FOREIGN_KEY_CHECKS=0;")
            try:
                result = fun(*args)
            except ProgrammingError as err:
                raise SQLError(f"Error in execution: {err}")
            else:
                crsr.execute("SET FOREIGN_KEY_CHECKS=1;")
                return result

    return wrapper


class DBArchitect(DBEngineer):
    """A structure creator. Handles both tables and views cases.

    Attributes:
        db_connector: Custom data base connector.

    Args:
        db_connector: Custom data base connector.
    """

    @staticmethod
    def read_statements(q_type: str) -> str:
        """Get all the sql statements of a given type from the external file.

        Args:
            q_type (str): Type of an object group to be created.

        Raises:
            ValueError: If the type is other than tables or views.

        Returns:
            str: A list of statements.
        """
        if q_type == "tables":
            file_path = Path("sql/tables.sql")
        elif q_type == "views":
            file_path = Path("sql/views.sql")
        else:
            raise ValueError(f"Unknown object type '{q_type}'")
        with open(file_path, "r") as f:
            content = f.read()
        return content.split(";")

    @modify_safely
    def clear(self, q_type: str) -> None:
        """Clear the database by dropping objects of specified type.

        Args:
            q_type (str): Type of an object group to be deleted (tables, views).
        """
        elem_types = {"tables": "TABLE", "views": "VIEW"}
        if q_type not in elem_types.keys():
            raise ValueError(f"Unknown object type '{q_type}'")
        db_name = self.db_connector.db_name

        with self.cursor(commit=True) as crsr:
            crsr.execute(
                f"""SELECT table_name
                            FROM information_schema.{q_type}
                            WHERE table_schema = '{db_name}';"""
            )  # NOTE that only two q_types accepted
            elems = [row[0] for row in crsr.fetchall()]
            for elem in elems:
                crsr.execute(f"DROP {elem_types[q_type]} IF EXISTS {elem}")

    @modify_safely
    def create(self, q_type: str) -> None:
        """Create all the the tables/views in the database.

        Args:
            q_type (str): Type of an object group to be created (tables, views).
        """
        with self.cursor(commit=True) as crsr:
            for query in self.read_statements(q_type):
                crsr.execute(query)

    def build(self, q_type: str) -> None:
        """Build a database sector by dropping a group of objects and
        creating the new ones.

        Args:
            q_type (str): Type of an object group to be built (tables, views).
        """
        self.clear(q_type)
        self.create(q_type)

    def run(self) -> None:
        """Prepare a database by building the tables and the views."""
        self.build("tables")
        self.build("views")


class DBFiller(DBEngineer):
    """Database filler. Inserts all the records into the prepared database.

    Attributes:
        db_connector: Custom data base connector.

    Args:
        db_connector: Custom data base connector.
    """

    def fill_table(self, table: str, df: pd.DataFrame) -> None:
        """Fill one database table with the data provided.

        Args:
            table (str): A table name.
            df (pd.DataFrame): Data frame representation of the table.
                It has to keep the column order given by the database.
        """
        # ! TODO: test the errors if the col number does not match
        with self.cursor(commit=True) as crsr:
            for row in df.values.tolist():
                crsr.execute(f"INSERT INTO {table} VALUES {tuple(row)}")

    def fill_all_tables(self, random_data: dict) -> None:
        """Fill all the database tables with the data provided.
        Use the `fill_table` method multiple times and display the progress
        as a bar in the terminal.

        Args:
            random_data (dict): Dictionary of table names and the
                generated data frames.
        """
        # ! TODO: check if tqdm required. otherwise delete and uninstall
        bar_format = "Filled tables: {bar:20} {n_fmt}/{total_fmt}"
        for table, df in tqdm(random_data.items(), bar_format=bar_format):
            self.fill_table(table, df)

    def run(self, random_data: dict):
        """Fill all the tables in the database. Use the `fill_all_tables` method.

        Args:
            random_data (dict): Dictionary of table names and the
                generated data frames.
        """
        self.fill_all_tables(random_data)


def push(random_data: dict, conn: DBConnector) -> None:
    """Recreate and fill the database. Log the success info.

    Args:
        random_data (dict): Dictionary of table names and the
                generated data frames.
        conn (DBConnector): A database connector object.
    """
    DBArchitect(conn).run()
    DBFiller(conn).run(random_data)
    logging.info(
        "New database tables has been filled with random values and new views have been added."
    )
