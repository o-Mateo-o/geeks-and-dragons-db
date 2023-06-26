#!/usr/bin/env python
import argparse
from os import chdir
from pathlib import Path

from src import DBManagerApp

# Prepare the parser
parser = argparse.ArgumentParser(
    prog="Geeks & Dragons - Database Manager",
    description="To use the specific features of the app, add the flags.\
        When asked about the password, type the one received from the authors\
        or use your own database, having altered the configuration files.",
    epilog="Note that the tool deletes all the views and tables before\
        filling the database again.",
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
    help="if added, the report will be opened in a default browser",
)


if __name__ == "__main__":
    chdir(Path("."))
    args = parser.parse_args()
    DBManagerApp().run(f=args.fill, r=args.report, o=args.open)
