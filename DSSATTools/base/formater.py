
import fortranformat as ff
from pandas import isna


# Funciton to read a layer (row)
def soil_line_read(line, format_list):
    fmt = '1X'
    for n, field in enumerate(line.split()):
        if n != 0:
            fmt += ',1X'
        if field.replace('.', '') == '-99':
            fmt += ',A5'
        else:
            fmt += ',' + format_list[n]
    return ff.FortranRecordReader(fmt).read(line)


def soil_line_write(fields, line_fmt):
    fmt = '1X'
    for n, field in enumerate(fields):
        if n != 0:
            fmt += ',1X'
        if isna(field):
            fields[n] = '-99'
            fmt += ',A5'
        else:
            fmt += ',' + line_fmt[n]
    return ff.FortranRecordWriter(fmt).write(fields)

def soil_location_write(fields):
    fmt = '1X,A12,A12,1X,'
    for field in fields[2:4]:
        if not isinstance(field, float):
            fmt += 'A8,1X,'
        else:
            fmt += 'F8.3,1X,'
    fmt += 'A36'
    return ff.FortranRecordWriter(fmt).write(fields)

def weather_station(fields):
    fmt = '2X,A4,2(1X,F8.3),1X,I5'
    for n, field in enumerate(fields[4:], 4):
        fmt += ',1X'
        if isna(field):
            fields[n] = '-99'
            fmt += ',A5'
        else:
            fmt += ',F5.1'
    return ff.FortranRecordWriter(fmt).write(fields) + '\n'

def weather_data_header(fields):
    fmt = f'{len(fields)}(1X,A5)'
    return '@DATE' + ff.FortranRecordWriter(fmt).write(fields) + '\n'

def weather_data(fields):
    fmt = f'A5,{len(fields)}(1X,F5.1)'
    return ff.FortranRecordWriter(fmt).write(fields) + '\n'


