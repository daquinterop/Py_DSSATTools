"""
Parameter types
"""
from datetime import date, datetime
from collections.abc import MutableMapping, MutableSequence
from pandas import DataFrame
import numpy as np
from typing import Union, Type
from DSSATTools.crop import CROPS_MODULES

CODE_VARS = {
    "plme": ["B", "C", "H", "I", "N", "P", "R", "S", "T", "V"],
    "plds": ["H", "R", "U"],
    "hstg": [None] + [f"GS0{i:02d}" for i in range(50)], #TODO: Deppends of crop, how to address that? https://github.com/DSSAT/dssat-csm-os/blob/develop/Data/GRSTAGE.CDE
    "hcom": ["C", "L", "H", None],
    "hsize": ["A", "S", "M", "L", None],
    "cr": [
        'AL', 'BA', 'BC', 'BM', 'BH', 'BN', 'BR', 'BS', 'CB', 'CH', 'CI', 'CN', 
        'CO', 'CP', 'CS', 'FA', 'FB', 'GB', 'GG', 'GY', 'LT', 'ML', 'MZ', 'NP', 
        'PE', 'PI', 'PN', 'PO', 'PP', 'PR', 'PT', 'QU', 'RI', 'SB', 'SC', 'SF', 
        'SG', 'SQ', 'SR', 'SS', 'SU', 'SW', 'TF', 'TM', 'TN', 'TR', 'VB', 'WH', 
    ],
    "fmcd": [None] + [f"FE{i:03d}" for i in range(1, 71)] + \
            [f"FE{i:03d}" for i in range(201, 213)] + \
            [f"FE{i:03d}" for i in range(300, 313)] + \
            [f"FE{i:03d}" for i in range(400, 409)] + \
            [f"FE{i:03d}" for i in range(500, 514)] + \
            ['FE600', 'FE601', 'FE602', 'FE620', 'FE621', 'FE622', 'FE623',
             'FE640', 'FE641', 'FE660', 'FE661', 'FE662', 'FE663', 'FE664',
             'FE665', 'FE666', 'FE667', 'FE668', 'FE669', 'FE670', 'FE680',
             'FE681', 'FE682', 'FE683', 'FE684', 'FE685', 'FE700', 'FE701',
             'FE702', 'FE720', 'FE721', 'FE722', 'FE723', 'FE740', 'FE900',
             "IB001", "IB002"],
    "facd": [None] + [f"AP{i:03d}" for i in range(1, 21)],
    "smhb": [None] + ["SA011", "SA012"],
    "smpx": [None] + [f"SA{i:03d}" for i in range(1, 11)],
    "smke": [None] + ["SA013", "SA014", "SA015"],
    "iame": [None, "IB001"] + [f"IR{i:03d}" for i in range(1, 12)],
    "rcod": [None] + [
        'RE001','RE101','RE201','RE301','RE999','RE002','RE003', 'RE004',
        'RE005','RE006','RE102','RE103','RE104','RE105','RE106', 'RE107',
        'RE108','RE109','RE110','RE111','RE202','RE203','RE204', 'RE205',
        'RE206','RE207','RE208','RE302','RE303','RE304','RE305', 'RE306',
        'RE401','RE402','RE403','RE404', 
        "IB001"
    ],
    "cht": [],
    "chcod": [
        'CH001', 'CH002', 'CH003', 'CH004', 'CH005', 'CH006', 'CH007', 'CH008',
        'CH009', 'CH010', 'CH011', 'CH021', 'CH022', 'CH023', 'CH024', 'CH025', 
        'CH026', 'CH027', 'CH028', 'CH029', 'CH030', 'CH031', 'CH032', 'CH033', 
        'CH034', 'CH035', 'CH036', 'CH037', 'CH038', 'CH039', 'CH040', 'CH041', 
        'CH042', 'CH043', 'CH044', 'CH045', 'CH051', 'CH052', 'CH053', 'CH054', 
        'CH055', 'CH056', 'CH057', 'CH100', 'CH101', 'CH102',  None
    ],
    "timpl": [None] + [
        'TI001', 'TI002', 'TI003', 'TI004', 'TI005', 'TI006', 'TI007', 'TI008', 
        'TI009', 'TI010', 'TI011', 'TI012', 'TI013', 'TI014', 'TI015', 'TI016', 
        'TI017', 'TI018', 'TI019', 'TI020', 'TI021', 'TI022', 'TI023', 'TI024', 
        'TI025', 'TI026', 'TI031', 'TI032', 'TI033', 'TI034', 'TI035', 'TI036', 
        'TI037', 'TI038', 'TI039', 'TI041', 'TI042',
    ],
    "sltx": [None] + [
        "C", "CL", "L", "LS", "S", "SC", "SCL", "SI", "SIC", "SICL", "SIL", 
        "SL", "SA"
    ],
    "fldt": ["DR000", "DR001", "DR002", "DR003", "IB000"],
    "flst": [None, "00000", "0"],
    "flhst": [None] + ["FH101", "FH102", "FH201", "FH202", "FH301", "FH302"],
    "start": ["S"],
    "smodel": ["", None] + list(CROPS_MODULES.values()),
    "switch": ["Y", "N"],
    "co2": ["M", "D", "W"],
    "wther": ["M", "G", "S", "W"], 
    "incon": ["M", ], 
    "light": ["E", ],
    "evapo": ["R", "F", "S", "T"], 
    "infil": ["S", "R", "N"], 
    "photo": ["C", "L", "R"],
    "hydro": ["R", ], 
    "nswit": ["1", ], 
    "mesom": ["G", "P"],
    "mesev": ["R", "S"], 
    "mesol": ["1", "2", "3"],
    "plant": ["A", "F", "R", ], 
    "irrig": ["A", "D", "F", "N", "P", "R", "W"], 
    "ferti": ["D", "N", "R", ],
    "resid": ["D", "N", "R", ], 
    "harvs": ["A", "D", "M", "R", "W", "X", "Y", "Z"], 
    "vbose": ["A", "0", "D", "N", "Y"],
    "fmopt": ["C", "A"],
    "naoff": ["IB001", "GS000"]
}
CODE_VARS["pcr"] = CODE_VARS["cr"] 
CODE_VARS["focd"] = CODE_VARS["fmcd"]
CODE_VARS["ioff"] = CODE_VARS['hstg'] + ["IB001"]
CODE_VARS["irop"] = CODE_VARS["iame"]
CODE_VARS["rmet"] = CODE_VARS["facd"]
CODE_VARS["chme"] = CODE_VARS["facd"]
CODE_VARS["water"] = CODE_VARS["nitro"] = CODE_VARS["symbi"] = \
    CODE_VARS["phosp"] = CODE_VARS["potas"] = CODE_VARS["dises"] = \
    CODE_VARS["chem"] = CODE_VARS["till"] = CODE_VARS["fname"] =  \
    CODE_VARS["ovvew"] = CODE_VARS["sumry"] = CODE_VARS["grout"] = \
    CODE_VARS["caout"] = CODE_VARS["waout"] = CODE_VARS["niout"] =  \
    CODE_VARS["miout"] = CODE_VARS["diout"] = CODE_VARS["chout"] = \
    CODE_VARS["opout"] = CODE_VARS["switch"]
CODE_VARS["iroff"] = CODE_VARS["ioff"] # TODO: These are exactly the same!
CODE_VARS["imeth"] = CODE_VARS["iame"] # TODO: These are exactly the same!
CODE_VARS["ncode"] = CODE_VARS["fmcd"]

PROTECTED_ATTRS = [
    "prefix", "pars_fmt", "dtypes", "table_dtype", "table_index", 
    "section_header"
    ]
SECTION_HEADERS = {
    "Planting": "*PLANTING DETAILS",
    "Cultivar": "*CULTIVARS",
    "Harvest": "*HARVEST DETAILS",
    "InitialConditions": "*INITIAL CONDITIONS",
    "Fertilizer": "*FERTILIZERS (INORGANIC)",
    "SoilAnalysis": "*SOIL ANALYSIS",
    "Irrigation": "*IRRIGATION AND WATER MANAGEMENT",
    "Residue": "*RESIDUES AND ORGANIC FERTILIZER",
    "Chemical": "*CHEMICAL APPLICATIONS",
    "Tillage": "*TILLAGE AND ROTATIONS",
    "Field": "*FIELDS",
    "Treatment": "*TREATMENTS                        -------------FACTOR LEVELS------------"
}
FACTOR_LEVELS = {
    "Cultivar": "cu",
    "Field": "fl",
    "SoilAnalysis": "sa",
    "InitialConditions": "ic",
    "Planting": "mp",
    "Irrigation": "mi",
    "Fertilizer": "mf",
    "Residue": "mr",
    "Chemical": "mc",
    "Tillage": "mt",
    "Harvest": "mh",
    "SimulationControls": "sc"
}


class CodeType(str):
    def __new__(cls, name, value, fmt):
        if isinstance(value, str):
            value = value.strip()
        elif value is None:
            pass
        elif np.isnan(value):
            value = None
        else:
            pass

        if (value == "-99"):
            value = None
        assert (value in CODE_VARS[name]) or (CODE_VARS[name] == []), \
            f"{name} must be one of {CODE_VARS[name]}"
        if value is None:
            value = ""
        assert name in CODE_VARS, f"{name} is not defined as a CodeType"
        return super().__new__(cls, value)

    def __init__(self, name, value, fmt):
        self.name = name
        if fmt[0] == ".": # For the case of headers with leading points
            fmt = fmt[1:]
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
        if fmt[0] == ".": # For the case of headers with leading points
            fmt = fmt[1:]
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
        elif isinstance(value, str) and (len(value.split()) == 0):
            value = np.nan
        elif int(float(value)) == -99:
            value = np.nan
        else:
            pass
        return super().__new__(cls, value)
    
    def __init__(self, name, value, fmt):
        self.name = name
        if fmt[0] == ".": # For the case of headers with leading points
            fmt = fmt[1:]
        self.fmt = fmt

    @property
    def str(self):
        if np.isnan(self):
            return format(-99, f'{self.fmt.split(".")[0]}.0f')
        else:
            return format(self, self.fmt)

        
class DescriptionType(str):
    def __new__(cls, name, value, fmt):
        if isinstance(value, str):
            value = value.strip()
        elif value is None:
            pass
        elif np.isnan(value):
            value = None
        else:
            pass
        if (value is None) or (value == "-99"):
            value = ""
        return super().__new__(cls, value)

    def __init__(self, name, value, fmt):
        self.name = name
        if fmt[0] == ".": # For the case of headers with leading points
            fmt = fmt[1:]
        self.fmt = fmt

    @property
    def str(self):
        if (self is None) or (self == ""):
            return format(-99, f'{self.fmt}.0f')
        else:
            return format(self, self.fmt)
        

class TableType(MutableSequence):
    '''
    This is the class to handle table-like information in the fileX
    sections. A different class is created to:
        - Make sure the tables will contain a specific record. e.g. 
        fertilizer table will contain only fertilizer records and not
        irrigation records or some other record.
        - Table index is unique. e.g. Initial conditions won't have the
        same soil layer defined more than once. This only for soil layers.
        Schedules can have more than one value the same day (Multiple tillage
        events the same day)
    '''
    def __init__(self, values, dtype):
        if values is None:
            super().__init__()
            self.__data_dtype = dtype
            self.__data = []
            return
        # If values is a dataframe
        # TODO:
        # Verify that values is a list, tuple, or set
        assert isinstance(values, (list, set, tuple)), \
            f"Table must be a list of {dtype.__name__} records"
        # Verify that all elements in list are the correct dtype
        if not all([isinstance(val, dtype) for val in values]):
            raise TypeError(
                f"Records in table must be {dtype.__name__} type"
            )
        # # Raise if repeteaded ids
        # unique_ids = set([val[dtype.table_index] for val in values])
        # if len(unique_ids) != len(values):
        #     raise ValueError(
        #         f"Repeteaded values of {dtype.table_index} where found. "
        #         f"{dtype.table_index} values must be unique"
        #     )
        super().__init__()
        self.__data_dtype = dtype
        self.__data = [
            val for val in values
        ]
        self.__checkindex__()
        
    def __checkindex__(self):
        if self.__data_dtype.table_index is not None: 
            idx = self.__data_dtype.table_index
            assert len(set([v[idx] for v in self.__data])) \
                == len(self.__data), \
                f"{idx} values must be unique"

    def __getitem__(self, idx):
        return self.__data[idx]
    
    def __setitem__(self):
        raise NotImplementedError
        # if not isinstance(value, self.__data_dtype):
        #     raise TypeError(f"Value must be {self.__data_dtype.__name__} type")
        # assert idx == value[self.__data_dtype.table_index], (
        #     f"key does not correspont to {self.__data_dtype.table_index} in"
        #     f"the value to set ({idx}!={value[self.__data_dtype.table_index]})"
        # )
        # self.__data[idx] = value
    
    def __delitem__(self, idx):
        self.__data.pop(idx)
        
    def __len__(self):
        return len(self)

    def append(self, item):
        self.__data.append(item)
    
    def insert(self):
        raise NotImplementedError
    
    def _write_table(self):
        out_str = ""
        for n, record in enumerate(self.__data):
            if n == 0:
                for var in record.dtypes.keys():
                    var = record[var]
                    fmt = var.fmt.split('.')[0]
                    if fmt == "%y%j":
                        fmt = ">5"
                    out_str += \
                        f"{format(var.name.upper(), fmt)} "
                out_str += "\n"
            out_str += f"{record._write_row()}"
        return out_str
    
    def __repr__(self):
        kws = [f"{value!r}" for value in self.__data]
        return "{}({})".format(type(self).__name__, ", ".join(kws))
    
    def __len__(self):
        return len(self.__data)
    

class Record(MutableMapping):
    """
    Generic class to handle a single fileX row. The name and type of 
    variables contained in the record are defined in the child object.
    """ 
    prefix:dict # Prefix on FILEX
    dtypes:dict # Data type of each parameter in the record
    pars_fmt:dict # Format of each parameter
    n_tiers:int = 1 # Number of tiers. Sections like Field have more than one
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
    
    def __setattr__(self, name, value):
        if name in PROTECTED_ATTRS:
            raise AttributeError(f"Can't modify {name} attribute")
        else:
            super().__setattr__(name, value)
    
    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__data.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))
    
    def parameters(self):
        return self.__data
    
    def _write_row(self):
        return " ".join([
            par.str for name, par in self.items()
            if name != "table"
        ]) + "\n"
    
    def _write_section(self):
        header = ["@"+self.prefix.upper()]
        for key, fmt in self.pars_fmt.items():
            if fmt == "%y%j":
                fmt = ">5"
            if fmt[0] == ".":
                leading = "."
                fmt = fmt[1:]
            else:
                leading = ""
            fmt = leading + fmt.split(".")[0]
            header.append(format(key.upper(), fmt))
        out_str = SECTION_HEADERS[type(self).__name__] + "\n"
        out_str += " ".join(header) + "\n" + " 1 " + self._write_row()
        return out_str
    

class TabularRecord(Record):
    '''
    Basically the same as record, with a table attribute. The 
    table is list of Records.
    '''
    table_dtype:Type # Data type contained in the table
    table_index:str # Unique id for the table
    table:TableType # The table
    def __init__(self):
        super().__init__()
        self.table = []
        return 
    
    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.items()]
        out_str = "{}({}".format(type(self).__name__, ", ".join(kws))
        out_str += f", table={str(self.table)})"
        return out_str
    
    def __setattr__(self, name, value):
        if name == "table":
            # TODO: Implement DataFrame input
            table = TableType(value, self.table_dtype)
            super().__setattr__(name, table)
        else:
            super().__setattr__(name, value)

    def _write_section(self):
        out_str = super()._write_section()
        if len(self.dtypes) == 0:
            out_str = out_str.split("\n")[0]
            out_str += "\n"
        table_str = self.table._write_table().split("\n")
        out_str += f"@{self.prefix.upper()} {table_str[0]}\n"
        for row in table_str[1:-1]: # Table string ends with \n
            out_str += f" 1 {row}\n"
        return out_str
    
    def __bool__(self):
        return len(self.table) > 0

    