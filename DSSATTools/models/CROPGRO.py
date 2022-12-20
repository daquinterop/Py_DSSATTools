from DSSATTools.base.sections import Cultivar, Ecotype
from DSSATTools import VERSION
import os

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


class Species:
    '''
    Open the species file
    '''
    def __init__(self, spe_file:str):
        with open(spe_file) as f:
            self._file_lines = f.readlines()

    # TODO: Create a __repr__ method to print sections.
    # TODO: I have to work in the inclusion of the Species file

    def write(self):
        return ''.join(self._file_lines)


class Soybean:
    '''
    This class reunites the species, cultivar and ecotype parts of the crop.
    '''
    def __init__(self, spe_file:str=None):
        self.NAME = 'Soybean'
        self.CODE = 'SB'
        self.SMODEL = 'CRGRO'
        self.SPE_FILE = f'{self.CODE}{self.SMODEL[2:]}{VERSION}.SPE'
        if not spe_file:
            spe_file = self.SPE_FILE
        self.species = Species(spe_file)
        self.cultivar = Cultivar(spe_file, self.NAME)
        self.ecotype = Ecotype(spe_file, self.NAME)
    
    def write(self, filepath:str=''):
        cultivar_str = f'*{self.NAME.upper()} CULTIVAR COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        ecotype_str = f'*{self.NAME.upper()} ECOTYPE COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.ecotype.write()
        species_str = self.species.write()
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self.SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str)


class Canola:
    '''
    This class reunites the species, cultivar and ecotype parts of the crop.
    '''
    def __init__(self, spe_file:str=None):
        self.NAME = 'Canola'
        self.CODE = 'CN'
        self.SMODEL = 'CRGRO'
        self.SPE_FILE = f'{self.CODE}{self.SMODEL[2:]}{VERSION}.SPE'
        if not spe_file:
            spe_file = self.SPE_FILE
        self.species = Species(spe_file)
        self.cultivar = Cultivar(spe_file, self.NAME)
        self.ecotype = Ecotype(spe_file, self.NAME)
    
    def write(self, filepath:str=''):
        cultivar_str = f'*{self.NAME.upper()} CULTIVAR COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        ecotype_str = f'*{self.NAME.upper()} ECOTYPE COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.ecotype.write()
        species_str = self.species.write()
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self.SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str)


class Sunflower:
    '''
    This class reunites the species, cultivar and ecotype parts of the crop.
    '''
    def __init__(self, spe_file:str=None):
        self.NAME = 'Sunflower'
        self.CODE = 'SU'
        self.SMODEL = 'CRGRO'
        self.SPE_FILE = f'{self.CODE}{self.SMODEL[2:]}{VERSION}.SPE'
        if not spe_file:
            spe_file = self.SPE_FILE
        self.species = Species(spe_file)
        self.cultivar = Cultivar(spe_file, self.NAME)
        self.ecotype = Ecotype(spe_file, self.NAME)
    
    def write(self, filepath:str=''):
        cultivar_str = f'*{self.NAME.upper()} CULTIVAR COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        ecotype_str = f'*{self.NAME.upper()} ECOTYPE COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.ecotype.write()
        species_str = self.species.write()
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self.SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str)


class Tomato:
    '''
    This class reunites the species, cultivar and ecotype parts of the crop.
    '''
    def __init__(self, spe_file:str=None):
        self.NAME = 'Tomato'
        self.CODE = 'TM'
        self.SMODEL = 'CRGRO'
        self.SPE_FILE = f'{self.CODE}{self.SMODEL[2:]}{VERSION}.SPE'
        if not spe_file:
            spe_file = self.SPE_FILE
        self.species = Species(spe_file)
        self.cultivar = Cultivar(spe_file, self.NAME)
        self.ecotype = Ecotype(spe_file, self.NAME)
    
    def write(self, filepath:str=''):
        cultivar_str = f'*{self.NAME.upper()} CULTIVAR COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        ecotype_str = f'*{self.NAME.upper()} ECOTYPE COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.ecotype.write()
        species_str = self.species.write()
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self.SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str)


class Cabbage:
    '''
    This class reunites the species, cultivar and ecotype parts of the crop.
    '''
    def __init__(self, spe_file:str=None):
        self.NAME = 'Cabbage'
        self.CODE = 'CB'
        self.SMODEL = 'CRGRO'
        self.SPE_FILE = f'{self.CODE}{self.SMODEL[2:]}{VERSION}.SPE'
        if not spe_file:
            spe_file = self.SPE_FILE
        self.species = Species(spe_file)
        self.cultivar = Cultivar(spe_file, self.NAME)
        self.ecotype = Ecotype(spe_file, self.NAME)
    
    def write(self, filepath:str=''):
        cultivar_str = f'*{self.NAME.upper()} CULTIVAR COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.cultivar.write()
        ecotype_str = f'*{self.NAME.upper()} ECOTYPE COEFFICIENTS: {self.SMODEL}{VERSION} MODEL\n' \
            + self.ecotype.write()
        species_str = self.species.write()
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{self.SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{self.SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str)