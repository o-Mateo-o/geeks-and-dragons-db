#!/usr/bin/env python
import argparse
import os
import logging  # ! TO BE DELETED

from src import browser, fillup, logs, report

# Prepare the parser
parser = argparse.ArgumentParser(
    prog="Geeks & Dragons - Database Manager",
    description="To use the specific features of the app, add the flags.",
)
parser.add_argument(
    "-f",
    "--fill",
    action="store_true",
    help="if added, the database will be randomly filled",
)
parser.add_argument(
    "-r",
    "--report",
    action="store_true",
    help="if added, the report will be generated in the report dir",
)
parser.add_argument(
    "-o",
    "--open",
    action="store_true",
    help="if added, the report will be opened in the browser",
)


if __name__ == "__main__":
    # Do the logging, path and args setup
    os.chdir(".")
    args = parser.parse_args()
    logs.setup()

    # Perform all the possible steps
    if args.fill:
        logging.info("The database has been filled with random values.")
    if args.report:
        report.generate()
    if args.open:
        browser.open_report()
