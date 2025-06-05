import io
import os
import requests
import logging

from .generics import custom_sort_order, format_sex_chromosomes


logger = logging.getLogger("logger")

class Haplotype:
    def __init__(self, assembly_type):
        self.taxid                   = assembly_type["tax_id"]
        self.assembly_type           = assembly_type["assembly_type"]
        self.hap_name                = assembly_type["assembly_name"]
        self.hap_value               = self.hap_name.split(".")[1] if ".hap" in str(self.hap_name) else "NA"
        self.hap_accession           = assembly_type["accession"]
        self.hap_set_accession       = assembly_type["assembly_set_accession"]

        ### NCBI DATASET API CHUNK
        ncbi_assembly_data           = self.NCBI_fetch_primary_assembly_info()
        self.tolid                   = ncbi_assembly_data.get("tolid", "NA")                    # pyright: ignore
        self.assembly_level          = ncbi_assembly_data.get("assembly_level", "NA")           # pyright: ignore
        self.wgs_project_accession   = ncbi_assembly_data.get("wgs_project_accession", "NA")    # pyright: ignore
        self.raw_total_length        = int(ncbi_assembly_data.get("total_length", 0))           # pyright: ignore

        # Format as 1,000 rather than 1000
        self.contig_count            = f"{int(ncbi_assembly_data.get("num_contigs", 0)):,}"     # pyright: ignore
        self.scaffold_count          = f"{int(ncbi_assembly_data.get("num_scaffolds", 0)):,}"   # pyright: ignore

        # Format as val / 1e6 to get val in mb
        self.contig_N50_mb           = f"{int(ncbi_assembly_data.get("contig_N50", 0)) / 1e6:,.2f}"     # pyright: ignore
        self.scaffold_N50_mb         = f"{int(ncbi_assembly_data.get("scaffold_N50", 0)) / 1e6:,.2f}"   # pyright: ignore

        # Format genome length as raw, mb and gb
        self.genome_length_unrounded = int(ncbi_assembly_data.get("genome_length_unrounded", 0))        # pyright: ignore
        self.genome_length_mb        = f"{self.genome_length_unrounded / 1e6:,.2f}"
        self.genome_length_gb        = f"{self.genome_length_unrounded / 1e9:,.2f}"

        # No formatting needed
        self.chromosome_count        = int(ncbi_assembly_data.get("chromosome_count", 0))               # pyright: ignore
        self.coverage                = int(ncbi_assembly_data.get("coverage", 0))                       # pyright: ignore

        self.assembly_statistics     = self.NCBI_fetch_assembly_statistics()
        self.longest_scaffold        = self.get_longest_scaffold(self.assembly_statistics) if self.assembly_statistics != None else None

        if assembly_type == "pri_alt":
            self.chromosome_table    = self.get_chromosome_table(self.assembly_statistics)
        elif assembly_type == "hap_asm":
            # If chromosome scale then get chromosome_table
            # If not, then the Assembly Class will control it.
            self.chromosome_table    = self.get_chromosome_table(self.assembly_statistics) if self.assembly_level == "chromosome" else None
        else:
            self.chromosome_table    = None

        # TODO: DOES THIS MEAN `IF ASSEMBLY_LEVEL is CHROMOSOME`?
        #       - IF BOTH HAPS ARE TRUE AND TYPE IS `hap_asm` THEN THERE NEEDS TO BE A COMBINE_HAPLOTYPE_TABLES
        self.combine_the_haps        = True if self.assembly_level != 'scaffold' else False

        # Turn off sex chromosome ID if assembly type is hap_asm
        self.sex_chromosomes         = self.get_sex_chromosomes(self.chromosome_table) if self.chromosome_table != None and self.assembly_type != "hap_asm" else None
        self.formatted_sex_chr       = format_sex_chromosomes(self.sex_chromosomes) if self.sex_chromosomes != None else None


        self.collection              = self.__iter__()

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        return self.for_display()

    def __str__(self):
        return self.for_display()

    def for_display(self):
        txt = io.StringIO()
        txt.write(f"\n\t\t  {self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["raw_xml","collection"]
        ]
        txt.write("\t\t  )")
        return txt.getvalue()


    def NCBI_fetch_primary_assembly_info(self):
        """
        Fetch data for the given accession and extract necessary fields including tolid and wgs_project_accession.
        """
        api_url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{self.hap_accession}/dataset_report"
        headers = {
            'accept': 'application/json',
            'User-Agent': f'Python script; {os.environ["ENTREZ_EMAIL"]}'
        }
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            logger.info(f"Failed to fetch data for {self.hap_accession}: HTTP {response.status_code}")
            return None

        data = response.json()
        if not data or 'reports' not in data or len(data['reports']) == 0:
            logger.info(f"No valid report data found for {self.hap_accession}")
            return None

        report = data['reports'][0]
        assembly_stats = report['assembly_stats']

        parsed_assembly_data = {
            'assembly_level': report['assembly_info'].get('assembly_level', "NA").lower(),
            'total_length': assembly_stats.get('total_sequence_length', 0),
            'num_contigs': assembly_stats.get('number_of_contigs', 0),
            'contig_N50': assembly_stats.get('contig_n50', 0),
            'num_scaffolds': assembly_stats.get('number_of_scaffolds', 0),
            'scaffold_N50': assembly_stats.get('scaffold_n50', 0),
            'chromosome_count': assembly_stats.get('total_number_of_chromosomes', 0),
            'genome_length_unrounded': assembly_stats.get('total_sequence_length', 0),
            'coverage': assembly_stats.get('genome_coverage', 0)
        }

        # Extracting tolid from attributes if available
        biosample = report.get('assembly_info', {}).get('biosample', {})
        attributes = biosample.get('attributes', {})
        for attribute in attributes:
            if attribute.get('name') == 'tolid':
                parsed_assembly_data['tolid'] = attribute.get('value')
                break

        # Extracting wgs_project_accession from wgs_info if available
        wgs_info = report.get('wgs_info', {})
        parsed_assembly_data['wgs_project_accession'] = wgs_info.get('wgs_project_accession', 'N/A')
        return parsed_assembly_data


    def NCBI_fetch_assembly_statistics(self):
        """
        Fetch assembly stats from the NCBI API v2.
        """
        api_url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{self.hap_accession}/sequence_reports"

        headers = {
            'accept': 'application/json',
            'User-Agent': f'Python script; {os.environ["ENTREZ_EMAIL"]}'
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            logger.info(f"Failed to fetch data for {self.hap_accession}: HTTP {response.status_code}")
            return None
        data = response.json()

        if not data or 'reports' not in data or len(data['reports']) == 0:
            logger.info(f"No valid report data found for {self.hap_accession}")
            return None

        return [report for report in data['reports'] if report['role'] == "assembled-molecule"]


    def get_longest_scaffold(self, reports):
        """
        Get the longest scaffold from the API data, filtered by 'assembled-molecule'.
        Returns largest scaffold in megabase (mb)
        """
        longest_scaffold = max(reports, key=lambda x: x['length'])
        return round(float(longest_scaffold['length']) / 1e6, 2)


    def get_chromosome_table(self, reports):
        chr_table_list = []
        for chr_entry in reports:
            chr_dict = {
                "INSDC": chr_entry['genbank_accession'],
                "molecule": chr_entry['chr_name'],
                "length": round(chr_entry['length'] / 10**6, 2),
                "GC": chr_entry['gc_percent']
            }
            chr_table_list.append(chr_dict)

        return sorted(chr_table_list, key=lambda x: custom_sort_order(x['molecule']))


    def get_sex_chromosomes(self, chromosome_report):
        sex_chromosomes = set()
        valid_sex_chromosomes = {'X', 'Y', 'Z', 'W', 'X1', 'X2', 'B'}

        for chr_entry in chromosome_report:
            chr_name = chr_entry.get('molecule', '').upper()  # Normalize to uppercase
            if chr_name in valid_sex_chromosomes:
                sex_chromosomes.add(chr_name)

        return sorted(sex_chromosomes)


    def fetch_chromosome_data(self):
        chromosome_dict = self.get_chromosome_table(self.hap_accession) if self.assembly_type == 'prim_alt' else None
        return chromosome_dict
