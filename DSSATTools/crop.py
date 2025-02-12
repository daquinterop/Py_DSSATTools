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

from DSSATTools import VERSION
from DSSATTools.base.partypes import (
    CROPS_MODULES, NumberType, DescriptionType, Crop, Record
)
from DSSATTools import __file__ as module_path
import warnings
import re

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
    "Wheat": f"WHCER{VERSION}.SPE",
    "Bean": f"CRGRO{VERSION}.SPE",
    "Cassava": f"CSYCA{VERSION}.SPE"
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
    "Wheat": "WH",
    "Bean": "BN",
    "Cassava": "CS"
}


DSSAT_MODULE_PATH = os.path.dirname(module_path)
GENOTYPE_PATH = os.path.join(DSSAT_MODULE_PATH, 'static', 'Genotype')

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
    "WH": "VAR-NAME........",
    'BN': 'VRNAME..........',
    'CS': 'VAR-NAME........'
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


class Maize(Crop):
    code = "MZ"
    smodel = CROPS_MODULES["Maize"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        "vrname": DescriptionType, "expno": DescriptionType, 
        "eco#": Record, "p1": NumberType, "p2": NumberType, 
        "p5": NumberType, "g2": NumberType, "g3": NumberType, 
        "phint": NumberType
    }
    cul_pars_fmt = {
        "vrname": ".<16", "expno": ">5", "eco#": ">6", "p1": ">5.1f", 
        "p2": ">5.3f", "p5": ">5.3f", "g2": ">5.1f", "g3": ">5.2f", 
        "phint": ">5.2f"
    }
    eco_dtypes = {
        'econame': DescriptionType, 'tbase': NumberType, 'topt': NumberType, 
        'ropt': NumberType, 'p20': NumberType, 'djti': NumberType, 
        'gdde': NumberType, 'dsgft': NumberType, 'rue': NumberType, 
        'kcan': NumberType, 'tsen': NumberType, 'cday': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<16', 'tbase': '>6.1f', 'topt': '>5.1f', 
        'ropt': '>4.1f', 'p20': '>5.1f', 'djti': '>5.1f', 'gdde': '>5.1f', 
        'dsgft': '>6.1f', 'rue': '>4.1f', 'kcan': '>6.2f', 'tsen': '>5.1f', 
        'cday': '>5.1f'
    }

    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
