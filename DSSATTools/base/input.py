'''
Basic crop class. It initializes a crop instances based on the crop name and
crop file if provided.
'''
import os

from DSSATTools.models import (
    CERESMaize
)
from DSSATTools import __file__ as DSSATModulePath

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
        

        print()
        # TODO: A method to modify any given parameter. This has to be done!!!
