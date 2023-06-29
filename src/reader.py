"""Automatic report opening."""

import logging
import subprocess
from os import startfile
from pathlib import Path
from sys import platform


class ReportOpenError(Exception):
    """Error when the report cannot be opened."""

    ...


class ReportOpener:
    """Cross-platform report opener.

    Attributes:
        report_path: A path to the newest report.
    """

    def __init__(self) -> None:
        self.report_path = self.fresh_report_path()

    def fresh_report_path(self) -> Path:
        """Get the path to the newest report.

        Returns:
            Path: A path to the newest report.
        """
        # TODO: Evalate the newest path analyzing the dates
        return Path("reports/report.pdf")

    def _open_any(self) -> None:
        """Open the report using the different techniques, depending on the platform.

        Raises:
            ReportOpenError: If the platform infrastructure does not cooperate.
        """
        if platform == "win32":
            startfile(self.report_path.absolute())
        elif platform in ["linux", "linux2"]:
            subprocess.call(["xdg-open", self.report_path.absolute()])
        else:
            raise ReportOpenError(
                "Cannot open the report on this platform. Please try to do it manually:"
                + f"'./{self.report_path.as_posix()}'."
            )

    def run(self) -> None:
        """Open the report in a default browser handling the file errors.

        Raises:
            ReportOpenError: If the file was not found.
        """
        try:
            self._open_any()
        except FileNotFoundError:
            raise FileNotFoundError("Cannot open the report. The file was not found.")


def open_report() -> None:
    """Open the latest report in a default browser. Log the success info."""
    ReportOpener().run()
    logging.info("The newest report has been opened in a default browser.")
