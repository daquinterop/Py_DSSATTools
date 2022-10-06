'''
Basic crop class. It initializes a crop instances based on the crop name and
crop file if provided.
'''
import os

from DSSATTools.models import (
    CERESMaize
)
from DSSATTools import __file__ as DSSATModulePath
from DSSATTools.base.sections import unpack_keys

DSSATModulePath = os.path.dirname(DSSATModulePath)
CROPS_MODULES = {
    'Maize': CERESMaize
}

BASE_CROPS = [module.CropBase for module in CROPS_MODULES.values()]


class Gonorrea:
    def __init__(self, spe_file):
        print('Te equivocastes de clase hijueputa')
        self.ecotype = 'Ecotype ni que hijueputas'
        self.cultivar = 'QUISE CULTIVAR UN AMOR Y ME HE QUEDADO SOLOOOOOOOOO'
BASE_CROPS = [Gonorrea] + BASE_CROPS


class Crop(*BASE_CROPS):
    '''
    
    '''
    def __init__(self, crop_name:str='Maize', spe_file:str=None):
        '''
        Initializes a crop instance based on the default DSSAT Crop files, or 
        on a custom crop file provided as a cultivar.

        Arguments
        ----------
        crop: str
            Crop name, it must be one of these:
                - Maize
                - TODO: Implement more crops
        spe_file: str
            Optional. Path to the cultivar file to initialize the instance.
        '''
        crop_name = crop_name.title()
        GENOTYPE_PATH = os.path.join(DSSATModulePath, 'static', 'Genotype')
        assert crop_name in CROPS_MODULES.keys(), \
            f'{crop_name} is not a valid crop'

        self.MODEL = CROPS_MODULES[crop_name]

        if not spe_file:
            spe_file = os.path.join(GENOTYPE_PATH, self.MODEL.SPE_FILE)

        # defining where to start the MRO.
        MRO_START = self.__class__.__mro__.index(self.MODEL.CropBase)
        MRO_START = self.__class__.__mro__[MRO_START - 1]
        super(MRO_START, self).__init__(spe_file)
        # TODO: Ok, I won't be working in this until it's necessary, then,
        # by now I'll only work in the cultivar and ecotype files.
        
        self._pars_section_map = {}
        self.parameters = []

        for section in (self.cultivar, self.ecotype):
            section_name = section.__class__.__name__.lower()
            pars = unpack_keys(section)
            self._pars_section_map.update(
                dict(zip(pars, len(pars)*[section_name]))
            )
            self.parameters += pars
        
    def set_parameter(self, par_name:str, par_value, row_loc=0, col_loc=0):
        '''
        Set the value of one parameter in the Crop class.

        Arguments
        ----------
        par_name: str
            name of the parameter. Parameter's names are in the Crop.parameters 
            attribute.
        par_value: str, int, float
            Value of the parameter to set.
        row_loc: int, str
            id for the element to modify. This applies to parameters defined in 
            cols, such as cultivar or ecotype parameters. For example:
            
            @ECO#  ECONAME.........  TBASE  TOPT ROPT   P20  
            IB0001 GENERIC MIDWEST1    8.0 34.0  34.0  12.5 
            IB0002 GENERIC MIDWEST2    8.0 34.0  34.0  12.5
            
            for this set of parameters (ecotype), the column ECO# is the id to
            be passed as row_loc argument.
        col_loc: int, str
            same as row_loc, but for parameters defined in rows (array-like).
            For example:

            *TEMPERATURE EFFECTS
            !       TBASE TOP1  TOP2  TMAX
              PRFTC  6.2  16.5  33.0  44.0     
              RGFIL  5.5  16.0  27.0  35.0 

            In this case, to define the PRFTC parameter, you should specify one 
            of the columns (TBASE, TOP1, etc.) through the col_loc argument.
        '''
        assert par_name in self.parameters, \
            f'{par_name} is not a valid parameter name'
        section_name = self._pars_section_map[par_name]
        if row_loc:
            self.__dict__[section_name][row_loc][par_name] = par_value
        elif col_loc:
            self.__dict__[section_name][par_name][col_loc] = par_value
        else:
            self.__dict__[section_name][par_name] = par_value
        print()
