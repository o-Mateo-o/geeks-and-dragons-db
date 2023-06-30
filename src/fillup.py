"""Features related to the database creation and inserting the entire data set."""

import logging
from pathlib import Path

import pandas as pd
from typing import Any 
import numpy as np
from mysql.connector.errors import ProgrammingError
from tqdm import tqdm

from src.connection import DBConnector, DBEngineer, SQLError


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
        db_connector: A custom data base connector.

    Args:
        db_connector (DBConnector): A custom data base connector.
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
        db_connector: A custom data base connector.

    Args:
        db_connector (DBConnector): A custom data base connector.
    """
    @staticmethod
    def _sqlize_nans(value: Any) -> Any:
        """Replace numpy nan with sql null.

        Args:
            value (Any): Some value.

        Returns:
            Any: Safe, not-nan value.
        """
        if isinstance(value, float) and np.isnan(value):
            return None
        else:
            return value

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
                statement = f"INSERT INTO {table} VALUES ({','.join(['%s'] * len(row))});"
                crsr.execute(statement, list(map(self._sqlize_nans, row)))

    @modify_safely
    def fill_all_tables(self, random_data: dict) -> None:
        """Fill all the database tables with the data provided.
        Use the `fill_table` method multiple times and display the progress
        as a bar in the terminal.

        Args:
            random_data (dict): A dictionary of table names and the
                generated data frames.
        """
        bar_format = "Filled tables: {bar:20} {n_fmt}/{total_fmt} (it might take a while)"
        for table, df in tqdm(random_data.items(), bar_format=bar_format):
            self.fill_table(table, df)

    def run(self, random_data: dict):
        """Fill all the tables in the database. Use the `fill_all_tables` method.

        Args:
            random_data (dict): A dictionary of table names and the
                generated data frames.
        """
        self.fill_all_tables(random_data)


def push(random_data: dict, db_connector: DBConnector) -> None:
    """Recreate and fill the database. Log the success info.

    Args:
        random_data (dict): A dictionary of table names and the
                generated data frames.
        db_connector (DBConnector): A database connector object.
    """
    DBArchitect(db_connector).run()
    DBFiller(db_connector).run(random_data)
    logging.info(
        "New database tables has been filled with random values and new views have been added."
    )
