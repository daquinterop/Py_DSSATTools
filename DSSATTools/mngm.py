"""
New management module
"""
import pandas as pd
from datetime import date
from .base.partypes import (
    DateType, MethodType, NumberType, Event, Schedule
)
import typing
import inspect

EVENT_TYPES = []
    
class Planting(Event):
    '''
    Class to define a single planting event
    '''
    # Typehints must be in order following DSSAT column order
    pdate:DateType
    edate:DateType
    ppop:NumberType
    ppoe:NumberType
    plme:MethodType
    plds:MethodType
    plrs:NumberType
    plrd:NumberType
    pldp:NumberType
    plwt:NumberType
    page:NumberType
    penv:NumberType
    plph:NumberType
    sprl:NumberType
    def __init__(self, pdate:date, ppop:float, plrs:float, 
                 ppoe:float=None, plds:str="R", plrd:float=0, plme:str="S", 
                 pldp:float=5, plwt:float=None, page:float=None, penv:float=None, 
                 plph:float=None, sprl:float=0, edate:date=None):
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
        """
        args, _, _, values = inspect.getargvalues(inspect.currentframe())
        self.__type_hints = typing.get_type_hints(self)
        super().__init__()
        for name, _ in self.__type_hints.items():
            super().__setitem__(name, values[name])

    @property
    def pars_fmt(self):
        return {
            "pdate": "%y%j", "edate": "%y%j", "ppop": ">5.1f", "plrs": ">5.0f", 
            "ppoe": ">5.1f", "plds": ">5", "plrd": ">5.0f", "plme": ">5", 
            "pldp": ">5.0f", "plwt": ">5.1f", "page": ">5.0f", "penv": ">5.1f", 
            "plph": ">5.0f", "sprl": ">5.0f"
        }

    @property
    def prefix(self):
        return "p"
    
    
# class Harvest(Event):
#     def __init__(self):
#         return
    
# class Irrigation(Schedule):
#     def __init__(self):
#         return
    
# class Fertilizer(Schedule):
#     def __init__(self):
#         return

# class Residue(Schedule):
#     def __init__(self):
#         return
    
# class Chemicals(Schedule):
#     def __init__(self):
#         return
    
# class Tillage(Schedule):
#     def __init__(self):
#         return
    