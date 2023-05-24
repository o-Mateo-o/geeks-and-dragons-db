import argparse
import os
import logging

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
    os.chdir(".")
    args = parser.parse_args()
    logging.basicConfig(
        filename="log.log",
        level=logging.DEBUG,
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    if args.fill:
        logging.info("f")
    if args.report:
        logging.info("r")
    if args.open:
        logging.info("o")
