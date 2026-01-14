#!/usr/bin/env python

import json
import argparse
import logging
import textwrap
from datetime import date
from dotenv import load_dotenv

from genomenotekore.generics import file_to_list
from genomenotekore.bioproject import Bioproject

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # logs to terminal
        logging.FileHandler("genomenotekore.log")  # logs to file
    ]
)
logger = logging.getLogger('gnkore_logger')

TIME = date.today()
VERSION = "0.1.0"
DESCRIPTION = f"""
| ---
| GenomeNoteKore
| Version: {VERSION}
| ---
| A Python3.13 script developed to generate the data needed
| to generate a GenomeNote-Article.
| ---
| Originally written by Karen Houliston
| Re-written by Damon-Lee Pointon (DLBPointon, dp24)
| ---
| This script will:
|   - Take a txt file containing a single bioproject id per line
|   -
"""


def parse_args(argv = None):
    parser = argparse.ArgumentParser(
        prog = "GenomeNoteKore",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent(DESCRIPTION)
    )

    parser.add_argument(
        "bioproject_file",
        help = "Path to a txt file containing 1 bioproject ID per line."
    )

    parser.add_argument(
        "-t", "--template_file",
        help = "Path to the template Word Document",
        default = "./template/template.docx"
    )

    parser.add_argument(
        "-e", "--environmental_values",
        help = "Path to a .env file containing credentials",
        default = ".env"
    )

    parser.add_argument(
        "-j", "--to_json",
        help = "Export data to json file",
        action='store_true'
    )

    parser.add_argument(
        "-s", "--to_stdout",
        help = "Print the json of data",
        action='store_true'
    )

    return parser.parse_args(argv)


def main():
    args = parse_args()

    # Load dotenv into environmental values
    # os.getenv() is used later on to get the value
    load_dotenv(args.environmental_values)

    bioproject_list = file_to_list(args.bioproject_file)
    for bioproject_line in bioproject_list:
        logger.info(f"Processing Bioproject: {bioproject_line}")
        bioproject_data = Bioproject(bioproject_line[0].strip(), bioproject_line[1].strip())

        if args.to_json or args.to_stdout:
            logger.info(f"Converting to JSON output: saving to ./{bioproject_line[0]}.json")
            jsonised = json.dumps(dict(bioproject_data))

            if args.to_json:
                with open (f"{bioproject_line[0]}.json", 'w') as json_out:
                    json_out.write(jsonised)

            if args.to_stdout:
                print(jsonised)
