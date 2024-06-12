"""
Parameter types
"""
from datetime import date, datetime
from collections.abc import MutableMapping, MutableSequence
from pandas import DataFrame
import numpy as np
from dataclasses import dataclass

DATE_VARS = [ # This might not be needed as I won't let the user deal with the base classes
    "p.pdate"
]
METHOD_VARS = {
    "p.plme": ["B", "C", "H", "I", "N", "P", "R", "S", "T", "V"],
    "p.plds": ["H", "R", "U"]
}

class MethodType(str):
    def __new__(cls, name, value, fmt):
        assert value in METHOD_VARS[name], \
            f"{name} must be one of {METHOD_VARS[name]}"
        assert name in METHOD_VARS, f"{name} is not defined as a MethodType"
        return super().__new__(cls, value)

    def __init__(self, name, value, fmt):
        self.name = name
        self.fmt = fmt

    @property
    def str(self):
        return format(self, self.fmt)
    
class DateType(date):
    def __new__(cls, name, value, fmt):
        if value is None:
            value = date(9999, 1, 1)
        assert isinstance(value, (date, datetime)), \
            f"value must be a datetime.datetime or datetime.date instance"
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

class Event(MutableMapping):
    """
    Generic class to handle a single event, e.g. Irrigation event, planting event,
    tillage event, etc.
    """
    __data = {}
    def __init__(self):
        super().__init__()
        
    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __setitem__(self, key, value):
        type_hints = self.__dict__[f"_{type(self).__name__}__type_hints"]
        if key not in type_hints:
            raise KeyError(key)
        if "ECO#" in key: 
            raise Exception(
                "The ecotype code can't be changed. If any change is to be done in the ecotype modify the ecotype parameters directly"
            )
        self.__data[key] = type_hints[key](
            f'{self.prefix}.{key}', value, self.pars_fmt[key]
        )

    def __delitem__(self, k):
        raise NotImplementedError

    def __getitem__(self, key):
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
    
class Schedule(MutableSequence):
    def __init__(self):
        return 
    
    def from_df(self, df:DataFrame):
        return
    
    def write(self):
        return