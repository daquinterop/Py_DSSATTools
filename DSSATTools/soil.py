"""
This module contains the classes and functions that handle the soil definition.
The soil profile object is created using the SoilProfile class. One way of 
doing that is just loading soil profile from an existing DSSAT Soil file. For
that, the from_file soil profile class function is used:
    >>> soil = SoilProfile.from_file("IBMZ910214", "SOIL.SOL")
The soil profile can also be created from scratch using the SoilProfile and 
SoilLayer classes similar to the layer-based sections of the FileX:
    >>> soil = SoilProfile(
    >>>     name='IBMZ910214', soil_series_name='Millhopper Fine Sand', 
    >>>     site='Gainesville', country='USA', lat=29.6, long=-82.37, 
    >>>     soil_data_source='Gainesville', soil_clasification='S',
    >>>     scs_family='Loamy,silic,hyperth Arnic Paleudult', scom='', salb=0.18, 
    >>>     slu1=2.0, sldr=0.65, slro=60.0, slnf=1.0, slpf=0.92, smhb='IB001',
    >>>     smpx='IB001', smke='IB001',
    >>>     table = [
    >>>         SoilLayer(
    >>>             slb=5.0, slmh='', slll=0.026, sdul=0.096, ssat=0.345, srgf=1.0, 
    >>>             ssks=7.4, sbdm=1.66, sloc=0.67, slcl=1.7, slsi=0.9, slcf=0.0, 
    >>>             slhw=7.0, scec=20.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=15.0, slmh='', slll=0.025, sdul=0.105, ssat=0.345, srgf=1.0, 
    >>>             ssks=7.4, sbdm=1.66, sloc=0.67, slcl=1.7, slsi=0.9, slcf=0.0, 
    >>>             slhw=7.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=30.0, slmh='', slll=0.075, sdul=0.12, ssat=0.345, srgf=0.7, 
    >>>             ssks=14.8, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
    >>>             slhw=7.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=45.0, slmh='', slll=0.025, sdul=0.086, ssat=0.345, srgf=0.3, 
    >>>             ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
    >>>             slhw=7.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=60.0, slmh='', slll=0.025, sdul=0.072, ssat=0.345, srgf=0.3, 
    >>>             ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
    >>>             slhw=7.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=90.0, slmh='', slll=0.028, sdul=0.072, ssat=0.345, srgf=0.1, 
    >>>             ssks=3.7, sbdm=1.66, sloc=0.17, slcl=2.4, slsi=2.6, slcf=0.0, 
    >>>             slhw=7.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=120.0, slmh='', slll=0.028, sdul=0.08, ssat=0.345, srgf=0.1, 
    >>>             ssks=0.1, sbdm=1.66, sloc=0.18, slcl=7.7, slsi=3.1, slcf=0.0, 
    >>>             slhw=7.0,
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=150.0, slmh='', slll=0.029, sdul=0.09, ssat=0.345, srgf=0.05, 
    >>>             ssks=0.1, sbdm=1.66, sloc=0.15, slcl=7.7, slsi=3.1, slcf=0.0, 
    >>>             slhw=7.0
    >>>         ),
    >>>         SoilLayer(
    >>>             slb=180.0, slmh='', slll=0.029, sdul=0.09, ssat=0.345, srgf=0.05, 
    >>>             ssks=0.1, sbdm=1.66, sloc=0.1, slcl=7.7, slsi=3.1, slcf=0.0, 
    >>>             slhw=7.0
    >>>         )
    >>>     ]
    >>> )

This module also contains some functions to estimate missing soil properties. The 
estimate_from_texture function estimates the soil hydro-dynamic properties based
on soil texture. The sloc_from_color estimates the soil organic carbon based on
the soil color.
"""

from .base.partypes import (
    NumberType, DescriptionType, Record, TabularRecord,
    CodeType, parse_pars_line, clean_comments
)
from . import __file__ as module_path
import os
from rosetta import rosetta, SoilData

DSSAT_MODULE_PATH = os.path.dirname(module_path)

SURF_PARS_1 = [
    "name", "soil_data_source", "soil_clasification", "soil_depth", 
    "soil_series_name"
]
SURF_PARS_2 = ['site', 'country', 'lat', 'long', 'scs_family']
SURF_PARS_3 = [
    'scom', 'salb', 'slu1', 'sldr', 'slro', 'slnf', 'slpf', 'smhb', 
    'smpx', 'smke'
]
PROF_PARS_1 = [
    'slb', 'slmh', 'slll', 'sdul', 'ssat', 'srgf', 'ssks', 'sbdm', 'sloc', 
    'slcl', 'slsi', 'slcf', 'slni', 'slhw', 'slhb', 'scec', 'sadc'
]
PROF_PARS_2 = [
    'slb', 'slpx', 'slpt', 'slpo', 'caco3', 'slal', 'slfe', 'slmn', 'slbs', 
    'slpa', 'slpb', 'slke', 'slmg', 'slna', 'slsu', 'slec', 'slca'
]

SOIL_LAB = {
    'BLK': (20, 2, 6), 
    'YBR': (51, 17, 35),
    'RBR': (41, 34, 30),
    'DBR': (31, 17, 17),
    'GRE': (61, 2, 6),
    'YLW': (71, 14, 50)
}

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

def sloc_from_color(L:float, a:float, b:float):
    '''
    Estimate Organic Carbon from Color as described in Vodyanidskii and Savichev 
    (2017).
    
    Color definitions and their CIE-L*a*b* equivalents were obtained from Munsell 
    tables. The Lab coordinates for some common colors are:
        Black: (20, 2, 6), 
        Yellowish Brown: (51, 17, 35),
        Redish Brown: (41, 34, 30),
        Dark Brown: (31, 17, 17),
        Grey: (61, 2, 6),
        Yellow: (71, 14, 50)
    '''
    return max(7.18 - 0.095*L - 0.164*a - 0.038*b, 0)

def estimate_from_texture(slcl, slsi, sbdm=None, sloc=None):
    """
    It estimates important soil parameters using soil texture, and soil organic
    carbon parameters.
    
    Soil Hydraulic parameters (ssat, ssks, ssll, ssdul) are estimated using the
    Van Genunchten equation. Van Genunchten parameters are estimated using the 
    USDA rosetta pedo-transfer model (Zhang et al., 2017).

    Bulk density is estimated using Alexander (1980) method if soil organic 
    carbon (sloc) is provided.
    """
    
    if sbdm:
        soil_data = SoilData.from_array(
            [[100 - slcl - slsi, slsi, slcl, sbdm]]
        )
        vangenuchten_pars, _, _ = rosetta(3, soil_data)
    else:
        soil_data = SoilData.from_array(
            [[100 - slcl - slsi, slsi, slcl]]
        )
        vangenuchten_pars, _, _ = rosetta(2, soil_data)
        
    vangenuchten_pars = vangenuchten_pars[0]
    ssat = vangenuchten_pars[1]
    ssks = (10**vangenuchten_pars[-1]) / 24
    slll = van_genuchten(*vangenuchten_pars[:-1], h=1500)
    sdul = van_genuchten(*vangenuchten_pars[:-1], h=33)
    if (not sbdm) and sloc:
        sbdm = 1.386 - 0.078*sloc + 0.001*slsi + 0.001*slcl
    return {"ssat": ssat, "ssks": ssks, "slll": slll, "sdul": sdul, "sbdm": sbdm}

class SoilLayer(Record):
    """
    Single soil layer
    """
    prefix = None
    dtypes = {
        'slb': NumberType, 'slmh': DescriptionType, 'slll': NumberType,
        'sdul': NumberType, 'ssat': NumberType, 'srgf': NumberType, 
        'ssks': NumberType, 'sbdm': NumberType, 'sloc': NumberType, 
        'slcl': NumberType, 'slsi': NumberType, 'slcf': NumberType, 
        'slni': NumberType, 'slhw': NumberType, 'slhb': NumberType, 
        'scec': NumberType, 'sadc': NumberType,

        'slpx': NumberType, 'slpt': NumberType, 'slpo': NumberType, 
        'caco3': NumberType, 'slal': NumberType, 'slfe': NumberType, 
        'slmn': NumberType, 'slbs': NumberType, 'slpa': NumberType, 
        'slpb': NumberType, 'slke': NumberType, 'slmg': NumberType, 
        'slna': NumberType, 'slsu': NumberType, 'slec': NumberType, 
        'slca': NumberType
    }
    pars_fmt = {
        'slb': '>5.0f', 'slmh': '<5', 'slll': '>5.3f', 'sdul': '>5.3f', 
        'ssat': '>5.3f', 'srgf': '>5.3f', 'ssks': '>5.2f', 'sbdm': '>5.2f', 
        'sloc': '>5.2f', 'slcl': '>5.1f', 'slsi': '>5.1f', 'slcf': '>5.1f', 
        'slni': '>5.3f', 'slhw': '>5.1f', 'slhb': '>5.1f', 'scec': '>5.1f', 
        'sadc': '>5.1f', 
        
        'slpx': '>5.1f', 'slpt': '>5.1f', 'slpo': '>5.1f', 'caco3': '>5.2f', 
        'slal': '>5.2f', 'slfe': '>5.2f', 'slmn': '>5.2f', 'slbs': '>5.2f', 
        'slpa': '>5.2f', 'slpb': '>5.2f', 'slke': '>5.2f', 'slmg': '>5.2f', 
        'slna': '>5.2f', 'slsu': '>5.2f', 'slec': '>5.2f', 'slca': '>5.2f'
    }
    n_tiers = 2
    table_index = "slb"
    def __init__(self, slb:float, slll:float, sdul:float, ssat:float, srgf:float, 
                 sbdm:float, sloc:float, ssks:float=None, slmh:str=None, 
                 slcl:float=None, slsi:float=None, slcf:float=None,
                 slni:float=None, slhw:float=None, slhb:float=None, 
                 scec:float=None, sadc:float=None, slpx:float=None, 
                 slpt:float=None, slpo:float=None, caco3:float=None,
                 slal:float=None, slfe:float=None, slmn:float=None,
                 slbs:float=None, slpa:float=None, slpb:float=None, 
                 slke:float=None, slmg:float=None, slna:float=None, 
                 slsu:float=None, slec:float=None, slca:float=None):
        """
        Initialize a SoilLayer instance.

        Arguments
        ----------
        slb: float
            Depth, base of layer, cm
        slmh: str
            Master horizon
        slll: float
            Lower limit of plant extractable soil water, cm3 cm-3
        sdul: float
            Drained upper limit, cm3 cm-3
        ssat: float
            Upper limit, saturated, cm3 cm-3
        srgf: float
            Root growth factor, soil only, 0.0 to 1.0
        ssks: float
            Sat. hydraulic conductivity, macropore, cm h-1
        sbdm: float
            Bulk density, moist, g cm-3
        sloc: float
            Organic carbon, %
        slcl: float
            Clay (<0.002 mm), %
        slsi: float
            Silt (0.05 to 0.002 mm), %
        slcf: float
            Coarse fraction (>2 mm), %
        slni: float
            Total nitrogen, %
        slhw: float
            pH in water
        slhb: float
            Albedo, fraction
        scec: float
            Cation exchange capacity, cmol kg-1
        sadc: float
            Anion adsorption coefficient (reduced nitrate flow), cm3 (H2O) g [soil]-1
        slpx: float
            Phosphorus, extractable, mg kg-1
        slpt: float
            Phosphorus, total, mg kg-1
        slpo: float
            Phosphorus, organic, mg kg-1
        caco3: float
            CaCO3 content, g kg-1'
        slal: float
            Aluminum, cmol kg-1
        slfe: float
            Iron, cmol kg-1
        slmn: float
            Manganese, cmol kg-1
        slbs: float
            Base saturation, cmol kg-1
        slpa: float
            Phosphorus isotherm A, mmol kg-1
        slpb: float
            Phosphorus iostherm B, mmol l-1
        slke: float
            Potassium, exchangeable, cmol kg-1
        slmg: float
            Magnesium, cmol kg-1
        slna: float
            Sodium, cmol kg-1
        slsu: float
            Sulphur, cmol kg-1
        slec: float
            Electric conductivity, seimen
        slca: float
            Calcium, exchangeable, cmol kg-1
        """
        super().__init__()
        kwargs = {
            'slb': slb, 'slmh': slmh, 'slll': slll, 'sdul': sdul, 
            'ssat': ssat, 'srgf': srgf, 'ssks': ssks, 'sbdm': sbdm, 
            'sloc': sloc, 'slcl': slcl, 'slsi': slsi, 'slcf': slcf, 
            'slni': slni, 'slhw': slhw, 'slhb': slhb, 'scec': scec, 
            'sadc': sadc, 
            
            'slpx': slpx, 'slpt': slpt, 'slpo': slpo, 'caco3': caco3, 
            'slal': slal, 'slfe': slfe, 'slmn': slmn, 'slbs': slbs, 
            'slpa': slpa, 'slpb': slpb, 'slke': slke, 'slmg': slmg, 
            'slna': slna, 'slsu': slsu, 'slec': slec, 'slca': slca
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)


class SoilProfile(TabularRecord):
    prefix = None
    dtypes = {
        'name': DescriptionType, 'soil_data_source': DescriptionType, 
        'soil_clasification': DescriptionType, 'soil_depth': NumberType, 
        'soil_series_name': DescriptionType, 'site': DescriptionType, 
        'country': DescriptionType, 'lat': NumberType, 'long': NumberType, 
        'scs_family': DescriptionType, 'scom': DescriptionType, 'salb': NumberType, 
        'slu1': NumberType, 'sldr': NumberType, 'slro': NumberType, 
        'slnf': NumberType, 'slpf': NumberType, 'smhb': CodeType, 
        'smpx': CodeType, 'smke': CodeType
    }
    pars_fmt = {
        'name': '<11', 'soil_data_source': "<11", 'soil_clasification': '<6', 
        'soil_depth': '>4.0f', 'soil_series_name': '<64', 'site': '<11', 
        'country': '<11', 'lat': '>8.3f', 'long': '>8.3f', 'scs_family': '<64', 
        'scom': '>5', 'salb': '>5.2f', 'slu1': '>5.1f', 'sldr': '>5.2f', 
        'slro': '>5.0f', 'slnf': '>5.2f', 'slpf': '>5.2f', 'smhb': '>5', 
        'smpx': '>5', 'smke': '>5'
    }
    table_dtype = SoilLayer
    code:str
    def __init__(self, table:list[SoilLayer], name:str, salb:float,slu1:float,
                 sldr:float, slro:float, slnf:float, slpf:float, 
                 soil_data_source:str=None, soil_clasification:str=None, 
                 soil_series_name:str=None, site:str=None, country:str=None, 
                 lat:float=None, long:float=None, scs_family:str=None, 
                 scom:float=None, smhb:str=None, smpx:str=None,smke:str=None):
        """
        Initialize a SoilProfile instance. It can be initialized from an existing
        soil profile, using the `from_file` method.

        Arguments
        ----------
        table: DataFrame or list[SoilLayer]
            The soil profile defined layer by layer.
        name: str
            Name of the soil profile. A 10 character code.
        soil_data_source: str
            Soil data source
        soil_clasification: str
            Soil texture clasification. One among C, CL, L, LS, S, SC, SCL, SI,
            SIC, SICL, SIL, SL.
        soil_series_name: str
            Name of the soil profile
        site: str
            Site
        country: str
            Country
        lat: float
            Latitude, decimal deg
        long: float
            Longitude, decimal deg
        scs_family: str
            SCS Soil family
        scom: str
            Soil color as two characters code: BN (brown), G (Grey), Y (Yellow),
            BL (Black), R (Red)
        salb: float
            Albedo, fraction
        slu1: float
            Stage 1 evaporation limit, mm
        sldr: float
            Drainage rate, fraction day-1
        slro: float
            Runoff curve no. (Soil Conservation Service/NRCS)
        slnf: float
            Mineralization factor, 0 to 1 scale
        slpf: float
            Soil fertility factor, 0 to 1 scale (for soil factors not simulated 
            by the model)
        smhb: str
            pH in buffer determination method, code
        smpx: str
            Phosphorus determination code
        smke: str
            Potassium determination method, code
        """
        super().__init__()
        kwargs = {
            'name': name, 'soil_data_source': soil_data_source, 
            'soil_clasification': soil_clasification, 'soil_depth': 0,
            'soil_series_name': soil_series_name, 'site': site, 
            'country': country, 'lat': lat, 'long': long, 'scs_family': scs_family, 
            'scom': scom, 'salb': salb, 'slu1': slu1, 'sldr': sldr, 'slro': slro, 
            'slnf': slnf, 'slpf': slpf, 'smhb': smhb, 'smpx': smpx, 'smke': smke
        }
        for name, value in kwargs.items():
            self.__setitem__(name, value)
        self.table = table
        self["soil_depth"] = self.table[-1]["slb"]

    def _write_section(self):
        raise NotImplementedError
    
    def _write_row(self):
        raise NotImplementedError

    def __setitem__(self, key, value):
        if key == "name":
            assert len(value) == 10, \
                "Soil profile Name must be 10 characters long"
        super().__setitem__(key, value)
    
    def _write_table(self):
        return
    
    def _write_sol(self):
        out_str = "*SOILS: General DSSAT Soil Input File\n\n"
        out_str += "*"+" ".join([
            self[name].str for name in SURF_PARS_1
            if name != "table"
        ])
        out_str += "\n@SITE        COUNTRY          LAT     LONG SCS FAMILY\n"
        out_str += " "+" ".join([
            self[name].str for name in SURF_PARS_2
            if name != "table"
        ])
        out_str += "\n@ SCOM  SALB  SLU1  SLDR  SLRO  SLNF  SLPF  SMHB  SMPX  SMKE\n"
        out_str += " "+" ".join([
            self[name].str for name in SURF_PARS_3
            if name != "table"
        ])
        out_str += "\n@  SLB  SLMH  SLLL  SDUL  SSAT  SRGF  SSKS  SBDM  SLOC  SLCL  SLSI  SLCF  SLNI  SLHW  SLHB  SCEC  SADC\n"
        for layer in self.table:
            out_str += " "+" ".join([
                layer[name].str for name in PROF_PARS_1
                if name != "table"
            ])
            out_str += "\n"
        out_str += "@  SLB  SLPX  SLPT  SLPO CACO3  SLAL  SLFE  SLMN  SLBS  SLPA  SLPB  SLKE  SLMG  SLNA  SLSU  SLEC  SLCA\n"
        for layer in self.table:
            out_str += " "+" ".join([
                layer[name].str for name in PROF_PARS_2
                if name != "table"
            ])
            out_str += "\n"
        return out_str
    
    @property
    def str(self):
        return self['name']

    @classmethod
    def from_file(cls, profile:str, file:str):
        """
        Returns the SoilProfile from a file. 
        """
        profile_lines = []
        with open(file, "r") as f:
            for line in f:
                if profile in line[:12]:
                    profile_lines.append(line)
                    continue
                if profile_lines and (not line.strip()):
                    break
                if line[0] == "!":
                    continue
                if profile_lines:
                    profile_lines.append(line)
            assert profile_lines, f"{profile} profile not in {file} file"

        # First row of parameters
        kwargs = parse_pars_line(
            profile_lines[0][1:], 
            {par: cls.pars_fmt[par] for par in SURF_PARS_1}
        )
        del kwargs["soil_depth"]
        # Second row of parameters
        kwargs = {**kwargs, **parse_pars_line(
            profile_lines[2][1:], 
            {par: cls.pars_fmt[par] for par in SURF_PARS_2}
        )}
        # Third row of parameters
        kwargs = {**kwargs, **parse_pars_line(
            profile_lines[4][1:], 
            {par: cls.pars_fmt[par] for par in SURF_PARS_3}
        )}
        # Soil profile values
        level_1_index = profile_lines.index(
            filter(lambda x: 'SLLL  SDUL  SSAT' in x, profile_lines).__next__()
        )
        try:
           level_2_index = profile_lines.index(
                filter(lambda x: '@  SLB  SLPX ' in x, profile_lines).__next__()
            )
        except StopIteration:
            level_2_index = len(profile_lines)
        level_1_pars = profile_lines[level_1_index:level_2_index]
        level_2_pars = profile_lines[level_2_index:]
        if not level_2_pars:
            level_2_pars = ["\n"] * len(level_1_pars)
        pars = [
            f"{l1.rstrip()}{l2[6:]}" 
            for l1, l2 in zip(level_1_pars, level_2_pars)
        ]
        table = []
        for line in pars[1:]:
            table.append(cls.table_dtype(
                **parse_pars_line(line[1:], cls.table_dtype.pars_fmt)
            ))
        
        kwargs['table'] = table
        return cls(**kwargs)

'''
References
----------
Alexander E B. 1980. Bulk densities of California soils in relation to other 
soil properties. Soil Sci Soc Am J. 44: 689–692.

Men M X, Peng Z P, Xu H, Yu Z R. 2008. Investigation on Pedo-transfer function 
for estimating soil bulk density in Hebei province. Chinese J Soil Sci (in 
Chinese). 39: 33–37.

Vodyanitskii, Yu. N., & Savichev, A. T. (2017). The influence of organic matter
on soil color using the regression equations of optical parameters in the system
CIE- L*a*b*. In Annals of Agrarian Science (Vol. 15, Issue 3, pp. 380–385).
Elsevier BV. https://doi.org/10.1016/j.aasci.2017.05.023 

Zhang, Y. and Schaap, M.G. 2017. Weighted recalibration of the Rosetta pedotransfer
model with improved estimates of hydraulic parameter distributions and summary
statistics (Rosetta3). Journal of Hydrology 547:39-53. doi: 10.1016/j.jhydrol.2017.01.004
'''
