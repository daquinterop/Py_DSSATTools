"""
Parameter types
"""
from datetime import date, datetime
from collections.abc import MutableMapping, MutableSequence
from pandas import DataFrame
import numpy as np
from typing import Union, Type

DATE_VARS = [ # This might not be needed as I won't let the user deal with the base classes
    "pdate"
]
METHOD_VARS = {
    "plme": ["B", "C", "H", "I", "N", "P", "R", "S", "T", "V"],
    "plds": ["H", "R", "U"],
    "hstg": [f"GS0{i:02d}" for i in range(50)], #TODO: Deppends of crop, how to address that? https://github.com/DSSAT/dssat-csm-os/blob/develop/Data/GRSTAGE.CDE
    "hcom": ["C", "L", "H", None],
    "hsize": ["A", "S", "M", "L", None],
    "cr": ["MZ", "SB"]
}

class MethodType(str):
    def __new__(cls, name, value, fmt):
        if isinstance(value, str):
            value = value.strip()
        elif np.isnan(value):
            value = None
        else:
            pass
        if (value == "-99"):
            value = None
        assert value in METHOD_VARS[name], \
            f"{name} must be one of {METHOD_VARS[name]}"
        if value is None:
            value = ""
        assert name in METHOD_VARS, f"{name} is not defined as a MethodType"
        return super().__new__(cls, value)

    def __init__(self, name, value, fmt):
        self.name = name
        self.fmt = fmt

    @property
    def str(self):
        if (self is None) or (self == ""):
            return format(-99, f'{self.fmt[:2]}.0f')
        else:
            return format(self, self.fmt)
            
    
class DateType(date):
    def __new__(cls, name, value, fmt):
        if isinstance(value, (date, datetime)):
            pass
        elif value is None:
            value = date(9999, 1, 1)
        elif int(value) == -99:
            value = date(9999, 1, 1)
        elif isinstance(value, str):
            try:
                value = datetime.strptime(value, "%y%j")
            except:
                try:
                    value = datetime.strptime(value, "%Y%j")
                except ValueError:
                    raise ValueError(f"{value} can't be interpreted as a date")
        else:
            raise ValueError(f"value must be datetime, date, None, -99 or some date representation")            
        return super().__new__(cls, value.year, value.month, value.day)
    
    def __init__(self, name, value, fmt):
        # I'm not sure if I should do this. I don't expect users to use this classes
        self.name = name
        self.fmt = fmt
    
    @property
    def str(self):
        if self.year == 9999 :
            len_fmt = len(self.strftime(self.fmt))
            return format(-99, f'>{len_fmt}.0f')
        else:
            return format(self, self.fmt)
    
class NumberType(float):
    def __new__(cls, name, value, fmt):
        if value is None:
            value = np.nan
        elif int(float(value)) == -99:
            value = np.nan
        else:
            pass
        return super().__new__(cls, value)
    
    def __init__(self, name, value, fmt):
        self.name = name
        self.fmt = fmt

    @property
    def str(self):
        if np.isnan(self):
            return format(-99, f'{self.fmt[:2]}.0f')
        else:
            return format(self, self.fmt)
        
class DescriptionType(str):
    def __new__(cls, name, value, fmt):
        if isinstance(value, str):
            value = value.strip()
        elif np.isnan(value):
            value = None
        else:
            pass
        if (value is None) or (value == "-99"):
            value = ""
        return super().__new__(cls, value)

    def __init__(self, name, value, fmt):
        self.name = name
        self.fmt = fmt

    @property
    def str(self):
        if (self is None) or (self == ""):
            return format(-99, f'{self.fmt}.0f')
        else:
            return format(self, self.fmt)

class Record(MutableMapping):
    """
    Generic class to handle a single event, e.g. Irrigation event, planting event,
    tillage event, etc.
    """
    def __init__(self):
        self.__data = {}
        super().__init__()
        
    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __setitem__(self, key, value):
        key = key.lower()
        if key not in self.dtypes:
            raise KeyError(key)
        if "ECO#" in key: 
            raise Exception(
                "The ecotype code can't be changed. If any change is to be done in the ecotype modify the ecotype parameters directly"
            )
        self.__data[key] = self.dtypes[key](
            f'{key}', value, self.pars_fmt[key]
        )

    def __delitem__(self, k):
        raise NotImplementedError

    def __getitem__(self, key):
        key = key.lower()
        return self.__data[key]

    def __contains__(self, k):
        return k in self.__data
    
    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__data.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))
    
    def parameters(self):
        return self.__data
    
    def write(self):
        return " ".join([par.str for name, par in self.items()])
    
class Tabular(MutableSequence):
    top: Union[Record, Type[None]] # For those tabular sections that also have non-tabular information at top
    def __init__(self):
        return 
    
    def from_df(self, df:DataFrame):
        return
    
    def write(self):
        return
    
class SimulationControls:
    def __init__(self):
        return
    
class Field:
    def __init__(self):
        return