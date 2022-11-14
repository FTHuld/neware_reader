**Neware reader**

This Python Package was developed to help researchers to extract data from Neware battery analyzers.

Free software: BSD-2 license

**Usage**::

  from neware_reader import read_nda, csv_to_nda
  
  filename = "path/to/cycling/data.nda"
  df = read_nda(filename) # returns pandas dataframe

Using the option ``beta=True`` in ``read_nda()`` or ``csv_to_nda()`` will use a function to calculate how to transform the current to mA correctly. If you use this option and it works, please let us know. If it doesn't work, please also let us know.

**Installation**

Install using pip directly from github:

``pip install git+https://github.com/FTHuld/neware_reader.git``
  
or (if git is not installed):

``pip install --upgrade https://github.com/FTHuld/neware_reader/tarball/master``

**Credits**

This is a collaborative work between Beyonder (http://beyonder.no/home), Corvus Energy (https://corvusenergy.com/), and IFE (http://ife.no/en/).

