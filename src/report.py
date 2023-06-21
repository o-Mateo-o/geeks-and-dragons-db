import logging
import os
import shutil
from pathlib import Path

import jinja2

from src.connection import DBConnector


class ReportCreator:
    def __init__(self) -> None:
        self.asset_paths = [
            Path("assets", "static", "style.css"),
            Path("assets", "static", "images", "top-image.jpg"),
        ]
        self.report_result = ""
        self.export_path = ""

    def _add_asset(self, *path_elems) -> Path:
        # ! USE THAT
        path = Path(*path_elems)
        self.asset_paths.append(path)
        self.asset_paths = list(set(self.asset_paths))
        return path

    def _fill_template(self, template_str: str) -> str:
        """Fill the template using Jinja templates.

        Args:
            template_str (str): String report template html file.

        Returns:
            str: String result report html file.
        """
        environment = jinja2.Environment()
        template = environment.from_string(template_str)
        context = {"name": "Siema"}
        return template.render(context)

    def _export_assets(self) -> None:
        for path in self.asset_paths:
            shutil.copy(path, self.export_path)
        index_path = self.export_path.joinpath("index.html")
        with index_path.open("w", encoding="utf-8") as f:
            f.write(self.report_result)

    def generate(self) -> str:
        """Read the template report file, fill the placeholders and save the results
        in the new report file.
        """
        try:
            template = Path("assets", "static", "report_template.html").read_text(
                encoding="utf-8"
            )
            self.report_result = self._fill_template(template)

            self.export_path = Path("reports", "report1")
            if not os.path.isdir(self.export_path):
                os.mkdir(self.export_path)
            self._export_assets()
            logging.info("New report has been generated.")

        except FileNotFoundError:
            logging.error(
                "Some assets were missing. The report could not be generated."
            )


def generate(db_connector: DBConnector) -> None:
    return ReportCreator().generate()
