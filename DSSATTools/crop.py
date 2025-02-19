'''

'''
import os
from . import VERSION
from .base.partypes import (
    CROPS_MODULES, NumberType, DescriptionType, Crop, Record
)
from . import __file__ as module_path

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
    "DryBean": f"CRGRO{VERSION}.SPE",
    "Cassava": f"CSYCA{VERSION}.SPE"
}

DSSAT_MODULE_PATH = os.path.dirname(module_path)
GENOTYPE_PATH = os.path.join(DSSAT_MODULE_PATH, 'static', 'Genotype')

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
    
class Sorghum(Crop):
    code = "SG"
    smodel = CROPS_MODULES["Sorghum"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        "var-name": DescriptionType, "expno": DescriptionType, "eco#": Record, 
        "p1": NumberType, "p2": NumberType, "p2o": NumberType, "p2r": NumberType, 
        "panth": NumberType, "p3": NumberType, "p4": NumberType, "p5": NumberType, 
        "phint": NumberType, "g1": NumberType, "g2": NumberType, "pbase": NumberType, 
        "psat": NumberType
    }
    cul_pars_fmt = {
        "var-name": ".<16", "expno": ">5", "eco#": ">6", "p1": ">5.1f", 
        "p2": ">5.1f", "p2o": ">5.2f", "p2r": ">5.1f", "panth": ">5.1f",
        "p3": ">5.1f", "p4": ">5.1f", "p5": ">5.1f", "phint": ">5.2f",
        "g1": ">5.1f", "g2": ">5.1f", "pbase": ">5.1f", "psat": ">5.1f"
    }
    eco_dtypes = {
        'econame': DescriptionType, 'tbase': NumberType, 'topt': NumberType, 
        'ropt': NumberType, 'gdde': NumberType, 'rue': NumberType, 
        'kcan': NumberType, 'stpc': NumberType, 'rtpc': NumberType, 
        'tilfc': NumberType, 'plam': NumberType
    }
    eco_pars_fmt = {
        'econame': '<16', 'tbase': '>6.1f', 'topt': '>5.1f', 'ropt': '>5.1f', 
        'gdde': '>5.1f', 'rue': '>5.1f', 'kcan': '>5.2f', 'stpc': '>5.3f', 
        'rtpc': '>5.3f', 'tilfc': '>5.1f', 'plam': '>5.0f'
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return

class Wheat(Crop):
    code = "WH"
    smodel = CROPS_MODULES["Wheat"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        'var-name': DescriptionType, 'exp#': DescriptionType, 'eco#': Record, 
        'p1v': NumberType, 'p1d': NumberType, 'p5': NumberType, 'g1': NumberType, 
        'g2': NumberType, 'g3': NumberType, 'phint': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'exp#': '>5', 'eco#': '>6', 'p1v': '>5.2f', 
        'p1d': '>5.2f', 'p5': '>5.1f', 'g1': '>5.2f', 'g2': '>5.2f', 
        'g3': '>5.3f', 'phint': '>5.1f'
    }
    eco_dtypes = {
        'p1': NumberType, 'p2fr1': NumberType, 'p2': NumberType, 
        'p3': NumberType, 'p4fr1': NumberType, 'p4fr2': NumberType, 
        'p4': NumberType, 'veff': NumberType, 'parue': NumberType,
        'paru2': NumberType, 'phl2': NumberType, 'phf3': NumberType,
        'la1s': NumberType, 'lafv': NumberType, 'lafr': NumberType,
        'slas': NumberType, 'lsphs': NumberType, 'lsphe': NumberType,
        'til#s': NumberType, 'tiphe': NumberType, 'tifac': NumberType,
        'tdphs': NumberType, 'tdphe': NumberType, 'tdfac': NumberType,
        'rdgs': NumberType, 'htstd': NumberType, 'awns': NumberType,
        'kcan': NumberType, 'rs%s': NumberType, 'gn%s': NumberType,
        'gn%mn': NumberType, 'tkfh': NumberType
    }
    eco_pars_fmt = {
        'p1': '>5.0f', 'p2fr1': '>5.2f', 'p2': '>5.0f', 'p3': '>5.0f', 
        'p4fr1': '>5.2f', 'p4fr2': '>5.2f', 'p4': '>5.0f', 'veff': '>5.2f', 
        'parue': '>5.2f', 'paru2': '>5.2f', 'phl2': '>5.1f', 'phf3': '>5.1f', 
        'la1s': '>5.1f', 'lafv': '>5.2f', 'lafr': '>5.2f', 'slas': '>5.0f', 
        'lsphs': '>5.1f', 'lsphe': '>5.1f', 'til#s': '>5.1f', 'tiphe': '>5.1f', 
        'tifac': '>5.1f', 'tdphs': '>5.1f', 'tdphe': '>5.1f', 'tdfac': '>5.1f', 
        'rdgs': '>5.1f', 'htstd': '>5.0f', 'awns': '>5.1f', 'kcan': '>5.2f', 
        'rs%s': '>5.0f', 'gn%s': '>5.1f', 'gn%mn': '>5.1f', 'tkfh': '>5.0f'
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return

class Tomato(Crop):
    code = "TM"
    smodel = CROPS_MODULES["Tomato"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        'vrname': DescriptionType, 'expno': DescriptionType, 
        'eco#': Record, 'csdl': NumberType, 'ppsen': NumberType, 
        'em-fl': NumberType, 'fl-sh': NumberType, 'fl-sd': NumberType, 
        'sd-pm': NumberType, 'fl-lf': NumberType, 'lfmax': NumberType, 
        'slavr': NumberType, 'sizlf': NumberType, 'xfrt': NumberType, 
        'wtpsd': NumberType, 'sfdur': NumberType, 'sdpdv': NumberType, 
        'podur': NumberType, 'thrsh': NumberType, 'sdpro': NumberType, 
        'sdlip': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.2f', 'em-fl': '>5.1f', 'fl-sh': '>5.1f', 'fl-sd': '>5.1f',
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.2f', 'slavr': '>5.0f',
        'sizlf': '>5.1f', 'xfrt': '>5.2f', 'wtpsd': '>5.3f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.1f', 'podur': '>5.1f', 'thrsh': '>5.1f', 'sdpro': '>5.3f',
        'sdlip': '>5.3f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'mg': DescriptionType, 'tm': DescriptionType, 
        'thvar': NumberType, 'pl-em': NumberType, 'em-v1': NumberType, 
        'v1-ju': NumberType, 'ju-r0': NumberType, 'pm06': NumberType, 
        'pm09': NumberType, 'lngsh': NumberType, 'r7-r8': NumberType, 
        'fl-vs': NumberType, 'trifl': NumberType, 'rwdth': NumberType, 
        'rhght': NumberType, 'r1ppo': NumberType, 'optbi': NumberType, 
        'slobi': NumberType, 'xmage': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'mg': '<2', 'tm': '<2', 'thvar': '>5.1f', 
        'pl-em': '>5.1f', 'em-v1': '>5.1f', 'v1-ju': '>5.1f', 'ju-r0': '>5.1f', 
        'pm06': '>5.2f', 'pm09': '>5.2f', 'lngsh': '>5.1f', 'r7-r8': '>5.1f', 
        'fl-vs': '>5.2f', 'trifl': '>5.2f', 'rwdth': '>5.1f', 'rhght': '>5.1f',
        'r1ppo': '>5.3f', 'optbi': '>5.1f', 'slobi': '>5.3f', 'xmage': '>5.1f'
    }
    
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return

class Soybean(Crop):
    code = "SB"
    smodel = CROPS_MODULES["Soybean"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        'var-name': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'csdl': NumberType, 'ppsen': NumberType, 'em-fl': NumberType, 
        'fl-sh': NumberType, 'fl-sd': NumberType, 'sd-pm': NumberType, 
        'fl-lf': NumberType, 'lfmax': NumberType, 'slavr': NumberType,
        'sizlf': NumberType, 'xfrt': NumberType, 'wtpsd': NumberType, 
        'sfdur': NumberType, 'sdpdv': NumberType, 'podur': NumberType, 
        'thrsh': NumberType, 'sdpro': NumberType, 'sdlip': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.3f', 'em-fl': '>5.2f', 'fl-sh': '>5.2f', 'fl-sd': '>5.2f',
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.3f', 'slavr': '>5.0f', 
        'sizlf': '>5.1f', 'xfrt': '>5.2f', 'wtpsd': '>5.2f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.2f', 'podur': '>5.2f', 'thrsh': '>5.1f', 'sdpro': '>5.3f', 
        'sdlip': '>5.3f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'mg': DescriptionType, 'tm': DescriptionType, 
        'thvar': NumberType, 'pl-em': NumberType, 'em-v1': NumberType, 
        'v1-ju': NumberType, 'ju-r0': NumberType, 'pm06': NumberType, 
        'pm09': NumberType, 'lngsh': NumberType, 'r7-r8': NumberType, 
        'fl-vs': NumberType, 'trifl': NumberType, 'rwdth': NumberType, 
        'rhght': NumberType, 'r1ppo': NumberType, 'optbi': NumberType, 
        'slobi': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'mg': '>2', 'tm': '>2', 'thvar': '>5.1f', 
        'pl-em': '>5.1f', 'em-v1': '>5.1f', 'v1-ju': '>5.1f', 'ju-r0': '>5.1f', 
        'pm06': '>5.1f', 'pm09': '>5.1f', 'lngsh': '>5.1f', 'r7-r8': '>5.1f', 
        'fl-vs': '>5.2f', 'trifl': '>5.2f', 'rwdth': '>5.2f', 'rhght': '>5.2f', 
        'r1ppo': '>5.3f', 'optbi': '>5.1f', 'slobi': '>5.3f'
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Alfalfa(Crop):
    code = "AL"
    smodel = CROPS_MODULES["Alfalfa"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class DryBean(Crop):
    code = "BN"
    smodel = CROPS_MODULES["DryBean"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Millet(Crop):
    code = "ML"
    smodel = CROPS_MODULES["Millet"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Sugarbeet(Crop):
    code = "BS"
    smodel = CROPS_MODULES["Sugarbeet"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Rice(Crop):
    code = "RI"
    smodel = CROPS_MODULES["Rice"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Sweetcorn(Crop):
    code = "SW"
    smodel = CROPS_MODULES["Sweetcorn"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Bermudagrass(Crop):
    code = "BM"
    smodel = CROPS_MODULES["Bermudagrass"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Canola(Crop):
    code = "CN"
    smodel = CROPS_MODULES["Canola"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Sunflower(Crop):
    code = "SU"
    smodel = CROPS_MODULES["Sunflower"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Potato(Crop):
    code = "PT"
    smodel = CROPS_MODULES["Potato"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Cabbage(Crop):
    code = "CB"
    smodel = CROPS_MODULES["Cabbage"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Sugarcane(Crop):
    code = "SC"
    smodel = CROPS_MODULES["Sugarcane"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class Cassava(Crop):
    code = "CS"
    smodel = CROPS_MODULES["Cassava"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
    }
    cul_pars_fmt = {
    }
    eco_dtypes = {
    }
    eco_pars_fmt = {
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return