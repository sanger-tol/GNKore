import os
import io
import requests

from .haplotype import Haplotype

class Assembly:
    def __init__(self, taxid, children):
        self.taxid = taxid
        self.accessions = children
        self.assembly_type, self.assembly_dict = self.fetch_assembly_data()

        self.assembly_data_1, self.assembly_data_2 = self.process_assembly_data()

        self.collection = self.__iter__()

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        return self.for_display()

    def __str__(self):
        return self.for_display()

    def for_display(self):
        txt = io.StringIO()
        txt.write(f"\n\t  {self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["raw_xml","collection", "assembly_dict", "assembly_type"]
        ]
        txt.write("\t  )")
        return txt.getvalue()

    def get_latest_revision(self, accession):
        """
        Fetch the revision history for a given assembly accession and return the latest
        accession and assembly name.
        """
        api_url = f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{accession}/revision_history?api_key={os.getenv('entrez_api_key')}"

        headers = {"Accept": "application/json"}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                data = response.json()
                # Check if there are assembly revisions
                if "assembly_revisions" in data and data["assembly_revisions"]:
                    # Sort revisions by release_date to get the latest one
                    revisions = sorted(data["assembly_revisions"], key=lambda x: x["release_date"], reverse=True)
                    latest_revision = revisions[0]
                    latest_accession = latest_revision.get("genbank_accession", accession)
                    latest_assembly_name = latest_revision.get("assembly_name", "Unknown assembly name")

                    if latest_accession != accession:
                        print(f"Update found: {accession} -> {latest_accession} ({latest_assembly_name})")
                    else:
                        print(f"No update needed for {accession} ({latest_assembly_name}).")

                    return latest_accession, latest_assembly_name
                else:
                    print(f"No revisions found for {accession}.")
                    return accession, None
            except ValueError:
                print("Error processing JSON response.")
                return accession, None
        else:
            print(f"Failed to fetch revision history, status code: {response.status_code}")
            return accession, None

    def fetch_assembly_details(self, assembly_bioproject):
        """
        Fetch specific assembly details for a given assembly BioProject and update
        all relevant fields to the latest versions.
        """
        url = "https://www.ebi.ac.uk/ena/portal/api/search"
        params = {
            'result': 'assembly',
            'includeAccessions': assembly_bioproject,
            'fields': 'accession,assembly_name,assembly_set_accession,tax_id',
            'limit': 40,
            'format': 'json'
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Failed to get data for project {assembly_bioproject}")
            return None

        assemblies = response.json()

        updated_assemblies = []
        for assembly in assemblies:
            current_accession = assembly.get('assembly_set_accession')
            if current_accession:
                latest_accession, latest_assembly_name = self.get_latest_revision(current_accession)
                if latest_accession != current_accession:
                    print(f"Updated assembly_set_accession: {current_accession} -> {latest_accession}")
                    assembly['assembly_set_accession'] = latest_accession
                if latest_assembly_name:
                    assembly['assembly_name'] = latest_assembly_name
            updated_assemblies.append(assembly)

        return updated_assemblies

    def determine_assembly_type(self, assembly_dicts):
        # TODO: WHERE ARE THE MULTI-PRIMARIES
        # Check if any assembly contains hap1 or hap2 in its name
        results = []
        for assembly in assembly_dicts:
            name = assembly['assembly_name']
            print(name)

            hap_list = ["hap1","hap2"]
            if any(id in name for id in hap_list):
                results.append('hap_asm')
            elif "alternate haplotype" in name: # 'assembly_name': 'iyTipFemo1.1 alternate haplotype'
                results.append('prim_alt')
            elif len(name.split(' ')) < 2: # 'assembly_name': 'iyTipFemo1.1'
                results.append('prim_alt')
            else:
                results.append(f'UNKNOWN ASSEMBLY TYPE: {name}')
        return results

    def fetch_assembly_data(self):
        """
        Fetch and process assembly data for a BioProject, ensuring correct tax_id.
        """
        assembly_dicts = []
        for bioproject in self.accessions:
            for assembly in self.fetch_assembly_details(bioproject):
                if assembly.get('tax_id') == self.taxid:
                    assembly_dicts.append(assembly)

        return self.determine_assembly_type(assembly_dicts), assembly_dicts


    def extract_prim_alt_assemblies(self, assembly_dicts, tax_id):
        """
        Extract primary and alternate haplotypes from assembly data, ensuring correct tax_id.
        """
        primary_assembly_dict = {}
        alternate_haplotype_dict = {}

        for assembly_dict in assembly_dicts:
            if assembly_dict['tax_id'] != tax_id:
                continue  # Skip assemblies with mismatched tax_id

            assembly_set_accession = assembly_dict['assembly_set_accession']
            assembly_name = assembly_dict['assembly_name']

            if 'alternate haplotype' in assembly_name.lower():
                alternate_haplotype_dict = {
                    "accession": assembly_set_accession,
                    "assembly_name": assembly_name
                }
            else:
                primary_assembly_dict = {
                    "accession": assembly_set_accession,
                    "assembly_name": assembly_name
                }

        return primary_assembly_dict, alternate_haplotype_dict

    def extract_haplotype_assemblies(self, assembly_dicts, tax_id):
        """Extract the latest haplotype assemblies from the assembly data."""
        hap1_dict = {}
        hap2_dict = {}

        for assembly_dict in assembly_dicts:
            name = assembly_dict['assembly_name'].lower()
            accession = assembly_dict['assembly_set_accession']

            # Identify haplotype 1 and select the latest version
            if "hap1" in name:
                if not hap1_dict or accession > hap1_dict["hap1_accession"]:
                    hap1_dict = {
                        "accession": accession,
                        "assembly_name": assembly_dict['assembly_name']
                    }

            # Identify haplotype 2 and select the latest version
            elif "hap2" in name:
                if not hap2_dict or accession > hap2_dict["hap2_accession"]:
                    hap2_dict = {
                        "accession": accession,
                        "assembly_name": assembly_dict['assembly_name']
                    }

        return hap1_dict, hap2_dict

    def extract_multiple_assemblies(self, assembly_dicts, tax_id):
        """Placeholder function to extract multiple primary assemblies."""
        # TODO: Placeholder implementation: This function should extract multiple assemblies.
        # Actual implementation should be added later.
        return {"accession": 'multiple_assemblies_info', "assembly_name": 'Placeholder for multiple assemblies extraction.'}


    def process_assembly_data(self):
        """
        Process assembly types and get further assembly data
        dict1 = the primary assembly
        dict2 = hap2/alternate
        """
        dict1, dict2 = {}, {}
        all_assemblies_same = all( i == self.assembly_type[0] for i in self.assembly_type)
        if all_assemblies_same & (len(self.assembly_type) > 0):

            if self.assembly_type[0] == 'hap_asm':
                dict1, dict2 = self.extract_haplotype_assemblies(self.assembly_dict, self.taxid)

            elif self.assembly_type[0] == 'prim_alt':
                dict1, dict2 = self.extract_prim_alt_assemblies(self.assembly_dict, self.taxid)

            elif self.assembly_type[0] == 'multiple_primary':
                dict1 = self.extract_multiple_assemblies(self.assembly_dict, self.taxid)
                dict2 = {}

            else:
                print("This is an unknown assembly type")

            return Haplotype(dict1, self.assembly_type[0], self.taxid), Haplotype(dict2, self.assembly_type[0], self.taxid)

        else:
            return dict1, dict2
