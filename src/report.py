"""Features regarding the final data collection and preparing the report."""


import logging
from pathlib import Path
from typing import Union

import jinja2
import pandas as pd
from matplotlib import pyplot as plt
from mysql.connector import ProgrammingError
from mysql.connector.cursor import MySQLCursor

from src.connection import DBConnector, DBEngineer, SQLError


class AssetsMissingError(Exception):
    """Error while creating a report."""


...


class AssetGenerator(DBEngineer):
    """A worker that pulls the relevant data from the server, prints the images
    and prepares the other results for the report.

    Attributes:
        db_connector: A custom data base connector.
        data: A dictionary of data frames pulled from the database.

    Args:
        db_connector (DBConnector): A custom data base connector.
    """

    def __init__(self, db_connector: DBConnector) -> None:
        super().__init__(db_connector)
        self.data = {
            "best_employees": pd.DataFrame(),
            "top_players": pd.DataFrame(),
            "top_saled_games": pd.DataFrame(),
            "top_rented_games": pd.DataFrame(),
            "game_category_ranking": pd.DataFrame(),
            "bw_profit_months": pd.DataFrame(),
            "weekly_trafic": pd.DataFrame(),
            "sales_n_dates": pd.DataFrame(),
        }

    def _fetch_one(self, cursor: MySQLCursor, view_name: str) -> pd.DataFrame:
        # TODO:DOC
        try:
            cursor.execute(f"SELECT * FROM {view_name}")
            result = cursor.fetchall()
            return pd.DataFrame(result)
        except ProgrammingError:
            raise SQLError(f"Could not fetch the '{view_name}' data.")

    def fetch(self) -> None:
        # TODO:DOC
        with self.cursor() as crsr:
            for view in self.data.keys():
                df = self._fetch_one(cursor=crsr, view_name=view)
                self.data[view] = df

    def export_table(self, name: str, df: pd.DataFrame) -> None:
        table_id = name.replace("_", "-")
        html_table = df.to_html(table_id=table_id, index=False)
        with open(Path(f"assets/generated/{name}.html"), "w") as f:
            f.write(html_table.replace("\n", ""))

    def export_text(self, name: str, text: str) -> None:
        with open(Path(f"assets/generated/{name}.html"), "w") as f:
            f.write(text)

    def export_piechart(
        self, name: str, df: pd.DataFrame, val: str, labels: str
    ) -> None:
        fig, ax = plt.subplots(1, 1)
        patches, texts, pcts = ax.pie(
            df[val],
            labels=df[labels],
            autopct="%.0f%%",
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            textprops={"size": "x-large"},
        )
        for i, patch in enumerate(patches):
            texts[i].set_color(patch.get_facecolor())
        plt.setp(pcts, color='white')
        plt.setp(texts, fontweight=600)
        plt.tight_layout()
        plt.savefig(Path(f"assets/generated/{name}.svg"))

    def export_barchart(
        self, name: str, df: pd.DataFrame, x: str, val: Union[list, str]
    ) -> None:
        pass

    def export_trendchart(
        self, name: str, df: pd.DataFrame, x: str, val: Union[list, str]
    ) -> None:
        pass

    def run(self) -> None:
        """Prepare all the images, tables and numbers and save them as a dynamic content."""
        self.fetch()


class ReportCreator:
    """Template filler which builds the whole report from the assets."""

    def _fill_template(self, template_str: str) -> str:
        """Fill the template using Jinja templates.

        Args:
            template_str (str): String report template html file.

        Returns:
            str: String result report html file.
        """
        environment = jinja2.Environment()
        template = environment.from_string(template_str)
        context = {"name": "Siema"}  # ! TODO: this is ofc temporary
        return template.render(context)

    def generate(self) -> str:
        """Read the template report file, fill the placeholders and save the results
        in the new report file.
        """
        try:
            template = Path("assets", "static", "report_template.html").read_text(
                encoding="utf-8"
            )
        except FileNotFoundError:
            AssetsMissingError(
                "Some assets were missing. The report could not be generated."
            )
        self.report_result = self._fill_template(template)
        temp_export_path = Path("assets/temp_report.html")
        # TODO ...


def generate(db_connector: DBConnector) -> None:
    """Prepare data and the assets for the report and generate it.
    Log the success info.

    Args:
        db_connector (DBConnector): A database connector object.
    """
    AssetGenerator(db_connector).run()
    # ReportCreator().generate()
    logging.info("New report has been generated.")
