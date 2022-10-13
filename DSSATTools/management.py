'''
Management file will be initialized with custom settings. There won't be any 

'''
from DSSATTools.base.sections import (
    Section, RowBasedSection, ColumnBasedSection, TabularSubsection
)
from datetime import datetime, timedelta
from os.path import basename

SECTIONS = [
    'fields', 'cultivars', 'initial conditions', 'planting details', 'irrigation', 
    'fertilizers', 'harvest details', 'simulation controls',
    'automatic management'
]

IMPLEMENTED_SECTIONS = {
    'CU': 1, 'FL': 1, 'SA': 0, 'IC': 1, 'MP': 1, 'MI': 1, 'MF': 1, 
    'MR': 0, 'MC': 0, 'MT': 0, 'ME': 0, 'MH': 1, 'SM': 1,
}

SECTIONS_TITLE = {
    'cultivars': '*CULTIVARS', 'fields': '*FIELDS',
    'initial conditions': '*INITIAL CONDITIONS',
    'planting details': '*PLANTING DETAILS',
    'irrigation': '*IRRIGATION AND WATER MANAGEMENT',
    'fertilizers': '*FERTILIZERS (INORGANIC)',
    'tillage': '*TILLAGE AND ROTATIONS', 'harvest details': '*HARVEST DETAILS',
    'simulation controls': '*SIMULATION CONTROLS',
    'automatic management': '@  AUTOMATIC MANAGEMENT'

}

TO_FILL = -999999 # To fill from other instances
class Management:
    '''
    Management classs
    '''
    # TODO: Define attributes for basic things such as:
    # - Planting date
    # - Variety
    # - Field weather station
    #
    def __init__(
        self, cultivar:str, planting_date:datetime, sim_start:datetime=None,
        emergence_date:datetime=None, initial_swc:float=.5
        ):
        '''
        Initializes a management instance.

        Arguments
        ----------
        cultivar: str
            Code of the cultivar. That code must match one of the codes in the
            Crop instance used when runing the model.
        planting_date: datetime
            Planting date.
        sim_start: datetime
            Date for start of the simulation. If None, it'll be calculated as
            the previous day to the planting date.
        emergence_date: datetime
            Emergence date. If None, I'll be calculated as 5 days after 
            planting.
        initial_swc: int
            Fraction of the total available water (FC - PWP) at the start of the 
            simulation. .5(50%) is the default value.
        '''
        # Non treatment section since there's only one posible treatment
        # TODO: There will be optional sections such as SA, MI, MR, MC
        # TODO: set argument to load a predefined management type, like 
        # automatic irrigation, etc.
        # soil_moisture = %TAW
        self.cultivar = cultivar
        self.planting_date = planting_date
        self.initial_swc = initial_swc
        if sim_start:
            self.sim_start = sim_start
        else:
            self.sim_start = self.planting_date - timedelta(days=1)
        if emergence_date:
            self.emergence_date = emergence_date
        else:
            self.emergence_date = self.planting_date + timedelta(days=5)
        self.cultivars = RowBasedSection(
            pars={'CR': TO_FILL, 'INGENO': self.cultivar, 'CNAME': TO_FILL},
            idcol='@C', # Fill from Crop instance
            name='cultivars',
        )
        # TODO: Sections to fill with default or passed values:
        # - Cultivar
        # - Treatments
        # - General
        
        self.fields = RowBasedSection(
            pars={
                'ID_FIELD': 'DFTF0001', 'WSTA....': TO_FILL, 'FLSA': None, 
                'FLOB': 0, 'FLDT': 'DR000', 'FLDD': 0, 'FLDS': 0,
                'FLST': '00000', 'SLTX': None, 'SLDP': TO_FILL, 'ID_SOIL': TO_FILL, 
                'FLNAME': None, '...........XCRD': None,
                '...........YCRD': None, '.....ELEV': None, 
                '.............AREA': None, '.SLEN': None,
                '.FLWR': None, '.SLAS': None, 'FLHST': None, 'FHDUR': None
            }, # Fill from Weather and Soil Instance
            idcol='@L',
            name='fields',
        )
        # self.soil_analysis = RowBasedSection(
        #     # Tabular
        # )
        self.initial_conditions = RowBasedSection(
            #TODO: If ICDAT is not defined,  then it's same as sim_start
            name='initial conditions',
            idcol='@C',
            pars={ 
                'PCR': None, 'ICDAT': None, 'ICRT': None, 'ICND': None, 
                'ICRN': 1, 'ICRE': 1, 'ICWD': None, 'ICRES': None, 
                'ICREN': None, 'ICREP': None, 'ICRIP': None, 'ICRID': None, 
                'ICNAME': 'DEFAULT',
                'table': TabularSubsection({
                    'ICBL': [15, 20, 50, 70, 100],
                    'SH2O': [.2, .2, .2, .3, .3],
                    'SNH4': [0., 0., 0., 0., 0.],
                    'SNO3': [1., .5, 0., 0., 0.]
                })
            } # Fill from crp instance and set in 
        )
        self.planting_details = RowBasedSection(
            name='planting details',
            idcol='@P',
            pars={
                'table': TabularSubsection({
                    'PDATE': [self.planting_date.strftime('%y%j')], 
                    'EDATE': [self.emergence_date.strftime('%y%j')],
                    'PPOP': [16], 'PPOE': [15], 'PLME': ['S'], 'PLDS': ['R'], 
                    'PLRS': [35], 'PLRD': [None], 'PLDP': [4], 'PLWT': [None], 
                    'PAGE': [None], 'PENV': [None], 'PLPH': [None], 
                    'SPRL': [None], 'PLNAME': [None]
                })
            }
        )
        self.irrigation = RowBasedSection(
            name='irrigation',
            idcol='@I',
            pars={
                'EFIR': 1, 'IDEP': 30, 'ITHR': 50, 'IEPT': 100, 
                'IOFF': 'GS000', 'IAME': 'IR001', 'IAMT': 10, 'IRNAME': 'DFLTIR',
                'table': TabularSubsection({
                    'IDATE': [self.planting_date.strftime('%y%j'),],
                    'IROP': ['IR001',],
                    'IVAL': [0,]
                })														
            }
        )
        self.fertilizers = RowBasedSection(
            name='fertilizers',
            idcol='@F',
            pars={
                'table': TabularSubsection({
                    'FDATE': [self.planting_date.strftime('%y%j'), ], 
                    'FMCD': ['FE001', ], 'FACD': ['AP001', ], 
                    'FDEP': [2, ], 'FAMN': [1, ], 'FAMP': [0, ], 
                    'FAMK': [0, ], 'FAMC': [0, ], 'FAMO': [0, ], 
                    'FOCD': [None, ], 'FERNAME': [None, ], 														
                })
            }
        )
        # self.tillage_and_rotations = RowBasedSection(
        #     # Tabular
        # )
        # self.environment_modifications = RowBasedSection(
        #     # Tabular
        # )
        self.harvest_details = RowBasedSection(
            name='harvest details',
            idcol='@H',
            pars={
                'table': TabularSubsection({
                    'HDATE': [None, ], 'HSTG': [None, ], 'HCOM': [None, ], 
                    'HSIZE': [None, ], 'HPC': [None, ], 'HBPC': [None, ], 
                    'HNAME': ['DEFAULT', ], 														
                })
            }
        )
        self.simulation_controls = RowBasedSection(
            name='simulation controls',
            idcol='@N',
            pars={
                'GENERAL': 'GE', 
                'NYERS': 1, 'NREPS': 1, 'START': 'S', 
                'SDATE': self.sim_start.strftime('%y%j'), 'RSEED': 2409, 
                'SNAME....................': 'DEFAULT', 'SMODEL': 'MZCER', 
                
                'OPTIONS': 'OP', 
                'WATER': 'Y', 'NITRO': 'N', 'SYMBI': 'N', 'PHOSP': 'N', 
                'POTAS': 'N', 'DISES': 'N', 'CHEM': 'N', 'TILL': 'N', 
                'CO2': 'M', 
                
                'METHODS': 'ME', 
                'WTHER': 'M', 'INCON': 'M', 'LIGHT': 'E', 'EVAPO': 'R', 
                'INFIL': 'S', 'PHOTO': 'C', 'HYDRO': 'R', 'NSWIT': 1, 
                'MESOM': 'G', 'MESEV': 'S', 'MESOL': 2, 
                # TODO: Management options have to be modified according to 
                # defined modules.
                'MANAGEMENT': 'MA', 
                'PLANT': 'R', 'IRRIG': 'R', 'FERTI': 'R', 'RESID': 'N', 
                'HARVS': 'R', 
                
                'OUTPUTS': 'OU',
                'FNAME': 'N', 'OVVEW': 'Y', 'SUMRY': 'Y', 'FROPT': 1, 
                'GROUT': 'Y', 'CAOUT': 'N', 'WAOUT': 'Y', 'NIOUT': 'N', 
                'MIOUT': 'N', 'DIOUT': 'N', 'VBOSE': 'Y', 'CHOUT': 'N', 
                'OPOUT': 'N', 'FMOPT':'A',
            }
        )
        self.automatic_management = RowBasedSection(
            name='automatic management',
            idcol='@N',
            pars={
                'PLANTING': 'PL',
                'PFRST': (self.planting_date-timedelta(days=3)).strftime('%y%j'),
                'PLAST': (self.planting_date+timedelta(days=3)).strftime('%y%j'), 
                'PH2OL': 40, 'PH2OU': 100, 'PH2OD': 30, 'PSTMX': 40, 'PSTMN': 40,
                
                'IRRIGATION': 'IR', 
                'IMDEP': 30, 'ITHRL': 50, 'ITHRU': 100, 'IROFF': 'GS000',
                'IMETH': 'IR001', 'IRAMT': 10, 'IREFF': 1, 
                
                'NITROGEN': 'NI',
                'NMDEP': 30, 'NMTHR': 50, 'NAMNT': 25, 'NCODE': 'FE001', 
                'NAOFF': 'GS000',
                
                'RESIDUES': 'RE', 
                'RIPCN': 100, 'RTIME': 1, 'RIDEP': 20, 
                
                'HARVEST': 'HA',
                'HFRST': 0, 'HLAST': 30365, 'HPCNP': 100, 'HPCNR': 0, 														
            }
        )
    
    def write(self, filename='EXP', expname='DEFAULT'):
        outstr = f'*EXP.DETAILS: {basename(filename)} {expname}\n\n'
        outstr += '*GENERAL\n'
        outstr += '@PEOPLE\nDSSATTools: A Python Library for DSSAT\n'
        outstr += '@ADDRESS\nSERVIR-NASA\n'
        outstr += '@SITE\nNSSTC, Huntsville, AL.\n'
        outstr += '@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........\n'
        outstr += '    -99   -99   -99   -99   -99   -99     1   -99   -99 pping\n\n'

        outstr += '*TREATMENTS                        -------------FACTOR LEVELS------------\n'
        outstr += '@N R O C TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM\n'
        outstr += f' 1 0 0 0 DEFAULT TREATMENT          {"  ".join(map(str, IMPLEMENTED_SECTIONS.values()))}\n\n'

        for section in SECTIONS:
            section_obj = self.__dict__[section.replace(' ', '_')]
            outstr += SECTIONS_TITLE[section] + '\n'
            outstr += section_obj.write() + '\n'

        with open(filename, 'w') as f:
            f.write(outstr)
        
        return