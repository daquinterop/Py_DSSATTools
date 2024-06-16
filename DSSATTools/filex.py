"""
New management module
"""
from datetime import date
from .base.partypes import (
    DateType, MethodType, NumberType, Record, Tabular, DescriptionType
)
    
class Planting(Record):
    '''
    Class to define a single planting event
    '''
    prefix = "p"
    dtypes = {
        "pdate": DateType, "edate": DateType, "ppop": NumberType, 
        "ppoe": NumberType, "plme": MethodType, "plds": MethodType, 
        "plrs": NumberType, "plrd": NumberType, "pldp": NumberType, 
        "plwt": NumberType, "page": NumberType, "penv": NumberType, 
        "plph": NumberType, "sprl": NumberType, "plname": DescriptionType
    }
    pars_fmt = {
        "pdate": "%y%j", "edate": "%y%j", "ppop": ">5.1f", "plrs": ">5.0f", 
        "ppoe": ">5.1f", "plds": ">5", "plrd": ">5.0f", "plme": ">5", 
        "pldp": ">5.0f", "plwt": ">5.1f", "page": ">5.0f", "penv": ">5.1f", 
        "plph": ">5.0f", "sprl": ">5.0f", "plname": ">25"
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
        ppoe: float, optional
            Plant population at emergence, m-2. Equal to ppop if not set.
        plrd: float, optional
            Row direction, degrees from N
        plme: str, optional
            Planting method. Direct dry seed is default.
        pldp: float, optional
            Planting depth, cm
        plwt: float, optional. It is mandatory for Potato crop
            Planting material dry weight, kg ha-1
        page: float, optional. Mandatory when plme is Transplanting.
            Transplant age, days
        penv: float, optional.
            Transplant environment, oC
        plph: float, optional.
            Plants per hill (if appropriate)
        sprl: float, optional
            Initial sprout lenght, cm
        plname: str, optional
            Planting treatment name
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


class Cultivars(Record):
    prefix = "c"
    dtypes = {
        "cr": MethodType, "ingeno": DescriptionType, "cname": DescriptionType
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
            Crop code
        ingeno: str
            Cultivar code
        cname: str
            Cultivar name
        """
        super().__init__()
        kwargs = {
            'cr': cr, 'ingeno': ingeno, 'cname': cname, 
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)


class Harvest(Record):
    prefix = "h"
    dtypes = {
        "hdate": DateType, "hstg": MethodType, "hcom": MethodType,
        "hsize": MethodType, "hpc": NumberType, "hbpc": NumberType, 
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
            Specified growth stage for harvesting.
        hcom: str
            Harvest component: C (Canopy), L (Leaves), or H (Harvest product)
        hsize: str
            Harvest size category: A (All), S (Small - less than 1/3 full size),
            M (Medium - from 1/3 to 2/3 full size), L (Large - greater than 2/3 full size)
        hpc: float
            Harvest percentage, %
        hbpc: float
            Byproduct takeoff, %. This is especially applicable when, in addition
            to the grains, the straw is also harvested
        """
        super().__init__()
        kwargs = {
            "hdate": hdate, "hstg": hstg, "hcom": hcom, "hsize": hsize, 
            "hpc": hpc, "hbpc": hbpc, "hname": hname
        }
        for name, value in kwargs.items():
            super().__setitem__(name, value)

class InitialConditions(Tabular):
    def __init__(self):
        return
    
class Irrigation(Tabular):
    def __init__(self):
        return
    
class Fertilizer(Tabular):
    def __init__(self):
        return

class Residue(Tabular):
    def __init__(self):
        return
    
class Chemicals(Tabular):
    def __init__(self):
        return
    
class Tillage(Tabular):
    def __init__(self):
        return

def get_header_range(l, h, pars_fmt):
    """Get variable start and index in the header line"""
    h_fmt = pars_fmt[h]
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
    Asumptions:
    - Values are below their header
    - Each column/header must be right or left justified
    - Treament number is always the first column
    """
    with open(filexpath, "r") as f:
        lines = f.readlines()
    lookup = "section"
    vals_list = []
    experiment = {}
    for l in lines:
        l = l.replace("\n", "")
        if len(l.strip()) == 0:
            if lookup == "values":
                experiment[cls.__name__] = vals_list
                vals_list = []
            lookup = "section"
            continue 
        elif lookup == "header":
            if l[0] == "@":
                header = l.lower().split()
                header_start_end = {
                    h: get_header_range(l, h, cls.pars_fmt) 
                    for h in header[1:]
                }
                lookup = "values"
                continue
        elif lookup == "values":
            vals = {
                key: l[header_start_end[key][0]:header_start_end[key][1]]
                for key in header[1:]
            }
            vals_list.append(cls(**vals))
            continue
        elif lookup == "section":
            if l[:6] == "*PLANT":
                cls = Planting
                lookup = "header"
            elif l[:6] == "*CULTI":
                cls = Cultivars
                lookup = "header"
            elif l[:6] == "*HARVE":
                cls = Harvest
                lookup = "header"
            else:
                continue
        else:
            raise ValueError
    return
    