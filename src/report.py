"""Features regarding the final data collection and preparing the report."""


import calendar
import glob
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Union

import jinja2
import numpy as np
import pandas as pd
import pdfkit
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
            rows = cursor.fetchall()
            cursor.execute(f"SHOW COLUMNS FROM {view_name};")
            header_info = cursor.fetchall()
            colnames = [col for col, *info in header_info]
            if rows:
                return pd.DataFrame(rows, columns=colnames)
            else:
                # in case the table is empty               
                return pd.DataFrame({col: [] for col in colnames})
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
        Do not export if the input is empty.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
        """
        table_id = name.replace("_", "-")
        html_table = df.to_html(table_id=table_id, index=False, border=0)
        with open(Path(f"assets/generated/{name}.html"), "w", encoding="utf-8") as f:
            f.write(html_table.replace("\n", ""))
        if df.empty:
            logging.warning(
                f"REPORT: '{name}' table was not created because of the lacking data."
            )

    def export_group_list(
        self,
        name: str,
        df: pd.DataFrame,
        group: str,
        keys: str,
        values: str,
        group_name: str,
    ) -> None:
        """Save the data frame to the file as a series of lists.
        Do not export if the input is empty.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
            group (str): A column of gorup names.
            keys (str): A column of key names.
            values (str): A column of keys' values.
            group_name (str): A group prefix of subsections.
        """
        # prepare the order
        df.sort_values(by=[group, values], ascending=[True, False], inplace=True)
        html_list_elems = []
        html_list_elems.append('<div class="list-area">')
        # divide by groups
        for group_unit in np.unique(df[group]):
            html_list_elems.append(f"<h3>{group_name} &ndash; {group_unit}</h3>")
            html_list_elems.append("<ol>")
            # list within a group
            for i, row in df[df[group] == group_unit].iterrows():
                html_list_elems.append(f"<li>{row[keys]} (<i>{row[values]:.2f}</i>)</li>")
            html_list_elems.append("</ol>")
        html_list_elems.append("</div>")
        # join the components
        html_list = "".join(html_list_elems)
        with open(Path(f"assets/generated/{name}.html"), "w", encoding="utf-8") as f:
            f.write(html_list)
        if df.empty:
            logging.warning(
                f"REPORT: '{name}' lists were not created because of the lacking data."
            )

    def export_dict(self, name: str, dictionary: str) -> None:
        """Save the selected values in a JSON format.

        Args:
            name (str): Name of the file.
            dictionary (str): JSON dictionary of content parameters.
        """
        with open(Path(f"assets/generated/{name.replace('_', '.')}.json"), "w") as f:
            json.dump(dictionary, f)

    def export_piechart(
        self, name: str, df: pd.DataFrame, val: str, labels: str
    ) -> None:
        """Save the pie chart created with the given data as a vector image.
        Do not export if the input is empty.

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
        if not df.empty:
            plt.savefig(Path(f"assets/generated/{name}.svg"), transparent=True, bbox_inches = 'tight')
        else:
            logging.warning(
                f"REPORT: '{name}' pie chart was not created because of the lacking data"
            )

    def export_barchart(
        self, name: str, df: pd.DataFrame, val: str, labels: str
    ) -> None:
        """Save the bar chart created with the given data as a vector image.
        Do not export if the input is empty.

        Args:
            name (str): Name of the file.
            df (pd.DataFrame): Some data frame.
            val (str): Values column or columns.
            labels (str): Labels column.
        """
        fig, ax = plt.subplots(1, 1)
        x = np.arange(df.shape[0])
        palete = sns.cubehelix_palette(rot=0.2, light=0.8, n_colors=2)
        alpha_color = (0, 0, 0, 0)
        # bars
        width = 0.5
        ax.barh(y=x, width=df[val], height=width, color=palete[1], label=val)
        # no colors
        fig.patch.set_facecolor(alpha_color)
        ax.set_facecolor(alpha_color)
        # no lines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        plt.tight_layout()
        ax.get_xaxis().set_ticks([])
        # text
        ax.set_yticks(x, df[labels], fontweight=300)
        for container in ax.containers:
            ax.bar_label(container, fontweight=600, padding=5)
        # export
        if not df.empty:
            plt.savefig(Path(f"assets/generated/{name}.svg"), transparent=True, bbox_inches = 'tight')
        else:
            logging.warning(
                f"REPORT: '{name}' bar chart was not created because of the lacking data"
            )

    def export_trendchart(
        self, name: str, df: pd.DataFrame, val: str, labels: str
    ) -> None:
        """Save the scatter + line plot created with the given data as a vector image.
        Do not export if the input is empty.

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
        if not df.empty:
            plt.savefig(Path(f"assets/generated/{name}.svg"), transparent=True)
        else:
            logging.warning(
                f"REPORT: '{name}' plot was not created because of the lacking data"
            )

    def remove_dynamic_assets(self) -> None:
        """Delete all the generated asset files."""
        str_path = str(Path("assets/generated/*"))
        files = glob.glob(str_path)
        for f in files:
            os.remove(f)

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
            dictionary={"name": str(best_empl)},
        )
        # top players per game
        self.export_group_list(
            name="top_players_lists",
            df=self.data["top_players"],
            group="game",
            keys="player",
            values="avg_score",
            group_name="Gra",
        )
        # top saled and renter games
        self.export_barchart(
            name="top_rented_games",
            df=self.data["top_rented_games"],
            val="total_amount",
            labels="game",
        )
        self.export_barchart(
            name="top_saled_games",
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
        reven_data = {
            "worst.date": "NONE",
            "worst.amount": "NONE",
            "best.date": "NONE",
            "best.amount": "NONE",
        }
        try:
            reven_data = {
                "worst.date": f'{calendar.month_name[worst_revenue["month"].values[0]]} {worst_revenue["year"].values[0]}',
                "worst.amount": str(worst_revenue["amount"].values[0]),
                "best.date": f'{calendar.month_name[best_revenue["month"].values[0]]} ,{best_revenue["year"].values[0]}',
                "best.amount": str(best_revenue["amount"].values[0]),
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
            name="plot_sales_n_dates_sales",
            df=self.data["sales_n_dates"],
            val="Sales",
            labels="Employee",
        )
        self.export_barchart(
            name="plot_sales_n_dates_dates",
            df=self.data["sales_n_dates"],
            val="Dates",
            labels="Employee",
        )
        corr = self.data["sales_n_dates"].corr(numeric_only=True, method="pearson").loc["Sales", "Dates"]
        corr = np.round(corr, 2)
        if np.isnan(corr):
            corr = "NONE"
            logging.warning("REPORT: Dates & sales correlation could not be evaluated.")
        self.export_dict(
            name="correlation",
            dictionary={"pearson": str(corr)},
        )

    def run(self) -> None:
        """Prepare all the images, tables and numbers and save them as a dynamic content."""
        self.remove_dynamic_assets()
        self.fetch()
        self.analyze()


class ReportCreator:
    """Template filler which builds the whole report from the assets.

    Attributes:
        context: A dicttionary of jinja replaced values.
    """

    def __init__(self) -> None:
        self.context = {
            "abs_path": f"file:///{os.getcwd()}",
            "style": "",
            "today": f"{datetime.today().strftime('%d.%m.%Y')} r.",
            "table_best_employees": "",
            "top_players_lists": "",
            "recent_best_employee_name": None,
            "revenue_data_worst_amount": None,
            "revenue_data_worst_date": None,
            "revenue_data_best_amount": None,
            "revenue_data_best_date": None,
            "correlation_pearson": None,
        }
        try:
            # best employees - name
            with open(Path("assets/generated/recent.best.employee.json")) as f:
                recent_best_employee = json.load(f)
                self.context["recent_best_employee_name"] = recent_best_employee["name"]
            # revenue records
            with open(Path("assets/generated/revenue.data.json")) as f:
                recent_best_employee = json.load(f)
                self.context["revenue_data_worst_amount"] = recent_best_employee[
                    "worst.amount"
                ]
                self.context["revenue_data_worst_date"] = recent_best_employee[
                    "worst.date"
                ]
                self.context["revenue_data_best_amount"] = recent_best_employee[
                    "best.amount"
                ]
                self.context["revenue_data_best_date"] = recent_best_employee[
                    "best.date"
                ]
            # dates & sales correlation
            with open(Path("assets/generated/correlation.json"), "r") as f:
                recent_best_employee = json.load(f)
                self.context["correlation_pearson"] = recent_best_employee["pearson"]
            # best emplotyees - table
            self.context["table_best_employees"] = Path(
                "assets/generated/table_best_employees.html"
            ).read_text(encoding="utf-8")
            # top players - list
            self.context["top_players_lists"] = Path(
                "assets/generated/top_players_lists.html"
            ).read_text(encoding="utf-8")
            # style
            css = Path("assets/static/style.css").read_text(encoding="utf-8")
            self.context["style"] = f"<style>{css}</style>"
        except FileNotFoundError:
            raise AssetsMissingError(
                "Some assets were missing. The report could not be generated."
            )

    def _fill_template(self, template_str: str) -> str:
        """Fill the template using Jinja templates.

        Args:
            template_str (str): String report template html file.

        Returns:
            str: String result report html file.
        """
        environment = jinja2.Environment()
        template = environment.from_string(template_str)
        return template.render(self.context)

    def generate(self) -> None:
        """Read the template report file, fill the placeholders and save the results
        in the new report file.
        """
        try:
            template = Path("assets/static/template.html").read_text(encoding="utf-8")
        except FileNotFoundError:
            AssetsMissingError(
                "The main template is missing. The report could not be generated."
            )
        self.report_result = self._fill_template(template)
        Path("assets/generated/_temp_report.html").write_text(
            self.report_result, encoding="utf-8"
        )


class ToPDFConverter:
    """HTML to PDF report converter.
    Reads the configuration when created.

    Attributes:
        config: Wkhtmltopdf configuration.

    """

    def __init__(self) -> None:
        with open(Path("config/pdf.gener.json"), "r") as f:
            pdf_config = json.load(f)
        self.config = pdfkit.configuration(wkhtmltopdf=pdf_config["wkhtmltopdf.path"])

    def convert(self) -> None:
        """Convert the temporary HTML to PDF and delete the prior.
        Save the newest path in an optional config file.

        Raises:
            FileNotFoundError: If there is no temporary report file.
            AssetsMissingError: If some of the images are missing.
        """
        str_temp_html_path = str(Path("assets/generated/_temp_report.html"))
        str_out_path = str(
            Path(f"reports/report{datetime.today().strftime('%y%m%d%H%M')}.pdf")
        )
        # convert
        try:
            pdfkit.from_file(
                str_temp_html_path,
                output_path=str_out_path,
                configuration=self.config,
                options={"enable-local-file-access": None},
            )
        except FileNotFoundError:
            raise FileNotFoundError("The temporary report file is missing.")
        except OSError:
            logging.error(
                "Some images are missing or the PDF file is opened. The PDF report was not be generated properly."
            )
        # remove temp data
        try:
            os.remove(str_temp_html_path)
        except FileNotFoundError:
            logging.warning(
                "Temporary HTML report was not removed, because it was not found."
            )
        # new path in config
        with open(Path("reports/recent.json"), "w") as f:
            json.dump({"report": str_out_path}, f)


def generate(db_connector: DBConnector) -> None:
    """Prepare data and the assets for the report and generate it.
    Log the success info.

    Args:
        db_connector (DBConnector): A database connector object.
    """
    AssetGenerator(db_connector).run()
    ReportCreator().generate()
    ToPDFConverter().convert()
    logging.info("New report has been generated.")

