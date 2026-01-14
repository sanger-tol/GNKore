import os
import io
import sys
import logging
import requests
# import tenacity # <-
import xml.etree.ElementTree as ET

from .assembly import Assembly
from .generics import fetch_data

logger = logging.getLogger("gnkore_logger")

class Bioproject:
    def __init__(self, bioproject_id, note):
        self.bioproject: str                        = bioproject_id
        self.note: str                              = note
        self.raw_xml, self.study_title, self.taxid  = self.parse_xml_data()
        self.child_accessions                       = self.Bioproject_get_child_accessions(self.raw_xml)
        self.taxonomy_ranks                         = self.NCBI_get_taxonomy_lineage_and_ranks()
        gbif_data                                   = self.GBIF_get_data()
        self.taxonomic_authority: str               = gbif_data["tax_auth"]
        self.common_name: str                       = gbif_data["common_name"]
        self.gbif_url: str                          = gbif_data["gbif_url"]
        self.gbif_usage_key: str                    = gbif_data["gbif_usage_key"]
        self.assembly                               = Assembly(self.taxid, self.child_accessions)
        self.collection                             = self.__iter__()


    def __iter__(self):
        for attr, value in self.__dict__.items():
            if attr not in ["raw_xml","collection", "assembly_dict", "assembly_type"]:
                if isinstance(value, Assembly):
                    yield attr, dict(value)
                else:
                    yield attr, value


    def parse_xml_data(self):
        """
        Parses the study_title and tax_id for the umbrella bioproject from the fetched data.
        """
        raw_xml = fetch_data(self.bioproject)
        title = raw_xml.find(".//TITLE")
        description = title.text if title is not None else "No description available"
        tax_id = str(raw_xml.find(".//TAXON_ID").text) if raw_xml.find(".//TAXON_ID") is not None else None # pyright: ignore
        return raw_xml, description, tax_id

    def Bioproject_get_child_accessions(self, raw_xml):
        "Parses all child project accessions for a given BioProject from the fetched data."
        return [child_project.get('accession') for child_project in raw_xml.iter('CHILD_PROJECT')]


    def NCBI_parse_xml(self, response_content):
        """
        Parse the NCBI XML response for taxonomy data.
        """
        root = ET.fromstring(response_content)
        lineage = []
        ranks = {'class': None, 'family': None, 'order': None, 'phylum': None, 'species': None}
        for taxon in root.iter('Taxon'):
            rank = taxon.find('Rank').text if taxon.find('Rank') is not None else None # pyright: ignore
            scientific_name = taxon.find('ScientificName').text if taxon.find('ScientificName') is not None else None # pyright: ignore

            # Assign scientific names to their respective ranks
            if rank in ranks:
                ranks[rank] = scientific_name # pyright: ignore

            # Extract lineage information
            lineage_ex = taxon.find('LineageEx')
            if lineage_ex is not None:
                for element in lineage_ex:
                    lineage.append(element.find('ScientificName').text) # pyright: ignore

        # Remove "cellular organisms" if present at the start of the lineage
        if lineage and lineage[0] == "cellular organisms":
            lineage = lineage[1:]

        return {'lineage': '; '.join(lineage), **ranks}


    def NCBI_get_taxonomy_lineage_and_ranks(self):
        """
        Fetch taxonomic classification and lineage from NCBI if available
        """
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id={self.taxid}&retmode=xml&api_key={os.getenv("ENTREZ_API")}"
        headers = {"User-Agent": f"Sanger ToL GenomeNote Script Suite; {os.getenv("ENTREZ_EMAIL")}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.content:
            try:
                return self.NCBI_parse_xml(response.content)
            except ET.ParseError as e:
                print(f"Error parsing XML: {e}")
                return {}
        else:
            sys.exit(f"NCBI_get_taxonomy_lineage_and_ranks: Failed to fetch data for taxid {self.taxid}, status code: {response.status_code}\n Data = {response.content}")
            logger.warn(f"NCBI_get_taxonomy_lineage_and_ranks: Failed to fetch data for taxid {self.taxid}, status code: {response.status_code}\n Data = {response.content}")
            return {}


    def GBIF_get_data(self):
        """
        Collect GBIF related data about taxonomy
        """
        tax_dict = {
            "tax_auth": "",
            "common_name": "",
            "gbif_url": "",
            "gbif_usage_key": ""
        }

        try:
            genus, specificEpithet = self.taxonomy_ranks["species"].split(" ")
        except ValueError:
            # TODO: Handle input that doesn't split into exactly two parts
            return tax_dict

        initial_url = f"https://api.gbif.org/v1/species/match?specificEpithet={specificEpithet}&strict=true&genus={genus}"

        response = requests.get(initial_url)
        if response.status_code == 200:
            match_data = response.json()
            usage_key = match_data.get("usageKey")

            if usage_key:
                species_url = f"https://api.gbif.org/v1/species/{usage_key}"
                species_response = requests.get(species_url)

                if species_response.status_code == 200:
                    species_data = species_response.json()

                    tax_dict["tax_auth"] = species_data.get("authorship", "").strip()
                    tax_dict["common_name"] = species_data.get("vernacularName", "")
                    tax_dict["gbif_url"] = species_url
                    tax_dict["gbif_usage_key"] = usage_key

        return tax_dict
