#!/bin/python3.4
import pandas as pd
from . import new_nda, old_nda

def read_nda(inpath, testcols=False, split=False, small=False):
    # inpath: 'yourfile.nda'
    # testcols: columns of data that are empty in my files, but might contain data (e.g. temperature).
    # split: in newer nda files capacity and energy are in separate columns depending on the direction of the current.
    # split=False outputs a single column for each (one for capacity and one for energy), while split=True outputs two
    # for each (chg_capacity_mAh, dchg_capacity_mAh, chg_energy_mWh, and dchg_energy_mWh)
    # small: converts the data from float64 to float32. small=True also omits the 'timestamp', as well as returning numbers
    # instead of strings for 'step_name'. small=True tends to reduce the size of the dataframe by 50-70%

    with open(inpath, 'rb') as f:
        data = f.read()

    if data[112:115] == b'BTS':
        outdata = old_nda.old_nda(inpath, testcols=testcols, split=split, small=small)
    else:
        outdata = new_nda.new_nda(inpath, testcols=testcols, split=split, small=small)

    return outdata

def nda_to_csv(inpath, outpath=':auto:', testcols=False, split=False, small=False):
#    process_nda(inpath)

    if outpath == ':auto:':
        outpath = inpath + '.csv'

    df = read_nda(inpath, testcols=testcols, split=split, small=small)
    df.to_csv(outpath)