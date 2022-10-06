'''

'''
from re import S
import fortranformat as ff
import magic #To handle possible encoding compatibility issues
from pandas import NA, isna

NA_VALS = (None, '-99', -99)

CULTIVAR_HEADER_FMT = {
    'Maize': 'A6,1X,A16,1X,A5,1X,A6,6(1X,A5)'
}
CULTIVAR_ROWS_FMT = {
    'Maize': 'A6,1X,A16,1X,A5,1X,A6,4(1X,F5.1),2(1X,F5.2)'
}

def get_cultivar_row_fmt(crop, **kwargs):
    # This function is juts in case format strings have to be created 
    # dynamically
    if crop == 'Maize':
        return CULTIVAR_ROWS_FMT[crop]

ECOTYPE_HEADER_FMT = {
    'Maize': 'A6,1X,A16,1X,11(1X,A5)'
}
ECOTYPE_ROWS_FMT = {
    'Maize': 'A6,1X,A16,1X,11(1X,F5.1)'
}

def unpack_keys(section):
    keys = map(lambda x: x.keys(), section.values())
    unique_keys = []
    for k in keys:
        unique_keys += list(k)
    unique_keys = set(unique_keys)
    return list(unique_keys)

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

def clean_comments(lines):
    clean_lines = []
    for line in lines:
        if '!' in line[:3]:
            continue
        clean_lines.append(line)
    return clean_lines

def magic_open(filename):
    blob = open(filename, 'rb').read()
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(blob)
    return open(filename, 'r', encoding=encoding)


class Section(dict):
    '''
    Section class. Reads and writes sections.
    '''
    def __init__(self, section:str='', section_map:dict={}, file_lines:list=[]):
        '''
        Arguments
        ----------
        section: str
            name of the section. Should be one of the section_map keys.
        '''
        init_dict = {}
        
        if self.__class__.__name__ in ['Cultivar', 'Ecotype']:
            if self.__class__.__name__ == 'Cultivar':
                self._HEADER_FMT = CULTIVAR_HEADER_FMT[self.crop]
                row_reader = ff.FortranRecordReader(
                    CULTIVAR_ROWS_FMT[self.crop]
                )
                self._row_writer = lambda x: ecotype_row_write(
                    self.crop, x, CULTIVAR_ROWS_FMT
                    )
            else: 
                self._HEADER_FMT = ECOTYPE_HEADER_FMT[self.crop]
                row_reader = ff.FortranRecordReader(
                    ECOTYPE_ROWS_FMT[self.crop]
                )
                self._row_writer = lambda x: ecotype_row_write(
                    self.crop, x, ECOTYPE_ROWS_FMT)

            for line in self._file_lines:
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
                    for n, field in enumerate(row_reader.read(line)):
                        if isinstance(field, str):
                            field = field.strip()
                        if n == 0:
                            row_id = field
                            init_dict[row_id] = {}
                        else:
                            init_dict[row_id][self.PAR_NAMES[n]] = field

        super().__init__(init_dict)

        # TODO: Define FORMATS Depending on section type

    def write(self):
        '''
        Ok, this thing basically returns a str for the section to be written.
        Up today this is only implemented for Cultivar and Ecotype Classes.
        '''
        outstr = ff.FortranRecordWriter(self._HEADER_FMT).write(
            self.PAR_NAMES) + '\n'
        for row_id, fields in self.items():
            row = [row_id]
            for par in self.PAR_NAMES[1:]:
                row.append(fields[par])
            outstr += self._row_writer(row) + '\n'

        return outstr

            


class Cultivar(Section):
    '''

    '''
    def __init__(self, spe_file:str, crop:str):
        self.crop = crop
        cul_file = spe_file[:-3] + 'CUL'
        with magic_open(cul_file) as f:
            self._file_lines = f.readlines()
        self._file_lines = clean_comments(self._file_lines)
        super().__init__()
        print()



class Ecotype(Section):
    '''
    
    '''
    def __init__(self, eco_file:str, crop:str):
        self.crop = crop
        eco_file = eco_file[:-3] + 'ECO'
        with magic_open(eco_file) as f:
            self._file_lines = f.readlines()
        self._file_lines = clean_comments(self._file_lines)
        super().__init__()