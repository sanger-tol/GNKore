# GenomeNoteKore
---
Originally written by Karen Houliston (GRIT) and ChatGPT.

Project has been written by Damon-Lee Pointon to improve functionality, performance and robustness.

---

GenomeNoteKore is a series of script to take a list of accession numbers and retrieve information from the NCBI/ENA/COPO databases and then process the data to generate a GenomeNote-Article. These scripts will be used in conjuction with the GenomeNote-Pipeline (sanger-tol/genomenote).

---

In an effort for test data to be as wide reaching as possible, then file `/src/data/test_list.txt` contains a list of real and false bioproject_ids:
```
Spaceship <- Junk data
PRJDB101 <- A random project ID for the `Mouse oocyte methylome` project
Stargate <- Junk data at a second index
PRJEB51917 <-- ToL sample `Tiphia Femorata`, which should be a perfect example
PRJEB27699 <-- ToL sample `Aquila chrysaetos chrysaetos` with a three part name which is shrunk by NCBI
```
