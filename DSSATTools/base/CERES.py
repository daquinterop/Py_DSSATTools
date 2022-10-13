'''
Basic classes for Sepecies file.
'''

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

