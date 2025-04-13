"""
Parameter types.

Contains classes to handle the different sections of the fileX. Each section
is represented by its own class. Overall, there are four types of base 
classes that are used to construct all the sections:

    Record: 
    It is to be interpreted as a single row in the FileX. There
    are three sections that are built based only in this class: Planting, 
    Cultivar, and Harvest. Those are basically the sections that can only
    contain a single row per treatment.

    TabularRecord: 
    It is to be interpreted as those sections that are formed by tabular 
    entries. For example, all the other sections that can contain more 
    than one row per treatment. Overall, there are two types of 
    TabularRecords defined. Soil Tables (Soil Analysis, Initial
    Conditions), and Schedule Tables (Fertilizer, Irrigation, Residue,
    Chemical, Tillage). 

The order of the elements in the pars_fmt and dtype dictionaries is extremely
important. They must follow the order of the columns in the DSSAT files.
    
"""
from datetime import date, datetime
from collections.abc import MutableMapping, MutableSequence
from pandas import DataFrame
import numpy as np
from typing import Type
import re
import os
from .utils import detect_encoding


CROPS_MODULES = {
    "Maize": "MZCER",
    'PearlMillet': "MLCER",
    'Sugarbeet': "BSCER",
    'Rice': "RICER",
    'Sorghum': "SGCER",
    'SweetCorn': "SWCER",
    'Alfalfa': "PRFRM",
    'Bermudagrass': "PRFRM",
    'Soybean': "CRGRO",
    'Canola': "CRGRO",
    'Sunflower': "CRGRO",
    'Potato': "PTSUB",
    'Tomato': "CRGRO",
    'Cabbage': "CRGRO",
    'Sugarcane': "SCCAN",
    "Wheat": "CSCER",
    "DryBean": "CRGRO",
    "Cassava": "CSYCA"
}
CODE_VARS = {
    "plme": ["B", "C", "H", "I", "N", "P", "R", "S", "T", "V", None],
    "plds": ["H", "R", "U", None],
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
             "IB001", "IB002", 'SI001', 'IFE01', '0', '00000', '0000'],
    "facd": [None] + [f"AP{i:03d}" for i in range(1, 21)],
    "smhb": [None, "IB001", "IB00", 'B001'] + [f"SA{i:03d}" for i in range(16)],
    "smpx": [None, "IB001", "IB00", 'B001'] + [f"SA{i:03d}" for i in range(16)],
    "smke": [None, "IB001", "IB00", 'B001'] + [f"SA{i:03d}" for i in range(16)],
    "iame": [None, "IB001", "IB00", 'B001', 'SI001', 'IBI01'] +\
          [f"IR{i:03d}" for i in range(1, 12)],
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
        "SL", "SA", 'LO', 'CLLO'
    ],
    "fldt": ["DR000", "DR001", "DR002", "DR003", "IB000", None, "-99"],
    "flst": [None, "00000", "0", '0000'],
    "flhst": [None] + ["FH101", "FH102", "FH201", "FH202", "FH301", "FH302"],
    "start": ["S", 'P'],
    "smodel": ["", None] + list(CROPS_MODULES.values()),
    "switch": ["Y", "N"],
    "co2": ["M", "D", "W"],
    "wther": ["M", "G", "S", "W"], 
    "incon": ["M", ], 
    "light": ["E", ],
    "evapo": ["R", "F", "S", "T", 'H'], 
    "infil": ["S", "R", "N"], 
    "photo": ["C", "L", "R", "V"],
    "hydro": ["R", ], 
    "nswit": ["1", '0'], 
    "mesom": ["G", "P"],
    "mesev": ["R", "S"], 
    "mesol": ["1", "2", "3"],
    "plant": ["A", "F", "R", ], 
    "irrig": ["A", "D", "F", "N", "P", "R", "W"], 
    "ferti": ["D", "N", "R", ],
    "resid": ["D", "N", "R", 'A'], 
    "harvs": ["A", "D", "M", "R", "W", "X", "Y", "Z"], 
    "vbose": ["A", "0", "D", "N", "Y"],
    "fmopt": ["C", "A"],
    "naoff": ["IB001", "GS000", 'SI001'],
    'scom': ['BN', 'G', 'Y', 'BL', 'R', 'BROWN', 'BK', 'YR', None],
    "soil_clasification": [
        'C', 'CL', 'L', 'LS', 'S', 'SC', 'SCL', 'SI', 'SIC', 'SICL', 
        'SIL', 'SL', None
    ]
}
CODE_VARS["pcr"] = CODE_VARS["cr"] + [None]
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
    "section_header", "code", "smodel", "spe_file", "spe_path", "cul_dtypes",
    "cul_pars_fmt", "eco_dtypes", "eco_pars_fmt"
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
    "Treatment": "*TREATMENTS                        -------------FACTOR LEVELS------------",
    "Mow": '!This file is for parameters controlling simulated mowing events for alfalfa\n!for CROPGRO-Forage model.\n!Mow height is not used any where, except to affect canopy height as m or cm.'
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

def _format(s, fmt):
    """
    Formats and trim the string to match the specific width
    """
    if fmt == "%y%j":
        width = 5
    elif fmt == "%Y%j":
        width = 7
    else:
        width = int(re.findall("\d+", fmt.split(".")[0])[0])
    return format(s, fmt)[:width]

def clean_comments(lines):
    clean_lines = []
    for line in lines:
        if '!' in line[:3]:
            continue
        if len(line) < 2:
            continue
        clean_lines.append(line)
    return clean_lines

class CodeType(str):
    """
    A class for Code variables in the DSSAT FileX. For example: fertilizer
    application methods, fertilizer materials, tillage operations, irrigation
    methods, etc. Those are the variables that are defined using a Dropdown menu 
    in DSSAT XBuild. 
    CodeType variables can only take the value that is allowed for that specific
    variable. 
    """
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
            return _format(-99, f'{self.fmt[:2]}.0f')
        else:
            return _format(self, self.fmt)


class DateType(date):
    """
    A Class to handle all date variables in DSSAT.
    """
    def __new__(cls, name, value, fmt):
        if isinstance(value, (date, datetime)):
            pass
        elif value is None:
            value = date(9999, 1, 1)
        elif int(value) == -99:
            value = date(9999, 1, 1)
        elif isinstance(value, str):
            if len(value.strip()) < 5:
                value = f"{int(value):05d}"
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
            return _format(-99, f'>{len_fmt}.0f')
        else:
            return _format(self, self.fmt)


class NumberType(float):
    """
    A class to handle all Number type varibles in DSSAT.
    """
    def __new__(cls, name, value, fmt):
        if value is None:
            value = np.nan
        elif isinstance(value, str) and (len(value.split()) == 0):
            value = np.nan
        elif float(value) == -99.:
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
            return _format(-99, f'{self.fmt.split(".")[0]}.0f')
        else:
            return _format(self, self.fmt)

        
class DescriptionType(str):
    """
    A Class to handle the Description type variables in all DSSAT files. This
    includes all the user defined code-like variables, such as Soil profiles' id,
    INSI codes, description and name of treatments, cultivars, ecotypes, etc.
    """
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
            return _format(-99, f'{self.fmt}.0f')
        else:
            return _format(self, self.fmt)
        

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
        if isinstance(values, DataFrame):
            values = list(values.apply(
                lambda row: dtype(**{
                    par: row.get(par)
                    for par in dtype.dtypes.keys()
                }), axis=1
            ))

        # Verify that values is a list, tuple, or set
        assert isinstance(values, (list, set, tuple)), \
            f"Table must be a list of {dtype.__name__} records"
        # Verify that all elements in list are the correct dtype
        if not all([isinstance(val, dtype) for val in values]):
            raise TypeError(
                f"Records in table must be {dtype.__name__} type"
            )
        super().__init__()
        self.__data_dtype = dtype
        self.__data = [
            val for val in values
        ]
        self.__checkindex__()
        
    def __checkindex__(self):
        if self.__data_dtype.table_index is not None: 
            idx = self.__data_dtype.table_index
            # Check if index is unique
            assert len(set([v[idx] for v in self.__data])) \
                == len(self.__data), \
                f"{idx} values must be unique"
            # Sort indexes
            self.__data = sorted(
                self.__data, 
                key=lambda x: x[self.__data_dtype.table_index]
            )

    def __getitem__(self, idx):
        return self.__data[idx]
    
    def __setitem__(self):
        raise NotImplementedError
    
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
                    if fmt == "%Y%j":
                        fmt = ">7"
                    out_str += f"{_format(var.name.upper(), fmt)} "
                out_str += "\n"
            out_str += f"{record._write_row()}"
        return out_str
    
    def __repr__(self):
        out_str = "\n"
        for n, record in enumerate(self.__data):
            if n == 0:
                for var in record.dtypes.keys():
                    var = record[var]
                    fmt = var.fmt.split('.')[0]
                    if fmt == "%y%j":
                        fmt = ">5"
                    if fmt == "%Y%j":
                        fmt = ">7"
                    out_str += \
                        f"{_format(var.name.upper(), fmt)} "
                out_str += "\n"
            out_str += f"{record._write_row()}"
            if n >= 5:
                out_str += "...\n..."
                break
        return out_str
    
    def __len__(self):
        return len(self.__data)
    

class Record(MutableMapping):
    """
    Generic class to handle a single fileX, WTH, CUL, ECO, or SOL row. The name 
    and type of variables contained in the record are defined in the child object.

    This is also used for a row of ECO or CUL parmeters
    """ 
    prefix:str # Prefix on FILEX/CUL/ECO
    dtypes:dict # Data type of each parameter in the record
    pars_fmt:dict # Format of each parameter
    n_tiers:int = 1 # Number of tiers. Sections like Field have more than one
    table_index:str = None # Needed for records within tables
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
        if isinstance(self.dtypes[key], tuple): # Field objects
            if issubclass(type(value), Record):
                assert isinstance(value, self.dtypes[key][1])
                self.__data[key] = value
            else:
               self.__data[key] = self.dtypes[key][0](
                f'{key}', value, self.pars_fmt[key]
            )
        elif self.dtypes[key] is Record: # Crop objects
            self.__data[key] = value
        else:
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
        kws = [f"{key}={self[key]!r}" for key in self.dtypes.keys()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))
    
    def parameters(self):
        return self.__data
    
    def _write_row(self):
        return " ".join([
            self[name].str for name in self.dtypes.keys()
            if name != "table"
        ]) + "\n"
    
    def _write_section(self):
        header = ["@"+self.prefix.upper()]
        for key, fmt in self.pars_fmt.items():
            if fmt == "%y%j":
                fmt = ">5"
            if fmt == "%Y%j":
                fmt = ">7"
            if fmt[0] == ".":
                leading = "."
                fmt = fmt[1:]
            else:
                leading = ""
            fmt = leading + fmt.split(".")[0]
            header.append(format(key.upper(), fmt))
        out_str = SECTION_HEADERS[type(self).__name__] + "\n"
        out_str += " ".join(header) + "\n" + " "*len(self.prefix) + "1 " + \
              self._write_row()
        return out_str
    

class TabularRecord(Record):
    '''
    Basically the same as record, with a table attribute. The table is list of 
    Record subinstances.
    '''
    table_dtype:Type # Data type contained in the table
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
            out_str += " "*len(self.prefix) + f"1 {row}\n"
        return out_str
    
    def __bool__(self):
        return len(self.table) > 0

def parse_pars_line(line, fmt):
    """
    A Parser for crop parameters 
    """
    line = line[:]
    pars = {}
    for par, f in fmt.items():
        if f == '%y%j':
            f = '>5'
        if f[0] == ".":
            f = f[1:] # Remove point
        f = f[1:] # Remove right or left justifier
        width = int(f.split(".")[0])
        pars[par] = line[:width].strip()
        line = line[width+1:]
    return pars

def _get_croppars(spe_path, code, dtypes_dict, pars_fmt_dict, par_prefix):
    """
    It constructs and returns a CropPars instance for the Cultivar and Ecotype
    parameters
    """
    assert par_prefix in ("var#", "eco#")
    class CropPars(Record):
        """
        Generic class for Crop parameters
        """
        prefix = par_prefix
        _code = code
        dtypes = dtypes_dict
        pars_fmt = pars_fmt_dict
        def __init__(self):
            if self.prefix == "var#":
                file_path = spe_path[:-3] + "CUL"
            else: 
                file_path = spe_path[:-3] + "ECO"
            if os.path.basename(spe_path)[:2] in ["WH", "CS"]:
                header_character = '$'
            else:
                header_character = '*'

            encoding = detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                file_lines = f.readlines()
            self._file_header = filter(
                lambda x: x[0] == header_character, file_lines
            ).__next__()
            file_lines = clean_comments(file_lines)

            try:
                line = filter(lambda x: code in x[:10], file_lines).__next__()
            except StopIteration:
                raise RuntimeError({
                    "var#": f"Cultivar {code} not in {file_path} file",
                    "eco#": f"Ecotype {code} not in {file_path} file"
                }[self.prefix])
            
            kwargs = parse_pars_line(line[7:], self.pars_fmt)
            super().__init__()
            for name, value in kwargs.items():
                if name != "eco#":
                    super().__setitem__(name, value)
                else:
                    self._ecocode = value.strip()

        def _write_section(self):
            raise NotImplementedError

        def _write_file(self):
            out_str = self._file_header
            out_str += f"\n@{self.prefix.upper()} "
            for key, fmt in self.pars_fmt.items():
                if fmt[0] == ".":
                    leading = "."
                    fmt = fmt[1:]
                else:
                    leading = ""
                fmt = leading + fmt.split(".")[0]
                if key == 'maxparce': # This is spacial case for SugarCane CANEGRO CUL
                    out_str += f" {format('MaxPARCE', fmt)}"
                elif key[:5] == 'tfin_': # This is spacial case for SugarCane CANEGRO ECO
                    out_str += f" {format('TFin_'+key[5:].upper(), fmt)}"
                else:
                    out_str += f" {format(key.upper(), fmt)}"
            out_str += f"\n{self._code} "
            out_str += self._write_row()
            return out_str

        @property
        def str(self):
            return str(self._code)
    
    return CropPars()


class Crop(MutableMapping):
    """
    Generic class for crops
    """
    code:str
    smodel:str 
    spe_file:str
    spe_path:str 
    cul_dtypes:dict
    cul_pars_fmt:dict
    eco_dtypes:dict
    eco_pars_fmt:dict
    def __init__(self, cultivar_code):
        self.__cultivar = _get_croppars(
            self.spe_path, cultivar_code, self.cul_dtypes, self.cul_pars_fmt, 
            "var#"
        )
        if self.eco_dtypes:
            self.__cultivar["eco#"] = _get_croppars(
                self.spe_path, self.__cultivar._ecocode, self.eco_dtypes, 
                self.eco_pars_fmt, "eco#"
            )
        else:
            self.__cultivar["eco#"] = self.__cultivar._ecocode
        return
    
    def __repr__(self):
        return self.__cultivar.__repr__()

    def __len__(self):
        return len(self.__cultivar)

    def __iter__(self):
        raise NotImplementedError

    def __setitem__(self, key, value):
        key = key.lower()
        self.__cultivar[key] = value

    def __delitem__(self, k):
        raise NotImplementedError

    def __getitem__(self, key):
        key = key.lower()
        return self.__cultivar[key]

    def __contains__(self, k):
        raise NotImplementedError
    
    def __setattr__(self, name, value):
        if name in PROTECTED_ATTRS:
            raise AttributeError(f"Can't modify {name} attribute")
        else:
            super().__setattr__(name, value)
    
    def _write_section(self):
        out_str = "*CULTIVARS\n@C CR INGENO CNAME\n"
        cr = self.code
        ingeno = self.__cultivar.str
        if "vrname" in self.__cultivar:
            cname = self.__cultivar['vrname']
        elif "var-name" in self.__cultivar:
            cname = self.__cultivar['var-name']
        else:
            raise RuntimeError
        out_str += f" 1 {cr:>2} {ingeno:>6} {cname:<16}\n"
        return out_str
    
    def _write_eco(self):
        return self.__cultivar["eco#"]._write_file()
    
    def _write_cul(self):
        return self.__cultivar._write_file()
    
    @classmethod
    def cultivar_list(cls):
        """
        Returns a list with the cultivars available for that crop.
        """
        cul_path = cls.spe_path[:-4] + '.CUL'
        with open(cul_path, "r") as f:
            lines = f.readlines()
        lines = [l for l in lines if l[:1] not in ["@", "*", "!", "$"]]
        lines = [l for l in lines if len(l) > 5]
        return [l.split()[0] for l in lines if len(l.strip()) > 6]
    