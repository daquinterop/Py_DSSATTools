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

    # TODO: Implement some attribute to allocate sections.
    # TODO: Create a __repr__ method to print sections.

    def write(self):
        return ''.join(self._file_lines)

