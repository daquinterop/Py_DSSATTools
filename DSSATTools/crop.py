'''
This module hosts the classes that represent each crop. Not all crops are 
implemented. Each crop class is child of a generic Crop class. A crop is 
instantiated by passing the cultivar code:
    >>> crop = Sorghum('IB0026')
This will create a dictionary-like object with keys as the cultivar parameters' 
names. Then, the cultivar parameters can be modified
by assigning values:
    >>> crop['p1'] = 450.
    >>> crop['g1'] = 0.1
The ecotype parameter is itself a dictionary-like object with the ecotype 
parameters' names as keys. Then, the ecotype parameters are modified in the same 
way as the cultivar parameters:
    >>> crop['eco#']['topt'] = 35.5
The cultivar_list class function will return a list of all the cultivars availble
for a crop:
    >>> available_cultivars = Sorghum.cultivar_list()
'''
import os
from . import VERSION
from .base.partypes import (
    CROPS_MODULES, NumberType, DescriptionType, Crop, Record
)
from . import __file__ as module_path

SPE_FILES = {
    'Maize': f'MZCER{VERSION}.SPE',
    'PearlMillet': f'MLCER{VERSION}.SPE',
    'Sugarbeet': f'BSCER{VERSION}.SPE',
    'Rice': f'RICER{VERSION}.SPE',
    'Sorghum': f'SGCER{VERSION}.SPE',
    'SweetCorn': f'SWCER{VERSION}.SPE',
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
GENOTYPE_PATH = os.path.join(
    DSSAT_MODULE_PATH, 'dssat-csm-os', 'Data', 'Genotype'
)

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
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'csdl': NumberType, 'ppsen': NumberType, 'em-fl': NumberType, 
        'fl-sh': NumberType, 'fl-sd': NumberType, 'sd-pm': NumberType, 
        'fl-lf': NumberType, 'lfmax': NumberType, 'slavr': NumberType, 
        'sizlf': NumberType, 'xfrt': NumberType, 'wtpsd': NumberType, 
        'sfdur': NumberType, 'sdpdv': NumberType, 'podur': NumberType, 
        'thrsh': NumberType, 'sdpro': NumberType, 'sdlip': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.3f', 'em-fl': '>5.1f', 'fl-sh': '>5.1f', 'fl-sd': '>5.1f', 
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.2f', 'slavr': '>5.1f', 
        'sizlf': '>5.2f', 'xfrt': '>5.2f', 'wtpsd': '>5.3f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.2f', 'podur': '>5.1f', 'thrsh': '>5.1f', 'sdpro': '>5.3f', 
        'sdlip': '>5.3f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'mg': DescriptionType, 'tm': DescriptionType, 
        'thvar': NumberType, 'pl-em': NumberType, 'em-v1': NumberType, 
        'v1-ju': NumberType, 'ju-r0': NumberType, 'pm06': NumberType, 
        'pm09': NumberType, 'lngsh': NumberType, 'r7-r8': NumberType, 
        'fl-vs': NumberType, 'trifl': NumberType, 'rwdth': NumberType, 
        'rhght': NumberType, 'r1ppo': NumberType, 'optbi': NumberType, 
        'slobi': NumberType, 'rdrmt': NumberType, 'rdrmg': NumberType, 
        'rdrmm': NumberType, 'rchdp': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'mg': '>2', 'tm': '>2', 'thvar': '>5.2f', 
        'pl-em': '>5.2f', 'em-v1': '>5.2f', 'v1-ju': '>5.2f', 'ju-r0': '>5.0f', 
        'pm06': '>5.2f', 'pm09': '>5.2f', 'lngsh': '>5.2f', 'r7-r8': '>5.2f', 
        'fl-vs': '>5.2f', 'trifl': '>5.2f', 'rwdth': '>5.2f', 'rhght': '>5.2f', 
        'r1ppo': '>5.3f', 'optbi': '>5.2f', 'slobi': '>5.3f', 'rdrmt': '>5.3f', 
        'rdrmg': '>5.3f', 'rdrmm': '>5.3f', 'rchdp': '>5.3f'
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
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'csdl': NumberType, 'ppsen': NumberType, 'em-fl': NumberType, 
        'fl-sh': NumberType, 'fl-sd': NumberType, 'sd-pm': NumberType, 
        'fl-lf': NumberType, 'lfmax': NumberType, 'slavr': NumberType, 
        'sizlf': NumberType, 'xfrt': NumberType, 'wtpsd': NumberType, 
        'sfdur': NumberType, 'sdpdv': NumberType, 'podur': NumberType, 
        'thrsh': NumberType, 'sdpro': NumberType, 'sdlip': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.3f', 'em-fl': '>5.1f', 'fl-sh': '>5.2f', 'fl-sd': '>5.2f', 
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.2f', 'slavr': '>5.0f', 
        'sizlf': '>5.1f', 'xfrt': '>5.2f', 'wtpsd': '>5.3f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.2f', 'podur': '>5.1f', 'thrsh': '>5.1f', 'sdpro': '>5.3f', 
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
        'econame': '.<17', 'mg': '>2', 'tm': '>2', 'thvar': ">5.2f", 
        'pl-em': ">5.2f", 'em-v1': ">5.2f", 'v1-ju': ">5.2f", 'ju-r0': ">5.2f", 
        'pm06': ">5.2f", 'pm09': ">5.2f", 'lngsh': ">5.2f", 'r7-r8': ">5.2f", 
        'fl-vs': ">5.2f", 'trifl': ">5.2f", 'rwdth': ">5.2f", 'rhght': ">5.2f", 
        'r1ppo': ">5.3f", 'optbi': ">5.2f", 'slobi': ">5.3f"
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
        'var-name': DescriptionType, 'expno': DescriptionType, 
        'eco#': DescriptionType, 'p1': NumberType, 'p2r': NumberType, 
        'p5': NumberType, 'p2o': NumberType, 'g1': NumberType, 'g2': NumberType, 
        'g3': NumberType, 'phint': NumberType, 'thot': NumberType, 
        'tcldp': NumberType, 'tcldf': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'expno': '>5', 'eco#': '>6', 'p1': '>5.1f', 
        'p2r': '>5.1f', 'p5': '>5.1f', 'p2o': '>5.1f', 'g1': '>5.1f', 
        'g2': '>5.3f', 'g3': '>5.2f', 'phint': '>5.2f', 'thot': '>5.1f', 
        'tcldp': '>5.1f', 'tcldf': '>5.1f'
    }
    eco_dtypes = None
    eco_pars_fmt = None
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return

class PearlMillet(Crop):
    code = "ML"
    smodel = CROPS_MODULES["PearlMillet"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        'var-name': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'p1': NumberType, 'p2o': NumberType, 'p2r': NumberType, 'p5': NumberType, 
        'g1': NumberType, 'g4': NumberType, 'phint': NumberType, 'gt': NumberType, 
        'g5': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'expno': '>5', 'eco#': '>6', 'p1': '>5.1f', 
        'p2o': '>5.2f', 'p2r': '>5.1f', 'p5': '>5.1f', 'g1': '>5.3f', 
        'g4': '>5.2f', 'phint': '>5.3f', 'gt': '>5.2f', 'g5': '>5.2f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'tbase': NumberType, 'topt': NumberType, 
        'ropt': NumberType, 'djti': NumberType, 'gdde': NumberType, 
        'rue': NumberType, 'kcan': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'tbase': '>5.1f', 'topt': '>5.1f', 'ropt': '>5.1f', 
        'djti': '>5.1f', 'gdde': '>5.1f', 'rue': '>5.1f', 'kcan': '>5.2f'
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
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'p1': NumberType, 'p2': NumberType, 'p5': NumberType, 'g2': NumberType, 
        'g3': NumberType, 'phint': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'p1': '>5.1f', 
        'p2': '>5.3f', 'p5': '>5.1f', 'g2': '>5.1f', 'g3': '>5.1f', 
        'phint': '>5.2f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'tbase': NumberType, 'topt': NumberType, 
        'ropt': NumberType, 'p20': NumberType, 'djti': NumberType, 
        'gdde': NumberType, 'dsgft': NumberType, 'rue': NumberType, 
        'kcan': NumberType, 'tsen': NumberType, 'cday': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'tbase': '>5.1f', 'topt': '>4.1f', 'ropt': '>5.1f', 
        'p20': '>5.1f', 'djti': '>5.1f', 'gdde': '>5.1f', 'dsgft': '>5.1f', 
        'rue': '>5.1f', 'kcan': '>6.2f', 'tsen': '>5.1f', 'cday': '>5.1f'
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return
    
class SweetCorn(Crop):
    code = "SW"
    smodel = CROPS_MODULES["SweetCorn"]
    spe_file = f'{code}{smodel[2:]}{VERSION}.SPE'
    spe_path = os.path.join(GENOTYPE_PATH, spe_file)
    cul_dtypes = {
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'p1': NumberType, 'p2': NumberType, 'p5': NumberType, 'g2': NumberType, 
        'g3': NumberType, 'phint': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'p1': '>5.1f', 
        'p2': '>5.3f', 'p5': '>5.1f', 'g2': '>5.1f', 'g3': '>5.2f', 
        'phint': '>5.2f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'tbase': NumberType, 'topt': NumberType, 
        'ropt': NumberType, 'p20': NumberType, 'djti': NumberType, 
        'gdde': NumberType, 'dsgft': NumberType, 'rue': NumberType, 
        'kcan': NumberType, 'tsen': NumberType, 'cday': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'tbase': '>5.1f', 'topt': '>5.1f', 'ropt': '>5.1f', 
        'p20': '>5.1f', 'djti': '>5.1f', 'gdde': '>5.1f', 'dsgft': '>5.1f', 
        'rue': '>5.1f', 'kcan': '>5.2f', 'tsen': '>5.1f', 'cday': '>5.1f'
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
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'csdl': NumberType, 'ppsen': NumberType, 'em-fl': NumberType, 
        'fl-sh': NumberType, 'fl-sd': NumberType, 'sd-pm': NumberType, 
        'fl-lf': NumberType, 'lfmax': NumberType, 'slavr': NumberType, 
        'sizlf': NumberType, 'xfrt': NumberType, 'wtpsd': NumberType, 
        'sfdur': NumberType, 'sdpdv': NumberType, 'podur': NumberType, 
        'thrsh': NumberType, 'sdpro': NumberType, 'sdlip': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.3f', 'em-fl': '>5.1f', 'fl-sh': '>5.1f', 'fl-sd': '>5.1f', 
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.2f', 'slavr': '>5.1f', 
        'sizlf': '>5.2f', 'xfrt': '>5.2f', 'wtpsd': '>5.2f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.2f', 'podur': '>5.1f', 'thrsh': '>5.1f', 'sdpro': '>5.3f', 
        'sdlip': '>5.3f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'mg': DescriptionType, 'tm': DescriptionType, 
        'thvar': NumberType, 'pl-em': NumberType, 'em-v1': NumberType, 
        'v1-ju': NumberType, 'ju-r0': NumberType, 'pm06': NumberType, 
        'pm09': NumberType, 'lngsh': NumberType, 'r7-r8': NumberType, 
        'fl-vs': NumberType, 'trifl': NumberType, 'rwdth': NumberType, 
        'rhght': NumberType, 'r1ppo': NumberType, 'optbi': NumberType, 
        'slobi': NumberType, 'rdrmt': NumberType, 'rdrmg': NumberType, 
        'rdrmm': NumberType, 'rchdp': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'mg': '<2', 'tm': '<2', 'thvar': '>5.2f', 
        'pl-em': '>5.2f', 'em-v1': '>5.2f', 'v1-ju': '>5.2f', 'ju-r0': '>5.0f', 
        'pm06': '>5.2f', 'pm09': '>5.2f', 'lngsh': '>5.1f', 'r7-r8': '>5.0f', 
        'fl-vs': '>5.0f', 'trifl': '>5.2f', 'rwdth': '>5.2f', 'rhght': '>5.2f', 
        'r1ppo': '>5.3f', 'optbi': '>5.2f', 'slobi': '>5.3f', 'rdrmt': '>5.3f', 
        'rdrmg': '>5.3f', 'rdrmm': '>5.3f', 'rchdp': '>5.2f'
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
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'csdl': NumberType, 'ppsen': NumberType, 'em-fl': NumberType, 
        'fl-sh': NumberType, 'fl-sd': NumberType, 'sd-pm': NumberType, 
        'fl-lf': NumberType, 'lfmax': NumberType, 'slavr': NumberType, 
        'sizlf': NumberType, 'xfrt': NumberType, 'wtpsd': NumberType, 
        'sfdur': NumberType, 'sdpdv': NumberType, 'podur': NumberType, 
        'thrsh': NumberType, 'sdpro': NumberType, 'sdlip': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.3f', 'em-fl': '>5.1f', 'fl-sh': '>5.1f', 'fl-sd': '>5.1f', 
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.3f', 'slavr': '>5.1f', 
        'sizlf': '>5.1f', 'xfrt': '>5.2f', 'wtpsd': '>5.3f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.1f', 'podur': '>5.1f', 'thrsh': '>5.2f', 'sdpro': '>5.3f', 
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
        'econame': '.<17', 'mg': '<2', 'tm': '<2', 'thvar': '>5.1f', 
        'pl-em': '>5.1f', 'em-v1': '>5.1f', 'v1-ju': '>5.1f', 'ju-r0': '>5.1f', 
        'pm06': '>5.1f', 'pm09': '>5.2f', 'lngsh': '>5.1f', 'r7-r8': '>5.1f', 
        'fl-vs': '>5.2f', 'trifl': '>5.2f', 'rwdth': '>5.1f', 'rhght': '>5.1f', 
        'r1ppo': '>5.3f', 'optbi': '>5.1f', 'slobi': '>5.3f'
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
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.2f', 'slavr': '>5.1f', 
        'sizlf': '>5.1f', 'xfrt': '>5.2f', 'wtpsd': '>5.2f', 'sfdur': '>5.1f', 
        'sdpdv': '>5.2f', 'podur': '>5.1f', 'thrsh': '>5.1f', 'sdpro': '>5.3f', 
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
        'econame': '.<17', 'mg': '>2', 'tm': '>2', 'thvar': '>5.2f', 
        'pl-em': '>5.2f', 'em-v1': '>5.2f', 'v1-ju': '>5.2f', 'ju-r0': '>5.2f', 
        'pm06': '>5.2f', 'pm09': '>5.2f', 'lngsh': '>5.2f', 'r7-r8': '>5.2f', 
        'fl-vs': '>5.2f', 'trifl': '>5.2f', 'rwdth': '>5.2f', 'rhght': '>5.2f', 
        'r1ppo': '>5.3f', 'optbi': '>5.3f', 'slobi': '>5.3f'
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
        'var-name': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'g2': NumberType, 'g3': NumberType, 'pd': NumberType, 'p2': NumberType, 
        'tc': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'expno': '>5', 'eco#': '>6', 'g2': '>5.1f', 
        'g3': '>5.2f', 'pd': '>5.3f', 'p2': '>5.3f', 'tc': '>5.2f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'rue1': NumberType, 'rue2': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'rue1': '>5.2f', 'rue2': '>5.2f'
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
        'vrname': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'csdl': NumberType, 'ppsen': NumberType, 'em-fl': NumberType, 
        'fl-sh': NumberType, 'fl-sd': NumberType, 'sd-pm': NumberType, 
        'fl-lf': NumberType, 'lfmax': NumberType, 'slavr': NumberType, 
        'sizlf': NumberType, 'xfrt': NumberType, 'wtpsd': NumberType, 
        'sfdur': NumberType, 'sdpdv': NumberType, 'podur': NumberType, 
        'thrsh': NumberType, 'sdpro': NumberType, 'sdlip': NumberType
    }
    cul_pars_fmt = {
        'vrname': '.<16', 'expno': '>5', 'eco#': '>6', 'csdl': '>5.2f', 
        'ppsen': '>5.3f', 'em-fl': '>5.2f', 'fl-sh': '>5.2f', 'fl-sd': '>5.2f', 
        'sd-pm': '>5.2f', 'fl-lf': '>5.2f', 'lfmax': '>5.3f', 'slavr': '>5.1f', 
        'sizlf': '>5.1f', 'xfrt': '>5.3f', 'wtpsd': '>5.2f', 'sfdur': '>5.2f', 
        'sdpdv': '>5.2f', 'podur': '>5.1f', 'thrsh': '>5.2f', 'sdpro': '>5.3f', 
        'sdlip': '>5.3f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'mg': DescriptionType, 'tm': DescriptionType, 
        'pp-ss': NumberType, 'pl-em': NumberType, 'em-v1': NumberType, 
        'v1-ju': NumberType, 'ju-r0': NumberType, 'pm06': NumberType, 
        'pm09': NumberType, 'lnhsh': NumberType, 'r7-r8': NumberType, 
        'fl-vs': NumberType, 'trifl': NumberType, 'rwdth': NumberType, 
        'rhght': NumberType, 'r1ppo': NumberType, 'optbi': NumberType, 
        'slobi': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'mg': '>2', 'tm': '>2', 'pp-ss': '>5.2f', 
        'pl-em': '>5.2f', 'em-v1': '>5.2f', 'v1-ju': '>5.2f', 'ju-r0': '>5.2f', 
        'pm06': '>5.2f', 'pm09': '>5.2f', 'lnhsh': '>5.1f', 'r7-r8': '>5.2f', 
        'fl-vs': '>5.2f', 'trifl': '>5.2f', 'rwdth': '>5.2f', 'rhght': '>5.2f', 
        'r1ppo': '>5.3f', 'optbi': '>5.1f', 'slobi': '>5.3f'
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
        'var-name': DescriptionType, 'expno': DescriptionType, 'eco#': Record, 
        'maxparce': NumberType, 'apfmx': NumberType, 'stkpfmax': NumberType, 
        'suca': NumberType, 'tbft': NumberType, 'lfmax': NumberType, 
        'mxlfarea': NumberType, 'mxlfarno': NumberType, 'pi1': NumberType, 
        'pi2': NumberType, 'pswitch': NumberType, 'ttplntem': NumberType, 
        'ttratnem': NumberType, 'chupibase': NumberType, 'tt_popgrowth': NumberType,
        'poptt16': NumberType, 'tar0': NumberType, 'tdelay': NumberType, 
        'ler0': NumberType, 'ser0': NumberType, 'lg_ambase': NumberType, 
        'aqp_up5': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'expno': '>5', 'eco#': '>6', 'maxparce': '>14.4f', 
        'apfmx': '>14.4f', 'stkpfmax': '>14.4f', 'suca': '>14.4f', 'tbft': '>14.4f',
        'lfmax': '>14.4f', 'mxlfarea': '>14.4f', 'mxlfarno': '>14.4f', 
        'pi1': '>14.4f', 'pi2': '>14.4f', 'pswitch': '>14.4f', 'ttplntem': '>14.4f', 
        'ttratnem': '>14.4f', 'chupibase': '>14.4f', 'tt_popgrowth': '>14.4f', 
        'poptt16': '>14.4f', 'tar0': '>14.4f', 'tdelay': '>14.4f', 'ler0': '>14.4f', 
        'ser0': '>14.4f', 'lg_ambase': '>14.4f', 'aqp_up5': '>14.4f'
    }
    eco_dtypes = {
        'eco-name': DescriptionType, 'delttmax': NumberType, 'swdf2amp': NumberType, 
        'extcfn': NumberType, 'extcfst': NumberType, 'lfnmxext': NumberType, 
        'areamx_cf(2)': NumberType, 'areamx_cf(3)': NumberType, 'widcor': NumberType,
        'wmax_cf(1)': NumberType, 'wmax_cf(2)': NumberType, 'wmax_cf(3)': NumberType, 
        'popdecay': NumberType, 'ttbaseem': NumberType, 'ttbaselfex': NumberType, 
        'lg_amrange': NumberType, 'lg_gp_reduc': NumberType, 
        'ldg_fi_reduc': NumberType, 'lmax_cf(1)': NumberType, 
        'lmax_cf(2)': NumberType, 'lmax_cf(3)': NumberType, 'maxlflength': NumberType, 
        'maxlfwidth': NumberType, 'tbase_ge_em': NumberType, 'topt_ge_em': NumberType, 
        'tfin_ge_em': NumberType, 'tbase_lfem': NumberType, 'topt_lfem': NumberType, 
        'tfin_lfem': NumberType, 'tbase_tlrem': NumberType, 'topt_tlrem': NumberType, 
        'tfin_tlrem': NumberType, 'tbase_lfsen': NumberType, 'topt_lfsen': NumberType, 
        'tfin_lfsen': NumberType, 'tbase_stkex': NumberType, 'topt_stkex': NumberType,
        'tfin_stkex': NumberType, 'tbase_lfex': NumberType, 'topt_lfex': NumberType, 
        'tfin_lfex': NumberType, 'tbase_rex': NumberType, 'topt_rex': NumberType, 
        'tfin_rex': NumberType, 'topt_phot': NumberType, 'topt_pho2': NumberType, 
        'tfin_phot': NumberType, 'tbase_resp': NumberType, 'topt_resp': NumberType, 
        'tfin_resp': NumberType
    }
    eco_pars_fmt = {
        'eco-name': '.<18', 'delttmax': '>14.4f', 'swdf2amp': '>14.4f', 
        'extcfn': '>14.4f', 'extcfst': '>14.4f', 'lfnmxext': '>14.4f', 
        'areamx_cf(2)': '>14.4f', 'areamx_cf(3)': '>14.4f', 'widcor': '>14.4f', 
        'wmax_cf(1)': '>14.4f', 'wmax_cf(2)': '>14.4f', 'wmax_cf(3)': '>14.4f', 
        'popdecay': '>14.4f', 'ttbaseem': '>14.4f', 'ttbaselfex': '>14.4f', 
        'lg_amrange': '>14.4f', 'lg_gp_reduc': '>14.4f', 'ldg_fi_reduc': '>14.4f', 
        'lmax_cf(1)': '>14.4f', 'lmax_cf(2)': '>14.4f', 'lmax_cf(3)': '>14.4f', 
        'maxlflength': '>14.4f', 'maxlfwidth': '>14.4f', 'tbase_ge_em': '>14.4f', 
        'topt_ge_em': '>13.4f', 'tfin_ge_em': '>15.4f', 'tbase_lfem': '>14.4f', 
        'topt_lfem': '>14.4f', 'tfin_lfem': '>14.4f', 'tbase_tlrem': '>14.4f', 
        'topt_tlrem': '>14.4f', 'tfin_tlrem': '>14.4f', 'tbase_lfsen': '>14.4f', 
        'topt_lfsen': '>14.4f', 'tfin_lfsen': '>14.4f', 'tbase_stkex': '>14.4f', 
        'topt_stkex': '>14.4f', 'tfin_stkex': '>14.4f', 'tbase_lfex': '>14.4f', 
        'topt_lfex': '>14.4f', 'tfin_lfex': '>14.4f', 'tbase_rex': '>14.4f', 
        'topt_rex': '>14.4f', 'tfin_rex': '>14.4f', 'topt_phot': '>14.4f', 
        'topt_pho2': '>14.4f', 'tfin_phot': '>14.4f', 'tbase_resp': '>14.4f', 
        'topt_resp': '>14.4f', 'tfin_resp': '>14.4f'
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
        'var-name': DescriptionType, 'exp#': DescriptionType, 'eco#': Record, 
        'b01nd': NumberType, 'b12nd': NumberType, 'b23nd': NumberType, 
        'b34nd': NumberType, 'br1fx': NumberType, 'br2fx': NumberType, 
        'br3fx': NumberType, 'br4fx': NumberType, 'laxs': NumberType, 
        'slas': NumberType, 'llifa': NumberType, 'lpefr': NumberType, 
        'lnslp': NumberType, 'nodwt': NumberType, 'nodlt': NumberType
    }
    cul_pars_fmt = {
        'var-name': '.<16', 'exp#': '>5', 'eco#': '>6', 'b01nd': '>5.1f', 
        'b12nd': '>5.1f', 'b23nd': '>5.1f', 'b34nd': '>5.1f', 'br1fx': '>5.2f', 
        'br2fx': '>5.2f', 'br3fx': '>5.2f', 'br4fx': '>5.2f', 'laxs': '>5.0f', 
        'slas': '>5.0f', 'llifa': '>5.0f', 'lpefr': '>5.2f', 'lnslp': '>5.2f', 
        'nodwt': '>5.2f', 'nodlt': '>5.2f'
    }
    eco_dtypes = {
        'econame': DescriptionType, 'parue': NumberType, 'tblsz': NumberType, 
        'srn%s': NumberType, 'kcan': NumberType, 'pgerm': NumberType, 
        'pps1': NumberType, 'pps2': NumberType, 'pps3': NumberType, 
        'phtv': NumberType, 'phsv': NumberType, 'rdgs': NumberType, 
        'rlwr': NumberType, 'wfsu': NumberType, 'rsuse': NumberType, 
        'hmpc': NumberType
    }
    eco_pars_fmt = {
        'econame': '.<17', 'parue': '>5.2f', 'tblsz': '>5.1f', 'srn%s': '>5.2f', 
        'kcan': '>5.2f', 'pgerm': '>5.0f', 'pps1': '>5.2f', 'pps2': '>5.2f', 
        'pps3': '>5.2f', 'phtv': '>5.2f', 'phsv': '>5.2f', 'rdgs': '>5.2f', 
        'rlwr': '>5.0f', 'wfsu': '>5.2f', 'rsuse': '>5.2f', 'hmpc': '>5.0f'
    }
    def __init__(self, cultivar_code):
        super().__init__(cultivar_code)
        return