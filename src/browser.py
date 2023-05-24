import webbrowser
from pathlib import Path
import logging


def open_report() -> None:
    report = Path("reports", "report.html")
    webbrowser.open_new_tab(report)
    logging.info("The report has been opened in a browser.")
