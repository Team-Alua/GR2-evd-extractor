import struct
import pandas as pd
import os
import json

folder = 'F:\GR2\\GravityRush2\\arc\\'
output_folder = 'F:\GR2\evd_extracted\\'

files = []


def unpack():
    global chunk_count
    chunk_count = chunk_count + 1
    global data_count
    local_data_set = {}
    numOfData = int.from_bytes(file.read(4), byteorder='little')
    offsetToDataChunk = int.from_bytes(file.read(4), byteorder='little')
    #print("Chunk #%i: %s\tDataCount: %i" % (chunk_count, hex(file.tell() - 8), numOfData))
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
            variable_name = file.read(200).split(b'\x00')[0].decode('UTF8')
            file.seek(currentCursor + 4, 0)
        name_hash = file.read(4).hex()
        data_location = file.tell()
        type = file.read(4)
        if type == b'\x35\x85\xba\xb7':
            # data.append('List')
            file.seek(int.from_bytes(file.read(4), byteorder='little') - 0x04, 1)
            #print(hex(file.tell()))
            data_location = file.tell()
            value = unpack()
            file.seek(currentCursor + 0x10, 0)
        elif type == b'\x38\x65\xc1\x17':
            # data.append('String')
            file.seek(int.from_bytes(file.read(4), byteorder='little') - 0x04, 1)
            value = file.read(200).split(b'\x00')[0].decode('UTF8')
            file.seek(currentCursor + 0x10, 0)
        elif type == b'\x85\x5d\xc4\xa6':
            # data.append('Float')
            value = struct.unpack('f', file.read(4))[0]
        else:
            # data.append('Error %s' % type.hex())
            value = file.read(4).hex()
        if variable_name == None:
            variable_name = hex(data_location)
        else:
            if show_offset:
                variable_name = variable_name = "%s %s" % (variable_name, hex(data_location))
        local_data[variable_name] = value
        #print(value)
    print(".", end='')
    return local_data


for r, d, f in os.walk(folder):
    for file in f:
        print("Scaning directory: %s" % file)
        if '.evd' in file:
            files.append(os.path.join(r, file))

for file_path in files:
    file = open(file_path, mode='rb')
    data = file.read()
    data_set = {}
    chunk_count = 0
    data_count = 0
    show_offset = True

    print("Read file: %s" % file_path)
    if len(data) > 0x40  and data[0:4] == b'FBKK':
        file.seek(0x30, 0)
        data_set = unpack()
        print()
        print("Complete with %i chunk(s) and %i data" % (chunk_count, data_count))
        output_filepath = r"%s%s.txt" % (output_folder, file_path.split(folder)[1].split('.')[0])
        print("Save json to %s" % output_filepath)
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        with open(output_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(data_set, json_file, indent=4, sort_keys=True, ensure_ascii=False)
    else:
        print("File Incorrect")
        print(data[0:4])
        print(data[0:4] == b'FBKK')










