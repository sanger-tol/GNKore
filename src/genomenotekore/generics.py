import sys
import regex as re

"""
Generic Functions with multiple uses
"""

def validate_bioproject(putative_bid):
    """
    Validate the bioproject ID with regex
    """
    bid = re.search(r"^PRJ[DEN][A-Z]\d+$", putative_bid)
    if bid is None:
        print(f"BIOPROJECT_ID {putative_bid} DOESN'T MATCH THE REGEX: '^PRJ[DEN][A-Z]\\d+$'")
        return "NA"
    else:
        return bid.string

def file_to_list(file_path):
    """
    Read file and return a line per item in list
    """
    with open(file_path, 'r') as file:
        lines = [ line.strip() for line in file.readlines() ]
        if lines == [''] or len(lines) < 1:
            sys.exit(f"No valid entries in {file_path}")
        else:
            validated_list = [validate_bioproject(line.strip()) for line in lines if validate_bioproject(line.strip()) != "NA"]
            return validated_list
