
import fortranformat as ff



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


# def line_write():
#     fmt = '1X'
#     for n, field in enumerate(fields):
#         if n != 0:
#             fmt += ',1X'
#         if isna(field):
#             fields[n] = '-99'
#             fmt += ',A5'
#         else:
#             fmt += ',' + LAYER_ROW_FMT[n]
#     return ff.FortranRecordWriter(fmt).write(fields)