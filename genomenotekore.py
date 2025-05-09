#!/usr/bin/env python

import os
import argparse
import logging
import textwrap
from datetime import date
from dotenv import load_dotenv

from src.genomenotekore.generics import file_to_list
from src.genomenotekore.bioproject import Bioproject

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # logs to terminal
        logging.FileHandler("genomenotekore.log")  # logs to file
    ]
)

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
        default = "./template/template.docx",
        type = argparse.FileType('r')
    )

    parser.add_argument(
        "-e", "--environmental_values",
        help = "Path to a .env file containing credentials",
        default = ".env"
    )

    return parser.parse_args(argv)


def main(args):
    load_dotenv(args.environmental_values)

    bioproject_list = file_to_list(args.bioproject_file)
    for i in bioproject_list:
        logging.info(f"Processing Bioproject: {i}")
        bioproject_data = Bioproject(i)
        print(bioproject_data)


if __name__ == "__main__":
    main(
        parse_args()
    )
