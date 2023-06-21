#!/usr/bin/env python
import argparse
import os

from src import drandom, fillup, logs, reader, report, connection

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
    db_connector = connection.DBConnector()
    if args.fill:
        data = drandom.generate_data()
        fillup.push(data, db_connector)
    if args.report:
        report.generate(db_connector)
    if args.open:
        reader.open_report()
