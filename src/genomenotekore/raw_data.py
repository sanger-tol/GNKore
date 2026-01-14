import io
import sys
import logging
import requests

logger = logging.getLogger("gnkore_logger")

class RawAssemblyData():
    def __init__(self, sample_id):
        self.sample_id: str = sample_id
        self.ena_data_on_sample = self.get_ena_data()

        self.collection                         = self.__iter__()

    def __iter__(self):
        for attr, value in self.__dict__.items():
            if attr not in ["raw_xml","collection", "assembly_dict", "assembly_type"]:
                yield attr, value


    def get_ena_data(self) -> dict:
        ena_fields: list[str] = [
            "study_accession","sample_accession","experiment_accession",
            "run_accession","tax_id","scientific_name","instrument_model",
            "library_name","library_layout","library_strategy","center_name",
            "fastq_md5","fastq_ftp","submitted_md5","submitted_ftp",
            "submitted_format","bam_file_role"
        ]
        api_url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={self.sample_id}&result=read_run&fields={",".join(ena_fields)}&format=json"

        headers = {"Accept": "application/json"}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                logger.info(f"Got raw data info from ENA for {self.sample_id}")
                data = response.json()

            except ValueError:
                logger.info("Error processing JSON response")
                data = {}

        return data
