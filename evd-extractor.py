import struct
import pandas as pd
import json

file_path = "lt_cc_a_root.evd"
show_offset = True
show_hash = True

def unpack():
    global chunk_count
    chunk_count = chunk_count + 1
    global data_count
    local_data_set = {}
    numOfData = int.from_bytes(file.read(4), byteorder='little')
    offsetToDataChunk = int.from_bytes(file.read(4), byteorder='little')
    print("Chunk #%i: %s\tDataCount: %i" % (chunk_count, hex(file.tell() - 8), numOfData))
    # numOfDataIndex = int.from_bytes(file.read(4), byteorder='little')
    # offsetToDataIndexChunk = int.from_bytes(file.read(4), byteorder='little')
    file.seek(offsetToDataChunk - 4, 1)
    noName_counter = 0
    local_data = {}
    for i in range(0, numOfData):
        data_count = data_count + 1
        currentCursor = file.tell()
        offsetDataChunk = int.from_bytes(file.read(4), byteorder='little')
        variable_name = None
        if offsetDataChunk != 0:
            file.seek(currentCursor + offsetDataChunk, 0)
            variable_name = file.read(200).split(b'\x00')[0].decode('UTF8') #Use UTF8 because some strings are in Japanese
            file.seek(currentCursor + 4, 0)
        name_hash = file.read(4).hex()
        type = file.read(4)
        data_location = file.tell()
        if type == b'\x35\x85\xba\xb7':  # List
            file.seek(int.from_bytes(file.read(4), byteorder='little') - 0x04, 1)
            data_location = file.tell()
            value = unpack()
            file.seek(currentCursor + 0x10, 0)
        elif type == b'\x38\x65\xc1\x17':  # String
            file.seek(int.from_bytes(file.read(4), byteorder='little') - 0x04, 1)
            value = file.read(200).split(b'\x00')[0].decode('UTF8')
            file.seek(currentCursor + 0x10, 0)
        elif type == b'\x85\x5d\xc4\xa6':  # Float
            value = struct.unpack('f', file.read(4))[0]
        elif type == b'\x3D\x95\x94\xC8':  # Boolean
            value = int.from_bytes(file.read(4), byteorder='little') > 0
        elif type == b'\x00\x00\x00\x00':  # Boolean
            if int.from_bytes(file.read(4), byteorder='little') == 0:
                value = None
            else:
                print("Non null value in null type")
                print()
        else:
            value = file.read(4).hex()
            print("Warring!!! Unknow type!!! %s at %s with value %s" % (hex(int.from_bytes(type, byteorder='big')), hex(file.tell()-8), value))
            print()
        if variable_name == None:
            variable_name = hex(data_location)
        else:
            if show_hash:
                variable_name = variable_name = "%s %s" % (variable_name, name_hash)
            if show_offset:
                variable_name = variable_name = "%s %s" % (variable_name, hex(data_location))
        local_data[variable_name] = value
        print(value)
    return local_data


file = open(file_path, mode='rb')
data = file.read()

data_set = {}
chunk_count = 0
data_count = 0
if len(data) > 0x40 and data[0:4] == b'FBKK':
    file.seek(0x30, 0)
    data_set = unpack()
    print()
    print("Complete with %i chunk(s) and %i data" % (chunk_count, data_count))
    with open(r"%s.txt" % (file_path.split('.')[0]), 'w', encoding='utf-8') as json_file:
        json.dump(data_set, json_file, indent=4, sort_keys=True, ensure_ascii=False)
else:
    print("File Incorrect")