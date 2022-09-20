from distutils.command.config import LANG_EXT
from pandas import Series, NA, isna
import fortranformat as ff

HEADER = "*Soils: Brazil\n"

TEMPLATE = """
*SLPR000001  ESALQ       C       150 TERRA ROXA (IRRIGATED)
@SITE        COUNTRY          LAT     LONG SCS FAMILY
 SiteName    CountryName  -22.430  -47.250 Typic Eutrudox

@ SCOM  SALB  SLU1  SLDR  SLRO  SLNF  SLPF  SMHB  SMPX  SMKE
     R  0.14   9.1  0.20  83.0  1.00  0.96 IB001 IB001 IB001
@  SLB  SLMH  SLLL  SDUL  SSAT  SRGF  SSKS  SBDM  SLOC  SLCL  SLSI  SLCF  SLNI  SLHW  SLHB  SCEC  SADC
    20     A 0.280 0.349 0.530 1.000  0.39  1.23  1.47  65.0  15.0   0.0 0.120   5.0   -99  10.8   -99 
    40    AA 0.284 0.345 0.530 1.000  0.63  1.13  1.11  65.0  17.0   0.0 0.100   5.5   -99   9.2   -99 
   120    AB 0.280 0.311 0.530 0.900  1.21  1.08  0.90  62.0  16.0   0.0 0.090   5.5   -99   9.0   -99 
   150     B 0.280 0.311 0.530 0.100  1.21  1.08  0.90  62.0  16.0   0.0 0.090   5.5   -99   9.0   -99 
"""

FST_LVL_PARS = [
    'SLMH',  'SLLL',  'SDUL',  'SSAT',  'SRGF',  'SSKS',  'SBDM',  'SLOC',
    'SLCL',  'SLSI',  'SLCF',  'SLNI',  'SLHW',  'SLHB',  'SCEC',  'SADC'
]
SCD_LVL_PARS = [
    'SLPX',  'SLPT',  'SLPO', 'CACO3',  'SLAL',  'SLFE',  'SLMN',  'SLBS',
    'SLPA',  'SLPB',  'SLKE',  'SLMG',  'SLNA',  'SLSU',  'SLEC',  'SLCA'
]

LAYER_ROW_FMT = ['I5', 'A5'] + 4*['F5.3'] + 3*['F5.2'] + 3*['F5.1'] + ['F5.3'] + 4*['F5.1']

LAYER_HEAD_FMT = 'A6,16(1X,A5)'


# TODO: A list_parameters function that lists parameters with their descriptions. Found at: https://github.com/DSSAT/dssat-csm-os/blob/develop/Data/SOIL.CDE

# TODO: A parameter_check funciton. It has to check if the values for non-numerical parameters are right. If they are not, it must to raise an error. That error must include the allowable values for that parameter.

class SoilLayer(Series):
    '''
    Class representing a soil layer.
    '''
    def __init__(self):
        super().__init__(
            {
                key: NA
                for key in ['@  SLB'] + FST_LVL_PARS + ['@  SLB'] + SCD_LVL_PARS
            }
        )
        return

    # Funciton to read a layer (row)
    def layer_read(self, line):
        fmt = '1X'
        for n, field in enumerate(line.split()):
            if n != 0:
                fmt += ',1X'
            if field.replace('.', '') == '-99':
                fmt += ',A5'
            else:
                fmt += ',' + LAYER_ROW_FMT[n]
        return ff.FortranRecordReader(fmt).read(line)

    # Function to write a layer (row)
    def layer_write(fields):
        fmt = '1X'
        for n, field in enumerate(fields):
            if n != 0:
                fmt += ',1X'
            if isna(field):
                fields[n] = '-99'
                fmt += ',A5'
            else:
                fmt += ',' + LAYER_ROW_FMT[n]
        return ff.FortranRecordWriter(fmt).write(fields)

class SoilClass():
    '''
    Soil class. It can be initialized from an existing file.
    It also can be initialized from scratch.
    '''
    def __init__(self, file:str=None, id:str=None, default_class:str=None):
        '''
        Initialize a SoilClass instance. If a file is provided, then the soil
        is initilized as the soil with the matching id in the file.

        Arguments
        ----------
        file: str
            Optional. Path to the soil file.
        id: str
            Optional. Must be passed if file argument is passed. It's the 
            id of the soil within the file.
        default_class: str
            Optional. It's a string defining a DSSAT default soil class. If not None,
            then the SoilClass instance is initialized with the paremeters of the 
            specified default_class.
            default_class must match any of the next codes:
                 -------------------------- 
                 Soil texture    |  Code
                 --------------------------
                 Sand            |  S 
                 Loamy Sand      |  LS  
                 Sandy Loam      |  SL 
                 Loam            |  L 
                 Silty Loam      |  SIL 
                 Silt            |  SI 
                 Sandy Clay Loam |  SCL 
                 Clay Loam       |  CL 
                 Silty Clay Loam |  SICL 
                 Sandy Clay      |  SC 
                 Silty Clay      |  SIC 
                 Clay            |  C 
        '''
        self.n_layers = 0
        self.id = ''
        self.data_source = ''
        self.texture = ''
        self.total_depth = 0
        self.series_name = ''
        self.site = ''
        self.country = ''
        self.lat = ''
        self.lon = ''
        self.csc_family = ''
        if file:
            self._file_initilized = True
            self._file_path = file
        else:
            self._file_initilized = False

        # TODO: Initialize from a soil file, or default class soil file.
        # TODO: if default class does not match any of the available, then raise error and print docstring.
        return

    def add_layer(self, layer: SoilLayer):
        '''
        Add a new layer to the Soil.
        
        Arguments
        ----------
        layer: DSSATTools.soil.SoilLayer
            Soil Layer object
        '''
        # TODO: if SLB already exists then show overwrite warning
        # TODO: if SLB is between an existing one, then show warning.
        return

    def set_parameter(self, parameter, value):
        '''
        Set the value of a soil parameter.

        Arguments
        ----------
        parameter: str
            Parameter name. You can use the DSSATTools.soil.list_parameters function
            to have a list of the parameters and their description.
        value: int, float, str
            Value for that parameter
        '''

    def write(self, filename:str='SOIL.SOL'):
        '''
        It's called by the DSSATTools.run.Dscsm.run() method to write the file.

        Arguments
        ----------
        filename: str
            Path to the file to write
        '''
        # TODO: If Instance was initialized from file, then skip
        if self._file_initilized:
            return
        # TODO: Check if it exists. If it does, then remove and raise overwrite warning.


    # TODO: Check Soil id. If soil id is empty, then it'll be created from the .CRX file.
    # TODO: Check soil's non-numerical parameters (SMHB  SMPX  SMKE) Do this throught a set_parameter method.
    