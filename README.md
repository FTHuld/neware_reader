# neware_reader
This is a simple binary reader for Neware .nda files. It is based on the excellent work already done by thebestpatrick, who published the nda-extractor package in 2015. This package updates the exiting package and allows it to read the newest .nda files

The package currently does two things:
1. Output a .csv from an .nda input file with process_nda('input.nda')
2. Read a .nda directly into Python, using read_csv from pandas. read_nda('input.nda') also changes the step_ID column so that there is a unique identifier available for easy subsetting.
