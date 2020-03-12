#!/bin/python3.4
import pandas as pd
from . import new_nda, old_nda

def read_nda(inpath):
#def process_nda(inpath, outpath=':auto:'):
#    if outpath == ':auto:':
#        outpath = inpath + '.csv'

    with open(inpath, 'rb') as f:
        data = f.read()

    if data[112:115] == b'BTS':
        outdata = old_nda.old_nda(inpath)
#        old_nda.old_nda(inpath, outpath=':auto:')
    else:
        outdata = new_nda.new_nda(inpath)
#        new_nda.new_nda(inpath, outpath=':auto:')
    return outdata

# read_nda() just takes the output of process_nda() and reads it into python.
# It also sorts the lines in the file and removes duplicates (which may occur
# due to error signals when e.g. Voltage exceed the set limits), as well as
# setting sequential values for step_ID. This makes subsetting easier, since
# you don't need to refer to the procedure file.
#
# If you just want to read the file without doing this extra stuff just use
# read_csv() from pandas and apply it to the csv file outputted by process_nda()

def nda_to_csv(inpath, outpath=':auto:'):
#    process_nda(inpath)

    if outpath == ':auto:':
        outpath = inpath + '.csv'

    df = read_nda(inpath)
    df.to_csv(outpath)