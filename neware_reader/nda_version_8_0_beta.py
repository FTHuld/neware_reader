#!/bin/python3.4

import sys, getopt
import binascii
import time
import math
import datetime
import numpy as np
import pandas as pd


def get_step_name(s):

    if s==1:
        return 'CC_Chg'
    elif s==2:
        return 'CC_Dchg'
    elif s==3:
        return 'N/A'
    elif s==4:
        return 'Pause'
    elif s==5:
        return 'Cycle'
    elif s==6:
        return 'End'
    elif s==7:
        return 'CCCV_Chg'
    elif s==8:
        return 'CP_Dchg'
    elif s==9:
        return 'CP_Chg'
    elif s==10:#WHAT IS 11-19??
        return 'CR_Dchg'
    elif s==19:
        return 'CV_Dchg'
    elif s == 20:
        return "CCCV_Dchg"
    else:
        return str(s)


def multiplier(rng_cur):
    cur_scale_10 = 10
    cur_scale_100 = 100
    cur_scale_1000 = 1000

    cur_scale_factor_10 = 10000
    cur_scale_factor_100 = 1000
    cur_scale_factor_1000 = 100
    cur_scale_factor_max = 10

    if rng_cur >= 0:
        factor = cur_scale_factor_max
        if rng_cur < cur_scale_10:
            factor = cur_scale_factor_10
        elif (rng_cur >= cur_scale_10) & (rng_cur < cur_scale_100):
            factor = cur_scale_factor_100
        elif (rng_cur >= cur_scale_100) & (rng_cur < cur_scale_1000):
            factor = cur_scale_factor_1000
        else:
            factor = cur_scale_factor_max

    # Or if rng_cur is negative
    else:
        d_rng_cur = 0  # mA
        rng_cur = abs(rng_cur)
        if (rng_cur > 0) & (rng_cur < 999):  # Negative current between 0 and 999 is mA
            d_rng_cur = rng_cur
        elif (rng_cur >= 1000) & (rng_cur < 999999):  # Negative current between 1000 and 999999 is mA ##Is this wrong?
            d_rng_cur = rng_cur
        elif (rng_cur >= 1000000) & (rng_cur <= 999999999):  # Negative current between 1000000-999999999 is uA
            d_rng_cur = rng_cur / 1000000000.0

        factor = cur_scale_factor_max
        if (d_rng_cur < 0.01):  # 10uA
            factor = 100000000
        elif (d_rng_cur >= 0.01) & (d_rng_cur < 0.1):  # 100uA
            factor = 10000000
        elif (d_rng_cur >= 0.1) & (d_rng_cur < 1.0):  # 1000uA
            factor = 1000000
        elif (d_rng_cur >= 1.0) & (d_rng_cur < 10.0):  # 10mA
            factor = 100000
        elif (d_rng_cur >= 10.0) & (d_rng_cur < 100.0):  # 100mA
            factor = 10000
        elif (d_rng_cur >= 100.0) & (d_rng_cur < 1000.0):  # 1000mA
            factor = 1000
        elif (d_rng_cur >= 1000.0):  #
            factor = 100.0
        else:
            factor = 10.0
            # Factor returns transformation to milli_ampere
    return factor


# Return a dict containing the relevant data. all nice and pretty like.
def new_byte_stream(byte_stream, small=False):
    curr_dict = {}

    # Seems to be record ID * 256
    column_1 = int.from_bytes(byte_stream[0:1], byteorder='little', signed=True)  # ?? indicator of subheader?
    curr_dict['column_1'] = column_1

    # Record ID
    record_ID = int.from_bytes(byte_stream[1:5], byteorder='little', signed=True)  # 1 record id
    curr_dict['record_ID'] = record_ID

    # Not sure
    column_2 = int.from_bytes(byte_stream[5:9], byteorder='little', signed=True)  # 0 ?
    curr_dict['column_2'] = column_2

    # Step number?
    step_jump = int.from_bytes(byte_stream[9:11], byteorder='little', signed=True)  # 1 step number
    curr_dict['step_jump'] = step_jump

    # Step name
    step_name = int.from_bytes(byte_stream[11:12], byteorder='little', signed=True)  # 2 CC_DChg
    if small==False:
        curr_dict['step_name'] = get_step_name(step_name)
    else:
        curr_dict['step_name'] = step_name

    # Multiplier for large currents
    # Gives values of 5 for small currents, 50 for large currents
    # Current is 1/10 too small for large currents if this is not included


    #current_multiplier = 1
    #if int.from_bytes(byte_stream[77:78], byteorder='little', signed=True) == -1:
    #    current_multiplier = 0.1

    curr_multiplier = multiplier(int.from_bytes(byte_stream[77:81], byteorder='little', signed=True))

    # Not sure - jumpto?
    step_jump_two = int.from_bytes(byte_stream[12:13], byteorder='little', signed=True)  # 2 step number again?
    curr_dict['step_jump_two'] = step_jump_two

    # Elapsed time in seconds
    tot_seconds = int.from_bytes(byte_stream[13:21], byteorder='little', signed=True)  # 0 elapsed time in ms
    curr_dict['time_in_step'] = tot_seconds/1000

    # Voltage V
    vol = int.from_bytes(byte_stream[21:25], byteorder='little', signed=True)  # 22126   voltage in 100 uV
    curr_dict['voltage_V'] = vol / 10000

    # Current mA
    cur = int.from_bytes(byte_stream[25:28], byteorder='little', signed=True)  # 7  current
    # 26:29 for BTS8.0 with no current change
    curr_dict['current_mA'] = cur/curr_multiplier

    # Capacity Charge mAh
    chg_cap = int.from_bytes(byte_stream[37:45], byteorder='little', signed=True)# ?
    curr_dict['chg_capacity_mAh'] = chg_cap / (3600*curr_multiplier)

    # Capacity Discharge mAh
    dchg_cap = int.from_bytes(byte_stream[45:53], byteorder='little', signed=True)  # ?
    curr_dict['dchg_capacity_mAh'] = dchg_cap / (3600*curr_multiplier)

    curr_dict['capacity_mAh'] = abs(chg_cap + dchg_cap) / (3600*curr_multiplier)

    # Energy Charge mWh
    chg_eng = int.from_bytes(byte_stream[53:59], byteorder='little', signed=True)  # ?
    curr_dict['chg_energy_mWh'] = chg_eng / (3600*curr_multiplier)

    # Energy Discharge mWh
    dchg_eng = int.from_bytes(byte_stream[61:67], byteorder='little', signed=True)  # ?
    curr_dict['dchg_energy_mWh'] = dchg_eng / (3600*curr_multiplier)

    curr_dict['energy_mWh'] = (chg_eng + dchg_eng) / (3600*curr_multiplier)

    # 29-45 and 65-69 Other stuff? eg capacity and energy of CCCV and CV curves
    # Print it anyway
    column_3 = int.from_bytes(byte_stream[41:45], byteorder='little', signed=True)
    curr_dict['column_3'] = column_3

    column_4 = int.from_bytes(byte_stream[65:69], byteorder='little', signed=True)
    curr_dict['column_4'] = column_4

    # Date and time
    year = int.from_bytes(byte_stream[69:71], byteorder='little', signed=True)  # 8 year
    month = int.from_bytes(byte_stream[71:72], byteorder='little', signed=True)  # 8 month
    day = int.from_bytes(byte_stream[72:73], byteorder='little', signed=True)  # 9 day
    hour = int.from_bytes(byte_stream[73:74], byteorder='little', signed=True)  # 10 hour
    minute = int.from_bytes(byte_stream[74:75], byteorder='little', signed=True)  # 10 minute
    second = int.from_bytes(byte_stream[75:76], byteorder='little', signed=True)  # 11 second

    curr_dict['timestamp'] = f'{year}-{month}-{day} {hour}:{minute}:{second}'

    # 78-86 Not sure. Extra space?
    column_5 = int.from_bytes(byte_stream[77:80], byteorder='little', signed=True)  # 11
    curr_dict['column_5'] = column_5

    # print(curr_dict)
    # Raw binary available for bugfixing purposes only
    raw_bin = str(binascii.hexlify(bytearray(byte_stream)))
    curr_dict['RAW_BIN'] = raw_bin
    # time.sleep(.1)

    return curr_dict


def process_header(header_bytes):
    magic_number = header_bytes[0:6].decode('utf-8')
    if magic_number != 'NEWARE':
        raise RuntimeError("Magic number wrong. Not valid .nda file")
        # Possibly ASCI coding but whatever.  This works.
    year = header_bytes[6:10].decode('utf-8')
    month = header_bytes[10:12].decode('utf-8')
    day = header_bytes[12:14].decode('utf-8')

    hour = header_bytes[2137:2139].decode('utf-8')
    minute = header_bytes[2140:2142].decode('utf-8')
    second = header_bytes[2143:2145].decode('utf-8')

    version = header_bytes[112:142].decode('utf-16').strip()
    name = header_bytes[2166:2178].decode('utf-8').strip('\00')
    # Comments is odd. Creation date?
    comments = header_bytes[2181:2300].decode('utf-8').strip('\00')

    # Not sure if this is really channel stuff...
    machine = int.from_bytes(header_bytes[2091:2092], byteorder='little')
    channel = int.from_bytes(header_bytes[2092:2093], byteorder='little')

    # ret = {}
    ret = {
        'year': year, 'month': month, 'day': day, 'hour': hour,
        'minute': minute, 'second': second, 'version': version,
        'comments': comments, 'machine': machine, 'channel': channel,
        'name': name
    }
    # TODO: find mass or something
    return ret


def process_subheader(subheader_bytes):
    pass


def dict_to_csv_line(indict, lorder, csv_line=None):
    if csv_line is None:
        csv_line = []
    for a in lorder:
        if a == 'time_in_step':
            seconds = indict.get(a) / 1000
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            #            csv_line.append('record_ID')
            csv_line.append("%d:%02d:%02d" % (h, m, s))
        #            csv_line.append(f'{h}:{m}:{s}')
        # FIXME: do a proper handling of these lines, I think they are special
        # in some way, so will need special handling.  until then, ignore them
        #        elif a == "step_ID" and indict.get(a) == 0:
        #            return None
        else:
            csv_line.append(str(indict.get(a)))
    return csv_line


# Output for newest BTSDA version

def nda_version_8_0(inpath, testcols=False, split=False, csv_line_order=None, small=False, list_data=None):

    if csv_line_order is None:
        csv_line_order = []
    if list_data is None:
        list_data = []

    line_size = 86
    main_data = False

    if small==True:
        all_cols = ['column_1',
                    'record_ID',
                    'step_ID',
                    'column_2',
                    'step_jump',
                    'step_name',
                    'step_jump_two',
                    'time_in_step',
                    'voltage_V',
                    'current_mA',
                    'chg_capacity_mAh',
                    'dchg_capacity_mAh',
                    'capacity_mAh',
                    'chg_energy_mWh',
                    'dchg_energy_mWh',
                    'energy_mWh',
                    'column_3',
                    'column_4',
                    'column_5']

        if testcols == False and split==False:
            csv_line_order = ['record_ID',
                              'step_ID',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh']
        elif testcols == False and split==True:
            csv_line_order = ['record_ID',
                              'step_ID',
                              'step_jump',
                              'step_name',
                              'step_jump_two',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'chg_capacity_mAh',
                              'dchg_capacity_mAh',
                              'chg_energy_mWh',
                              'dchg_energy_mWh']
        elif testcols == True and split==False:
            csv_line_order = ['column_1',
                              'record_ID',
                              'step_ID',
                              'column_2',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'column_3',
                              'column_4',
                              'column_5']
        elif testcols == True and split == True:
            csv_line_order = all_cols

    else:
        all_cols = ['column_1',
                    'record_ID',
                    'step_ID',
                    'column_2',
                    'step_jump',
                    'step_name',
                    'step_jump_two',
                    'time_in_step',
                    'voltage_V',
                    'current_mA',
                    'chg_capacity_mAh',
                    'dchg_capacity_mAh',
                    'capacity_mAh',
                    'chg_energy_mWh',
                    'dchg_energy_mWh',
                    'energy_mWh',
                    'current_multiplier',
                    'column_3',
                    'column_4',
                    'timestamp',
                    'column_5']

        if testcols == False and split == False:
            csv_line_order = ['record_ID',
                              'step_ID',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'timestamp']
        elif testcols == False and split == True:
            csv_line_order = ['record_ID',
                              'step_ID',
                              'step_jump',
                              'step_name',
                              'step_jump_two',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'chg_capacity_mAh',
                              'dchg_capacity_mAh',
                              'chg_energy_mWh',
                              'dchg_energy_mWh',
                              'timestamp']
        elif testcols == True and split == False:
            csv_line_order = ['column_1',
                              'record_ID',
                              'step_ID',
                              'column_2',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'current_multiplier',
                              'column_3',
                              'column_4',
                              'timestamp',
                              'column_5']
        elif testcols == True and split == True:
            csv_line_order = all_cols

    with open(inpath, "rb") as f:
        header_finder = f.read()
        header_size = header_finder.find(b'U\x00\x01')

    with open(inpath, "rb") as f:
        header_bytes = f.read(header_size)
        byte = f.read(1)
        pos = 0
        subheader = b''
        while byte:
            if not main_data:
                local = int.from_bytes(byte, byteorder='little', signed=True)
                if local == 85:
                    main_data = True
                    continue
                else:
                    subheader += byte
                    byte = f.read(1)
                    continue
            line = f.read(line_size)
            if line == b'':
                break

            dict_line = new_byte_stream(line, small=small)
            if bool(dict_line)==True:
                list_data.append(dict_line)

    #print(sys.getsizeof(list_data))
    # This if statement keeps the file small during construction (if small=True).
    if small==True:
        outdata = pd.DataFrame(list_data, columns=all_cols, dtype='float32')
    else:
        outdata = pd.DataFrame(list_data, columns=all_cols)
    #print(sys.getsizeof(outdata))

    outdata = outdata.sort_values(by=['record_ID'])
    outdata = outdata.drop_duplicates(subset=['record_ID'], keep='first')

    corr = [1]
    a = 1
    count_a_vals = outdata['step_jump'].values
    count_b_vals = outdata['step_jump_two'].values

    diffs_a = count_a_vals[:-1] - count_a_vals[1:]
    diffs_b = count_b_vals[:-1] - count_b_vals[1:]

    for g, h in zip(diffs_a, diffs_b):
        if (g != 0) or (h != 0):
            a += 1

        corr.append(a)

    outdata['step_ID'] = corr
    if small==True:
        outdata = outdata.astype('float32')
    outdata = outdata[csv_line_order]
    return outdata

if __name__ == "__main__":
    print(process_nda(sys.argv[1], sys.argv[2]))


def process_nda(inpath, outpath=':auto:'):
    if outpath == ':auto:':
        outpath = inpath + '.csv'

    with open(inpath, 'rb') as f:
        data = f.read()

    if data[112:115] == b'BTS':
        old_nda(inpath, outpath=':auto:')
    else:
        new_nda(inpath, outpath=':auto:')
