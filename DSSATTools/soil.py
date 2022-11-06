"""
`soil` module includes the basic soil class `SoilProfile`. This class contains all the soil information necessary to run the DSSAT model. Each of the layers of the soil profile is a `SoilLayer` instance. After a `SoilProfile` instance is created, a new layer can added by calling the `SoilProfile.add_layer` method passing a `SoilLayer` object as argument. You can also use the `SoilProfile.drop_layer` to drop the layer at the specified depth.

`SoilLayer` class represents each layer in the soil profile. The layer is initialized by passing the layer base depth and a dict with the parameteters as argument. Clay fraction (SLCL) and Silt fraction (SLSI) are the only mandatory parameters when creating a layer, the rest of the parameters are estimated.

There are three basic ways of creating a `SoilProfile object`:
    1. Specify a .SOL file and Soil id. Of course, the soil id must match one of the profiles in the .SOL file.

        >>> soilprofile = SoilProfile(
            file='SOIL.SOL',
            profile='IBBN910030'
        )

    2. Passing a string code of one the available default soils.

        >>> soilprofile = SoilProfile(
            default_class='SCL', # Silty Clay Loam
        )

    3. Pasing a dict with the profile parameters (different from the layer pars). `DSSAT.soil.list_profile_parameters` function prints a detailed list of the layer parameters. And empty dict can be pased as none of the parameters is mandatory.

        >>> soilprofile = SoilProfile(
            pars={
                'SALB': 0.25, # Albedo
                'SLU1': 6, # Stage 1 Evaporation (mm)
                'SLPF': 0.8 # Soil fertility factor
            }
        )
        >>> layers = [
            soil.SoilLayer(20, {'SLCL': 50, 'SLSI': 45}),
            soil.SoilLayer(50, {'SLCL': 30, 'SLSI': 30}),
            soil.SoilLayer(100, {'SLCL': 30, 'SLSI': 35}),
            soil.SoilLayer(180, {'SLCL': 20, 'SLSI': 30})
        ]
        >>> for layer in layers: soilprofile.add_layer(layer)

That layer must be initialized with the texture information ('SLCL' and 'SLSI' parameters), or the hydraulic soil parameters ('SLLL', 'SDUL', 'SSAT', 'SRGF', 'SSKS', 'SBDM', 'SLOC'). If a soil hydraulic parameter is not defined, then it's estimated from soil texture using Pedo-transfer Functions. The previous parameters are the mandatory ones, but all the available parameters can be includedin the pars dict. 

If you want to save your soil profile in .SOL a file, you can use the `SoilProfile.write` method. The only argument of this method is the filename.

For both classes any of the parameters can be modified after the initialization as each parameter is also an attribute of the instance.

    >>> soilprofile = SoilProfile(
        pars={
            'SALB': 0.25, # Albedo
            'SLU1': 6, # Stage 1 Evaporation (mm)
            'SLPF': 0.8 # Soil fertility factor
        }
    >>> # Modify the albedo of the created instance
    >>> soilprofile.SALB = 0.36
"""

from re import L
from pandas import Series, NA, isna
import fortranformat as ff
import math
import os
import numpy as np

from DSSATTools.base.formater import (
    soil_line_read, soil_line_write, soil_location_write
)
from rosetta import rosetta, SoilData

FST_LVL_PARS = [
    'SLMH',  'SLLL',  'SDUL',  'SSAT',  'SRGF',  'SSKS',  'SBDM',  'SLOC',
    'SLCL',  'SLSI',  'SLCF',  'SLNI',  'SLHW',  'SLHB',  'SCEC',  'SADC'
]
SCD_LVL_PARS = [
    'SLPX',  'SLPT',  'SLPO', 'CACO3',  'SLAL',  'SLFE',  'SLMN',  'SLBS',
    'SLPA',  'SLPB',  'SLKE',  'SLMG',  'SLNA',  'SLSU',  'SLEC',  'SLCA'
]

LAYER_PARS = FST_LVL_PARS + SCD_LVL_PARS

DATA_FMT = {
    'layer_lvl_1_pars': ['I5', 'A5'] + 4*['F5.3'] + 3*['F5.2'] + 3*['F5.1'] +\
    ['F5.3'] + 4*['F5.1'],
    'layer_lvl_2_pars': ['I5', 'A5'] + 4*['F5.3'] + 3*['F5.2'] + 3*['F5.1'] +\
    ['F5.3'] + 4*['F5.1'],
    'profile_lvl_pars': ['A5'] + ['F5.2'] + ['F5.1'] + ['F5.2'] + ['F5.1'] +\
        2*['F5.2'] + 3*['A5'],
    'location': 2*['A12'] + 2*['F6.3'] + ['A24']
}

PARS_DESC = {
    'CACO3': 'CaCO3 content, g kg-1',
    'SABD':  'Bulk density, moist, g cm-3',
    'SABL':  'Depth, base of layer, cm',
    'SADC':  'Anion adsorption coefficient (reduced nitrate flow), cm3 (H2O) g [soil]-1',
    'SAHB':  'pH in buffer',
    'SAHW':  'pH in water',
    'SAKE':  'Potassium, exchangeable, cmol kg-1',
    'SALB':  'Albedo, fraction',
    'SANI':  'Total nitrogen, %',
    'SAPX':  'Phosphorus, extractable, mg kg-1',
    'SBDM':  'Bulk density, moist, g cm-3',
    'SCEC':  'Cation exchange capacity, cmol kg-1',
    'SCOM':  """ CIELab coordinates as a tuple (L, a, b) or any of the following strings:
        'BLK': Black (10YR 2/1)
        'YBR': Yellowish Brown (7.5YR 5/6)
        'RBR': Redish Brown (10R 4/8)
        'DBR': Dark Brown (2.5YR 3/4) 
        'GRE': Grey (10YR 6/1)
        'YLW': Yellow (10YR 7/8)
    """,
    'SDUL':  'Drained upper limit, cm3 cm-3',
    'SLAL':  'Aluminum',
    'SLB':   'Depth, base of layer, cm',
    'SLBS':  'Base saturation, cmol kg-1',
    'SLCA':  'Calcium, exchangeable, cmol kg-1',
    'SLCF':  'Coarse fraction (>2 mm), %',
    'SLCL':  'Clay (<0.002 mm), %',
    'SLDP':  'Soil depth, cm',
    'SLDR':  'Drainage rate, fraction day-1',
    'SLEC':  'Electric conductivity, seimen',
    'SLFE':  'Iron',
    'SLLL':  'Lower limit of plant extractable soil water, cm3 cm-3',
    'SLMG':  'Magnesium, cmol kg-1',
    'SLMH':  'Master horizon',
    'SLMN':  'Manganese',
    'SLNA':  'Sodium, cmol kg-1',
    'SLNF':  'Mineralization factor, 0 to 1 scale',
    'SLNI':  'Total nitrogen, %',
    'SLOC':  'Organic carbon, %',
    'SLPA':  'Phosphorus isotherm A, mmol kg-1',
    'SLPB':  'Phosphorus iostherm B, mmol l-1',
    'SLPF':  'Soil fertility factor, 0 to 1 scale [for soil factors not simulated by the model]',
    'SLPO':  'Phosphorus, organic, mg kg-1',
    'SLPT':  'Phosphorus, total, mg kg-1',
    'SLPX':  'Phosphorus, extractable, mg kg-1',
    'SLRO':  'Runoff curve no. [Soil Conservation Service/NRCS]',
    'SLSI':  'Silt (0.05 to 0.002 mm), %',
    'SLSU':  'Sulphur',
    'SLU1':  'Stage 1 evaporation limit, mm',
    'SMHB':  'pH in buffer determination method, code',
    'SMKE':  'Potassium determination method, code',
    'SMPX':  'Phosphorus determination code',
    'SRGF':  'Root growth factor, soil only, 0.0 to 1.0',
    'SSAT':  'Upper limit, saturated, cm3 cm-3',
    'SSKS':  'Sat. hydraulic conductivity, macropore, cm h-1'
    
}

MANDATORY_PARS = [
    'SLLL', 'SDUL', 'SSAT', 'SRGF', 'SSKS', 'SBDM', 'SLOC', 'SLCL', 'SLSI'
]

PROFILE_SECTIONS = [
    'location', 'profile_lvl_pars',
    'layer_lvl_1_pars', 'layer_lvl_2_pars'
]

SOIL_LAB = {
    'BLK': (20, 2, 6), 
    'YBR': (51, 17, 35),
    'RBR': (41, 34, 30),
    'DBR': (31, 17, 17),
    'GRE': (61, 2, 6),
    'YLW': (71, 14, 50)
}

DEFAULT_PROFILES_IDS = {
    'S': 'IB00000011',
    'LS': 'IBMZ910023',  
    'SL': 'IB00000008', 
    'L': 'IUBF970211', 
    'SIL': 'IB00000005', 
    'SI': 'IBWH980018', 
    'SCL': 'IBSB910009', 
    'CL': 'IBSB910009', 
    'SICL': 'CCPA000030', 
    'SC': 'IBPT910002', 
    'SIC': 'IB00000002', 
    'C': 'CCQU000033', 
}

def wrap_NA_types(inp):
    if isna(inp):
        return inp
    try:
        if np.isclose(float(inp), -99, atol=1):
            return NA
        else:
            return inp
    except ValueError:
        return inp

def list_layer_parameters():
    '''
    Print a list of the soil parameters
    '''
    for key, value in PARS_DESC.items():
        if key in LAYER_PARS:
            print(key + ': ' + value)

def list_profile_parameters():
    '''
    Print a list of the soil parameters
    '''
    for key, value in PARS_DESC.items():
        if key not in LAYER_PARS:
            print(key + ': ' + value)

def van_genuchten(theta_r, theta_s, alpha, n, h):
    '''
    Van Genuchten function for soil water retention. Returns theta for a given h (kPa)
    Arguments
    ----------
    theta_r: float
        residual water content
    theta_s: float
        saturated water content
    log10(alpha): float
        van Genuchten 'alpha' parameter (1/cm)
    log10(n): float
        van Genuchten 'n' parameter
    '''
    alpha = 10**alpha 
    n = 10**n
    m = 1 - 1/n 
    theta = theta_r + (theta_s - theta_r)/(1 + abs(alpha * h)**n)**m
    return theta

def color_to_oc(color=None, L=None, a=None, b=None):
    '''
    Estimate Organic Carbon from Color as described in Vodyanidskii and Savichev (2017).https://doi.org/10.1016/j.aasci.2017.05.023 
    
    Color definitions and their CIE-L*a*b* equivalents were obtained from Munsell tables. Color argument's possible values are:
        BLK: Black (10YR 2/1); 
        YBR: Yellowish Brown (7.5YR 5/6); 
        RBR: Redish Brown (10R 4/8); 
        DBR: Dark Brown (2.5YR 3/4); 
        GRE: Grey (10YR 6/1); 
        YLW: Yellow (10YR 7/8); 

    L, a and b values can be pased directly too.
    '''
    if any([i == None for i in [L, a, b]]):
        L, a, b = SOIL_LAB[color]
    return max(7.18 - 0.095*L - 0.164*a - 0.038*b, 0)
  

class SoilLayer(Series):
    '''
    Initialize a soil layer instance.

    Arguments
    ----------
    base_depth: int
        Depth to the bottom of that layer (cm)
    pars: dict
        Dict including the parameter values to initialize the instance. Layer parameters include: 'SLMH',  'SLLL',  'SDUL',  'SSAT',  'SRGF',  'SSKS',  'SBDM',  'SLOC', 'SLCL',  'SLSI',  'SLCF',  'SLNI',  'SLHW',  'SLHB',  'SCEC',  'SADC', 'SLPX',  'SLPT',  'SLPO', 'CACO3',  'SLAL',  'SLFE',  'SLMN',  'SLBS', 'SLPA',  'SLPB',  'SLKE',  'SLMG',  'SLNA',  'SLSU',  'SLEC',  'SLCA'.Only mandatory parameters are 'SLCL' and 'SLSI'. The rest of the basic parameters can be calculated from the texture. SCOM is optional, and it can be passed as an string referencing the color, or a tupple with CIELAB coordinates (L, a, b). The string can be one of these:

            BLK: Black (10YR 2/1); 
            YBR: Yellowish Brown (7.5YR 5/6); 
            RBR: Redish Brown (10R 4/8); 
            DBR: Dark Brown (2.5YR 3/4); 
            GRE: Grey (10YR 6/1); 
            YLW: Yellow (10YR 7/8)
    '''
    def __init__(self, base_depth:int, pars:dict):
        super().__init__(
            {
                key: NA
                for key in ['@  SLB'] + LAYER_PARS
            }
        )
        self.SCOM = pars.get('SCOM')
        self['@  SLB'] = base_depth

        TEXTURE_PARS = all([i in pars.keys() for i in MANDATORY_PARS[-2:]])
        HYDR_PARS = all([i in pars.keys() for i in MANDATORY_PARS[:-2]])

        assert any([TEXTURE_PARS, HYDR_PARS]), ( 
            "You must define at least 'SLCL' and 'SLSI' if soil hydraulic properties " + 
            "('SLLL', 'SDUL', 'SSAT', 'SRGF', 'SSKS', 'SBDM', 'SLOC') are not defined."
        )

        # Load the parameters in the new instance
        for par, value in pars.items():
            if par in LAYER_PARS:
                self[par] = value

        # Calculate missing parameters
        if not HYDR_PARS:
            self._estimate_missing()
            
    def _estimate_missing(self):
        # Soil Hydraulic parameters are estimated from van_genuchten equation's parameters.
        # Those parameters are estimated using Pedo-Transfer Funcitons (PTF). For this case
        # USDA rosetta model (Zhang et al., 2017) was used. doi: 10.1016/j.jhydrol.2017.01.004
        if isna(self.SBDM):
            soil_data = SoilData.from_array(
                [[100 - self.SLCL - self.SLSI, self.SLSI, self.SLCL]]
            )
            vangenuchten_pars, _, _ = rosetta(2, soil_data)
            # Calculate SBDM
        else:
            soil_data = SoilData.from_array(
                [[100 - self.SLCL - self.SLSI, self.SLSI, self.SLCL, self.SBDM]]
            )
            vangenuchten_pars, _, _ = rosetta(3, soil_data)

        vangenuchten_pars = vangenuchten_pars[0]
        if isna(self.SSAT): self.SSAT = vangenuchten_pars[1]
        if isna(self.SSKS): self.SSKS = (10**vangenuchten_pars[-1]) / 24
        if isna(self.SLLL): self.SLLL = van_genuchten(*vangenuchten_pars[:-1], h=1500)
        if isna(self.SDUL): self.SDUL = van_genuchten(*vangenuchten_pars[:-1], h=33)
        if isna(self.SCOM):
            self.SCOM = 'DBR'
        else:
            assert self.SCOM in SOIL_LAB.keys(), (
            'SCOM is optional, and it must be passed as an string referencing the color,'+
            'or a tupple with CIELAB coordinates (L, a, b). The string can be one of '+
            'these:\n' +
            '    BLK: Black (10YR 2/1)\n'+
            '    YBR: Yellowish Brown (7.5YR 5/6)\n'+
            '    RBR: Redish Brown (10R 4/8)\n'+
            '    DBR: Dark Brown (2.5YR 3/4)\n'+ 
            '    GRE: Grey (10YR 6/1)\n'+
            '    YLW: Yellow (10YR 7/8)\n'
            )                
        if isna(self.SBDM):
            # It estimates bulk density from other soil's parameters. If Organic Carbon (%) is
            # provided, Alexander (1980) method is used. If it's not, then Men et al. (2008)
            # method is used. References from https://doi.org/10.1016/S1002-0160(15)60049-2
            if isna(self.SLOC):
                self.SLOC = color_to_oc(self.SCOM)
                self.SBDM = 1.386 - 0.078*self.SLOC + 0.001*self.SLSI + 0.001*self.SLCL
            else:
                self.SBDM = 1.72 - 0.294*self.SLOC**0.5
        
        if isna(self.SLOC): self.SLOC = color_to_oc(self.SCOM)


class SoilProfile():
    '''
    Soil Profile class. It can be initialized from an existing file. It also can be initialized from scratch.  If a file is provided, then the soil is initialized as the soil profile with the matching profile id in the file.

    Arguments
    ----------
    file: str
        Optional. Path to the soil file.
    profile: str
        Optional. Must be passed if file argument is passed. It's the id of the profile within the file.
    pars: dict
        Dict with the non-layer soil parameters. 
    default_class: str
        Optional. It's a string defining a DSSAT default soil class. If not None, then the SoilClass instance is initialized with the paremeters of the specified default_class. default_class must match any of the next codes: Sand=S; Loamy Sand=LS; Sandy Loam=SL; Loam=L; Silty Loam=SIL; Silt=SI; Sandy Clay Loam=SCL; Clay Loam=CL; Silty Clay Loam=SICL; Sandy Clay=SC; Silty Clay=SIC; Clay=C.
    
    '''
    def __init__(
        self, file:str=None, profile:str=None, default_class:str=None,
        pars:dict={}
        ):
        self.n_layers = 0
        self.id = 'IB12345678'
        self.description = 'Soil profile'
        self.total_depth = 0
        self.site = 'Huntsville'
        self.country = 'AL-USA'
        self.lat = 34.7246
        self.lon = -86.6451
        self.csc_family = 'Custom'
        # Set default values
        self.SALB = .12 
        self.SLU1 = 6.
        self.SLNF = 1.
        self.SLPF = 1.
        self.SMHB = 'IB001'
        self.SMKE = 'IB001'
        self.SMPX = 'IB001'
        self.SCOM = NA
        self.SLDR = 0.5
        self.SLRO = 60

        self.layers = {}

        if file:
            self._file_initilized = True
            self._file_path = file
            self.id = profile
            self._open_file()
        elif default_class:
            assert default_class in DEFAULT_PROFILES_IDS.keys(), \
                f'{default_class} is not a valid default soil profile' 
            self._file_initilized = True
            from DSSATTools import __file__ as DSSATToolsPath
            self._file_path = os.path.join(
                os.path.dirname(DSSATToolsPath), 'static', 'Soil', 'SOIL.SOL'
            )
            self.id = DEFAULT_PROFILES_IDS[default_class]
            self._open_file()
        else:
            self._file_initilized = False
            for par, value in pars.items():
                assert self.__dict__.get(par, False), \
                    f'{par} is not a valid SoilProfile parameter'
                self.__dict__[par] = value

    def _calculate_SRGF(self):
        '''
        It has to be recalculated for all the layers after a layer is added or droped. The calculation method is specified in the DSSAT proceeding calulations
        '''
        for base_depth, lay in self.layers.items():
            for d in sorted(self.layers.keys(), reverse=True):
                if d < base_depth:
                    layer_depth = base_depth - d
                    break
                layer_depth = base_depth   
            layer_center = base_depth - 0.5*layer_depth
            if (layer_center > 20) and (self.n_layers > 1):
                lay.SRGF = math.exp(-0.02*layer_center)
            else:
                lay.SRGF = 1 
            

    def add_layer(self, layer: SoilLayer):
        '''
        Add a new layer to the Soil.
        
        Arguments
        ----------
        layer: DSSATTools.soil.SoilLayer
            Soil Layer object
        '''
        base_depth = layer['@  SLB']
        if base_depth in self.layers.keys():
            UserWarning(f'Layer at {base_depth} cm was overwriten')
        layer = layer.map(wrap_NA_types)
        self.layers[base_depth] = layer
        self.n_layers = len(self.layers)
        self.total_depth = max(self.layers.keys())
        # Calculate SRGF if missing
        if isna(layer.SRGF): self._calculate_SRGF()

    def drop_layer(self, layer: int):
        '''
        Drop the layer at the specified depth
        '''
        del self.layers[layer['@  SLB']]
        self._calculate_SRGF()
        return

    def set_parameter(self, parameter, value):
        '''
        Set the value of a soil parameter.

        Arguments
        ----------
        parameter: str
            Parameter name. You can use the DSSATTools.soil.list_parameters function to have a list of the parameters and their description.
        value: int, float, str
            Value for that parameter
        '''

    def write(self, filename:str='SOIL.SOL'):
        '''
        It's called by the DSSATTools.run.Dscsm.run() method to write the file.

        Arguments
        ----------
        filename: str
            Path to the file to write
        '''
        assert self.n_layers > 0, 'SoilProfile must have at least one layer'
        
        rep = '*SOILS: File created with DSSATTools\n\n'
        rep += self.__repr__()
        with open(filename, 'w') as f:
            f.write(rep)
        

    def _open_file(self):
        '''
        Open a file and loads the paramters of the requested profile into the instance attributes.
        '''
        HEADER = False
        FOUND_PROFILE = False
        with open(self._file_path, 'r') as f:
            for line in f:
                stiped_line = line.strip()
                if len(stiped_line) == 0: 
                    continue

                first_char = stiped_line[0]
                if first_char == '!':
                    continue
                elif first_char == '*':
                    if not HEADER:
                        HEADER = line
                        continue
                    else:
                        if FOUND_PROFILE:
                            return
                        profile_id = line[1:11]
                        if profile_id != self.id:
                            continue
                        self.description = line[11:].strip()
                        section_idx = -1
                        FOUND_PROFILE = True
                        self.layers = {}
                        continue
                elif not FOUND_PROFILE:
                    continue
                elif first_char == '@':
                    section_idx += 1
                    continue
                else:
                    pass

                if section_idx == 0:
                    reader = ff.FortranRecordReader(
                        '1X,A12,A12,1X,F8.3,1X,F8.3,A48'
                    )
                    self.site, self.country, self.lat, \
                        self.lon, self.csc_family = reader.read(line)
                elif section_idx == 1:
                    self.SCOM, self.SALB, self.SLU1, self.SLDR, self.SLRO,\
                        self.SLNF, self.SLPF, self.SMHB, self.SMKE, self.SMPX\
                            = soil_line_read(
                        line, DATA_FMT[PROFILE_SECTIONS[section_idx]]
                    )
                elif section_idx == 2:
                    pars = soil_line_read(
                        line, DATA_FMT[PROFILE_SECTIONS[section_idx]]
                    )
                    layer_depth = pars[0]
                    self.add_layer(
                        SoilLayer(
                            layer_depth,
                            dict(zip(FST_LVL_PARS, pars[1:]))
                        )
                    )
                else: 
                    # TODO: This only implements First level parameters so far so remember to implement
                    # nutrient balance parameters as well
                    pars = soil_line_read(
                        line, DATA_FMT[PROFILE_SECTIONS[section_idx]]
                    )
                    layer_depth = pars[0]
                    for par, value in zip(FST_LVL_PARS, pars[1:]):
                        self.layers[layer_depth][par] = value
        assert FOUND_PROFILE, f'{self.id} profile was not found at '+\
            f'{self._file_path}'
    
    def __repr__(self):
        '''
        repr of the class defined in the DSSAT profile format. 
        '''
        rep = f'*{self.id}  {self.description}\n'
        rep += '@SITE        COUNTRY          LAT     LONG SCS FAMILY\n'
        rep += soil_location_write(
            [self.site, self.country, self.lat, self.lon, self.csc_family]
        ) + '\n'
        rep += '@ SCOM  SALB  SLU1  SLDR  SLRO  SLNF  SLPF  SMHB  SMPX  SMKE\n'
        rep += soil_line_write(
            [self.SCOM, self.SALB, self.SLU1, self.SLDR, self.SLRO,
             self.SLNF, self.SLPF, self.SMHB, self.SMPX, self.SMKE],
            DATA_FMT['profile_lvl_pars']
        ) + '\n'
        rep += '@  SLB  SLMH  SLLL  SDUL  SSAT  SRGF  SSKS  SBDM  SLOC' +\
            '  SLCL  SLSI  SLCF  SLNI  SLHW  SLHB  SCEC  SADC\n'
        for depth, layer in self.layers.items():
            rep += soil_line_write(
                [depth] + list(layer[FST_LVL_PARS]),
                DATA_FMT['layer_lvl_1_pars']
            ) + '\n'
        return rep
    
'''
References
----------
Alexander E B. 1980. Bulk densities of California soils in relation to other soil properties. Soil Sci Soc Am J. 44: 689–692.

Men M X, Peng Z P, Xu H, Yu Z R. 2008. Investigation on Pedo-transfer function for estimating soil bulk density in Hebei province. Chinese J Soil Sci (in Chinese). 39: 33–37.

Vodyanitskii, Yu. N., & Savichev, A. T. (2017). The influence of organic matter on soil color using the regression equations of optical parameters in the system CIE- L*a*b*. In Annals of Agrarian Science (Vol. 15, Issue 3, pp. 380–385). Elsevier BV. https://doi.org/10.1016/j.aasci.2017.05.023 

Zhang, Y. and Schaap, M.G. 2017. Weighted recalibration of the Rosetta pedotransfer model with improved estimates of hydraulic parameter distributions and summary statistics (Rosetta3). Journal of Hydrology 547:39-53. doi: 10.1016/j.jhydrol.2017.01.004
'''