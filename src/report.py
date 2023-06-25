"""Features regarding the final data collection and preparing the report."""


import logging
from pathlib import Path

import jinja2

from src.connection import DBConnector


class AssetsMissingError(Exception):
    """Error while creating a report."""


...


class AssetGenerator:
    """A worker that pulls the relevant data from the server, prints the images
    and prepares the other results for the report.

    Attributes:
        db_connector: A custom data base connector.

    Args:
        db_connector (DBConnector): A custom data base connector.
    """

    def __init__(self, db_connector: DBConnector) -> None:
        self.db_connector = db_connector

    def run(self) -> None:
        """Prepare all the images, tables and numbers and save them as a dynamic content."""
        NotImplemented


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
        context = {"name": "Siema"} # ! TODO: this is ofc temporary
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
    ReportCreator().generate()
    logging.info("New report has been generated.")
