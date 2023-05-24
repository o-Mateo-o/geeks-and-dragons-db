import webbrowser
from pathlib import Path
import logging


def open_report() -> None:
    report = Path("reports", "report1", "index.html")
    webbrowser.open_new_tab(report)
    logging.info("The newest report has been opened in a browser.")
