# GNK (GenomeNoteKore): Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.1.0 - Rugby Chicken [12/05/2025]

Version 0.1.0 of GNK, the initial re-write of the GenomeNote Scripts provided by Karen Houliston

### Enhancements & Fixes

- Re-write of a number of scripts into OOP style Python3.13.
- List of Dictionaries of Lists are replaced with classes for Bioproject, Assebmly and Haplotype
    - Bioproject contains all information on a species assemblies
    - Assembly contains all information on the data in the form of linked accessions and component haplotypes.
    - In cases where there are multiple associated assemblies, the script will split them by assembly_version unless they are hap1/2. iyLasCalc2.1 -> 2.1. Each grouping (each assembly version) is then treated seperately for assembly_type search, in case they have been treated differently.
