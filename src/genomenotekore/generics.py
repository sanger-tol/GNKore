import sys
import regex as re

"""
Generic Functions with multiple uses
"""

def find(lst, key, value):
    """
    Found this function on SO to get the index of item in list where items are dicts
    https://stackoverflow.com/questions/4391697/find-the-index-of-a-dict-within-a-list-by-matching-the-dicts-value
    """
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

def format_sex_chromosomes(sex_chromosomes):
    """
    Format a list of sex chromosomes for natural language output.

    Returns:
    - str: Formatted string for use in the abstract.
    """
    if len(sex_chromosomes) == 1:
        return sex_chromosomes[0]
    elif len(sex_chromosomes) == 2:
        return f"{sex_chromosomes[0]} and {sex_chromosomes[1]}"
    else:
        return ", ".join(sex_chromosomes[:-1]) + f", and {sex_chromosomes[-1]}"

def custom_sort_order(molecule):
    special_order = {
        'X'     : (10000, 'X'),
        'Y'     : (10001, 'Y'),
        'W'     : (10002, 'W'),
        'Z'     : (10003, 'Z'),
        'MT'    : (10004, 'MT'),
        'Pltd'  : (10005, 'Pltd')
    }
    if molecule in special_order:
        return special_order[molecule]

    match = re.match(r"(\d+)([A-Za-z]*)", molecule)
    if match:
        return (int(match.group(1)), match.group(2))

    return (float('inf'), molecule)


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
