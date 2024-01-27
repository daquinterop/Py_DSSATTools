'''
`Crop` is the only implemented class in the crop module. DSSAT's crop parameters
are grouped in three different files: ecotype (.ECO), cultivar (.CUL) and 
species (.SPE). Not all crops have the ecotype file though. DSSATTools uses the 
default .SPE, .ECO, and .CUL files. The ecotype and cultivar parameters are
defined as attributes of the `Crop` instance. Each parameter is accessible and can
be modified using the key, value syntax, e.g.
`crop.cultivar["PARAMETER"] = VALUE`. 

It is well known that for a species there can be multiple varieties. Therefore, 
when initializing a `Crop` instance, two parameters must be provided: the crop 
name (species), and the cultivar code. The cultivar codes are defined in the .CUL
file. If an unknown cultivar is passed, then the last cultivar in the .CUL file is
used and a warning is shown. To get a list of the available cultivars for a crop
the user can use the `DSSATTools.available_cultivars` function passing the 
crop name as the only argument.

If the user wants to modify the cultivar or ecotype parameters they can through
the `Crop.cultivar` and `Crop.ecotype` attributes respectively. In these two
attributes both the cultivar and ecotype parameters are defined as a `Section`
class (DSSATTools.sections.Section). `Section` class simply maps the parameter's
name to a value; it can be treated as a python dictionary. Each of the different
sections of the `Management` class are defined in the same way.

The next example shows how to define the crop and modify one cultivar and ecotype
parameter.

    >>> crop = Crop('maize')
    >>> crop.cultivar["P1"] = 240
    >>> crop.ecotype["P20"] = 13.

Note that only the cultivar and ecotype parameters can be modified. If the user
wants to modify the species parameters, they'll have to directly do it on the
Genotype files located in `DSSATTools.crop.GENOTYPE_PATH`
'''
import os

from DSSATTools.base.sections import Section, clean_comments
from DSSATTools import VERSION
from DSSATTools import __file__ as module_path
import warnings

# To add a new crop you have to do the next: 
# 1. Add all the new crop to DEFAULT_CULTIVARS, CROP_CODES, CROPS_MODULES, CUL_VARNAME 
#    in this file
# 2. Add the new crop to CULTIVAR_HEADER_FMT, CULTIVAR_ROWS_FMT, ECOTYPE_HEADER_FMT, and
#    ECOTYPE_ROWS_FMT in sections.py
# 3. Add the crop in the __init__ docstring and the README file.

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
    'Sugarcane': f'SCCAN{VERSION}.SPE',
    "Wheat": f"WHCER{VERSION}.SPE"
}

DEFAULT_CULTIVARS = {
    "Maize": "990002",
    'Millet': "990002",
    'Sugarbeet': "CR0001",
    'Rice': "990002",
    'Sorghum': "990002",
    'Sweetcorn': "SW0001",
    'Alfalfa': "AL0001",
    'Bermudagrass': "UF0001",
    'Soybean': "990011",
    'Canola': "000001",
    'Sunflower': "IB0001",
    'Potato': "IB0003",
    'Tomato': "TM0001",
    'Cabbage': "990001",
    'Sugarcane': "IB0001",
    "Wheat": "IB1500"
}

CROP_CODES = {
    "Maize": "MZ",
    'Millet': "ML",
    'Sugarbeet': "BS",
    'Rice': "RI",
    'Sorghum': "SG",
    'Sweetcorn': "SW",
    'Alfalfa': "AL",
    'Bermudagrass': "BM",
    'Soybean': "SB",
    'Canola': "CN",
    'Sunflower': "SU",
    'Potato': "PT",
    'Tomato': "TM",
    'Cabbage': "CB",
    'Sugarcane': "SC",
    "Wheat": "WH"
}

CROPS_MODULES = {
    "Maize": "MZCER",
    'Millet': "MLCER",
    'Sugarbeet': "BSCER",
    'Rice': "RICER",
    'Sorghum': "SGCER",
    'Sweetcorn': "SWCER",
    'Alfalfa': "PRFRM",
    'Bermudagrass': "PRFRM",
    'Soybean': "CRGRO",
    'Canola': "CRGRO",
    'Sunflower': "CRGRO",
    'Potato': "PTSUB",
    'Tomato': "CRGRO",
    'Cabbage': "CRGRO",
    'Sugarcane': "SCCAN",
    "Wheat": "WHCER"
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

CUL_VARNAME = {
    'MZ': 'VRNAME..........',
    'ML': 'VAR-NAME........',
    'BS': 'VRNAME..........',
    'RI': 'VAR-NAME........',
    'SG': 'VAR-NAME........',
    'SW': 'VRNAME..........',
    'AL': 'VRNAME..........',
    'BM': 'VRNAME..........',
    'SB': 'VAR-NAME........',
    'CN': 'VRNAME..........',
    'SU': 'VAR-NAME........',
    'PT': 'VAR-NAME........',
    'TM': 'VRNAME..........',
    'CB': 'VRNAME..........',
    'SC': 'VAR-NAME........',
    "WH": "VAR-NAME........"
}


def available_cultivars(crop_name):
    """
    Returns the code and description of the available cultivars for the specified
    crop. 
    """
    crop_name = crop_name.title()
    assert crop_name in CROPS_MODULES.keys(), \
        f'{crop_name} is not a valid crop'
    SMODEL = CROPS_MODULES[crop_name]
    CODE = CROP_CODES[crop_name]
    cul_path = os.path.join(GENOTYPE_PATH, f'{CODE}{SMODEL[2:]}{VERSION}.CUL')
    with open(cul_path, "r") as f:
        lines = f.readlines()
    lines = [l for l in lines if l[:1] not in ["@", "*", "!", "$"]]
    lines = [l for l in lines if len(l) > 5]
    return [l.split()[0] for l in lines if len(l.strip()) > 6]

class Crop:
    def __init__(self, crop_name:str='Maize', cultivar_code:str=None):
        '''
        Initializes a Crop instance based on the crop name and the cultivar name.
        If the cultivar name is not provided then a custom cultivar will be used. 

        The cultivar and ecotype parameters are represented by the cultivar and 
        ecotype attribute, which is a `DSSATTools.sections.Section` instance.

        Arguments
        ----------
        crop: str
            Crop name, available at the moment: Maize, Millet, Sugarbeet, Rice,
            Sorghum, Sweetcorn, Alfalfa, Bermudagrass, Soybean, Canola, Sunflower,
            Potato, Tomato, Cabbage, Potato and Sugarcane.
        cultivar: str
            The cultivar identifier. To check the available cultivars for that
            crop use the DSSATTools.available_cultivars function. If a new
            cultivar (not in the .CUL file for that crop) is passed, then default
            parameters are be used.
        '''
        self._crop_name = crop_name.title()
        assert self._crop_name in CROPS_MODULES.keys(), \
            f'{self._crop_name} is not a valid crop'
        self._SMODEL = CROPS_MODULES[self._crop_name]
        self._CODE = CROP_CODES[self._crop_name]
        self._SPE_FILE = f'{self._CODE}{self._SMODEL[2:]}{VERSION}.SPE'
        self._spe_path = os.path.join(GENOTYPE_PATH, self._SPE_FILE)
        self._cultivar_code = cultivar_code
        if self._cultivar_code is None:
            self._cultivar_code = DEFAULT_CULTIVARS[self._crop_name]
            warnings.warn(
                f"No cultivar was indicated, default cultivar {self._cultivar_code} will be used"
            )            

        # Read cultivar
        cul_file = self._spe_path[:-3] + 'CUL'
        with open(cul_file, 'r') as f:
            file_lines = f.readlines()
        file_lines = clean_comments(file_lines)
        self.cultivar = Section(
            name="cultivar", file_lines=file_lines, crop_name=self._crop_name,
            code=self._cultivar_code
        )
        self._cultivar_code = self.cultivar["@VAR#"]

        # Read ecotype if assigned
        eco_file = self._spe_path[:-3] + 'ECO'
        try:
            with open(eco_file, 'r') as f:
                file_lines = f.readlines()
            file_lines = clean_comments(file_lines)
            self.ecotype = Section(
                name="ecotype", file_lines=file_lines, crop_name=self._crop_name,
                code=self.cultivar["ECO#"]
            )
        except FileNotFoundError:
            pass

    def write(self, filepath:str=''):
        cultivar_str = self.cultivar.__dict__.get("_Section__versionLine", "")
        cultivar_str += f'*{self._crop_name.upper()} CULTIVAR COEFFICIENTS: {self._SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        with open(self._spe_path, "r") as f:
            species_str = f.read()
        
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self._SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self._SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        if hasattr(self, "ecotype"):
            ecotype_str = self.ecotype.__dict__.get("_Section__versionLine", "")
            ecotype_str += f'*{self._crop_name.upper()} ECOTYPE COEFFICIENTS: {self._SMODEL}{VERSION} MODEL\n' \
                + self.ecotype.write()
            with open(os.path.join(filepath, f'{self._SPE_FILE[:-3]}ECO'), 'w') as f:
                f.write(ecotype_str)

    def __repr__(self):
        repr_str = f"{self._crop_name} crop, {self.cultivar[CUL_VARNAME[self._CODE]]} cultivar"
        return repr_str
    
    @property
    def crop_name(self):
        return self._crop_name
    
    @property
    def cultivar_code(self):
        return self._cultivar_code