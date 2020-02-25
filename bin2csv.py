#!/bin/python3.4
import sys, getopt
import binascii
import time
import math
import datetime
import csv

def get_step_name(s):
    if s == 1:
        return "CC_Chg"
    
    elif s == 2:
        return "CC_Dchg"
    
    # TODO: 3
    
    elif s == 4:
        return "Rest"
    # TODO: 5, 6

    elif s == 7:
        return "CCCV_Chg"
    # TODO: The rest
    else:
        return str(s)


# Return a dict containing the relevant data.  all nice and pretty like.
def old_byte_stream(byte_stream):
    curr_dict = {}
    
    # Line ID
    line_idb = int.from_bytes(byte_stream[0:4], byteorder='little')
    curr_dict['record_ID'] = line_idb
    # End line ID

    # Jumpto
    col2 = int.from_bytes(byte_stream[4:8], byteorder='little')
    curr_dict['jumpto'] = col2
    # end jumpto

    # Step ID
    sid = int.from_bytes(byte_stream[8:9], byteorder='little')
    # If step id is zero, there is funny behavior.
    curr_dict['step_ID'] = sid
    # End Step ID

    # Step name? Might be with step ID too.  In any case, probably an
    # identifier for charge, rest, discharge, etc.
    # 4=REST. 1=CC_Chg. 7=CCCV_Chg. 2=CC_DChg.
    sjob = int.from_bytes(byte_stream[9:10], byteorder='little')
    sjob_name = get_step_name(sjob)
    curr_dict['step_name'] = sjob_name
    # End step name

    # Time in step
    tis = int.from_bytes(byte_stream[10:14], byteorder='little')
    curr_dict['time_in_step'] = tis
    #print(tic)
    # end time in step

    # Voltage
    volts = int.from_bytes(byte_stream[14:18], byteorder='little')
    if volts > 0x7FFFFFFFFF:
        volts -= 0x100000000000000
    curr_dict['voltage'] = volts/10000
    # End voltage
    
    # Current
    current = int.from_bytes(byte_stream[18:22], byteorder='little')
    if current > 0x7FFFFFFF:
            current -= 0x100000000
    curr_dict['current'] = current / 10000
    # End Current
    
    # blank? This section seems to be blank, but it might not be?
    # By process of elimination, it might be tempurature.
    blank = int.from_bytes(byte_stream[22:30], byteorder='little')
    curr_dict['blank'] = blank
    # end blank?
    
    # Charge and Energy
    comp1 = int.from_bytes(byte_stream[30:38], byteorder='little')
    if comp1 > 0x7FFFFFFF:
        comp1 -= 0x100000000

    comp2 = int.from_bytes(byte_stream[38:46], byteorder='little')
    if comp2 > 0x7FFFFFFF:
        comp2 -= 0x100000000

    comp1 = comp1 / 3600000
    comp2 = comp2 / 3600000

    curr_dict['charge_mAh'] = comp1
    curr_dict['energy_mWh'] = comp2
    # End charge and energy

    # Time and date
#    timestamp = int.from_bytes(byte_stream[46:54], byteorder='little')
    #timestamp = int.from_bytes(byte_stream[3280:3289], byteorder='little')
#    newt = datetime.datetime.fromtimestamp(timestamp)
#    curr_dict['timestamp'] = newt.strftime('%m-%d-%Y %H:%M:%S')
    # end time and date
    
    # last 5?  silly number.  The last one might be an indicator, and the other 
    # 4 might be a number.  Possibly a checksum
    last = int.from_bytes(byte_stream[54:59], byteorder='little')
    curr_dict['last'] = last
    # end

    #stuff = []
    #for a in byte_stream:
    #    stuff.append(a)
    
    #print(curr_dict)
    # Raw binary available for bugfixing purposes only
    raw_bin = str(binascii.hexlify(bytearray(byte_stream)))
    curr_dict['RAW_BIN'] = raw_bin
    #time.sleep(.1)
    
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
    
    version = header_bytes[112:142].decode('utf-8').strip()
    name = header_bytes[2166:2178].decode('utf-8').strip('\00')
    # Comments is odd. Creation date?
    comments = header_bytes[2181:2300].decode('utf-8').strip('\00')
    
    # Not sure if this is really channel stuff...
    machine = int.from_bytes(header_bytes[2091:2092], byteorder='little')
    channel = int.from_bytes(header_bytes[2092:2093], byteorder='little')
    
    #ret = {}
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


def dict_to_csv_line(indict, lorder):
    csv_line = []
    for a in lorder:
        if a == 'time_in_step':
            seconds = indict.get(a)
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            csv_line.append("%d:%02d:%02d" % (h, m, s))
        # FIXME: do a proper handling of these lines, I think they are special 
        # in some way, so will need special handling.  until then, ignore them
        elif a == "step_ID" and indict.get(a) == 0:
            return None

        else:
            csv_line.append(str(indict.get(a)))
    return csv_line


def old_nda(inpath, outpath=':auto:', csv_line_order=['record_ID', 'jumpto', 
            'step_ID', 'step_name','time_in_step', 'voltage', 'current', 'blank', 
            'charge_mAh', 'energy_mWh']):
    header_size = 2304

    byte_line = []

    line_size = 59

    line_number = 0
    main_data = False
    
    if outpath == ':auto:':
        outpath = inpath + '.csv'

    if outpath != ':mem:':
        outfile = open(outpath, 'w')

    else: 
        import io
        outfile = io.StringIO()
    csv_out = csv.writer(outfile, delimiter=',', quotechar="\"")
    csv_out.writerow(csv_line_order)
    
    header_data = {}
    with open(inpath, "rb") as f:
        header_bytes = f.read(header_size) 
        # TODO: header decoding, including finding a mass
        header_data = process_header(header_bytes)

        byte = f.read(1)
        pos = 0
        subheader = b''
        while byte:
            if not main_data:
                local = int.from_bytes(byte, byteorder='little')
                if local == 255:
                    main_data = True
                    # TODO: Secondary header decoding
                    #header_data['subheader'] = process_subheader(subheader)
                    continue
                else:
                    subheader += byte
                    byte = f.read(1)
                    continue
            line = f.read(line_size)
            if line == b'':
                break
               
            dict_line = old_byte_stream(line)
            csv_line = dict_to_csv_line(dict_line, csv_line_order)
            #print(csv_line)
            if csv_line:
                csv_out.writerow(csv_line)
    
    if outpath == ':mem:':
        return outfile, header_data, csv_line
    
    outfile.close()

    return outpath, header_data, csv_line
    #print(subheader)


if __name__ == "__main__":
        print(process_nda(sys.argv[1], sys.argv[2]))
