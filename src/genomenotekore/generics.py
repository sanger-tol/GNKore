import sys
import regex as re

"""
Generic Functions with multiple uses
"""

def validate_bioproject(putative_bid):
    """
    Validate the bioproject ID with regex
    """
    if ", " in putative_bid:
        bioproject_id, note = putative_bid.split(", ")
    else:
        bioproject_id = putative_bid
        note = "NA"

    bid = re.search(r"^PRJ[DEN][A-Z]\d+$", bioproject_id)
    if bid is None:
        sys.exit(f"BIOPROJECT_ID {bioproject_id} DOESN'T MATCH THE REGEX: '^PRJ[DEN][A-Z]\\d+$'")
    else:
        return bid.string, note

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
