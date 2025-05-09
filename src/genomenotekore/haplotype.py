import io

class Haplotype:
    def __init__(self, assembly_dict, assembly_type, taxid):
        self.taxid = taxid
        self.assembly_type = assembly_type
        self.hap_name = assembly_dict["assembly_name"]
        self.hap_accession = assembly_dict["accession"]
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
        txt.write(f"\n\t\t  {self.__class__.__name__}(\n")
        [
            txt.write(f"\t\t\t{a} = '{v}' \n")
            for a, v in self.collection
            if a not in ["raw_xml","collection"]
        ]
        txt.write("\t\t  )")
        return txt.getvalue()
