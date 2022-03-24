from distutils.log import warn
from turtle import position
from attr import has
import pandas as pd
from numpy import cumsum
from .exceptions import DSSATInputError

class outFile(list):
    def __init__(self, out):
        super().__init__(out)
        return
    
    def __str__(self) -> str:
        return ''.join(self)


class DSSATOutput(dict):
    def __init__(self, treatments):
        self.treatments = treatments
        super().__init__({treat: {} for treat in treatments})
        return

    def addTreatmentOut(self, treat, treatOut):
        self[treat] = treatOut
        for key in self[treat].keys():
            out = self[treat][key]
            if isinstance(out, list):
                self[treat][key] = outFile(out)
        return

    def listOutput(self):
        '''
        List the Variables included in the Output
        '''
        return list(self.get(self.treatments[0]).keys())

    def getOutput(self, outName, treat):
        '''
        Get the output for the specified OutName and treatment
        '''
        return self.get(treat).get(outName)
        

def writeDSSBATCH(crop, wdir, dssatExe, exp, treat):
    BatchStr = '''
        $BATCH(%(crop)s)
        !
        ! Directory    : %(wdir)s
        ! Command Line : %(dssatExe)s %(crop)s B DSSBatch.v47
        ! Crop         : %(crop)s         
        ! Experiment   : %(exp)s
        ! ExpNo        : %(treat)s
        ! Debug        : %(dssatExe)s %(crop)s " B DSSBatch.v47"
        !
        @FILEX                                                                                        TRTNO     RP     SQ     OP     CO''' \
            % {'crop': crop, 'wdir': wdir, 'exp': exp, 'treat': treat, 'dssatExe': dssatExe}
    lines = [line[8:] + '\n' for line in BatchStr[1:].split('\n')]
    filex_len = lines[-1].index('TRTNO')
    lines.append(f'{exp}{(filex_len - len(exp) + 4)*" "}{treat}      1      0      1      0')
    return lines

def out_wrapper(filename):
    '''
    Takes a file separated by spaces and return a df a list with
    the lines of the file.
    '''
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    copy_lines = list(lines)
    if len(lines) < 1:
        return lines
    for n, line in enumerate(lines):
        if '@' in line:   
            break
            
    lines = lines[n:]
    lines = [line.replace('\n', '') for line in lines]
    n_cols = len(lines[0].split())
    df = pd.DataFrame(
        [line.split() for line in lines[1:] if len(line.split()) == n_cols],
        columns=lines[0].split()
    )
    if len(df) == 0:
        return copy_lines
    else:
        return df


def printSysOut(sysOut):
    prev_line = ''
    for line in sysOut:
        line = line.decode('utf-8')
        if prev_line == line:
            pass
        else:
            print(line, end='')
        prev_line = line
    print()
    return

class CropParser():
    def __init__(self, crop_file, raise_missing_pars=True):
        self.CROPFILE = crop_file
        with open(self.CROPFILE, 'r') as f:
            self._FILELINES = f.readlines()
        self._SEC_START_LINES = {
            line[:8]: n 
            for n, line in enumerate(self._FILELINES)
            if line.strip()[:2] == '!*'
        }
        self.RAISE_MISS = raise_missing_pars
        self.parameters = {}
        self._parsloc = {}
        self.__read_phot()
        self.__read_resp()
        self.__read_plantcomp()
        self.__read_Nfix()
        self.__read_vegPart()
        self.__read_leafGrowth()
        self.__read_leafSenscence()
        self.__read_root()
        self.__read_canopy()
        self.__read_ET()
        self.__read_dormancy()
        self.__read_dormancy()
        return
    
    def __ignore(self, start_line):
        for n, line in enumerate(self._FILELINES[start_line:]):
            if line[:1] not in ['!', '*'] and len(line.strip()) > 0:
                return n + start_line + 1, self._FILELINES[n + start_line]
    

    def __read(self, line, n_pars, lenght, names, curr_line):
        if not all([name in line for name in names]):
            if self.RAISE_MISS:
                raise DSSATInputError(f'One or some of {", ".join(names)} parameters were not found at line {curr_line+1} of {self.CROPFILE}')
            else: 
                warn(f'\033[93mWarn: One or some of {", ".join(names)} parameters were not found at line {curr_line+1} of {self.CROPFILE}')
                return False
        
        parameters = []
        positions = []
        if not hasattr(lenght, '__iter__'):
            lenght = [lenght]*n_pars
        pos = [0] + list(cumsum(lenght))
        for bottom, upper  in zip(pos[:-1], pos[1:]):
            parameters.append(line[bottom:upper])
            positions.append((curr_line, (bottom, upper))) # (line_of_parameter, (left_pos, right_pos))
        
        extra_pos = 0
        for n, name in enumerate(names):
            name_plain = name.replace('VALUES', '').replace('1-', '')
            if '(' in name or (len(names) == 1 and n_pars > 1): # Last term is for Veg Part parameters
                if '(' in name:
                    vec_len = int(name_plain.split('(')[1].split(')')[0])
                else:
                    vec_len = n_pars
                self.parameters[name] = parameters[n:n + vec_len]
                self._parsloc[name] = positions[n:n + vec_len]
                extra_pos += vec_len - 1
            else:
                self.parameters[name] = parameters[n + extra_pos]
                self._parsloc[name] = positions[n + extra_pos]
        return True


    def __read_phot(self):
        start_line = self._SEC_START_LINES['!*PHOTOS']
        PARS_NAMES_LIST = [
            ['PARMAX', 'PHTMAX','KCAN', 'KC_SLOPE'],
            ['CCMP','CCMAX','CCEFF'],
            ['FNPGN(4)', 'TYPPGN'], ['FNPGT(4)', 'TYPPGT'],
            ['XLMAXT (6 VALUES)'], ['YLMAXT (6 VALUES)'],
            ['FNPGL(4)', 'TYPPGL'],
            ['PGEFF', 'SCV', 'KDIF', 'LFANGB'],
            ['SLWREF', 'SLWSLO', 'NSLOPE', 'LNREF', 'PGREF'],
            ['XPGSLW(1-10)'], ['YPGSLW(1-10)'],
            ['CICA', 'CCNEFF', 'CMXSF', 'CQESF', 'PGPATH']
        ]
        N_PARS_LIST = [4, 3 ,5, 5, 6, 6, 5, 4, 5, 10, 10, 5]
        LENGHT_LIST = [6] * len(PARS_NAMES_LIST)
        
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return


    def __read_resp(self):
        start_line = self._SEC_START_LINES['!*RESPIR']
        PARS_NAMES_LIST = [
            ['RES30C', 'R30C2'],
            ['RNO3C', 'RNH4C', 'RPRO', 'RFIXN' ],
            ['RCH20', 'RLIP', 'RLIG', 'ROA', 'RMIN', 'PCH2O'],
            ['MRSWITCH'], ['LFMRC', 'STMMRC', 'RTMRC'],
            ['STRMRC', 'SHELMRC', 'SDMMRC'],
            ['TRSFN(4)', 'TRSTYP']

        ]
        N_PARS_LIST = [2, 4, 6, 1, 3, 3, 5]
        LENGHT_LIST = [[12, 6], 6, 6, 6, 12, 12, 6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return


    def __read_plantcomp(self):
        start_line = self._SEC_START_LINES['!*PLANT ']
        PARS_NAMES_LIST = [
            ['PROLFI', 'PROLFG', 'PROLFF', 'PROSTI', 'PROSTG', 'PROSTF'],
            ['PRORTI', 'PRORTG', 'PRORTF', 'PROSHI', 'PROSHG', 'PROSHF']
        ]
        N_PARS_LIST = [6, 6]
        LENGHT_LIST = [6, 6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return


    def __read_Nfix(self):
        start_line = self._SEC_START_LINES['!*NITROG']
        PARS_NAMES_LIST = [
            ['SNACTM', 'NODRGM', 'DWNODI', 'TTFIX', 'NDTHMX', 'CNODCR'],
            ['FNNGT(4)', 'TYPNGT'], ['FNFXT(4)', 'TYPFXT']
        ]
        N_PARS_LIST = [6, 5, 5]
        LENGHT_LIST = [6, 6, 6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return

    
    def __read_vegPart(self):
        start_line = self._SEC_START_LINES['!*VEGETA']
        PARS_NAMES_LIST = [
            ['XLEAF'], ['YLEAF'], ['YSTEM']
        ]
        N_PARS_LIST = [8, 8, 8]
        LENGHT_LIST = [6, 6, 6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return

    def __read_leafGrowth(self):
        start_line = self._SEC_START_LINES['!*LEAF G']
        PARS_NAMES_LIST = [
            ['FINREF', 'SLAREF', 'SIZREF', 'VSSINK', 'EVMODC'],
            ['SLAMAX', 'SLAMIN', 'SLAPAR', 'TURSLA', 'NSLA', 'NHGT'],
            ['XVGROW(1-6)'], ['YVREF(1-6)'], ['XSLATM(1-5)'],
            ['YSLATM(1-5)']
        ]
        N_PARS_LIST = [5, 6, 6, 6, 5, 5]
        LENGHT_LIST = [6, 6, 6, 6, 6, 5]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return
    
    def __read_leafSenscence(self):
        start_line = self._SEC_START_LINES['!*LEAF S']
        PARS_NAMES_LIST = [
            ['SENRTE', 'SENRT2', 'SENDAY', 'FREEZ1', 'FREEZ2']
        ]
        N_PARS_LIST = [5]
        LENGHT_LIST = [6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return

    def __read_root(self):
        start_line = self._SEC_START_LINES['!*ROOT P']
        PARS_NAMES_LIST = [
            ['RTDEPI', 'RFAC1', 'RTSEN', 'RLDSM', 'RTSDF', 'RWUEP1', 'RWUMX']
        ]
        N_PARS_LIST = [7]
        LENGHT_LIST = [6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return

    def __read_canopy(self):
        start_line = self._SEC_START_LINES['!*CANOPY']
        PARS_NAMES_LIST = [
            ['XVSHT(1-10)'], ['YVSHT(1-10)'], ['YVSWH(1-10)'],
            ['XHWTEM(1-5)'], ['YHWTEM(1-5)'], 
        ]
        N_PARS_LIST = [10, 10, 10, 5, 5]
        LENGHT_LIST = [6, 6, 6, 6, 6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return

    def __read_ET(self):
        start_line = self._SEC_START_LINES['!*EVAPOT']
        PARS_NAMES_LIST = [
            ['KEP', 'EORATIO']
        ]
        N_PARS_LIST = [2]
        LENGHT_LIST = [6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return

    def __read_dormancy(self):
        start_line = self._SEC_START_LINES['!*DORMAN']
        PARS_NAMES_LIST = [
            ['FNPTD(4)', 'TYPPTD'], ['FNPMD(4)', 'TYPPMD'],
            ['FMPGD(4)', 'TYPPGD'], ['HARD1', 'HARD2', 'FRZDC'],
            ['FRZHRD(4)', 'TYPHRD'], ['FRZDHD(4)', 'TYPDHD']
        ]
        N_PARS_LIST = [5, 5, 5, 3, 5, 5]
        LENGHT_LIST = [6, 6, 6, 6, 6, 6]
        for n_pars, lenght, names in zip (N_PARS_LIST, LENGHT_LIST, PARS_NAMES_LIST):
            start_line, line = self.__ignore(start_line)
            read = self.__read(line, n_pars, lenght, names, start_line - 1)
            if not read:
                start_line -= 1
        return
    

    