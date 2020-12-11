#!/bin/python3.4

import sys, getopt
import binascii
import time
import math
import datetime
import numpy as np
import pandas as pd


def get_step_name(s):
    if s == 1:
        return "CC_Chg"

    elif s == 2:
        return "CC_Dchg"

    # TODO: 3s

    elif s == 4:
        return "Rest"
    # TODO: 5

    elif s == 6:
        return "End"

    elif s == 7:
        return "CCCV_Chg"

    elif s == 8:
        return "CP_Dchg"

    elif s == 9:
        return "CP_Chg"

    elif s == 10:
        return "CR_Dchg"
    # TODO: The rest

    elif s == 20:
        return "CCCV_Dchg"
    else:
        return str(s)


# Return a dict containing the relevant data.  all nice and pretty like.
def new_byte_stream(byte_stream, small=False):
    curr_dict = {}

    # Seems to be record ID * 256
    aux_ch = int.from_bytes(byte_stream[0:1], byteorder='little', signed=True)  # Notifies AUX channel data maybe boolean not int?
    curr_dict['AUX_channel'] = aux_ch

    # Record ID
    record_ID = int.from_bytes(byte_stream[1:5], byteorder='little', signed=True)  # 1 record id
    curr_dict['record_ID'] = record_ID

    # Cycle ID
    cycle_ID = int.from_bytes(byte_stream[5:9], byteorder='little', signed=True)  # cycle ID offset by 4 (?!?) might be missing a bit
    curr_dict['cycle_ID'] = cycle_ID

    # Step number?
    step_jump = int.from_bytes(byte_stream[9:11], byteorder='little', signed=True)  # 1 step number
    curr_dict['step_jump'] = step_jump

    # Step name
    step_name = int.from_bytes(byte_stream[11:12], byteorder='little', signed=True)  # 2 CC_DChg
    if small==False:
        curr_dict['step_name'] = get_step_name(step_name)
    else:
        curr_dict['step_name'] = step_name



    # Not sure - jumpto?
    step_jump_two = int.from_bytes(byte_stream[12:13], byteorder='little', signed=True)  # 2 step number again?
    curr_dict['step_jump_two'] = step_jump_two

    # Elapsed time in seconds
    tot_seconds = int.from_bytes(byte_stream[13:21], byteorder='little', signed=True)  # 0 elapsed time
    curr_dict['time_in_step'] = tot_seconds/1000

    # Voltage V
    vol = int.from_bytes(byte_stream[21:25], byteorder='little', signed=True)  # 22126   voltage
    curr_dict['voltage_V'] = vol / 10000

    #######
    #
    # Noticed that on AUX channel connected the voltage from AUX is placed in voltage if AUC_channel is true (or 1)
    # If the AUX_voltage is not connected the voltage will be ~0
    # One should connect both voltage and temperature from the AUX channel linked to the cycler channel 
    # END bytes are 55 when cycler data and 65 when aux data
    # Added loop to exclude data.
    # 
    ######

    # Current mA
    cur = int.from_bytes(byte_stream[25:29], byteorder='little', signed=True)  # 7  current
    curr_dict['current_mA'] = cur / 10000

    #aux channel temp if connected
    aux_temp = int.from_bytes(byte_stream[33:35], byteorder='little', signed=True) # 12 #Aux temperature
    curr_dict['aux_temp'] = aux_temp /10

    # Capacity Charge mAh
    chg_cap = int.from_bytes(byte_stream[37:45], byteorder='little', signed=True)  # ?
    curr_dict['chg_capacity_mAh'] = chg_cap / 36000000

    # Capacity Discharge mAh
    dchg_cap = int.from_bytes(byte_stream[45:53], byteorder='little', signed=True)  # ?
    curr_dict['dchg_capacity_mAh'] = dchg_cap / 36000000

    curr_dict['capacity_mAh'] = (chg_cap + dchg_cap) / 36000000

    # Energy Charge mWh
    chg_eng = int.from_bytes(byte_stream[53:59], byteorder='little', signed=True)  # ?
    curr_dict['chg_energy_mWh'] = chg_eng / 36000000

    # Energy Discharge mWh
    dchg_eng = int.from_bytes(byte_stream[61:67], byteorder='little', signed=True)  # ?
    curr_dict['dchg_energy_mWh'] = dchg_eng / 36000000

    curr_dict['energy_mWh'] = (chg_eng + dchg_eng) / 36000000

    # Date and time
    year = int.from_bytes(byte_stream[69:71], byteorder='little', signed=True)  # 8 year
    month = int.from_bytes(byte_stream[71:72], byteorder='little', signed=True)  # 8 month
    day = int.from_bytes(byte_stream[72:73], byteorder='little', signed=True)  # 9 day
    hour = int.from_bytes(byte_stream[73:74], byteorder='little', signed=True)  # 10 hour
    minute = int.from_bytes(byte_stream[74:75], byteorder='little', signed=True)  # 10 minute
    second = int.from_bytes(byte_stream[75:76], byteorder='little', signed=True)  # 11 second

    curr_dict['timestamp'] = f'{year}-{month}-{day} {hour}:{minute}:{second}'

    # 29-45 and 65-69 Other stuff? eg capacity and energy of CCCV and CV curves
    # Print it anyway
    column_3 = int.from_bytes(byte_stream[41:45], byteorder='little', signed=True)
    curr_dict['column_3'] = column_3

    column_4 = int.from_bytes(byte_stream[65:69], byteorder='little', signed=True)
    curr_dict['column_4'] = column_4


    # 76-86 Not sure. Extra space?

    ##
    ## Column_5 contains data as long as AUX_channel is false.
    ## Looks to be high number during charge / discharge and low during rest
    ## 
    ##

    column_5 = int.from_bytes(byte_stream[76:78], byteorder='little', signed=True)  # 11  
    curr_dict['column_5'] = column_5

    column_7 = int.from_bytes(byte_stream[78:80], byteorder='little', signed=True)  # 11 
    curr_dict['column_7'] = column_7

    column_8 = int.from_bytes(byte_stream[79:80], byteorder='little', signed=True)  # 11
    curr_dict['column_8'] = column_8

    column_9 = int.from_bytes(byte_stream[80:85], byteorder='little', signed=True)  # 11
    curr_dict['column_9'] = column_9

   
    #print(curr_dict)
    # Raw binary available for bugfixing purposes only
    raw_bin = str(binascii.hexlify(bytearray(byte_stream)))
    curr_dict['RAW_BIN'] = raw_bin
    # time.sleep(.1)
       
    return curr_dict


def process_header(header_bytes):
    # print("process_header") 
    magic_number = header_bytes[0:6].decode('utf-8')
    if magic_number != 'NEWARE':
        raise RuntimeError("Magic number wrong. Not valid .nda file")
        # Possibly ASCI coding but whatever.  This works.

    year = header_bytes[6:10].decode('utf-8')
    month = header_bytes[10:12].decode('utf-8')
    day = header_bytes[12:14].decode('utf-8')

    hour = header_bytes[2138:2139].decode('utf-8')
    minute = header_bytes[2140:2142].decode('utf-8')
    second = header_bytes[2143:2145].decode('utf-8')

    version = header_bytes[112:142].decode('utf-16').strip('\00')
    name = header_bytes[2166:2178].decode('utf-8').strip('\00')
    #PN added in step file 
    PN = header_bytes[2227:2271].decode('utf-8').strip('\00')
     # Comments is odd. 
    comments = header_bytes[2316:2436].decode('utf-8').strip('\00')
    #step file name
    step_file_name = header_bytes[2533:2575].decode('utf-8').strip('\00') #might be to many bits
    #BTS Server listing 1
   # bts_server_1 = header_bytes[2593:2628].decode('utf-8').strip('\00')
    #BTS Server listing 2
   # bts_server_2 = header_bytes[2643:2678].decode('utf-8').strip('\00')
    #BTS Server listing 3
  #  bts_server_3 = header_bytes[2693:2718].decode('utf-8').strip('\00')

    # Not sure if this is really channel stuff...
    machine = int.from_bytes(header_bytes[2091:2092], byteorder='little')
    channel = int.from_bytes(header_bytes[2092:2093], byteorder='little')

    # ret = {}
    ret = {
        'year': year, 'month': month, 'day': day, 'hour': hour,
        'minute': minute, 'second': second, 'version': version,
        'comments': comments, 'machine': machine, 'channel': channel,
        'name': name, 'PN': PN, 'step_file_name': step_file_name #, 'BTS_server_1': bts_server_1,
        #'BTS_server_2': bts_server_2, 'BTS_server_3': bts_server_3
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

def new_nda(inpath, testcols=True, split=True, csv_line_order=None, small=False, list_data=None, list_data_aux= None):

    if csv_line_order is None:
        csv_line_order = []
    if list_data is None:
        list_data = []
    if list_data_aux is None:
        list_data_aux = []

    line_size = 86
    main_data = False

    if small==True:
        all_cols = ['AUX_channel',
                    'record_ID',
                    'step_ID',
                    'cycle_ID',
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
                    'column_5',
                    'aux_temp']

        if testcols == False and split==False:
            csv_line_order = ['record_ID',
                              'step_ID',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'aux_temp']
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
                              'dchg_energy_mWh',
                              'aux_temp']
        elif testcols == True and split==False:
            csv_line_order = ['AUX_channel',
                              'record_ID',
                              'step_ID',
                              'cycle_ID',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'aux_temp',
                              'column_4',
                              'column_5']
        elif testcols == True and split == True:
            csv_line_order = all_cols

    else:
        all_cols = ['record_ID',
                    'step_ID',
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
                    'timestamp',
                    'AUX_channel',
                    'aux_temp',
                    'AUX_voltage_V',
                    'AUX_timestamp',
                    'cycle_ID',
                    'column_3',
                    'column_4',
                    'column_5',
                    'column_7',
                    'column_8',
                    'column_9']

        if testcols == False and split == False:
            csv_line_order = ['record_ID',
                              'step_ID',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'timestamp',
                                'aux_temp']
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
                              'timestamp',
                              'aux_temp']
        elif testcols == True and split == False:
            csv_line_order = ['column_1',
                              'record_ID',
                              'step_ID',
                              'cycle_ID',
                              'step_name',
                              'time_in_step',
                              'voltage_V',
                              'current_mA',
                              'capacity_mAh',
                              'energy_mWh',
                              'column_3',
                              'column_4',
                              'timestamp',
                              'aux_temp',
                              'column_5',
                              'AUX_channel']
        elif testcols == True and split == True:
            csv_line_order = all_cols

    with open(inpath, "rb") as f:
        header_finder = f.read()
        header_size = header_finder.find(b'U\x00\x01')

    with open(inpath, "rb") as f:
        header_bytes = f.read(header_size)
        #added these 4 lines to add PN as filename if COR is part of PN        
        header = process_header(header_bytes)
        PN_name = header['PN']
        if PN_name.__contains__("COR") == True:
            outpath = PN_name + ".csv"

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
                if dict_line['AUX_channel'] == 1:
                    list_data_aux.append(dict_line)     #Store Aux data in separate list
                else:
                    list_data.append(dict_line)

    #print(sys.getsizeof(list_data))
    #print(list_data_aux)
    # This if statement keeps the file small during construction (if small=True).
    if small==True:
        outdata_cycler = pd.DataFrame(list_data, columns=all_cols, dtype='float32')
        outdata_aux = pd.DataFrame(list_data_aux, columns=all_cols, dtype='float32') 
    else:
        outdata_cycler = pd.DataFrame(list_data, columns=all_cols)
        outdata_aux = pd.DataFrame(list_data_aux, columns=all_cols)
    #print(sys.getsizeof(outdata))
    if outdata_aux.empty:
        #outdata_cycler.drop(['aux_temp','AUX_timestamp', 'AUX_voltage_V' ], axis = 1, inplace = True)
        
        outdata = outdata_cycler
    else:
        columns = ['voltage_V', 'aux_temp', 'timestamp' ]               # selct columns to copy to outdata DF  , 'record_ID'
        outdata_aux = outdata_aux.loc[:,outdata_aux.columns.isin(columns)]      # keep only selected coulmns
        outdata_aux.rename(columns={'voltage_V': 'AUX_voltage_V'}, inplace=True)
        outdata_aux.rename(columns={'timestamp': 'AUX_timestamp'}, inplace=True)
        outdata_cycler.drop(['aux_temp','AUX_timestamp', 'AUX_voltage_V' ], axis = 1, inplace = True)
        outdata = pd.concat([outdata_aux, outdata_cycler], join = 'outer', axis = 1)
        print(outdata_aux)
        print(outdata_cycler) 
        print(outdata)

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
    #pd.DataFrame.to_csv(outdata, outpath) #Did not get any output file if this line were not present
    return outdata




def process_nda(inpath, outpath=':auto:'):
    if outpath == ':auto:':
        outpath = inpath + '.csv'

    with open(inpath, 'rb') as f:
        data = f.read()

    if data[112:115] == b'BTS':
        old_nda(inpath, outpath=':auto:')
    else:
        new_nda(inpath, outpath=':auto:')

if __name__ == "__main__":
   print(process_nda(sys.argv[1], sys.argv[2]))

