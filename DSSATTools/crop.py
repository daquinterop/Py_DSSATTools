'''
Basic crop class. It initializes a crop instances based on the crop name and 
crop file if provided.

`Crop` class is the only needed class to initialize a Crop instance. You need to
specify the crop name (Those can be checked at DSSATTools.crop.CROPS_MODULES 
object), and you can also specify a .SPE file to initialize the instance. If no 
.SPE file is passed as argument, then default .SPE, .ECO and .CUL are used.

Please, take into account that if you initialize the instance with a custom 
Species file the three files (.SPE, .ECO, .CUL) must be in the same directory as
the passed Species file.

The only method implemented is `set_parameter`, that of course is used to set 
the value of any crop parameter. `Crop` class inherits from the `BaseCrop` class
of the specified crop. The `BaseCrop` class has only two sections (attributes):
cultivar and ecotype. Those sections are defined as a dict with a 
`{cultivar_code1: {parameter1: value, parameter2: value, ...}, cultivar_code2: ..., ...}`
structure. 

The usage of the Crop class is explaied by this example. In here we initialize a
Crop instance, modify a parameter and write the cropfile (All of them).

    >>> crop = Crop('maize')
    >>> crop.set_parameter(
            par_name = 'TBASE',
            par_value = 30.,
            row_loc = 'IB0002'
        )
    >>> # the next line does the same:
    >>> crop.ecotype['IB0002']['TBASE'] = 30.0
    >>> crop.write('crop_test')
'''
import os

# from DSSATTools.models import (
#     CERES, FORAGE, CROPGRO, SUBSTOR, CANEGRO
# )
from DSSATTools.base.sections import Section, unpack_keys, clean_comments
from DSSATTools import VERSION
from DSSATTools import __file__ as module_path

# To add a new crop you have to do the next:
# 1. Create a new Class for the crop within the model's submodule in the models module.
# 2. Add the new model to the CROPS_MODULES and SPE_FILES mapping dict just below.
# 3. Add the VARNAME item for the crop in the CUL_VARNAME dict in run.py
#   3.1. If forage or root, add to the PERENIAL_FORAGES and ROOTS constants
# 4. Add the fortran format strings in the sections module
# 5. Create a test in test_run.py
# 6. Run the test and fix the bugs until it works (of course, including all of the previous test as well).
# 7. Add crop to the crop.Crop docstirng and README
# CROPS_MODULES = {
#     'Maize': CERES.Maize,
#     'Millet': CERES.Millet,
#     'Sugarbeet': CERES.Sugarbeet,
#     'Rice': CERES.Rice,
#     'Sorghum': CERES.Sorghum,
#     'Sweetcorn': CERES.Sweetcorn,
#     'Alfalfa': FORAGE.Alfalfa,
#     'Bermudagrass': FORAGE.Bermudagrass,
#     'Soybean': CROPGRO.Soybean,
#     'Canola': CROPGRO.Canola,
#     'Sunflower': CROPGRO.Sunflower,
#     'Potato': SUBSTOR.Potato,
#     'Tomato': CROPGRO.Tomato,
#     'Cabbage': CROPGRO.Cabbage,
#     'Sugarcane': CANEGRO.Sugarcane
# }
SPE_FILES = {
    'Maize': f'MZCER{VERSION}.SPE',
    'Millet': f'MLCER{VERSION}.SPE',
    'Sugarbeet': f'BSCER{VERSION}.SPE',
    'Rice': f'RICER{VERSION}.SPE',
    'Sorghum': f'SGCER{VERSION}.SPE',
    'Sweetcorn': f'SWCER{VERSION}.SPE',
    'Alfalfa': f'ALFRM{VERSION}.SPE',
    'Bermudagrass': f'BMFRM{VERSION}.SPE',
    'Soybean': f'SBGRO{VERSION}.SPE',
    'Canola': f'CNGRO{VERSION}.SPE',
    'Sunflower': f'SUGRO{VERSION}.SPE',
    'Potato': f'PTSUB{VERSION}.SPE',
    'Tomato': f'TMGRO{VERSION}.SPE',
    'Cabbage': f'CBGRO{VERSION}.SPE',
    'Sugarcane': f'SCCAN{VERSION}.SPE'
}

DEFAULT_CULTIVARS = {
    "Maize": "990002"
}

CROP_CODES = {
    "Maize": "MZ"
}

CROPS_MODULES = {
    "Maize": "MZCER"
}

DSSAT_MODULE_PATH = os.path.dirname(module_path)
GENOTYPE_PATH = os.path.join(DSSAT_MODULE_PATH, 'static', 'Genotype')

SECTIONS = {
    'TemperatureEffects': '*TEMP',
    'Photosynthesis': '*PHOT',
    'StressResponse': '*STRE',
    'SeedGrowth': '*SEED',
    'EmergenceInitialConditions': '*EMER',
    'Nitrogen': '*NITR',
    'Root': '*ROOT',
    'PlantComposition': '*PLAN',
    'PhosphorusContent': '*PHOS',
    'Evapotranspiration': '*EVAP'
}

# BASE_CROPS = [model for model in CROPS_MODULES.values()]


def available_cultivars(crop_name):
    """
    Returns the code and description of the available cultivars for the specified
    crop. 
    """

class Crop:
    '''
        Initializes a Crop instance based on the crop name and the cultivar name.
        If the cultivar name is not provided then a custom cultivar will be used.
        If an unexisting cultivar (not included in the available cultivars) is 
        provided, then a new cultivar will be created and the cultivar parameters
        must be passed as well. 

        To create a new cultivar a new name must be passed, and then the parameters
        modified in the already initialized instance. The cultivar parameters are
        represented by the cultivar attribute, which is a sections.Section. 
        The ecotype is one of those parameters, and at the same time it is a 
        sections.Section object. 

        Arguments
        ----------
        crop: str
            Crop name, available at the moment: Maize, Millet, Sugarbeet, Rice,
            Sorghum, Sweetcorn, Alfalfa, Bermudagrass, Soybean, Canola, Sunflower,
            Potato, Tomato, Cabbage, Potato and Sugarcane.
        cultivar: str
            The cultivar identifier. To check the available cultivars for that crop
            use the crop.available_cultivars function. If a new cultivar (not 
            in the .CUL file for that crop) is passed, then default parameters
            will be used.
        '''
    def __init__(self, crop_name:str='Maize', cultivar_code:str=None):
        self.crop_name = crop_name.title()
        self._SMODEL = CROPS_MODULES[self.crop_name]
        self._CODE = CROP_CODES[self.crop_name]
        self._SPE_FILE = f'{self._SMODEL}{VERSION}.SPE'
        self._spe_path = os.path.join(GENOTYPE_PATH, self._SPE_FILE)
        self._cultivar_code = cultivar_code
        if self._cultivar_code is None:
            self._cultivar_code = DEFAULT_CULTIVARS[self.crop_name]
            UserWarning(
                f"No cultivar was indicated, default cultivar {self._cultivar_code} will be used"
            )            
        
        assert self.crop_name in CROPS_MODULES.keys(), \
            f'{self.crop_name} is not a valid crop'

        # Read cultivar
        cul_file = self._spe_path[:-3] + 'CUL'
        with open(cul_file, 'r') as f:
            file_lines = f.readlines()
        file_lines = clean_comments(file_lines)
        self.cultivar = Section(
            name="cultivar", file_lines=file_lines, crop_name=self.crop_name,
            code=self._cultivar_code
        )

        # Read ecotype if assigned
        eco_file = self._spe_path[:-3] + 'ECO'
        try:
            with open(eco_file, 'r') as f:
                file_lines = f.readlines()
            file_lines = clean_comments(file_lines)
            self.ecotype = Section(
                name="ecotype", file_lines=file_lines, crop_name=self.crop_name,
                code=self.cultivar["ECO#"]
            )
        except FileNotFoundError:
            pass

    def write(self, filepath:str=''):
        cultivar_str = f'*{self.crop_name.upper()} CULTIVAR COEFFICIENTS: {self._SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        ecotype_str = f'*{self.crop_name.upper()} ECOTYPE COEFFICIENTS: {self._SMODEL}{VERSION} MODEL\n' \
            + self.ecotype.write()
        with open(self._spe_path, "r") as f:
            species_str = f.read()
        
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self._SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self._SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{self._SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str)
        
    def set_parameter(self, par_name:str, par_value, row_loc=0, col_loc=0): #TODO: Differenciate among cultivar and ecotype parameters
        '''
        Set the value of one parameter in the Crop class.

        Arguments
        ----------
        par_name: str
            name of the parameter. Parameter's names are in the Crop.parameters attribute.
        par_value: str, int, float
            Value of the parameter to set.
        row_loc: int, str
            id for the element to modify. This applies to parameters defined in cols, such as cultivar or ecotype parameters. For example:
            
                @ECO#  ECONAME.........  TBASE  TOPT ROPT   P20
                IB0001 GENERIC MIDWEST1    8.0 34.0  34.0  12.5
                IB0002 GENERIC MIDWEST2    8.0 34.0  34.0  12.5

            for this set of parameters (ecotype), the column ECO# is the id to be passed as row_loc argument.
        col_loc: int, str
            same as row_loc, but for parameters defined in rows (array-like). For example:

                TEMPERATURE EFFECTS
                !       TBASE TOP1  TOP2  TMAX
                PRFTC  6.2  16.5  33.0  44.0     
                RGFIL  5.5  16.0  27.0  35.0

            In this case, to define the PRFTC parameter, you should specify one of the columns (TBASE, TOP1, etc.) through the col_loc argument.
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

    def __repr__(self):
        repr_str = f"{self.crop_name} crop, {self.cultivar['VRNAME..........']} cultivar"
        return repr_str