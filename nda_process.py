#!/bin/python3.4
import sys, getopt
import binascii
import time
import math
import datetime
import csv
import pandas as pd
from nda_extractor import bin2csv, bin2csv2

def process_nda(inpath, outpath=':auto:'):
    if outpath == ':auto:':
        outpath = inpath + '.csv'

    with open(inpath, 'rb') as f:
        data = f.read()

    if data[112:115] == b'BTS':
        bin2csv.old_nda(inpath, outpath=':auto:')
    else:
        bin2csv2.new_nda(inpath, outpath=':auto:')

# read_nda() just takes the output of process_nda() and reads it into python.
# It also sorts the lines in the file and removes duplicates (which may occur
# due to error signals when e.g. Voltage exceed the set limits), as well as
# setting sequential values for step_ID. This makes subsetting easier, since
# you don't need to refer to the procedure file.
#
# If you just want to read the file without doing this extra stuff just use
# read_csv() from pandas and apply it to the csv file outputted by process_nda()
def read_nda(inpath, outpath=':auto:'):
    process_nda(inpath)
    
    if outpath == ':auto:':
        outpath = inpath + '.csv'
    
    df = pd.read_csv(outpath)
    df = df.sort_values(by=['record_ID'])
    df = df.drop_duplicates(subset=['record_ID'], keep='first')

    if 'jumpto' in df.columns:
        corr = [1]
        a = 1
        count_a_vals = df['jumpto'].values
        count_b_vals = df['step_ID'].values

        diffs_a = count_a_vals[:-1] - count_a_vals[1:]
        diffs_b = count_b_vals[:-1] - count_b_vals[1:]

        for g, h in zip(diffs_a, diffs_b):
            if (g !=0) or (h != 0):
                a += 1

            corr.append(a)

        df['step_ID'] = corr    

    else:
        corr = [0]
        a = 0
        count_a_vals = df['step_jump'].values
        diffs_a = count_a_vals[:-1] - count_a_vals[1:]

        for i in diffs_a:
            if i > 0:
                a += 1
            if i == -2:
                a += 1
            corr.append(a)


        df['step_ID'] = df['step_ID']-corr
    
    return df
