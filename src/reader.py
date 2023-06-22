import logging
import subprocess
from os import startfile
from pathlib import Path
from sys import platform


class ReportOpenError(Exception):
    ...


class ReportOpener:
    def __init__(self) -> None:
        self.report_path = Path("reports/report.pdf")

    def error(self, platform_origin: bool = False) -> Exception:
        platform_info = " on this platform" if platform_origin else ""
        return ReportOpenError(
            f"Cannot open the report{platform_info}. "
            + f"Please try to do it manually: './{self.report_path.as_posix()}'."
        )

    def _open_any(self) -> None:
        if platform == "win32":
            startfile(self.report_path.absolute())
        elif platform in ["linux", "linux2"]:
            subprocess.call(["xdg-open", self.report_path.absolute()])
        else:
            raise self.error(platform_origin=True)

    def run(self) -> None:
        try:
            self._open_any()
        except FileNotFoundError:
            raise self.error()


def open_report() -> None:
    ReportOpener().run()
    logging.info("The newest report has been opened in a default browser.")
