# TODO: Check parameter values and format directly when setting them. Use the defined formating just to check if the value can be formated. If it can't be formated then throw error. 
import fortranformat as ff
from pandas import isna, DataFrame
from collections import MutableMapping
import warnings 

NA_VALS = (None, '-99', -99, -999999)

CULTIVAR_HEADER_FMT = {
    'Maize':        'A5,1X,1X,A16,1X,A5,1X,A6,6(1X,A5)',
    'Millet':       'A5,1X,1X,A16,1X,A5,1X,A6,9(1X,A5)',
    'Sugarbeet':    'A5,1X,1X,A16,1X,A5,1X,A6,6(1X,A5)',
    'Rice':         'A5,1X,1X,A16,1X,A5,1X,A6,11(1X,A5)',
    'Sorghum':      'A5,1X,1X,A16,1X,A5,1X,A6,13(1X,A5)',
    'Sweetcorn':    'A5,1X,1X,A16,1X,A5,1X,A6,6(1X,A5)',
    'Alfalfa':      'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Bermudagrass': 'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Soybean':      'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Canola':       'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Sunflower':    'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Potato':       'A5,1X,1X,A16,1X,A5,1X,A6,5(1X,A5)',
    'Tomato':       'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Cabbage':      'A5,1X,1X,A16,1X,A5,1X,A6,18(1X,A5)',
    'Sugarcane':    'A5,1X,1X,A16,1X,A5,1X,A6,22(1X,A14)'
}
CULTIVAR_ROWS_FMT = {
    'Maize':        'A6,1X,A16,1X,A5,1X,A6,1X,F5.1,1X,F5.3,2(1X,F5.0),2(1X,F5.2)',
    'Millet':       'A6,1X,A16,1X,A5,1X,A6,1X,F5.1,1X,F5.2,2(1X,F5.1),5(1X,F5.2)',
    'Sugarbeet':    'A6,1X,A16,1X,A5,1X,A6,5(1X,F5.1),1X,F5.2',
    'Rice':         'A6,1X,A16,1X,A5,1X,A6,5(1X,F5.1),1X,F5.4,1X,F5.2,4(1X,F5.1)',
    'Sorghum':      'A6,1X,A16,1X,A5,1X,A6,2(1X,F5.1),1X,F5.2,5(1X,F5.1),1X,F5.2,4(1X,F5.1)',
    'Sweetcorn':    'A6,1X,A16,1X,A5,1X,A6,1X,F5.1,1X,F5.3,2(1X,F5.1),2(1X,F5.2)',
    'Alfalfa':      'A6,1X,A16,1X,A5,1X,A6,1X,F5.2,1X,F5.3,3(1X,F5.1),2(1X,F5.2),1X,F5.1,1X,F5.0,1X,F5.1,1X,F5.2,1X,F5.3,1X,F5.1,1X,F5.2,2(1X,F5.1),2(1X,F5.3)',
    'Bermudagrass': 'A6,1X,A16,1X,A5,1X,A6,1X,F5.2,1X,F5.3,3(1X,F5.1),3(1X,F5.2),1X,F5.0,1X,F5.1,2(1X,F5.2),1X,F5.1,1X,F5.2,2(1X,F5.1),2(1X,F5.3)',
    'Soybean':      'A6,1X,A16,1X,A5,1X,A6,1X,F5.2,1X,F5.3,3(1X,F5.1),2(1X,F5.2),1X,F5.3,1X,F5.0,1X,F5.1,2(1X,F5.2),1X,F5.1,1X,F5.2,2(1X,F5.1),2(1X,F5.3)',
    'Canola':       'A6,1X,A16,1X,A5,1X,A6,1X,F5.2,1X,F5.3,3(1X,F5.1),2(1X,F5.2),1X,F5.3,1X,F5.0,1X,F5.1,1X,F5.2,1X,F5.3,4(1X,F5.1),2(1X,F5.3)',
    'Sunflower':    'A6,1X,A16,1X,A5,1X,A6,1X,F5.2,1X,F5.3,3(1X,F5.1),3(1X,F5.2),1X,F5.0,1X,F5.1,2(1X,F5.2),4(1X,F5.1),2(1X,F5.3)',
    'Potato':       'A6,1X,A16,1X,A5,1X,A6,1X,F5.0,4(1X,F5.1)',
    'Tomato':       'A6,1X,A20,1X,A1,1X,A6,2(1X,F5.2),3(1X,F5.1),3(1X,F5.2),1X,F5.0,1X,F5.1,1X,F5.2,1X,F5.4,4(1X,F5.1),2(1X,F5.3)',
    'Cabbage':      'A6,1X,A16,1X,A5,1X,A6,1X,F5.2,1X,F5.3,3(1X,F5.1),2(1X,F5.2),1X,F5.3,1X,F5.0,1X,F5.1,1X,F5.3,1X,F5.2,1X,F5.1,1X,F5.2,2(1X,F5.1),2(1X,F5.3)',
    'Sugarcane':    'A6,1X,A16,1X,A5,1X,A6,22(1X,F14.4)'
}
ECOTYPE_HEADER_FMT = {
    'Maize':        'A5,1X,1X,A16,1X,11(1X,A5)',
    'Millet':       'A5,1X,1X,A16,1X,7(1X,A5)',
    'Sugarbeet':    'A5,1X,1X,A16,1X,11(1X,A5)',
    'Rice':         '',
    'Sorghum':      'A5,1X,1X,A16,1X,10(1X,A5)',
    'Sweetcorn':    'A5,1X,1X,A16,1X,11(1X,A5)',
    'Alfalfa':      'A5,1X,1X,A16,2(1X,A2)20(1X,A5)',
    'Bermudagrass': 'A5,1X,1X,A16,2(1X,A2)20(1X,A5)',
    'Soybean':      'A5,1X,1X,A16,2(1X,A2)16(1X,A5)',
    'Canola':       'A5,1X,1X,A16,2(1X,A2)16(1X,A5)',
    'Sunflower':    'A5,1X,1X,A17,2(1X,A2)16(1X,A5)',
    'Potato':       'A5,1X,1X,A17,2(1X,A5)',
    'Tomato':       'A5,1X,1X,A17,2(1X,A2)16(1X,A5)',
    'Cabbage':      'A5,1X,1X,A17,2(1X,A2)16(1X,A5)',
    'Sugarcane':    'A5,1X,1X,A17,1X,49(1X,A14)'
}
ECOTYPE_ROWS_FMT = {
    'Maize':        'A6,1X,A16,1X,11(1X,F5.1)',
    'Millet':       'A6,1X,A16,1X,6(1X,F5.1),1X,F5.2',
    'Sugarbeet':    'A6,1X,A16,1X,8(1X,F5.1),1X,F5.2,2(1X,F5.1)',
    'Rice':         '',
    'Sorghum':      'A6,1X,A16,1X,5(1X,F5.1),1X,F5.2,2(1X,F5.3),1X,F5.1,1X,F5.0',
    'Sweetcorn':    'A6,1X,A16,1X,8(1X,F5.1),1X,F5.2,2(1X,F5.1)',
    'Alfalfa':      'A6,1X,A16,2(1X,A2),1X,F5.2,3(1X,F5.1),1X,F5.0,1X,F5.1,1X,F5.2,1X,F5.1,2(1X,F5.0),1X,F5.2,2(1X,F5.1),1X,F5.3,1X,F5.1,5(1X,F5.3)',
    'Bermudagrass': 'A6,1X,A16,2(1X,A2),1X,F5.2,3(1X,F5.1),1X,F5.0,1X,F5.1,1X,F5.2,1X,F5.1,2(1X,F5.0),1X,F5.2,2(1X,F5.1),1X,F5.3,1X,F5.1,5(1X,F5.3)',
    'Soybean':      'A6,1X,A16,2(1X,A2),6(1X,F5.1),1X,F5.2,2(1X,F5.1),2(1X,F5.2),2(1X,F5.1),1X,F5.3,1X,F5.1,1X,F5.3',
    'Canola':       'A6,1X,A16,2(1X,A2),6(1X,F5.1),1X,F5.2,2(1X,F5.1),2(1X,F5.2),2(1X,F5.1),1X,F5.3,1X,F5.1,1X,F5.3',
    'Sunflower':    'A6,1X,A17,2(1X,A2),6(1X,F5.1),1X,F5.2,3(1X,F5.1),1X,F5.2,2(1X,F5.1),1X,F5.3,1X,F5.1,1X,F5.3',
    'Potato':       'A6,1X,A17,2(1X,F5.1)',
    'Tomato':       'A6,1X,A17,2(1X,A2),5(1X,F5.1),2(1X,F5.2),2(1X,F5.1),2(1X,F5.2),2(1X,F5.1),1X,F5.3,1X,F5.1,1X,F5.3',
    'Cabbage':      'A6,1X,A17,2(1X,A2),6(1X,F5.1),1X,F5.2,2(1X,F5.1),2(1X,F5.2),2(1X,F5.1),1X,F5.3,1X,F5.1,1X,F5.3',
    'Sugarcane':    'A6,1X,A17,1X,1X,F14.2,1X,F14.1,2(1X,F14.2),1X,F14.0,2(1X,F14.1),1X,F14.0,1X,F14.4,1X,F14.3,1X,F14.2,1X,F14.3,3(1X,F14.0),1X,F14.2,1X,F14.1,1X,F14.3,2(1X,F14.1),1X,F14.0,7(1X,F14.1),12(1X,F14.2),2(1X,F14.1),7(1X,F14.2)'
}
SECTIONS_HEADER_FMT = {
    'treatments': 'A2,3(1X,A1),1X,A25,13(1X,A2)',
    'cultivars': 'A2,1X,A2,1X,A6,1X,A25',
    'field': [
        'A2,1X,A8,1X,A8,6(1X,A5),1X,A4,1X,A5,1X,A8,1X,A9', 
        'A2,2(1X,A15),1X,A9,1X,A17,5(1X,A5)'
    ],
    'initial conditions': 'A2,12(1X,A5),1X,A6',
    'initial conditions_table': 'A2,4(1X,A5)',
    'planting details': 'A2,14(1X,A5),1X,A29',
    # 'planting details_table': 'A2,14(1X,A5),1X,A29',
    'irrigation': 'A2,7(1X,A5),1X,A6',
    'irrigation_table': 'A2,3(1X,A5)',
    'fertilizers': [],
    'fertilizers_table': 'A2,10(1X,A5),1X,A6',
    'harvest details': 'A2,7(1X,A5)',
    # 'harvest details_table': 'A2,7(1X,A5)',
    'simulation controls':[
        'A2,1X,A7,4X,5(1X,A5),1X,A25,1X,A6',
        'A2,1X,A7,4X,9(1X,A5)',
        'A2,1X,A7,4X,11(1X,A5)',
        'A2,1X,A10,1X,5(1X,A5)',
        'A2,1X,A7,4X,14(1X,A5)'
    ],
    'automatic management': [
        'A2,1X,A8,3X,7(1X,A5)',
        'A2,1X,A10,1X,7(1X,A5)',
        'A2,1X,A8,3X,5(1X,A5)',
        'A2,1X,A8,3X,3(1X,A5)',
        'A2,1X,A7,4X,4(1X,A5)'
    ],
    'mow': [],
    'mow_table': 'A5,1X,5(1X,A5)'
}
SECTIONS_ROW_FMT = {
    'treatments': '4(1X,I1),1X,A25,13(2X,I1)',
    'cultivars': '1X,I1,1X,A2,1X,A6,1X,A25',
    'field': [
        '1X,I1,1X,A8,1X,A8,1X,A5,1X,I5,1X,A5,2(1X,I5),1X,A5,1X,A4,1X,I5,2X,A10,A36',
        '1X,I1,2(1X,A15),1X,I9,1X,I17,5(1X,A5)'
    ],
    'initial conditions': '1X,I1,1X,A5,1X,A5,2(1X,I5),2(1X,F5.2),6(1X,I5),1X,A6',
    'initial conditions_table': '1X,I1,1X,I5,1X,F5.2,2(1X,F5.1)',
    'planting details': '1X,I1,2(1X,A5),2(1X,I5),2(1X,A5),7(1X,I5),1X,A5,1X,A29',
    # 'planting details_table': '1X,I1,2(1X,A5),2(1X,I5),2(1X,A5),7(1X,I5),1X,A5,1X,A29',
    'irrigation': '1X,I1,4(1X,I5),2(1X,A5),1X,I5,1X,A6',
    'irrigation_table': '1X,I1,2(1X,A5),1X,I5',
    'fertilizers': [],
    'fertilizers_table': '1X,I1,3(1X,A5),6(1X,I5),1X,A5,1X,A6',
    'harvest details': '1X,I1,4(1X,A5),2(1X,I5),1X,A5',
    # 'harvest details_table': '1X,I1,4(1X,A5),2(1X,I5),1X,A5',
    'simulation controls':[  
        '1X,I1,1X,A2,9X,2(1X,I5),2(1X,A5),1X,I5,1X,A25,1X,A6',
        '1X,I1,1X,A2,9X,9(1X,A5)',
        '1X,I1,1X,A2,9X,7(1X,A5),1X,I5,2(1X,A5),1X,I5',
        '1X,I1,1X,A2,9X,5(1X,A5)',
        '1X,I1,1X,A2,9X,3(1X,A5),1X,I5,10(1X,A5)'
    ],
    'automatic management': [
        '1X,I1,1X,A2,9X,2(1X,A5),5(1X,I5)',
        '1X,I1,1X,A2,9X,3(1X,I5),2(1X,A5),2(1X,I5)',
        '1X,I1,1X,A2,9X,3(1X,I5),2(1X,A5)',
        '1X,I1,1X,A2,9X,3(1X,I5)',
        '1X,I1,1X,A2,9X,1X,I5,1X,A5,2(1X,I5)'
    ],
    'mow': [],
    'mow_table': '1X,A5,1X,A5,3(1X,I5),1X,F5.1'
}

def unpack_keys(section):
    keys = map(lambda x: x.keys(), section.values())
    unique_keys = []
    for k in keys:
        unique_keys += list(k)
    unique_keys = set(unique_keys)
    return list(unique_keys)

def rowbased_write(fields, row_fmt):
    # This function is juts in case format strings have to be created 
    # dynamically
    fmt = ''
    for s in row_fmt.split(','):
        if '(' in s:
            N, X = s.split('(')
        elif ')' in s:
            F = s.split(')')[0]
            fmt += int(N)*f'{X},{F},'
        else:
            fmt += f'{s},'
    fmt = fmt.strip(',')
    n = -1
    new_fmt = ''
    for s in fmt.split(','):
        if 'X' not in s:
            n += 1
            if (fields[n] in NA_VALS) or (isna(fields[n])):
                fields[n] = '-99'
                if 'F' in s:
                    _, N = s.split('F')
                    N, _ = N.split('.')
                    s = f'A{N}'
                elif 'I' in s:
                    _, N = s.split('I') 
                    s = f'A{N}'
                else:
                    pass
        new_fmt += f'{s},'                
            
    fmt = new_fmt.strip(',')
    writer = ff.FortranRecordWriter(fmt)
    return writer.write(fields)

def clean_comments(lines):
    clean_lines = []
    for line in lines:
        if '!' in line[:3]:
            continue
        if len(line) < 2:
            continue
        clean_lines.append(line)
    return clean_lines

def ecotype_row_write(crop, fields, row_fmt):
    # This function is juts in case format strings have to be created 
    # dynamically
    fmt = ''
    for s in row_fmt[crop].split(','):
        if '(' in s:
            N, X = s.split('(')
        elif ')' in s:
            F = s.split(')')[0]
            fmt += int(N)*f'{X},{F},'
        else:
            fmt += f'{s},'
    fmt = fmt.strip(',')
    n = -1
    new_fmt = ''
    for s in fmt.split(','):
        if 'X' not in s:
            n += 1
            if (fields[n] in NA_VALS) or (isna(fields[n])):
                fields[n] = '-99'
                if 'F' in s:
                    _, N = s.split('F')
                    N, _ = N.split('.')
                    s = f'A{N}'
                elif 'I' in s:
                    _, N = s.split('I') 
                    s = f'A{N}'
                else:
                    pass
        new_fmt += f'{s},'                
            
    fmt = new_fmt.strip(',')
    writer = ff.FortranRecordWriter(fmt)
    return writer.write(fields)

            
class Section(MutableMapping):
    '''
    Each section contains the different parameters that define them. In DSSAT 
    files each section heading starts with *, and each header line specifying 
    variables start with @. This class storages the parameters of a section in
    a dict-like object. So, the next definitions in the PLANTING DETAILS section: 

    @P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE 
    1 82057   -99   7.2   7.2     S     R    61     0     7   -99   -99 

    would be stored in a Section instance as a dict; something like:
    {"PDATE": "82057", "EDATE": -99, "PROP": 7.2, ... , "PAGE": -99}
    '''
    def __init__(self, name:str, **kwargs):
        self.__name = name
        self.__description = None
        self.__idcol = kwargs.get('idcol')
        self.__crop = kwargs.get("crop_name")
        code = kwargs.get("code")
        file_lines = kwargs.get('file_lines', False)
        self.__repr_str = f"{self.name.title()} section"
        # When file's lines are passed. Case of CUL and ECO files.
        if file_lines:
            init_dict = {}
            if  'cultivar' in self.name:
                self._HEADER_FMT = CULTIVAR_HEADER_FMT[self.__crop]
                row_reader = ff.FortranRecordReader(
                    CULTIVAR_ROWS_FMT[self.__crop]
                )
                self._row_writer = lambda x: ecotype_row_write(
                    self.__crop, x, CULTIVAR_ROWS_FMT
                )
                self.__repr_str += f"\n  {self.__crop} crop"
            else: # Ecotype
                self._HEADER_FMT = ECOTYPE_HEADER_FMT[self.__crop]
                row_reader = ff.FortranRecordReader(
                    ECOTYPE_ROWS_FMT[self.__crop]
                )
                self._row_writer = lambda x: ecotype_row_write(
                    self.__crop, x, ECOTYPE_ROWS_FMT)

            for n, line in enumerate(file_lines):
                if line[0] == '*':
                    pass
                elif line[0] == '@':
                    reader = ff.FortranRecordReader(
                        self._HEADER_FMT
                    )
                    self.PAR_NAMES = [i.strip() for i in reader.read(line)]
                elif len(line) < 2:
                    pass
                else:
                    pars_line = row_reader.read(line)
                    if pars_line[0] == code:
                        init_dict = dict(zip(self.PAR_NAMES, pars_line))
                        break
            # If walked trhough all lines of the file and the cultivar was not found
            if (n + 1) == len(file_lines):
                warnings.warn(
                    f"{code} {self.name} not in file, default parameters will be used"
                )
                init_dict = dict(zip(self.PAR_NAMES, pars_line))

            kwargs['pars'] = init_dict
        self.__data = kwargs['pars']

        return

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __setitem__(self, k, v):
        if k not in self.__data:
            raise KeyError(k)
        if "ECO#" in k: 
            raise Exception(
                "The ecotype code can't be changed. If any change is to be done in the ecotype modify the ecotype parameters directly"
            )
        self.__data[k] = v

    def __delitem__(self, k):
        raise NotImplementedError

    def __getitem__(self, k):
        return self.__data[k]

    def __contains__(self, k):
        return k in self.__data
    
    def __repr__(self):
        out_str = self.__repr_str + "\n  Parameters:" 
        for key, value in self.__data.items():
            out_str += f"\n    {key}: {value}"
        return out_str
    
    def parameters(self):
        return self.__data
    
    @property
    def name(self):
        return self.__name
        
    @property
    def description(self):
        return self.__description

    def write(self):
        if self.name in ['cultivar', 'ecotype']:
            outstr = ff.FortranRecordWriter(self._HEADER_FMT).write(
            self.PAR_NAMES) + '\n'
            row = [self.__getitem__(par) for par in self.PAR_NAMES]
            outstr += self._row_writer(row) + '\n'
            return outstr

        outstr = ''
        fmt_header = SECTIONS_HEADER_FMT[self.name]
        fmt_row = SECTIONS_ROW_FMT[self.name]
        if isinstance(fmt_header, str):
            fmt_header = [fmt_header]
            fmt_row = [fmt_row]
        fmt_table_header = SECTIONS_HEADER_FMT.get(f'{self.name}_table', False)

        headers = list(self.keys())
        fields = list(self.values())
        start_idx = 0
        end_idx = 0
        for n, _ in enumerate(fmt_header):
            end_idx += (len(ff.FortranRecordReader(fmt_row[n]).read('')) - 1)
            outstr += ff.FortranRecordWriter(fmt_header[n]).write(
                [self.__idcol] + headers[start_idx:end_idx]
            ) + '\n'
            outstr += rowbased_write(
                [1] + fields[start_idx:end_idx], fmt_row[n]
            ) + '\n'
            start_idx = end_idx

        if fmt_table_header:
            fmt_table_row = SECTIONS_ROW_FMT.get(f'{self.name}_table')
            outstr += ff.FortranRecordWriter(fmt_table_header).write(
                [self.__idcol] + list(self['table'].columns)
            ) + '\n'
            for _, row in self['table'].iterrows():
                outstr += rowbased_write(
                    [1] + list(row), fmt_table_row
                ) + '\n'
        return outstr

class TabularSubsection(DataFrame):
    '''
    Parameter's values is a series of values. For instance, irrigation schedule 
    or initial conditions for different soil's layers. In that case, this object
    would be a part of a section. For instance, initial conditions:

    @C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME
     1    MZ 99115   200     0     1     1   -99   -99   -99   -99   -99   -99 -99
    @C  ICBL  SH2O  SNH4  SNO3
     1    15  .189     0     1
     1    20  .189     0    .5
     1    50  .228     0     0
    
    So, the previous table would be created as a `TabularSubsection` like this:

    >>> init_conditions = TabularSubsection([
        (15, .189, 0, 1),
        (20, .189, 0, .5),
        (50, .228, 0, 0)
    ], columns=['ICBL', 'SH2O', 'SNH4', 'SNO3'])

    Note that the id column (@C) is not included.
    '''
    def __init__(self, *args):
        super().__init__(args[0])
        # TODO: Include a Column check for the different tabular sections. 
        return


# TODO: Take this to the Section definition
def init_cultivar_section(spe_path, crop_name, cultivar_code):
    cul_file = spe_path[:-3] + 'CUL'
    with open(cul_file, 'r') as f:
        file_lines = f.readlines()
    file_lines = clean_comments(file_lines)

    return Section(
        name="cultivar", file_lines=file_lines, crop_name=crop_name,
        cultivar_code=cultivar_code
        )


def init_ecotype_section(spe_path, crop_name, cultivar_code):
    cul_file = spe_path[:-3] + 'ECO'
    with open(cul_file, 'r') as f:
        file_lines = f.readlines()
    file_lines = clean_comments(file_lines)

class Ecotype(Section):
    '''
    
    '''
    # Check if ecotype is here
    def __init__(self, eco_file:str, crop:str):
        self.crop = crop
        eco_file = eco_file[:-3] + 'ECO'
        with open(eco_file, 'r') as f:
            self._file_lines = f.readlines()
        self._file_lines = clean_comments(self._file_lines)
        super().__init__(name='ecotype')