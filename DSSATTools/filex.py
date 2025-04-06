"""
This module implement the sections of the DSSAT FileX as python objects. All 
sections are implemented, excepting the enviromental modifications section. 
Environmental modifications can be easily implemented by modifying the Weather
component of each experiment. One section object represents a single factor
level in the experiment.

Each section is defined using the same parameter names (lowercase) of the DSSAT 
FileX. For example, planting date is defined as follow:  
    >>> planting = Planting(
    >>>     pdate=date(1980, 6, 17), ppop=18, ppoe=18,
    >>>     plme='S', plds='R', plrs=45, plrd=0, pldp=5
    >>> )

Sections that include a schedule or soil profile (i.e. Initial conditions), are 
defined as a list of individual events or soil layers. For example, a fertilizer
section with two fertilizer events is defined as follows:
    >>> fertilizer = Fertilizer(table=[
    >>>     FertilizerEvent(
    >>>         fdate=date(1980, 7, 4), fmcd='FE005', fdep=5,
    >>>         famn=80, facd='AP002'
    >>>     ),
    >>>     FertilizerEvent(
    >>>         fdate=date(1980, 8, 7), fmcd='FE005', fdep=5,
    >>>         famn=80, facd='AP002'
    >>>     )
    >>> ])
Other sections based on events are irrigation, residue, chemical, and tillage.

Note that the Fertilizer object is initialized by passing a list of FertilizerEvent
objects in the 'table' parameter. The table parameter also accepts DataFrames, 
only if the column names of that DataFrame match the parameters for the individual
event or layer object. Next is an example of this for the initial conditions section:
    >>> initial_conditions = InitialConditions(
    >>>        pcr='SG', icdat=date(1980, 6, 1), icrt=500, icnd=0,
    >>>        icrn=1, icre=1, icres=1300, icren=.5, icrep=0, icrip=100, icrid=10,
    >>>        table=pd.DataFrame([
    >>>            (10, .06, 2.5, 1.8),
    >>>            (22, .06, 2.5, 1.8),
    >>>            (52, .195, 3., 4.5),
    >>>            (82, .21, 3.5, 5.0),
    >>>            (112, 0.2, 2., 2.0),
    >>>            (142, 0.2, 1., 0.7),
    >>>            (172, 0.2, 1., 0.6),
    >>>        ], columns=['icbl', 'sh2o', 'snh4', 'sno3'])
    >>>    )
Note that InitialConditions have more parameters besides the table parameter. The 
column names of the passed DataFrame are the same as the parameters for the 
InitialConditionsLayer class. The soil analysis section is the other section based
on soil layers.

The field and cultivar sections are the only sections that need other DSSATTools 
objects as input parameters. In this section, the 'wsta' must be a WeatherStation 
object, and the 'id_soil' must be a SoilProfile object.
    >>> field = Field(
    >>>        id_field='ITHY0001', wsta=weather_station, flob=0, fldt='DR000', 
    >>>        fldd=0, flds=0, id_soil=soil
    >>>     )
'wsta' and 'id_soil' also receives weather station and soil profile ids as strings.
However, this wouldn't make sense in the context of running DSSAT using this package.

The cultivar can be defined either using the Cultivar class, or by directly using the
one of the classes defined in DSSATTools.crop. 
    >>> cultivar = Sorghum('IB0026')
    >>> cultivar = Cultivar(cr='SG', ingeno='IB0026', cname='CSH-1')
These two definitions will yield the same result. However, when the cultivar is 
defined using the crop class it is posible to modify the cultivar and ecotype 
coefficients. More information is found at the DSSATTools.crop module documentation.
    
Finally, the simulations controls is created by using the SimulationsControls
class. Each sub-section of the simulation controls sections is created using its
own class. Next example shows how to create the simulations controls defining only
the general options.
    >>> simulation_controls = SimulationControls(
    >>>     general=SCGeneral(sdate=date(1980, 6, 1))
    >>> )

The sections can be created from an existing FileX using the read_filex function.
That function will return a dictionary, mapping each treatment to its correspondent
section definitions. The next example reads an existing FileX, and then assigns
the first treatment to the treatment variable. In this case, treatment is a 
dictionary mapping each section name to its python object. 
    >>> treatments = read_filex("Maize/BRPI0202.MZX")
    >>> treatment = treatments[1]

The create_filex function returns the string of the FileX for for the passed 
sections defined as their python objects. 
"""
from datetime import date
from .base.partypes import (
    DateType, CodeType, NumberType, Record, TabularRecord, DescriptionType,
    FACTOR_LEVELS, clean_comments, parse_pars_line
)
from .crop import (
    Maize, Wheat, Sorghum, PearlMillet, Sugarbeet, Rice, Alfalfa, Bermudagrass,
    Soybean, Canola, Sunflower, Potato, Tomato, Cabbage, Sugarcane, DryBean,
    Cassava, SweetCorn
)
from .weather import WeatherStation
from .soil import SoilProfile
from .base.utils import detect_encoding

CROP_OBJECTS = {
    "MZ": Maize, 'WH': Wheat, 'SG': Sorghum, 'ML': PearlMillet, 'BS': Sugarbeet,
    'RI': Rice, 'SW': SweetCorn, 'AL': Alfalfa, 'BM': Bermudagrass, 
    'SB': Soybean, 'CN': Canola, 'SU': Sunflower, 'PT': Potato, 'TM': Tomato,
    'CB': Cabbage, 'SC': Sugarcane, 'BN': DryBean, 'CS': Cassava
}

class Planting(Record):
    '''
    Class to define a single planting event
    '''
    prefix = "p"
    dtypes = {
        "pdate": DateType, "edate": DateType, "ppop": NumberType, 
        "ppoe": NumberType, "plme": CodeType, "plds": CodeType, 
        "plrs": NumberType, "plrd": NumberType, "pldp": NumberType, 
        "plwt": NumberType, "page": NumberType, "penv": NumberType, 
        "plph": NumberType, "sprl": NumberType, "plname": DescriptionType
    }
    pars_fmt = {
        "pdate": "%y%j", "edate": "%y%j", "ppop": ">5.1f", "ppoe": ">5.1f", 
        "plme": ">5", "plds": ">5", "plrs": ">5.0f", "plrd": ">5.0f", 
        "pldp": ">5.1f", "plwt": ">5.1f", "page": ">5.0f", "penv": ">5.1f", 
        "plph": ">5.0f", "sprl": ">5.0f", "plname": ">29"
    }
    # Typehints must be in order following DSSAT column order
    def __init__(self, pdate:date, ppop:float, plrs:float, 
                 ppoe:float=None, plds:str="R", plrd:float=0, plme:str="S", 
                 pldp:float=5, plwt:float=None, page:float=None, penv:float=None, 
                 plph:float=None, sprl:float=0, edate:date=None, plname:str=None):
        """
        Initializes a Planting instance.

        Arguments
        ----------
        pdate: datetime
            Planting date
        edate: datetime
            Emergence day
        ppop: float
            Plant population at seeding, m-2
        plrs: float
            Row spacing, cm
        plds: str
            Planting distribution, row R, broadcast B, hill H
        ppoe: float
            Plant population at emergence, m-2. Equal to ppop if not set.
        plrd: float
            Row direction, degrees from N
        plme: str
            Planting method, code
        pldp: float
            Planting depth, cm
        plwt: float
            Planting material dry weight, kg ha-1
        page: float
            Transplant age, days
        penv: float
            Transplant environment, oC
        plph: float
            Plants per hill 
        sprl: float
            Initial sprout lenght, cm
        plname: str
            Planting treatment name, description
        """
        super().__init__()
        kwargs = {
            "pdate": pdate, "edate": edate, "ppop": ppop, "ppoe": ppoe, 
            "plme": plme, "plds": plds, "plrs": plrs, "plrd": plrd, "pldp": pldp,
            "plwt": plwt, "page": page, "penv": penv, "plph": plph, "sprl": sprl, 
            "plname": plname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)


class Cultivar(Record):
    prefix = "c"
    dtypes = {
        "cr": CodeType, "ingeno": DescriptionType, "cname": DescriptionType
    }
    pars_fmt = {
        "cr": ">2", "ingeno": ">6", "cname": "<16"
    }
    def __init__(self, cr:str, ingeno:str, cname:str=None):
        """
        Initializes a Cultivar instance.

        Arguments
        ----------
        cr: str
            Crop, code
        ingeno: str
            Cultivar, code
        cname: str
            Cultivar name, description
        """
        super().__init__()
        kwargs = {
            'cr': cr, 'ingeno': ingeno, 'cname': cname, 
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        # The crop attribute stores the Crop object
        self.__crop = CROP_OBJECTS[cr.upper()](ingeno)
    
    @property
    def crop(self):
        """
        Returns the Crop object asociated to this Cultivar instance.
        """
        return self.__crop


class Harvest(Record):
    prefix = "h"
    dtypes = {
        "hdate": DateType, "hstg": CodeType, "hcom": CodeType,
        "hsize": CodeType, "hpc": NumberType, "hbpc": NumberType, 
        "hname": DescriptionType
    }
    pars_fmt = {
        "hdate": "%y%j", "hstg": ">5", "hcom": ">5", "hsize": ">5", 
        "hpc": ">5.1f", "hbpc": ">5.1f", "hname": "<25"
    }
    def __init__(self, hdate:date, hstg:str=None, hcom:str=None, hsize:str=None,
                hpc:float=None, hbpc:float=None, hname:str=None):
        """
        Initializes a Harvest instance.

        Arguments
        ----------
        hdate: datetime
            Harvest date
        hstg: str 
            Specified growth stage for harvesting, code
        hcom: str
            Harvest component, code: C (Canopy), L (Leaves), or H (Harvest 
            product)
        hsize: str
            Harvest size category code : A (All), S (Small - less than 1/3 full 
            size), M (Medium - from 1/3 to 2/3 full size), L (Large - greater 
            than 2/3 full size)
        hpc: float
            Harvest percentage, %
        hbpc: float
            Byproduct takeoff, %. This is especially applicable when, in 
            addition to the grains, the straw is also harvested
        """
        super().__init__()
        kwargs = {
            "hdate": hdate, "hstg": hstg, "hcom": hcom, "hsize": hsize, 
            "hpc": hpc, "hbpc": hbpc, "hname": hname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)


class InitialConditionsLayer(Record):
    prefix = "c"
    dtypes = {
        "icbl": NumberType, "sh2o": NumberType, "snh4": NumberType, 
        "sno3": NumberType
    }
    pars_fmt = {
        "icbl": ">5.0f", "sh2o": ">5.3f", "snh4": ">5.1f", "sno3": ">5.1f"
    }
    table_index = "icbl" # Index when buliding table
    def __init__(self, icbl:float, sh2o:float, snh4:float=None, 
                 sno3:float=None):
        """
        Initializes a initial conditions for soil layer instance.

        Arguments
        ----------
        icbl: float
            Depth of base layer, cm
        sh2o: float
            Volumetric water content, cm3 cm-3
        snh4: float
            Ammonioum (NH4), g[N] Mg-1[Soil]
        sno3: float
            Nitrate (NO3), g[N] Mg-1[Soil]
        """
        super().__init__()
        kwargs = {"icbl": icbl, "sh2o": sh2o, "snh4": snh4, "sno3": sno3}
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        return

class InitialConditions(TabularRecord):
    prefix = "c"
    dtypes = {
        "pcr": CodeType, "icdat": DateType, "icrt": NumberType, 
        "icnd": NumberType, "icrn": NumberType, "icre": NumberType,
        "icwd": NumberType, "icres": NumberType, "icren": NumberType,
        "icrep": NumberType, "icrip": NumberType, "icrid": NumberType,
        "icname": DescriptionType
    }
    pars_fmt = {
        "pcr": ">5", "icdat": "%y%j", "icrt": ">5.0f", "icnd": ">5.0f", 
        "icrn": ">5.0f", "icre": ">5.0f", "icwd": ">5.0f", "icres": ">5.0f", 
        "icren": ">5.2f", "icrep": ">5.0f", "icrip": ">5.0f", "icrid": ">5.0f",
        "icname": "<25"
    }
    table_dtype = InitialConditionsLayer
    def __init__(self, pcr:str, icdat:date=None, icrt:float=None, 
                 icnd:float=None, icrn:float=None, icre:float=None, 
                 icwd:float=None, icres:float=None, icren:float=None,
                 icrep:float=None, icrip:float=None, icrid:float=None,
                 icname:str=None, table:list[InitialConditionsLayer]=None):
        """
        Initializes a Initial conditions instance.

        Arguments
        ----------
        pcr: str
            Previous crop, code
        icdat: date
            Initial conditions measurement date
        icrt: float
            Root weight, kg/ha
        icnd: float
            Nodule weight, kg/ha
        icrn: float
            Rhizobia number, (0-1)
        icre: float
            Rhizobia effectivity, (0-1)
        icwd: float
            Water table depth, cm
        icres: float
            Crop residue, kg/ha
        icren: float
            Residue N, %
        icrep: float
            Residue P, %
        icrip: float
            Residue incorporation, %
        icrid: float
            Residue incorporation depth, cm
        icname: str
            Initial conditions name, description
        table: list of InitialConditionsLayer
            List of initial conditions defined for the soil layer
        """
        super().__init__()
        kwargs = {
            "pcr": pcr, "icdat": icdat, "icrt": icrt, "icnd": icnd, 
            "icrn": icrn, "icre": icre, "icwd": icwd, "icres": icres, 
            "icren": icren, "icrep": icrep, "icrip": icrip, "icrid": icrid,
            "icname": icname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        self.table = table
        return


class FertilizerEvent(Record):
    prefix = "f"
    dtypes = {
        "fdate": DateType, "fmcd": CodeType, "facd": CodeType, 
        "fdep": NumberType, "famn": NumberType, "famp": NumberType,
        "famk": NumberType, "famc": NumberType, "famo": NumberType,
        "focd": CodeType, "fername": DescriptionType
    }
    pars_fmt = {
        "fdate": "%y%j", "fmcd": ">5", "facd": ">5", "fdep": ">5.0f", 
        "famn": ">5.1f", "famp": ">5.1f", "famk": ">5.1f", "famc": ">5.1f",
        "famo": ">5.1f", "focd": ">5", "fername": "<16"
    }
    table_index = None
    def __init__(self, fdate:date, fmcd:str, facd:str, fdep:float, famn:float, 
                 famp:float=None, famk:float=None, famc:float=None, famo:float=None,
                 focd:str=None, fername:str=None):
        """
        Initializes a fertilizer application event.

        Arguments
        ----------
        fdate: date
            Fertilizer application date
        fcmd: str
            Fertilizer material, code
        facd: str
            Fertilizer application method, code
        fdep: float
            application depth, cm
        famn: float
            N amount, kg ha-1
        famp: float
            P amount, kg ha-1
        famk: float
            K amount, kg ha-1
        famc: float
            Ca amount, kg ha-1
        famo: float
            Other elements, kg ha-1
        focd: str
            Other element, code
        fername: str
            Fertilizer event name, description
        """
        super().__init__()
        kwargs = {
            "fdate": fdate, "fmcd": fmcd, "facd": facd, "fdep": fdep, 
            "famn": famn, "famp": famp, "famk": famk, "famc": famc, 
            "famo": famo, "focd": focd, "fername": fername
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        return

class Fertilizer(TabularRecord):
    prefix = "f"
    dtypes = {}
    pars_fmt = {}
    table_dtype = FertilizerEvent
    def __init__(self, table=list[FertilizerEvent]):
        """
        Initializes a fertilizer section instance.

        Arguments
         ----------
        table: list of FertilizerEvent
            Fertilizer events
        """
        super().__init__()
        self.table = table


class SoilAnalysisLayer(Record):
    prefix = "a"
    dtypes = {
        "sabl": NumberType, "sadm": NumberType, "saoc": NumberType, 
        "sani": NumberType, "saphw": NumberType, "saphb": NumberType,
        "sapx": NumberType, "sake": NumberType, "sasc": NumberType
    }
    pars_fmt = {
        "sabl": ">5.0f", "sadm": ">5.1f", "saoc": ">5.2f", "sani": ">5.2f",
        "saphw": ">5.1f", "saphb": ">5.1f", "sapx": ">5.1f", "sake": ">5.1f",
        "sasc": ">5.2f"
    }
    table_index = "sabl" # Index when buliding table
    def __init__(self, sabl:float, sadm:float=None, saoc:float=None, 
                 sani:float=None, saphw:float=None, saphb:float=None,
                 sapx:float=None, sake:float=None, sasc:float=None):
        """
        Initializes a soil analysis for a soil layer instance.

        Arguments
        ----------
        sabl: float
            Depth of base layer, cm
        sadm: float
            Bulk density, moist, g cm-3
        saoc: float
            Organic carbon, %
        sani: float
            Total nitrogen, %
        saphw: float
            pH in water
        saphb: float
            pH in buffer
        sapx: float
            Phosphorus extractable, mg kg-1
        sake: float
            Potassium exchangeable, cmol kg-1
        sasc: float
            Stable organic carbon, %
        """
        super().__init__()
        kwargs = {"sabl": sabl, "sadm": sadm, "saoc": saoc, "sani": sani,
                  "saphw": saphw, "saphb": saphb, "sapx": sapx, "sake": sake,
                  "sasc": sasc}
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        return

class SoilAnalysis(TabularRecord):
    prefix = "a"
    dtypes = {
        "sadat": DateType, "smhb": CodeType, "smpx": CodeType, 
        "smke": CodeType, "saname": DescriptionType
    }
    pars_fmt = {
        "sadat": "%y%j", "smhb": ">5", "smpx": ">5", "smke": ">5", 
        "saname": "<16"
    }
    table_dtype = SoilAnalysisLayer
    def __init__(self, sadat:date, table:list[SoilAnalysisLayer],
                smhb:str=None, smpx:str=None, smke:str=None, saname:str=None):
        """
        Initializes a soil analysis section instance.

        Arguments
        ----------
        sadat: date
            Soil Analysis date
        table: list
            List of SoilAnalysisLayer instances
        smhb: str
            pH in buffer determination method, code
        smpx: str
            Phosphorus determination method, code
        smke: str
            Potassium determination method, code
        saname: str
            Soil Analysis name, description
        """
        super().__init__()
        kwargs = {
            "sadat": sadat, "smhb": smhb, "smpx": smpx, "smke": smke, 
            "saname": saname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        self.table = table


class IrrigationEvent(Record):
    prefix = "i"
    dtypes = {
        "idate": DateType, "irop": CodeType, "irval": NumberType, 
    }
    pars_fmt = {
        "idate": "%y%j", "irop": ">5", "irval": ">5.1f"
    }
    table_index = None
    def __init__(self, idate:date, irval:float, irop:str=None):
        """
        Initializes a irrigation event instance.

        Arguments
        ----------
        idate: date
            Irrigation date
        irval: float
            Irrigation amount, mm
        irop: str
            Operation method, code
        """
        super().__init__()
        kwargs = {"idate": idate, "irop": irop, "irval": irval}
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        return

class Irrigation(TabularRecord):
    prefix = "i"
    dtypes = {
        "efir": NumberType, "idep": NumberType, "ithr": NumberType,
        "iept": NumberType, "ioff": CodeType, "iame": CodeType,
        "iamt": NumberType, "irname": DescriptionType
    }
    pars_fmt = {
        "efir": ">5.2f", "idep": ">5.0f", "ithr": ">5.0f", "iept": ">5.0f",
        "ioff": ">5", "iame": ">5", "iamt": ">5.0f", "irname": "<16"
    }
    table_dtype = IrrigationEvent
    def __init__(self, table=list[IrrigationEvent], efir:float=1,
                    idep:float=None, ithr:float=None, iept:float=None,
                    ioff:str=None, iame:str=None, iamt:float=None, 
                    irname:str=None):
        """
        Initializes a Irrigation section instance.

        Arguments
        ----------
        table: list
            List of IrrigationEvent
        efir: float
            Irrigation efficiency, 0-1
        idep: float
            Management depth for automatic application, cm
        ithr: float
            Threshold for automatic appl., % of max. available
        iept: float
            End point for automatic appl., % of max. available
        ioff: str
            End of automatic applications (growth stage), code
        iame: str
            Method for automatic applications, code
        iamt: float
            Amount per automatic irrigation if fixed, mm
        irname: str
            Irrigation treatment name, description
        """
        super().__init__()
        kwargs = {
            "efir": efir, "idep": idep, "ithr": ithr, "iept": iept,
            "ioff": ioff, "iame": iame, "iamt": iamt, "irname": irname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        self.table = table


class ResidueEvent(Record):
    prefix = "r"
    dtypes = {
        "rdate": DateType, "rcod": CodeType, "ramt": NumberType,
        "resn": NumberType, "resp": NumberType, "resk": NumberType,
        "rinp": NumberType, "rdep": NumberType, "rmet": CodeType,
        "rename": DescriptionType
    }
    pars_fmt = {
        "rdate": "%y%j", "rcod": ">5", "ramt": ">5.0f", "resn": ">5.2f",
        "resp": ">5.2f", "resk": ">5.2f", "rinp": ">5.0f", "rdep": ">5.0f",
        "rmet": ">5", "rename": "<16"
    }
    table_index = None
    def __init__(self, rdate:date, rcod:str, ramt:float, resn:float,
                 resp:float, resk:float, rinp:float, rdep:float, rmet:str,
                 rename:str=None):
        """
        Initializes a residue application event instance.

        Arguments
        ----------
        rdate: date
            Residue application date
        rcod: str
            Residue material, code
        ramt: float
            Residue amount, kg ha-1
        resn: float
            Residue nitrogen concentration, %
        resp: float
            Residue phosph. concentration, %
        resk: float
            Residue potassium concentration, %
        rinp: float
            Residue incorporation, %
        rdep: float
            Incorporation depth, cm
        rmet: str
            Method of incorporation, code
        rename: str
            Residue application name, description
        """
        super().__init__()
        kwargs = {
            "rdate": rdate, "rcod": rcod, "ramt": ramt, "resn": resn,
            "resp": resp, "resk": resk, "rinp": rinp, "rdep": rdep,
            "rmet": rmet, "rename": rename
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)

class Residue(TabularRecord):
    prefix = "r"
    dtypes = {}
    pars_fmt = {}
    table_dtype = ResidueEvent
    def __init__(self, table=list[ResidueEvent]):
        """
        Initializes a residue section. 

        Arguments
         ----------
        table: list of ResidueEvent
            Residue application events
        """
        super().__init__()
        self.table = table
    

class ChemicalEvent(Record):
    prefix = "c"
    dtypes = {
        "cdate": DateType, "chcod": CodeType, "chamt": NumberType,
        "chme": CodeType, "chdep": NumberType, "cht": CodeType,
        "chname": DescriptionType
    }
    pars_fmt = {
        "cdate": "%y%j", "chcod": ">5", "chamt": ">5.2f", "chme": ">5",
        "chdep": ">5.0f", "cht": ">5", "chname": "<16"
    }
    table_index = None
    def __init__(self, cdate:date, chcod:str, chamt:float, chme:str,
                 chdep:float=None, cht:str=None, chname:str=None):
        """
        Initializes a chemical application event instance.

        Arguments
        ----------
        cdate: date
            Chemical application date
        chcod: str
            Chemical material, code
        chamt: float
            Application amount, kg/ha
        chdep: float
            Application depth, cm
        chme: str
            Aplication method, code
        cht: str
            Application target, code
        chname: str
            Application name, description
        """
        super().__init__()
        kwargs = {
            "cdate": cdate, "chcod": chcod, "chamt": chamt, "chdep": chdep,
            "chme": chme, "cht": cht, "chname": chname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    
class Chemical(TabularRecord):
    prefix = "c"
    dtypes = {}
    pars_fmt = {}
    table_dtype = ChemicalEvent
    def __init__(self, table=list[ChemicalEvent]):
        """
        Initializes a chemicals application section. 

        Arguments
         ----------
        table: list of ChemicalsEvent
            Chemicals application events
        """
        super().__init__()
        self.table = table


class TillageEvent(Record):
    prefix = "t"
    dtypes = {
        "tdate": DateType, "timpl": CodeType, "tdep": NumberType,
        "tname": DescriptionType
    }
    pars_fmt = {
        "tdate": "%y%j", "timpl": ">5", "tdep": ">5.0f", "tname": "<16"
    }
    table_index = None
    def __init__(self, tdate:date, timpl:str=None, tdep:float=None, 
                 tname:str=None):
        """
        Initializes a tillage event.

        Arguments
        ----------
        tdate: date
            Tillage event date
        timpl: str
            Tillage implement, code
        tdep: float
            Tillage depth, cm
        tname: str
            Tillage event name, description
        """
        super().__init__()
        kwargs = {
            "tdate": tdate, "timpl": timpl, "tdep": tdep, "tname": tname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value) 


class Tillage(TabularRecord):
    prefix = "t"
    dtypes = {}
    pars_fmt = {}
    table_dtype = TillageEvent
    def __init__(self, table=list[TillageEvent]):
        """
        Instanciates a tillage section. 

        Arguments
         ----------
        table: list of TillageEvent
            Tillage events
        """
        super().__init__()
        self.table = table
    

class Field(Record):
    '''
    Class to define a single field
    '''
    prefix = "l"
    dtypes = {
        "id_field": DescriptionType, "wsta": (DescriptionType, WeatherStation), 
        "flsa": NumberType, "flob": NumberType, "fldt": CodeType, 
        "fldd": NumberType, "flds": NumberType, "flst": CodeType, 
        "sltx": CodeType, "sldp": NumberType, "id_soil": (DescriptionType, SoilProfile), 
        "flname": DescriptionType, "xcrd": NumberType, "ycrd": NumberType, 
        "elev": NumberType, "area": NumberType, "slen": NumberType, 
        "flwr": NumberType, "slas": NumberType, "flhst": CodeType, 
        "fhdur": NumberType
    }
    pars_fmt = {
        "id_field": ">8", "wsta": ".<8", "flsa": ">5.0f", "flob": ">5.0f", 
        "fldt": ">5", "fldd": ">5.0f", "flds": ">5.0f", "flst": ">5", 
        "sltx": "<5", "sldp": ">5.0f", "id_soil": "<10", "flname": "<32", 
        "xcrd": ".>15.2f", "ycrd": ".>15.2f", "elev": ".>9.0f", 
        "area": ".>17.0f", "slen": ".>5.0f", "flwr": ".>5.1f", 
        "slas": ".>5.0f", "flhst": ">5", "fhdur": ">5.0f"
    }
    n_tiers = 2
    def __init__(self, id_field:str, wsta:str, id_soil:str, flsa:float=None,
                 flob:float=None, fldt:str=None, fldd:float=None, 
                 flds:float=None, flst:str=None, sltx:str=None, 
                 sldp:float=None, flname:str=None, xcrd:float=None, 
                 ycrd:float=None, elev:float=None, area:float=None, 
                 slen:float=None, flwr:float=None, slas:float=None, 
                 flhst:str=None, fhdur:float=None):
        """
        Initializes a Field instance.

        Arguments
        ----------
        id_field: str
            Field id
        wsta: str
            Weather station id
        id_soil: str
            Soil profile id
        flsa: float
            Slope and aspect, degrees from horizontal
        flob: float
            Obstruction to sun, degrees
        fldt: str
            Drainage type, code
        fldd: float
            Drain depth, cm
        flds: float
            Drain spacing, m
        flst: str
            Surface stones (Abundance, % + Size, S,M,L)
        sltx: str
            Soil texture, code
        sldp: float
            Soil depth, cm
        flname: str
            field name, description
        xcrd: float
            Longitude, decimal degrees
        ycrd: float
            Latitude, decimal degrees
        elev: float
            Altitude, m
        area: float
            Plot/field area, m2
        slen: float
            Length of slope, m
        flwr: float
            Polygon length-width ratio
        slas: float
            Slope aspect, degrees clockwise from north
        flhst: str
            Field history, code
        fhdur: float
            Field history duration
        """
        super().__init__()
        if fldt is None:
            fldt = "DR000"
        kwargs = {
            "id_field": id_field, "wsta": wsta, "flsa": flsa, "flob": flob, 
            "fldt": fldt, "fldd": fldd, "flds": flds, "flst": flst, 
            "sltx": sltx, "sldp": sldp, "id_soil": id_soil, "flname": flname, 
            "xcrd": xcrd, "ycrd": ycrd, "elev": elev, "area": area, 
            "slen": slen, "flwr": flwr, "slas": slas, "flhst": flhst, 
            "fhdur": fhdur
        }
        for name, value in kwargs.items():
            self.__setitem__(name, value)
        self.__tier1 = [
            "id_field", "wsta", "flsa", "flob", "fldt", "fldd", "flds", 
            "flst", "sltx", "sldp", "id_soil", "flname"
        ]
        self.__tier2 = [
            "xcrd", "ycrd", "elev", "area", "slen", "flwr", "slas", "flhst",
            "fhdur"
        ]
    
    def _write_section(self):
        out_str = "*FIELDS\n"
        for tiers in (self.__tier1, self.__tier2):
            header = ["@"+self.prefix.upper()]
            values = []
            for key in tiers:
                fmt = self.pars_fmt[key]
                if fmt == "%y%j":
                    fmt = ">5"
                if fmt[0] == ".":
                    leading = "."
                    fmt = fmt[1:]
                else:
                    leading = ""
                fmt = leading + fmt.split(".")[0]
                header.append(format(key.upper(), fmt))
                values.append(self[key].str)
            out_str += " ".join(header) + "\n" + " 1 " + " ".join(values) + "\n"
        return out_str
    
    def __setitem__(self, key, value):
        if key == "id_field":
            assert len(value) == 8, "id_field must be a 8 character string"
        # if (key == "wsta") and isinstance(value, WeatherStation):
        #     self.dtypes["wsta"] = WeatherStation
        if (key == "id_soil") and isinstance(value, SoilProfile):
            # self.dtypes["id_soil"] = SoilProfile
            self["sldp"] = value.table[-1]["slb"]
        super().__setitem__(key, value)


class SCGeneral(Record):
    prefix = "n"
    dtypes = {
        "nyers": NumberType, "nreps": NumberType, "start": CodeType,
        "sdate": DateType, "rseed": NumberType, "sname": DescriptionType,
        "smodel": CodeType
    }
    pars_fmt = {
        "nyers": ">5.0f", "nreps": ">5.0f", "start": ">5",
        "sdate": "%y%j", "rseed": ">5.0f", "sname": "<25",
        "smodel": ">6"
    }
    def __init__(self, sdate:date, nyers:int=1, nreps:int=1, start:str="S", 
                 rseed:int=2150, sname:str=None, smodel:str=None):
        """
        Initializes a Simulation Controls General section. 

        Arguments
        ----------
        nyers: int
            Number of years in Seasonal analysis
        nreps: int
            Number of repetitions (When weather generator in forecast mode)
        start: str
            Start method. Must be kept at 'S' (When specified)
        rseed: int
            Random seed
        sname: str
            Simulation name
        smodel: str
            Model to use
        """
        super().__init__()
        kwargs = {
            "nyers": nyers, "nreps": nreps, "start": start, "sdate": sdate,
            "rseed": rseed, "sname": sname, "smodel": smodel
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
        return
    

class SCOptions(Record):
    prefix = "n"
    dtypes = {
        "water": CodeType, "nitro": CodeType, "symbi": CodeType,
        "phosp": CodeType, "potas": CodeType, "dises": CodeType,
        "chem": CodeType, "till": CodeType, "co2": CodeType
    }
    pars_fmt = {
        "water": ">5", "nitro": ">5", "symbi": ">5",
        "phosp": ">5", "potas": ">5", "dises": ">5",
        "chem": ">5", "till": ">5", "co2": ">5"
    }
    def __init__(self, water:str="Y", nitro:str="Y", symbi:str="N",
                 phosp:str="N", potas:str="N", dises:str="N", 
                 chem:str="N", till:str="N", co2:str="M"):
        """
        Initializes a Simulation Controls Options section. 

        Arguments
        ----------
        water: str
            Water effect switch (Y or N)
        nitro: str
            Nitrogen effect switch (Y or N)
        symbi: str
            Symbiosis effect (nitrogen fixation) switch (Y or N)
        phosp: str
            Phosphorus effect switch (Y or N)
        potas: str
            Potasium effect switch (Y or N)
        dises: str
            Diseases effect swtich (Y or N)
        chem: str
            Chemical effect switch (Y or N)
        till: str
            Tillage effect switch (Y or N)
        co2: str
            CO2 data source (M: Mauna Loa, D: Default, W: In weather file)
        """
        super().__init__()
        kwargs = {
            "water": water, "nitro": nitro, "symbi": symbi,
            "phosp": phosp, "potas": potas, "dises": dises,
            "chem": chem, "till": till, "co2": co2
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class SCMethods(Record):
    prefix = "n"
    dtypes = {
        "wther": CodeType, "incon": CodeType, "light": CodeType,
        "evapo": CodeType, "infil": CodeType, "photo": CodeType,
        "hydro": CodeType, "nswit": CodeType, "mesom": CodeType,
        "mesev": CodeType, "mesol": CodeType
    }
    pars_fmt = {
        "wther": ">5", "incon": ">5", "light": ">5",
        "evapo": ">5", "infil": ">5", "photo": ">5",
        "hydro": ">5", "nswit": ">5", "mesom": ">5",
        "mesev": ">5", "mesol": ">5"
    }
    def __init__(self, wther:str="M", incon:str="M", light:str="E",
                 evapo:str="R", infil:str="R", photo:str="C", hydro:str="R",
                 nswit:str="1", mesom:str="P", mesev:str="R", mesol:str="1"):
        """
        Initializes a Simulation Controls Methods section. 

        Arguments
         ----------
        wther: str
            Weather data source (M: Measured data, G: Generated (WTG files)
            S: Simulated (SIMMETEO), W: Simualted internal (WGEN))
        incon: str
            Initial conditions soil conditions (M: As reported)
        light: str
            ? Light interception method
        evapo: str
            Evapotranspiration Method (R: Priestley-Taylor, F: FAO-56, 
            S: ASCE Std Ref ET-Short, T: ASCE Std Ref ET-Tall)
        infil: str
            Infiltration method (S: Soil conservation service , R: Ritchie, 
            N: No mulch)
        photo: str
            Photosyntesis method (C: Canopy curve, L: Leaf photosynt response
            curve , R: Radiation effiency)
        hydro: str
            Hydrology (R: Ritchie)
        nswit: str
            ??
        mesom: str
            Soil Organic Matter method (G: Ceres (Godwin), P: Century (Parton))
        mesev: str
            Soil evaporation method (R: Ritchie-Ceres, S: Suleiman-Ritchie)
        mesol: str
            Soil layer distribution (1: Model-specified soil layers,
            2: Modified soil profile, 3: Unmodified soil profile)
        """
        super().__init__()
        kwargs = {
            "wther": wther, "incon": incon, "light": light, "evapo": evapo,
            "infil": infil, "photo": photo, "hydro": hydro, "nswit": nswit,
            "mesom": mesom, "mesev": mesev, "mesol": mesol
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class SCManagement(Record):
    prefix = "n"
    dtypes = {
        "plant": CodeType, "irrig": CodeType, "ferti": CodeType,
        "resid": CodeType, "harvs": CodeType, 
    }
    pars_fmt = {
        "plant": ">5", "irrig": ">5", "ferti": ">5",
        "resid": ">5", "harvs": ">5", 
    }
    def __init__(self, plant:str="R", irrig:str="D", ferti:str="D",
                 resid:str="D", harvs:str="A"):
        """
        Initializes a Simulation Controls Mangement section. 

        Arguments
        ----------
        plant: str
            Planting option (A: Automatic window,  F: Automatic force in the 
            last day of window, R: On reported date)
        irrig: str
            Irrigation option (A: Automatic when required, D: days after
            planting, F: Fixed amount automatic, N: Not irrigated, P: As 
            reported through last day then automatic to refill, R: On reported
            dates, W: As reported thorugh last day then automatic with fixed)
        ferti: str
            Fertilization option (D: Days after planting, N: Not fertilized,
            R: On reported dates)
        residue: str
            Organic amendments option (D: Days after planting, N: Not
            fertilized, R: On reported dates)
        harvest: str
            Harvest option (A: Automatic, D: Days after planting, M: At 
            maturity, R: On reported dates, W: AutoMOW using days as harvest
            frequency, X: autoMOW using GDD as harvest frequency, Y: smartMOW
            using days as harvest frequency, Z: smartMOW using GDD as harvest
            frequency)
        """
        super().__init__()
        kwargs = {
            "plant": plant, "irrig": irrig, "ferti": ferti, "resid": resid,
            "harvs": harvs, 
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class SCOutputs(Record):
    prefix = "n"
    dtypes = {
        'fname': CodeType, 'ovvew': CodeType, 'sumry': CodeType, 
        'fropt': NumberType, 'grout': CodeType, 'caout': CodeType, 
        'waout': CodeType, 'niout': CodeType, 'miout': CodeType,
        'diout': CodeType, 'vbose': CodeType, 'chout': CodeType, 
        'opout': CodeType, 'fmopt': CodeType
    }
    pars_fmt = {
        'fname': ">5", 'ovvew': ">5", 'sumry': ">5", 'fropt': ">5.0f", 
        'grout': ">5", 'caout': ">5", 'waout': ">5", 'niout': ">5", 
        'miout': ">5", 'diout': ">5", 'vbose': ">5", 'chout': ">5", 
        'opout': ">5", 'fmopt': ">5"
    }
    def __init__(self, fname:str="N", ovvew:str="Y", sumry:str="Y", 
                 fropt:int=1, grout:str="Y", caout:str="Y", waout:str="N",
                 niout:str="N", miout:str="N", diout:str="N", vbose:str="Y",
                 chout:str="N", opout:str="N", fmopt:str="A"):
        """
        Initializes a Simulation Controls Output section. 

        Arguments
        ----------
        fname: str
            Use experiment name in output files (Y or N)
        ovvew, sumry, grout, caout, waout, niout, miout, diout,
        chout, opout: str
            Switch to produce output files (Y or N)
        fropt: int
            Output interval
        vbose: str
            Verbose level (A, D, N, Y, 0)
        fmopt: str
            Output format (A: Text file, C: csv)
        """
        super().__init__()
        kwargs = {
            'fname': fname, 'ovvew': ovvew, 'sumry': sumry, 'fropt': fropt, 
            'grout': grout, 'caout': caout, 'waout': waout, 'niout': niout, 
            'miout': miout, 'diout': diout, 'vbose': vbose, 'chout': chout, 
            'opout': opout, 'fmopt': fmopt
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class AMPlanting(Record):
    prefix = "n"
    dtypes = {
        'pfrst': DateType, 'plast': DateType, 'ph2ol': NumberType, 
        'ph2ou': NumberType, 'ph2od': NumberType, 'pstmx': NumberType, 
        'pstmn': NumberType,
    }
    pars_fmt = {
        'pfrst': "%y%j", 'plast': "%y%j", 'ph2ol': ">5.0f", 
        'ph2ou': ">5.0f", 'ph2od': ">5.0f", 'pstmx': ">5.0f", 
        'pstmn': ">5.0f",
    }
    def __init__(self, pfrst:date, plast:date, ph2ol:float=40, 
                 ph2ou:float=100, ph2od:float=30, pstmx:float=30,
                 pstmn:float=10):
        """
        Initializes a Automatic Management Planting section. 

        Arguments
        ----------
        pfrst: date
            Start of planting window
        plast: date
            End of planting window
        ph2ol: float
            Lower soil water level (%)
        ph2ou: float
            Upper soil water level (%)
        ph2od: float
            Depth of soil layer to consider for soil water level (cm)
        pstmx: float
            Maximum soil temperature (C)
        pstmn: float
            Minium soil temperature (C)
        """
        super().__init__()
        kwargs = {
            'pfrst': pfrst, 'plast': plast, 'ph2ol': ph2ol, 
            'ph2ou': ph2ou, 'ph2od': ph2od, 'pstmx': pstmx, 
            'pstmn': pstmn
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class AMIrrigation(Record):
    prefix = "n"
    dtypes = {
        'imdep': NumberType, 'ithrl': NumberType, 'ithru': NumberType, 
        'iroff': CodeType, 'imeth': CodeType, 'iramt': NumberType, 
        'ireff': NumberType,
    }
    pars_fmt = {
        'imdep': ">5.0f", 'ithrl': ">5.0f", 'ithru': ">5.0f", 
        'iroff': ">5", 'imeth': ">5", 'iramt': ">5.0f", 
        'ireff': ">5.2f",
    }
    def __init__(self, imdep:float=30, ithrl:float=50, ithru:float=100, 
                 iroff:str="IB001", imeth:str="IB001", iramt:float=10,
                 ireff:float=1.):
        """
        Initializes a Automatic Management Irrigation section. 

        Arguments
        ----------
        imdep: float
            Management depth (cm)
        ithrl: float
            Threshold, % of max available
        ithru: float
            End point, % of max available
        iroff: str
            End of application, Growth stage
        imeth: str
            Application method code
        iramt: float
            Fixed amount (mm)
        ireff: float
            Irrigation effiency (fraction)
        """
        super().__init__()
        kwargs = {
            'imdep': imdep, 'ithrl': ithrl, 'ithru': ithru, 
            'iroff': iroff, 'imeth': imeth, 'iramt': iramt, 
            'ireff': ireff,
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class AMNitrogen(Record):
    prefix = "n"
    dtypes = {
        'nmdep': NumberType, 'nmthr': NumberType, 'namnt': NumberType, 
        'ncode': CodeType, 'naoff': CodeType, 
    }
    pars_fmt = {
        'nmdep': ">5.0f", 'nmthr': ">5.0f", 'namnt': ">5.0f", 
        'ncode': ">5", 'naoff': ">5", 
    }
    def __init__(self, nmdep:float=30, nmthr:float=50, namnt:float=25, 
                 ncode:str="IB001", naoff:str="IB001"):
        """
        Initializes a Automatic Management Nitrogen section. 

        Arguments
        ----------
        nmdep: float
            Management depth (cm)
        nmthr: float
            Threshold, stress factor (%)
        namnt: float
            Amount per application (kg N/ha)
        ncode: str
            Fertilizer type code
        naoff: str
            End of applications, Growth factor
        """
        super().__init__()
        kwargs = {
            'nmdep': nmdep, 'nmthr': nmthr, 'namnt': namnt, 
            'ncode': ncode, 'naoff': naoff
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class AMResidues(Record):
    prefix = "n"
    dtypes = {
        'ripcn': NumberType, 'rtime': NumberType, 'ridep': NumberType, 
    }
    pars_fmt = {
        'ripcn': ">5.0f", 'rtime': ">5.0f", 'ridep': ">5.0f", 
    }
    def __init__(self, ripcn:float=100, rtime:float=1, ridep:float=20):
        super().__init__()
        """
        Initializes a Automatic Management Organic Amendment section. 

        Arguments
         ----------
        ripcn: float
            Incorporation percentage (%)
        rtime: float
            Incorporation, days after harvest
        ridep: float
            Incorporation depth (cm)
        """
        kwargs = {
            'ripcn': ripcn, 'rtime': rtime, 'ridep': ridep, 
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class AMHarvest(Record):
    prefix = "n"
    dtypes = {
        'hfrst': NumberType, 'hlast': DateType, 'hpcnp': NumberType, 
        'hpcnr': NumberType, 'hmfrq': NumberType, 'hmgdd': NumberType, 
        'hmcut': NumberType, 'hmmow': NumberType, 'hrspl': NumberType, 
        'hmvs': NumberType
    }
    pars_fmt = {
        'hfrst': ">5.0f", 'hlast': "%y%j", 'hpcnp': ">5.0f", 'hpcnr': ">5.0f", 
        'hmfrq': ">5.0f", 'hmgdd': ">5.0f", 'hmcut': ">5.2f", 'hmmow': ">5.0f", 
        'hrspl': ">5.0f", 'hmvs': ">5.0f"
    }
    def __init__(self, hfrst:date, hlast:date, hpcnp:float=100, hpcnr:float=0,
                 hmfrq:float=None, hmgdd:float=None, hmcut:float=None,
                 hmmow:float=None, hrspl:float=None, hmvs:float=None):
        """
        Initializes a Automatic Management Harvest section. 

        Arguments
        ----------
        hfrst: date
            First day of harvest window
        hlast: date
            Last day of harvest window
        hpcnp: float
            Percentage of product harvested
        hpcnr: float
            Percentafe of residue harvested
        hmfrq, hmgdd, hmcut, hmmow, hrspl, hmvs: float
            Automow parameters
        """
        hfrst = 0 # Option not implemented yet on the GUI
        super().__init__()
        kwargs = {
            'hfrst': hfrst, 'hlast': hlast, 'hpcnp': hpcnp, 'hpcnr': hpcnr,
            'hmfrq': hmfrq, 'hmgdd': hmgdd, 'hmcut': hmcut, 'hmmow': hmmow, 
            'hrspl': hrspl, 'hmvs': hmvs
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)
    

class SimulationControls:
    dtypes = {
        "general": SCGeneral, "options": SCOptions, 
        "methods": SCMethods, "management": SCManagement, 
        "outputs": SCOutputs, "planting": AMPlanting,
        "irrigation": AMIrrigation, "nitrogen": AMNitrogen,
        "residues": AMResidues, "harvest": AMHarvest
    }
    def __init__(self, general:SCGeneral, options:SCOptions=None, 
                 methods:SCMethods=None, management: SCManagement=None, 
                 outputs:SCOutputs=None, planting:AMPlanting=None, 
                 irrigation:AMIrrigation=None, nitrogen:AMNitrogen=None,
                 residues:AMResidues=None, harvest:AMHarvest=None):
        """
        Initializes a SimulationControls instance. If one of the arguments is 
        missing, it assumes default options.

        Arguments
        ----------
        general:SCGeneral, 
        options:SCOptions, 
        methods:SCMethods, 
        management: SCManagement, 
        outputs:SCOutputs, 
        planting:AMPlanting, 
        irrigation:AMIrrigation,
        nitrogen:AMNitrogen,
        residues:AMResidues
        harvest:AMHarvest
        """
        # Set default values if not passed as parameters
        if not options: 
            options = SCOptions()
        if not methods: 
            methods = SCMethods()
        if not management: 
            management = SCManagement()
        if not outputs: 
            outputs = SCOutputs()
        # Same with Automatic management
        if not planting: 
            planting = AMPlanting(pfrst=general["sdate"], plast=general["sdate"])
        if not irrigation:
            irrigation = AMIrrigation()
        if not nitrogen:
            nitrogen = AMNitrogen()
        if not residues:
            residues = AMResidues()
        if not harvest:
            harvest = AMHarvest(hfrst=general["sdate"], hlast=general["sdate"])
        
        self.__data = {
            "general": general, "options": options, "methods": methods,
            "management": management, "outputs": outputs, "planting": planting,
            "irrigation": irrigation, "nitrogen": nitrogen, "residues": residues,
            "harvest": harvest
        }
        return
    
    def __setitem__(self, key, value):
        if key not in self.__data.keys():
            raise KeyError
        if not isinstance(value, self.dtypes[key]):
            raise TypeError
        self.__data[key] = value

    def __getitem__(self, key):
        key = key.lower()
        return self.__data[key]
    
    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__data.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))
    
    def _write_section(self):
        out_str = "*SIMULATION CONTROLS\n"
        out_str += "@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL\n"
        out_str += f" 1 GE          {self.__data['general']._write_row()}"
        out_str += "@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2\n"
        out_str += f" 1 OP          {self.__data['options']._write_row()}"
        out_str += "@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL\n"
        out_str += f" 1 ME          {self.__data['methods']._write_row()}"
        out_str += "@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS\n"
        out_str += f" 1 MA          {self.__data['management']._write_row()}"
        out_str += "@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT\n"
        out_str += f" 1 OU          {self.__data['outputs']._write_row()}"
        out_str += f"\n@  AUTOMATIC MANAGEMENT\n"
        out_str += "@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN\n"
        out_str += f" 1 PL          {self.__data['planting']._write_row()}"
        out_str += "@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF\n"
        out_str += f" 1 IR          {self.__data['irrigation']._write_row()}"
        out_str += "@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF\n"
        out_str += f" 1 NI          {self.__data['nitrogen']._write_row()}"
        out_str += "@N RESIDUES    RIPCN RTIME RIDEP\n"
        out_str += f" 1 RE          {self.__data['residues']._write_row()}"
        out_str += "@N HARVEST     HFRST HLAST HPCNP HPCNR\n"
        out_str += f" 1 HA          {self.__data['harvest']._write_row()}"
        return out_str
    

class Treatment(Record):
    """
    This class is not suposed to be used by users. This is for library internal
    use.
    """
    prefix = "n"
    dtypes = {
        'r': NumberType, 'o': NumberType, "c": NumberType,
        'tname': DescriptionType, "cu": NumberType, "fl": NumberType,
        "sa": NumberType, "ic": NumberType, "mp": NumberType, "mi": NumberType,
        "mf": NumberType, "mr": NumberType, "mc": NumberType, "mt": NumberType,
        "me": NumberType, "mh": NumberType, "sm": NumberType
    }
    pars_fmt = {
        'r': ">1.0f", 'o': ">1.0f", "c": ">1.0f",
        'tname': ".<25", "cu": ">2.0f", "fl": ">2.0f",
        "sa": ">2.0f", "ic": ">2.0f", "mp": ">2.0f", "mi": ">2.0f",
        "mf": ">2.0f", "mr": ">2.0f", "mc": ">2.0f", "mt": ">2.0f",
        "me": ">2.0f", "mh": ">2.0f", "sm": ">2.0f"
    }
    def __init__(self, **kwargs):
        """
        Initializes a Treatment section. This class is not to be used by the 
        user. Therefore, no specific input parameters are defined.
        """
        assert all([par in kwargs for par in self.pars_fmt.keys()])
        super().__init__()
        kwargs = {par: kwargs[par] for par in self.pars_fmt.keys()}
        kwargs["o"] = kwargs["c"] = kwargs["me"] = 0
        for name, value in kwargs.items():
            super().__setitem__(name, value)


class MowEvent(Record):
    prefix = 'trno '
    dtypes = {
        'date': DateType, 'mow': NumberType, 'rsplf': NumberType, 
        'mvs': NumberType, 'rsht': NumberType
    }
    pars_fmt = {
        'date': '%y%j', 'mow': '>5.0f', 'rsplf': '>5.0f', 
        'mvs': '>5.0f', 'rsht': '>5.1f'
    }
    def __init__(self, date:date, mow:float, rsplf:float, mvs:float, rsht:float):
        """
        Instanciates a Mow event.

        Arguments
        ----------
        date: date
            Mow event date
        mow: float
            Residue biomass Residual biomass after mowing (kg/ha)
        rsplf: float
            Residual leaf   Residual leaf after mowing (%)   
        mvs: float
            Residual V stg  Residual vegetative stage after mowing (node #) 
        rsht: float
            Residule height after mowing (cm) [not used] 
        """
        super().__init__()
        kwargs = {
            "date": date, "mow": mow, "rsplf": rsplf, "rsht": rsht, 'mvs': mvs
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value) 


class Mow(TabularRecord):
    prefix = "trno "
    dtypes = {}
    pars_fmt = {}
    table_dtype = MowEvent
    def __init__(self, table=list[MowEvent]):
        """
        Instanciates a mow object. 

        Arguments
            ----------
        table: list of MowEvent
            Mow events
        """
        super().__init__()
        self.table = table

    @classmethod
    def from_file(cls, file):
        """
        Creates and return a Mow instance from a mow file.
        """
        encoding = detect_encoding(file)
        with open(file, 'r', encoding=encoding) as f:
            lines = f.readlines()
        lines = clean_comments(lines)
        lines = filter(lambda x: '@TRNO' not in x, lines)
        events = {}
        for line in lines:
            if len(line.strip()) > 10:
                pars = parse_pars_line(line[7:], cls.table_dtype.pars_fmt)
                level = int(line[:6])
                events[level] = events.get(level, []) + [cls.table_dtype(**pars)]
        events = {k: cls(v) for k, v in events.items()}
        return events


def get_header_range(l, h, pars_fmt):
    """Get variable start and index in the header line"""
    h_fmt = pars_fmt[h]
    # For the case of fields that have leading points, like those in 
    # field section
    if h_fmt[0] == ".": 
        h_fmt = h_fmt[1:]
    if h_fmt[0] == "<":
        start = l.lower().find(h)
        end = start + int(h_fmt[1:].split(".")[0])
    elif h_fmt[0] == ">":
        end = l.lower().find(h) + len(h)
        start = end - int(h_fmt[1:].split(".")[0])
    elif h_fmt[0] == "%":
        start = l.lower().find(h)
        end = start + 5 # Assuming all dates in FileX are a 5 character string
    else:
        raise ValueError("Variable format must be right or left justified")
    return (start, end)


def read_filex(filexpath):
    """
    It reads a FILEX and returns a dictionary where the keys are the treatments,
    and the values are the level objects. 

    Asumptions:
    Some of the assumptions are needed to deal with description fields 
    that can contain spaces, such as Cultivar name.
    - Values are below their header
    - Each column/header must be right or left justified
    - Treament number is always the first column
    - Treatment number is on the first two spaces
    """
    with open(filexpath, "r") as f:
        lines = f.readlines()
    lookup = "section"
    vals_dict = {}
    table_values = []
    vals = {}
    experiment = {}
    add_tier = False
    for l in lines:
        l = l.replace("\n", "")
        if len(l.strip()) < 2:
            if lookup == 'table header': # In case Table is not there
                experiment[section_cls.__name__] = vals_dict
                vals_dict = {}
                del level
            if lookup == "table values":
                if only_table:
                    for level, val in vals.items():
                        vals_dict[level] = section_cls(table=val)
                else:
                    vals["table"] = table_values
                    vals_dict[level] = section_cls(**vals)
                experiment[section_cls.__name__] = vals_dict
                vals_dict = {}
                table_values = []
                del level
            if lookup == "values":
                experiment[section_cls.__name__] = vals_dict
                vals_dict = {}
                del level
            if lookup == "simulation controls": 
                continue
            else:
                lookup = "section"
            vals = {}
            add_tier = False
            
            continue
        elif l[0] == "!":
            continue
        elif lookup == "header":
            if l[0] == "@":
                header = l.replace(".", " ").lower().split()
                header_start_end = {}
                start_i = 0
                for h in header[1:]:
                    header_start_end[h] = get_header_range(
                        l[start_i:], h, section_cls.pars_fmt
                    )
                    header_start_end[h] = (
                        header_start_end[h][0] + start_i,
                        header_start_end[h][1] + start_i
                    )
                    start_i = header_start_end[h][1]
                lookup = "values"
                continue
        elif lookup == "table header":
            if l[0] == "@":
                table_header = l.replace(".", " ").lower().split()
                table_header_start_end = {
                    h: get_header_range(l, h, section_cls.table_dtype.pars_fmt) 
                    for h in table_header[1:]
                }
                lookup = "table values"
                continue
        elif lookup == "values":
            # Special case for Field tier 2
            if (l[:2] == "@L"):
                add_tier = True
                header = l.replace(".", " ").lower().split()
                header_start_end = {
                    h: get_header_range(l, h, section_cls.pars_fmt) 
                    for h in header[1:]
                }
                continue
            vals = {
                key: l[header_start_end[key][0]:header_start_end[key][1]]
                for key in header[1:]
            }
            level = int(l[:2])
            if hasattr(section_cls, "table_dtype"):
                lookup = "table header"
            else:
                if add_tier:
                    for key, val in vals.items():
                        vals_dict[level][key] = val
                else:
                    vals_dict[level] = section_cls(**vals)
            continue                
        elif lookup == "table values":
            if l[0] == "@":
                vals["table"] = table_values
                vals_dict[level] = section_cls(**vals)
                table_values = []
                lookup = "values"
                del level
                continue
            row = section_cls.table_dtype(**{
                key: l[table_header_start_end[key][0]:
                    table_header_start_end[key][1]]
                for key in table_header[1:]
            })
            if only_table:
                level = int(l[:2])
                vals[level] = vals.get(level, []) + [row]
            table_values.append(row)
        elif lookup == "simulation controls":
            if l[0] == "@": # Header 
                if "AUTOMATIC" in l:
                    continue
                header = l.replace(".", " ").lower().split()
                simcon_dtype = SimulationControls.dtypes[header[1]]
                header_start_end = {
                    h: get_header_range(
                        l, h, simcon_dtype.pars_fmt
                    ) 
                    for h in header[2:]
                }
            else: # Values
                vals = {
                    key: l[header_start_end[key][0]:header_start_end[key][1]]
                    for key in header[2:]
                }
                level = int(l[:2])
                if sim_controls_dict.get(level, False):
                    sim_controls_dict[level][header[1]] = simcon_dtype(**vals)
                else:
                    sim_controls_dict[level] = {
                        header[1]: simcon_dtype(**vals)
                    }
            
        elif lookup == "section":
            if l[:6] == "*TREAT":
                section_cls = Treatment
            elif l[:6] == "*PLANT":
                section_cls = Planting
            elif l[:6] == "*CULTI":
                section_cls = Cultivar
            elif l[:6] == "*HARVE":
                section_cls = Harvest
            elif l[:6] == "*INITI":
                section_cls = InitialConditions
            elif l[:6] == "*FERTI":
                section_cls = Fertilizer
            elif l[:6] == "*SOIL ":
                section_cls = SoilAnalysis
            elif l[:6] == "*IRRIG":
                section_cls = Irrigation
            elif l[:6] == "*RESID":
                section_cls = Residue
            elif l[:6] == "*CHEMI":
                section_cls = Chemical
            elif l[:6] == "*TILLA":
                section_cls = Tillage
            elif l[:6] == "*FIELD": 
                section_cls = Field
            elif l[:6] == "*SIMUL":
                section_cls = SimulationControls
                sim_controls_dict = {}
                # Simulation Controls must be the last section
            else:
                continue
            # Some sections are only tables, for those go directly to table
            # header
            only_table = len(section_cls.dtypes) == 0
            if only_table:
                lookup = "table header"
                vals = {}
            else:
                lookup = "header"
                if section_cls.__name__ == "SimulationControls":
                    lookup = "simulation controls"
        else:
            raise ValueError
    
    # Build the treatments dictionary
    treatments = {}
    for n, treatment in experiment["Treatment"].items():
        treatments[n] = {}
        for factor, f in FACTOR_LEVELS.items():
            if factor in experiment:
                level = experiment[factor].get(treatment[f], False)
                if level:
                    treatments[n][factor] = level
        treatments[n]["SimulationControls"] = sim_controls_dict.get(
            treatment["sm"], False
        )
        assert treatments[n]["SimulationControls"]
        treatments[n]["SimulationControls"] = SimulationControls(
            **treatments[n]["SimulationControls"]
        )
    return treatments
        
def create_filex(field:Field, cultivar:Cultivar, planting:Planting, 
                simulation_controls:SimulationControls, harvest:Harvest=None,
                initial_conditions:InitialConditions=None, 
                fertilizer:Fertilizer=None, soil_analysis:SoilAnalysis=None, 
                irrigation:Irrigation=None, residue:Residue=None, 
                chemical:Chemical=None, tillage:Tillage=None):
    """
    Returns the FileX as a string
    """
    experiment_name = field["id_field"][:4] +\
        simulation_controls["general"]["sdate"].strftime('%y01') + cultivar.code
    out_str = f"*EXP.DETAILS: {experiment_name}\n\n"
    treatment = Treatment(**{
        "r": 1, "o": 0, "c": 0, "tname": "DSSATTools", "cu": 1, "fl": 1, 
        "mp": 1, 'sm': 1, 'me': 0,
        "sa": 1 if soil_analysis else 0,  
        "ic": 1 if initial_conditions else 0,
        'mi': 1 if irrigation else 0,
        'mf': 1 if fertilizer else 0,
        'mr': 1 if residue else 0,
        'mc': 1 if chemical else 0,
        'mt': 1 if tillage else 0,
        'mh': 1 if harvest else 0
    })
    out_str += treatment._write_section() + "\n"
    out_str += cultivar._write_section() + "\n"
    out_str += field._write_section() + "\n"
    out_str += planting._write_section() + "\n"
    if soil_analysis: out_str += soil_analysis._write_section() + "\n"
    if initial_conditions: out_str += initial_conditions._write_section() + "\n"
    if irrigation: out_str += irrigation._write_section() + "\n"
    if fertilizer: out_str += fertilizer._write_section() + "\n"
    if residue: out_str += residue._write_section() + "\n"
    if chemical: out_str += chemical._write_section() + "\n"
    if tillage: out_str += tillage._write_section() + "\n"
    if harvest: out_str += harvest._write_section() + "\n"
    out_str += simulation_controls._write_section()

    return out_str
    
    