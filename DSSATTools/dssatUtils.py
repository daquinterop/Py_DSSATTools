from concurrent.futures.process import BrokenProcessPool
from distutils.log import warn
import enum
from turtle import position
# from attr import has
import pandas as pd
from numpy import cumsum, isin
from .exceptions import DSSATInputError
import os

class outFile(list):
    def __init__(self, out):
        super().__init__(out)
        return
    
    def __str__(self) -> str:
        return ''.join(self)

# TODO: Allow the treatment to be pased as integer
class DSSATOutput(dict):
    '''
    A dict-like class to handle DSSAT Output Files. 
    Table-like outputs will be saved as a pandas.Dataframe object.
    Text-like outputs will be storaged as lists of text lines. By applying 
        print function on text-like outputs it will be pretty printed.
    ...
    Attributes
    ------------------
    treatments: list
        List os treaments on the simulation
    '''
    def __init__(self, treatments):
        '''
        
        '''
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
        ...
        Attributes
        ------------------
        outName: str
            Name of the output file. Don't include the .OUT extension

        treat: str
            Name of the treatment to retrieve
        '''
        if not isinstance(treat, str): treat = str(treat)
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
    '''
    A class to Load, modify and write DSSAT Crop Files (.SPE, .CUL, .ECO). When 
    reading the files it reads the parameters IN ORDER. If some warn or error states
    that the parameters were not found, but they are in the crop file, it's likely 
    because those parameters are on the wrong order.
    ...
    Attributes
    ------------------
    CROPFILE: str
        Path to the crop file
    parameters:
        Dict of parameters
    '''
    def __init__(self, crop_file, raise_missing_pars=True):
        '''
        Intialize the crop parser by finding the parameters in the crop file.
        crop_file: str
            Path to the .SPE crop file
        raise_missing_pars: bool
            Wheter to raise an error when some of the parameters are not present on the 
            crop file. If False, it will show warns when some of the parameters are not
            found on the crop file.
        '''
        self.CROPFILE = crop_file
        with open(self.CROPFILE, 'r') as f:
            self._FILELINES = f.readlines()
        self._SEC_START_LINES = {
            line[:8]: n 
            for n, line in enumerate(self._FILELINES)
            if line.strip()[:2] == '!*'
        }
        if len(self._SEC_START_LINES) == 0:
            raise DSSATInputError(
                f'No header sections were found on {self.CROPFILE}' + 
                'This file probably not valid for CROPGRO model'
            )
        self.RAISE_MISS = raise_missing_pars
        self.parameters = {}
        self._parsloc = {}
        self._modified_pars = []
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
        try:
            self.__read_dormancy()
        except KeyError:
            warn(f'\033[93mWarn: dormancy section was not found at {self.CROPFILE}')
        self.__read_cul()
        self.__read_eco()
        return
    
    def __ignore(self, start_line, filetype='SPE'):
        '''Iterate over the file until a valid line is found
        ...
        Arguments
        --------------
        start_line: int
            Line number to start iterating
        filetype: str
            File type, any value in SPE, ECO, CUL
        '''
        if filetype == 'ECO':
            FILELINES = self._ECOLINES
        elif filetype == 'CUL':
            FILELINES = self._CULLINES
        else:
            FILELINES = self._FILELINES
        for n, line in enumerate(FILELINES[start_line:]):
            if line[:1] not in ['!', '*'] and len(line.strip()) > 0:
                return n + start_line + 1, FILELINES[n + start_line]
    

    def __read(self, line, n_pars, lenght, names, curr_line, filetype='SPE'):
        '''
        Read the parameters on that line
        ...
        Attributes
        -----------------------
        line: str
            Line for the parameters to be read
        n_pars: int
            Number of parameters on that line
        lenght: int or list
            Lenght of all the parameters on the line (int) or list with the
            lenghts of the paramters on that line.
        names: list
            List with the names of the parameters to be read.
        curr_line: int
            Current line on the crop file being read
        '''
        if not any([name in line for name in names]):
            if self.RAISE_MISS:
                raise DSSATInputError(
                    f'One or some of {", ".join(names)} parameters were not' +
                    f' found at line {curr_line+1} of {self.CROPFILE}'
                )
            else: 
                warn(
                    f'\033[93mWarn: One or some of {", ".join(names)} parameters' +
                    f' were not found at line {curr_line+1} of {self.CROPFILE}'
                )
                return False
        
        parameters = []
        positions = []
        # When lenghts are variable among the same line
        if not hasattr(lenght, '__iter__'):
            lenght = [lenght]*n_pars
        pos = [0] + list(cumsum(lenght))
        for bottom, upper  in zip(pos[:-1], pos[1:]):
            parameters.append(line[bottom:upper])
            positions.append((curr_line, (bottom, upper))) # (line_of_parameter, (left_pos, right_pos))
        # For uniform lenghts
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
    

    def __read_cul(self):
        CUL_PATH = self.CROPFILE[:-3] + 'CUL'
        if not os.path.exists(CUL_PATH):
            warn(f'\033[93mWarn: .CUL file not in the same path as {self.CROPFILE}')
            return
        self.CULFILE = CUL_PATH
        with open(self.CULFILE, 'r') as f:
            self._CULLINES = f.readlines()
        start_line = 0
        start_line, line = self.__ignore(start_line, 'CUL')
        VAR_LOCS = [0, 6, 1, 16, 1, 6] + [6] * 18
        VAR_LOCS = cumsum(VAR_LOCS)
        self._cullocs = {}
        pars = []
        for bottom, upper in zip(VAR_LOCS[:-1], VAR_LOCS[1:]):
            parameter = (line[bottom:upper]).strip()
            if len(parameter.strip()) < 1:
                continue
            pars.append(parameter)
            self._cullocs[parameter] = (bottom, upper)
            self._parsloc[parameter] = [('CUL', (bottom, upper))]
            self.parameters[parameter] = []
        start_line, line = self.__ignore(start_line, 'CUL')
        # Append one for extraline
        for parameter in pars:
            for _ in range(len(self._CULLINES) - start_line):
                self._parsloc[parameter].append(self._parsloc[parameter][0])

        for line_n in range(start_line - 1, len(self._CULLINES)):
            line = self._CULLINES[line_n]
            if len(line.strip()) < 1:
                break
            for parameter, (bottom, upper) in self._cullocs.items():
                self.parameters[parameter].append(line[bottom:upper])


    def __read_eco(self):
        ECO_PATH = self.CROPFILE[:-3] + 'ECO'
        if not os.path.exists(ECO_PATH):
            warn(f'\033[93mWarn: .ECO file not in the same path for {self.CROPFILE}')
            return
        self.ECOFILE = ECO_PATH
        with open(self.ECOFILE, 'r') as f:
            self._ECOLINES = f.readlines()
        start_line = 0
        start_line, line = self.__ignore(start_line, 'ECO')
        VAR_LOCS = [0, 6, 1, 17, 1, 2, 1, 2] + [6] * 23
        VAR_LOCS = cumsum(VAR_LOCS)
        self._ecolocs = {}
        pars = []
        for bottom, upper in zip(VAR_LOCS[:-1], VAR_LOCS[1:]):
            parameter = (line[bottom:upper]).strip()
            if len(parameter.strip()) < 1:
                continue
            pars.append(parameter)
            self._ecolocs[parameter] = (bottom, upper)
            self._parsloc[parameter] = [('ECO', (bottom, upper))]
            self.parameters[parameter] = []
        start_line, line = self.__ignore(start_line, 'ECO')
        # Append one for extraline
        for parameter in pars:
            for _ in range(len(self._CULLINES) - start_line):
                self._parsloc[parameter].append(self._parsloc[parameter][0])

        for line_n in range(start_line - 1, len(self._ECOLINES)):
            line = self._ECOLINES[line_n]
            if len(line.strip()) < 1:
                break
            for parameter, (bottom, upper) in self._ecolocs.items():
                self.parameters[parameter].append(line[bottom:upper])


    def print_parameters(self):
        ''' It prints a list of the parameters obtained by the parser from the crop file'''
        print(', '.join(self.parameters.keys()))

    def set_parameter(self, parameter:str, value):
        '''
        Set the value of a parameter.
        ....
        Arguments
        ---------------------
        parameter: str
            Name of the parameter to set
        value: str, numeric or list
            Value of the parameter. If the parameter is a list of values then a list
            must be pased.
        '''
        if parameter not in self.parameters.keys():
            raise KeyError(f'Parameter {parameter} not found')
        # For list-like values
        if (hasattr(value, '__iter__') and (not isinstance(value, str))):
            LOCS = self._parsloc[parameter]
            for n, (val, (BOTTOM, UPPER)) in enumerate(zip(value, map(lambda x: x[1], LOCS))):
                VAL_LEN = UPPER - BOTTOM
                if isinstance(val, float):
                    if len(str(int(val))) > (VAL_LEN):
                        raise DSSATInputError(f'Input lenght exceeds parameter lenght ({VAL_LEN})')
                val = str(val)[:VAL_LEN]
                val = ' '*(VAL_LEN - len(val)) + val
                self.parameters[parameter][n] = val
        else: # For normal values
            _, (BOTTOM, UPPER) = self._parsloc[parameter]
            VAL_LEN = UPPER - BOTTOM
            if isinstance(value, float):
                if len(str(int(value))) > (VAL_LEN):
                    raise DSSATInputError(f'Input lenght exceeds parameter lenght ({VAL_LEN})')
            value = str(value)[:VAL_LEN]
            value = ' '*(VAL_LEN - len(value)) + value
            self.parameters[parameter] = value
        self._modified_pars.append(parameter)
        return

    def set_parameters(self, pars_dict={}):
        '''
        Set the value of several parameters at the same time.
        ....
        Arguments
        ---------------------
        pars_dict: dict
            A dict with the parameter name as key assigned to the value. For example: 
            {"par1": 94, "par2(4)": [1, 2, 3, 4]}
        '''
        for parameter, value in pars_dict.items():
            self.set_parameter(parameter, value)

    def write(self, file_path:str):
        '''
        Write the crop file
        ...
        Arguments
        ----------------------
        file_path: str
            File to write path. Do not include the extension.
        '''
        for parameter in self._modified_pars:
            value = self.parameters[parameter]
            if not (hasattr(value, '__iter__') and (not isinstance(value, str))):
                value = [value]
            locs = self._parsloc.get(parameter)
            if isinstance(locs, tuple):
                locs = [locs]
            for val, (line_n, (bottom, upper)) in zip(value, locs):
                if isinstance(line_n, str): # To break for the CUL and ECO files
                    break
                line = self._FILELINES[line_n]
                self._FILELINES[line_n] = line[:bottom] + val + line[upper:]
        with open(f'{file_path}.SPE', 'w') as f:
            f.writelines(self._FILELINES)

        # Save .CUL file it was included
        if hasattr(self, 'CULFILE'):
            start_line = 0
            start_line, line = self.__ignore(start_line, 'CUL')
            PARS_START_LINE, line = self.__ignore(start_line, 'CUL')
            PARS_START_LINE -= 1
            for parameter, (bottom, upper) in self._cullocs.items():
                values = self.parameters[parameter]
                for n, val in enumerate(values):
                    line_n = PARS_START_LINE + n 
                    line = self._CULLINES[line_n]
                    self._CULLINES[line_n] = line[:bottom] + val + line[upper:]
            with open(f'{file_path}.CUL', 'w') as f:
                f.writelines(self._CULLINES)
        
        # Save .ECO File
        if hasattr(self, 'ECOFILE'):
            start_line = 0
            start_line, line = self.__ignore(start_line, 'ECO')
            PARS_START_LINE, line = self.__ignore(start_line, 'ECO')
            PARS_START_LINE -= 1
            for parameter, (bottom, upper) in self._ecolocs.items():
                values = self.parameters[parameter]
                for n, val in enumerate(values):
                    line_n = PARS_START_LINE + n 
                    line = self._ECOLINES[line_n]
                    self._ECOLINES[line_n] = line[:bottom] + val + line[upper:]
            with open(f'{file_path}.ECO', 'w') as f:
                f.writelines(self._ECOLINES)
        
    