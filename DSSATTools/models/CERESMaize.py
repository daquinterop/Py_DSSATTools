'''

'''
from DSSATTools.base.CERES import Species
from DSSATTools.base.sections import Cultivar, Ecotype
import os
# from DSSATTools.base.input import Crop

CROP = 'Maize'
SPE_FILE = 'MZCER048.SPE'

class CropBase:
    '''
    gonorrea
    '''
    def __init__(self, spe_file:str):
        self.NAME = CROP
        self.species = Species(spe_file)
        self.cultivar = Cultivar(spe_file, self.NAME)
        self.ecotype = Ecotype(spe_file, self.NAME)
    
    def write(self, filepath:str=''):
        cultivar_str = '*MAIZE CULTIVAR COEFFICIENTS: MZCER048 MODEL\n' \
            + self.cultivar.write()
        ecotype_str = '*MAIZE ECOTYPE COEFFICIENTS: MZCER048 MODEL\n' \
            + self.ecotype.write()
        species_str = self.species.write()
        if filepath:
            if not os.path.exists(filepath): os.mkdir(filepath)
        with open(os.path.join(filepath, f'{SPE_FILE}'), 'w') as f:
            f.write(species_str)
        with open(os.path.join(filepath, f'{SPE_FILE[:-3]}CUL'), 'w') as f:
            f.write(cultivar_str)
        with open(os.path.join(filepath, f'{SPE_FILE[:-3]}ECO'), 'w') as f:
            f.write(ecotype_str) 
