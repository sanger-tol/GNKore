# GenomeNoteKore
---
Originally written by Karen Houliston (GRIT).

Project has been written by Damon-Lee Pointon to improve functionality, performance, organisation and robustness.

---

GenomeNoteKore is a series of script to take a list of accession numbers and retrieve information from the NCBI/ENA/COPO databases and then process the data to generate a GenomeNote-Article. These scripts will be used in conjuction with the GenomeNote-Pipeline (sanger-tol/genomenote).

---

In an effort for test data to be as wide reaching as possible, then file `/src/data/test_list.txt` contains a list of real and false bioproject_ids:
```
Spaceship <- Junk data
PRJDB101 <- A random project ID for the `Mouse oocyte methylome` project
Stargate <- Junk data at a second index
PRJEB51917 <-- ToL sample `Tiphia Femorata`, which should be a perfect example
PRJEB27699 <-- ToL sample `Aquila chrysaetos chrysaetos` with a three part name which is shrunk by
```

---

You can run the script with:
```
genomenotekore.py \
    src/data/minimal_list.txt \
    -t src/data/Psyche_accepted_GN_structure_Feb\ 2025.docx
```

---

An example of a bioproject with multiple versions of assembly is `PRJEB55936` also known as `Lasioglossum calceatum (common furrow bee)`, the class structure is currently (12/05/2025):

```python
Bioproject(
	bioproject = 'PRJEB55936'
	note = 'Lasioglossum calceatum (common furrow bee)'
	study_title = 'Lasioglossum calceatum (common furrow bee)'
	taxid = '88504'
	child_accessions = '['PRJEB55935', 'PRJEB72768', 'PRJEB72769', 'PRJEB73469', 'PRJEB73470', 'PRJEB74371']'
	taxonomy_ranks = '{'lineage': 'Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Ecdysozoa; Panarthropoda; Arthropoda; Mandibulata; Pancrustacea; Hexapoda; Insecta; Dicondylia; Pterygota; Neoptera; Endopterygota; Hymenoptera; Apocrita; Aculeata; Apoidea; Anthophila; Halictidae; Halictinae; Halictini; Lasioglossum; Evylaeus', 'class': 'Insecta', 'family': 'Halictidae', 'order': 'Hymenoptera', 'phylum': 'Arthropoda', 'species': 'Lasioglossum calceatum'}'
	taxonomic_authority = '(Scopoli, 1763)'
	common_name = 'Slender Mining Bee'
	gbif_url = 'https://api.gbif.org/v1/species/1354476'
	gbif_usage_key = '1354476'
	assembly_data = '
	  Assembly(
		taxid = '88504'
		accessions = '['PRJEB55935', 'PRJEB72768', 'PRJEB72769', 'PRJEB73469', 'PRJEB73470', 'PRJEB74371']'
		assembly_data = '[
		  Haplotype(
			taxid = '88504'
			assembly_type = 'prim_alt'
			hap_name = 'iyLasCalc2.1 alternate haplotype'
			hap_accession = 'GCA_963966685'
			hap_set_accession = 'GCA_963966685.1'
		  ),
		  Haplotype(
			taxid = '88504'
			assembly_type = 'prim_alt'
			hap_name = 'iyLasCalc2.1'
			hap_accession = 'GCA_963966675'
			hap_set_accession = 'GCA_963966675.1'
		  ),
		  Haplotype(
			taxid = '88504'
			assembly_type = 'prim_alt'
			hap_name = 'iyLasCalc3.1 alternate haplotype'
			hap_accession = 'GCA_963971085'
			hap_set_accession = 'GCA_963971085.1'
		  ),
		  Haplotype(
			taxid = '88504'
			assembly_type = 'prim_alt'
			hap_name = 'iyLasCalc3.1'
			hap_accession = 'GCA_963971175'
			hap_set_accession = 'GCA_963971175.1'
		  )]'
	  )'
)
2025-05-12 12:49:01,662 [INFO] Processing Bioproject: ('PRJEB79186', 'Kretania trappi (Alpine zephyr blue)')
No update needed for GCA_964264435.1 (ilKreTrap1.hap1.1).
No update needed for GCA_964264395.1 (ilKreTrap1.hap2.1).
 ASSEM GROUP [{'accession': 'GCA_964264435', 'assembly_name': 'ilKreTrap1.hap1.1', 'assembly_set_accession': 'GCA_964264435.1', 'tax_id': '2505780', 'assembly_type': 'hap_asm'}, {'accession': 'GCA_964264395', 'assembly_name': 'ilKreTrap1.hap2.1', 'assembly_set_accession': 'GCA_964264395.1', 'tax_id': '2505780', 'assembly_type': 'hap_asm'}]
HAP_ASM: [{'accession': 'GCA_964264435', 'assembly_name': 'ilKreTrap1.hap1.1', 'assembly_set_accession': 'GCA_964264435.1', 'tax_id': '2505780', 'assembly_type': 'hap_asm'}, {'accession': 'GCA_964264395', 'assembly_name': 'ilKreTrap1.hap2.1', 'assembly_set_accession': 'GCA_964264395.1', 'tax_id': '2505780', 'assembly_type': 'hap_asm'}]
Bioproject(
	bioproject = 'PRJEB79186'
	note = 'Kretania trappi (Alpine zephyr blue)'
	study_title = 'Kretania trappi (Alpine zephyr blue)'
	taxid = '2505780'
	child_accessions = '['PRJEB79185', 'PRJEB80179', 'PRJEB80180']'
	taxonomy_ranks = '{'lineage': 'Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Ecdysozoa; Panarthropoda; Arthropoda; Mandibulata; Pancrustacea; Hexapoda; Insecta; Dicondylia; Pterygota; Neoptera; Endopterygota; Amphiesmenoptera; Lepidoptera; Glossata; Neolepidoptera; Heteroneura; Ditrysia; Obtectomera; Papilionoidea; Lycaenidae; Polyommatinae; Kretania', 'class': 'Insecta', 'family': 'Lycaenidae', 'order': 'Lepidoptera', 'phylum': 'Arthropoda', 'species': 'Kretania trappi'}'
	taxonomic_authority = '(Verity, 1927)'
	common_name = 'Alpine Zephyr Blue'
	gbif_url = 'https://api.gbif.org/v1/species/10854079'
	gbif_usage_key = '10854079'
	assembly_data = '
	  Assembly(
		taxid = '2505780'
		accessions = '['PRJEB79185', 'PRJEB80179', 'PRJEB80180']'
		assembly_data = '[
		  Haplotype(
			taxid = '2505780'
			assembly_type = 'hap_asm'
			hap_name = 'ilKreTrap1.hap1.1'
			hap_accession = 'GCA_964264435'
			hap_set_accession = 'GCA_964264435.1'
		  ),
		  Haplotype(
			taxid = '2505780'
			assembly_type = 'hap_asm'
			hap_name = 'ilKreTrap1.hap2.1'
			hap_accession = 'GCA_964264395'
			hap_set_accession = 'GCA_964264395.1'
		  )]'
	  )'
)
```
