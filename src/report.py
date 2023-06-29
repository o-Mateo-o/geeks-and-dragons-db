"""Features regarding the final data collection and preparing the report."""


import calendar
import json
import logging
from pathlib import Path
from typing import Union

import jinja2
import numpy as np
import pandas as pd
import seaborn as sns
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
            "bw_revenue_months": pd.DataFrame(),
            "weekly_traffic": pd.DataFrame(),
            "sales_n_dates": pd.DataFrame(),
        }

    def _fetch_one(self, cursor: MySQLCursor, view_name: str) -> pd.DataFrame:
        """Fetch one data frame for the views section in the database.

        Args:
            cursor (MySQLCursor): A cursor.
            view_name (str): A view name.

        Raises:
            SQLError: If something has gone wrong with the execution.

        Returns:
            pd.DataFrame: Data frame representation of the view.
        """
        try:
            cursor.execute(f"SELECT * FROM {view_name};")
            result = cursor.fetchall()
            if result:
                return pd.DataFrame(result)
            else:
                # in case the table is empty
                cursor.execute(f"SHOW COLUMNS FROM {view_name};")
                result = cursor.fetchall()
                return pd.DataFrame({col: [] for col, *info in result})
        except ProgrammingError:
            raise SQLError(f"Could not fetch the '{view_name}' data.")

    def fetch(self) -> None:
        """Fetch all the views necessary for analyses and save them to the data attribute."""
        with self.cursor() as crsr:
            for view in self.data.keys():
                df = self._fetch_one(cursor=crsr, view_name=view)
                self.data[view] = df

    def export_table(self, name: str, df: pd.DataFrame) -> None:
        """Save the data frame to the file as a HTML table.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
        """
        table_id = name.replace("_", "-")
        html_table = df.to_html(table_id=table_id, index=False)
        with open(Path(f"assets/generated/{name}.html"), "w") as f:
            f.write(html_table.replace("\n", ""))

    def export_dict(self, name: str, dictionary: str) -> None:
        """Save the selected values in a JSON format.

        Args:
            name (str): Name of the file.
            dictionary (str): JSON dictionary of content parameters.
        """
        with open(Path(f"assets/generated/{name}.json"), "w") as f:
            json.dump(dictionary, f)

    def export_piechart(
        self, name: str, df: pd.DataFrame, val: str, labels: str
    ) -> None:
        """Save the pie chart created with the given data as a vector image.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
            val (str): Values column.
            labels (str): Labels column.
        """
        fig, ax = plt.subplots(1, 1)
        patches, texts, pcts = ax.pie(
            df[val],
            labels=df[labels],
            autopct="%.0f%%",
            wedgeprops={"linewidth": 3.0, "edgecolor": "white"},
            textprops={"size": "x-large"},
            colors=sns.cubehelix_palette(rot=0.2, light=0.8, n_colors=df.shape[0]),
        )
        for i, patch in enumerate(patches):
            texts[i].set_color(patch.get_facecolor())
        plt.setp(pcts, color="white")
        plt.setp(texts, fontweight=600)
        plt.tight_layout()
        plt.savefig(Path(f"assets/generated/{name}.svg"))

    def export_barchart(
        self, name: str, df: pd.DataFrame, val: Union[list, str], labels: str
    ) -> None:
        """Save the bar chart created with the given data as a vector image.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
            val (Union[list, str]): Values column or columns.
            labels (str): Labels column.
        """
        fig, ax = plt.subplots(1, 1)
        x = np.arange(df.shape[0])
        palete = sns.cubehelix_palette(rot=0.2, light=0.8, n_colors=2)
        alpha_color = (0, 0, 0, 0)
        # bars
        if len(val) == 2:
            width = 0.35
            ax.bar(
                x=x - 0.2, height=df[val[0]], width=width, color=palete[1], label=val[0]
            )
            ax.bar(
                x=x + 0.2, height=df[val[1]], width=width, color=palete[0], label=val[1]
            )
            ax.legend()
        elif len(val) == 1:
            width = 0.5
            ax.bar(x=x, height=df[val[0]], width=width, color=palete[1], label=val[0])
        # no colors
        fig.patch.set_facecolor(alpha_color)
        ax.set_facecolor(alpha_color)
        # no lines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.get_yaxis().set_ticks([])
        # text
        ax.set_xticks(x, df[labels], fontweight=600, rotation=20)
        for container in ax.containers:
            ax.bar_label(container, fontweight=600, padding=5)
        # export
        plt.savefig(Path(f"assets/generated/{name}.svg"), transparent=True)

    def export_trendchart(
        self, name: str, df: pd.DataFrame, val: str, labels: str
    ) -> None:
        """Save the scatter + line plot created with the given data as a vector image.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
            val (str): Values column.
            labels (str): Labels column.
        """
        fig, ax = plt.subplots(1, 1)
        x = np.arange(df.shape[0])
        palete = sns.cubehelix_palette(rot=0.2, light=0.8, n_colors=3)
        # scater and the line
        ax.scatter(x, df[val], zorder=100, color=palete[2], marker="D")
        ax.plot(x, df[val], ls="--", zorder=50, color=palete[1])
        # no colors
        fig.patch.set_facecolor((0, 0, 0, 0))
        ax.set_facecolor((0, 0, 0, 0))
        # no lines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        # text & grid
        ax.grid(axis="y")
        ax.set_xticks(x, df[labels], fontweight=600)
        # export
        plt.savefig(Path(f"assets/generated/{name}.svg"), transparent=True)

    def analyze(self) -> None:
        """Perform all the analyses with the fetched data set and export the results
        as they are parts of a report dynamic content.
        """
        # employees
        all_best_employees = self.data["best_employees"].copy()
        fdates = all_best_employees[["month", "year"]].apply(
            lambda args: f"{calendar.month_name[args[0]]} {args[1]}", axis=1
        )
        if fdates.empty:
            all_best_employees["Date"] = []
        else:
            all_best_employees["Date"] = fdates

        all_best_employees.rename(
            columns={"employee": "Employee", "number_of_sales": "Sales Number"},
            inplace=True,
        )
        self.export_table(
            name="table_best_employees",
            df=all_best_employees[["Date", "Employee", "Sales Number"]],
        )
        best_empl = "NONE"
        try:
            best_empl = all_best_employees.iloc[0]["Employee"]
        except IndexError:
            logging.warning("REPORT: Best employee not found.")

        self.export_dict(
            name="recent_best_employee",
            dictionary={"name": best_empl},
        )
        # .........

        # top saled and renter games
        self.export_barchart(
            name="top_rented_games",
            df=self.data["top_rented_games"],
            val="total_amount",
            labels="game",
        )
        self.export_barchart(
            name="top_rented_games",
            df=self.data["top_saled_games"],
            val="total_amount",
            labels="game",
        )
        # categories
        self.export_piechart(
            name="top_categories",
            df=self.data["game_category_ranking"],
            val="popularity",
            labels="game_category",
        )
        # max and min revenue
        worst_revenue = self.data["bw_revenue_months"].loc[
            self.data["bw_revenue_months"]["record_type"] == "minimal"
        ]
        best_revenue = self.data["bw_revenue_months"].loc[
            self.data["bw_revenue_months"]["record_type"] == "maximal"
        ]

        reven_data = {"MAXIMAL_MONTH": "NONE", "MINIMAL_MONTH": "NONE"}
        try:
            reven_data = {
                "worst.date": f'{calendar.month_name[worst_revenue["month"].values[0]]} {worst_revenue["year"].values[0]}',
                "worst.amount": worst_revenue["amount"].values[0],
                "best.date": f'{calendar.month_name[best_revenue["month"].values[0]]} ,{best_revenue["year"].values[0]}',
                "best.amount": best_revenue["amount"].values[0],
            }
        except IndexError:
            logging.warning("REPORT: Revenue data not valid.")
        self.export_dict(
            name="revenue_data",
            dictionary=reven_data,
        )
        # weekly traffic
        self.data["weekly_traffic"]["name_of_day"] = self.data["weekly_traffic"][
            "name_of_day"
        ].apply(lambda name: name.capitalize())
        self.export_trendchart(
            name="weekly_traffic",
            df=self.data["weekly_traffic"],
            val="number_of_sales",
            labels="name_of_day",
        )
        # sales and dates
        self.data["sales_n_dates"].rename(
            columns={
                "employee": "Employee",
                "dates_number": "Dates",
                "sales_number": "Sales",
            },
            inplace=True,
        )
        self.export_barchart(
            name="plot_sales_n_dates",
            df=self.data["sales_n_dates"],
            val=["Dates", "Sales"],
            labels="Employee",
        )
        corr = self.data["sales_n_dates"]["Dates"].corr(
            self.data["sales_n_dates"]["Sales"], method="pearson"
        )
        if np.isnan(corr):
            corr = "NONE"
        self.export_dict(
            name="correlation",
            dictionary={"pearson": corr},
        )

    def run(self) -> None:
        """Prepare all the images, tables and numbers and save them as a dynamic content."""
        self.fetch()
        self.analyze()


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
