# TODO: Implement class for Irrigation Schedule and Fertilizer Application schedule or make sure the columns of the `TabularSubsection` will be checked for consistency with the section they belong to.
# TODO: Remove all the non-section attributes from the Management class
'''
This module hosts the `Management` class, which includes all the information 
related to management. There are multiple arguments to initialize a `Management`
instance, however, the only  mandatory argument is planting_date. If not provided, 
simulation start is calculated as the day before the planting date, emergence date
is assumed to 5 days after planting, and the initial soil water content is assumed
to be 50% of the total available water (PWP + 0.5(FC-PWP)).

`Management` class has one attribute per management section. Up to date not all
of the sections have been implemented and the next sections are available for the
user to modify: field, initial conditions, planting details, irrigation, fertilizers, 
harvest details, simulation controls, automatic management. All the sections are a
`DSSATTools.section.Sections` object. The options that are not defined when
initializing the `Management` instance can be defined by modifying the value of
the parameters in each of the sections. An example will be shown. If the user is
not familiar to the different sections of the DSSAT experimental file then
reviewing the DSSAT documentation is suggested.

`DSSATTools.section.TabularSubsection` class is intended to represent tabular
information like irrigation schedules, fertilizer applications, or initial
condition through the different soil's layers. The `TabularSubsection` can be
initialized the same way a pandas.DataFrame. It's important to mention that the
columns must have the same names as the DSSAT variables the are representing
(See example).

In the next example a `Management` object is created, defining the irrigation
method option as non-irrigated; then the location of the field is defined in the
field section. 

    >>> man = Management( # Initialize instance
            planting_date=datetime(2020, 1, 1),
            irrigation="N",
        )
    >>> # Modify the location of the field
    >>> man.field["...........XCRD"] = 35.32
    >>> man.field["...........YCRD"] = -3.21

Even though the irrigation method was defined when the object was created, it can
still be modified:

    >>> man.simulation_controls["IRRIG"] = "R"
    >>> # Create a irrigation schedule as a pandas.DataFrame
    >>> schedule = pd.DataFrame([
            (datetime(2000,1,15), 80),
            (datetime(2000,1,30), 60),
            (datetime(2000,2,15), 40),
            (datetime(2000,3,1),  20)
        ], columns = ['date', 'IRVAL'])
    >>> schedule['IDATE'] = schedule.date.dt.strftime('%y%j')
    >>> schedule['IROP'] = 'IR001' # irrigation operation code
    >>> man.irrigation['table'] = TabularSubsection(
            schedule[['IDATE', 'IROP', 'IRVAL']]
        )

Note how the date is is converted to the format required by DSSAT. This has to be 
done for all dates.
'''
from DSSATTools.base.sections import (
    Section, TabularSubsection
)
from datetime import datetime, timedelta
from os.path import basename

SECTIONS = [
    'field', '_Management__cultivars', 'initial conditions', 'planting details', 'irrigation', 
    'fertilizers', 'harvest details', 'simulation controls',
    'automatic management'
]

IMPLEMENTED_SECTIONS = {
    'CU': 1, 'FL': 1, 'SA': 0, 'IC': 1, 'MP': 1, 'MI': 1, 'MF': 1, 
    'MR': 0, 'MC': 0, 'MT': 0, 'ME': 0, 'MH': 1, 'SM': 1,
}

SECTIONS_TITLE = {
    '_Management__cultivars': '*CULTIVARS', 
    'field': '*FIELDS',
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
    def __init__(
            self, planting_date:datetime, 
            sim_start:datetime=None, emergence_date:datetime=None, 
            initial_swc:float=1, irrigation='N',fertilization='N', 
            harvest='M', organic_matter='G'):
        '''
        Initializes a management instance.

        Arguments
        ----------
        planting_date: datetime
            Planting date.
        sim_start: datetime
            Date for start of the simulation. If None, it'll be calculated as the
            previous day to the planting date.
        emergence_date: datetime
            Emergence date. If None, I'll be calculated as 5 days after planting.
        initial_swc: int
            Fraction of the total available water (FC - PWP) at the start of the
            simulation. 1(100%) is the default value.
        irrigation: str
            Default 'N'. Irrigation management option, options available are:
                A        Automatic when required
                N        Not irrigated
                F        Fixed amount automatic
                R        On reported dates
                D        Days after planting
                P        As reported through last day, then automatic to re-fill (A)
                W        As reported through last day, then automatic with fixed
                        amount (F)
        harvest: str
            Default 'M'. Harvest management options. available options are:
                A        Automatic      
                M        At maturity
                R        On reported date(s)
                D        Days after planting
        fertilization: str
            Default 'N'. Fertilization management options. available options are:
                N        Not fertilized
                R        On reported dates
                D        Days after planting
        organic_matter: str
            Default 'G'. Fertilization management options. available options are:
                G        Ceres (Godiwn)
                P        Century (Parton)
        '''
        self.initial_swc = initial_swc
        if sim_start:
            self.sim_start = sim_start
        else:
            self.sim_start = planting_date - timedelta(days=1)
        if emergence_date:
            self.emergence_date = emergence_date.strftime('%y%j')
        else: 
            self.emergence_date = None
        self._treatmentOptions = IMPLEMENTED_SECTIONS
        self.__cultivars = Section(
            pars={'CR': TO_FILL, 'INGENO': None, 'CNAME': TO_FILL},
            idcol='@C', # Fill from Crop instance
            name='cultivars',
        )
        self.field = Section(
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
            name='field',
        )
        # self.soil_analysis = Section(
        #     # Tabular
        # )
        self.initial_conditions = Section(
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
        self.planting_details = Section(
            name='planting details',
            idcol='@P',
            pars={
                'PDATE': planting_date.strftime('%y%j'), 
                'EDATE': self.emergence_date,
                'PPOP': 16, 'PPOE': 15, 'PLME': 'S', 'PLDS': 'R', 
                'PLRS': 35, 'PLRD': None, 'PLDP': 4, 'PLWT': None, 
                'PAGE': None, 'PENV': None, 'PLPH': None, 
                'SPRL': None, 'PLNAME': None
            }
        )
        self.irrigation = Section(
            name='irrigation',
            idcol='@I',
            pars={
                'EFIR': 1, 'IDEP': 30, 'ITHR': 50, 'IEPT': 100, 
                'IOFF': 'GS000', 'IAME': 'IR001', 'IAMT': 10, 'IRNAME': 'DFLTIR',
                'table': TabularSubsection({
                    'IDATE': [planting_date.strftime('%y%j'),],
                    'IROP': ['IR001',],
                    'IRVAL': [0,]
                })														
            }
        )
        self.fertilizers = Section(
            name='fertilizers',
            idcol='@F',
            pars={
                'table': TabularSubsection({
                    'FDATE': [planting_date.strftime('%y%j'), ], 
                    'FMCD': ['FE001', ], 'FACD': ['AP001', ], 
                    'FDEP': [2, ], 'FAMN': [0, ], 'FAMP': [0, ], 
                    'FAMK': [0, ], 'FAMC': [0, ], 'FAMO': [0, ], 
                    'FOCD': [None, ], 'FERNAME': [None, ], 														
                })
            }
        )
        # self.tillage_and_rotations = Section(
        #     # Tabular
        # )
        # self.environment_modifications = Section(
        #     # Tabular
        # )
        self.harvest_details = Section(
            name='harvest details',
            idcol='@H',
            pars={
                'HDATE': None, 
                'HSTG': None, 'HCOM': None, 'HSIZE': None, 
                'HPC': None, 'HBPC': None, 'HNAME': 'DEFAULT',						
            }
        )
        self.simulation_controls = Section(
            name='simulation controls',
            idcol='@N',
            pars={
                'GENERAL': 'GE', 
                'NYERS': 1, 'NREPS': 1, 'START': 'S', 
                'SDATE': self.sim_start.strftime('%y%j'), 'RSEED': 2409, 
                'SNAME....................': 'DEFAULT', 'SMODEL': TO_FILL, 
                
                'OPTIONS': 'OP', 
                'WATER': 'Y', 'NITRO': 'N', 'SYMBI': 'N', 'PHOSP': 'N', 
                'POTAS': 'N', 'DISES': 'N', 'CHEM': 'N', 'TILL': 'N', 
                'CO2': 'M', 
                
                'METHODS': 'ME', 
                'WTHER': 'M', 'INCON': 'M', 'LIGHT': 'E', 'EVAPO': 'R', 
                'INFIL': 'S', 'PHOTO': 'C', 'HYDRO': 'R', 'NSWIT': 1, 
                'MESOM': organic_matter, 'MESEV': 'S', 'MESOL': 2, 

                'MANAGEMENT': 'MA', 
                'PLANT': 'R', 'IRRIG': irrigation, 
                'FERTI': fertilization, 'RESID': 'N', 
                'HARVS': harvest, 
                
                'OUTPUTS': 'OU',
                'FNAME': 'N', 'OVVEW': 'Y', 'SUMRY': 'Y', 'FROPT': 1, 
                'GROUT': 'Y', 'CAOUT': 'Y', 'WAOUT': 'Y', 'NIOUT': 'N', 
                'MIOUT': 'N', 'DIOUT': 'N', 'VBOSE': 'Y', 'CHOUT': 'N', 
                'OPOUT': 'N', 'FMOPT':'A',
            }
        )
        self.automatic_management = Section(
            name='automatic management',
            idcol='@N',
            pars={
                'PLANTING': 'PL',
                'PFRST': (planting_date-timedelta(days=3)).strftime('%y%j'),
                'PLAST': (planting_date+timedelta(days=3)).strftime('%y%j'), 
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
                'HFRST': None, 
                'HLAST': None,
                'HPCNP': 100, 'HPCNR': 0, 														
            }
        )
        # Mowing schedule for Perennial Forages:
        self.mow = Section(
            name='mow',
            idcol='@TRNO',
            pars={
                    'table': TabularSubsection({
                    'DATE': [], 'MOW': [], 'RSPLF': [], 'MVS': [], 'RSHT': []
                })
            }
        )
    
    def write(self, filename='EXP', expname='DEFAULT'):
        outstr = f'*EXP.DETAILS: {basename(filename)} {expname}\n\n'
        outstr += '*GENERAL\n'
        outstr += '@PEOPLE\nDSSATTools: A Python Library for DSSAT\n'
        outstr += '@ADDRESS\nhttps://github.com/daquinterop/Py_DSSATTools\n'
        outstr += '@SITE\nhttps://py-dssattools.readthedocs.io\n'
        outstr += '@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........\n'
        outstr += '    -99   -99   -99   -99   -99   -99     1   -99   -99 pping\n\n'

        outstr += '*TREATMENTS                        -------------FACTOR LEVELS------------\n'
        outstr += '@N R O C TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM\n'
        self._treatmentOptions["MI"] = min(1, self.irrigation['table']["IRVAL"].sum())
        self._treatmentOptions["MF"] = min(1, self.fertilizers["table"][["FAMN", "FAMP", "FAMK", "FAMC", "FAMO"]].values.max())
        self._treatmentOptions["MH"] = min(1, int(self.harvest_details["HDATE"] is not None))
        outstr += f' 1 1 0 0 DEFAULT TREATMENT          {"  ".join(map(str, IMPLEMENTED_SECTIONS.values()))}\n\n'

        for section in SECTIONS:
            section_obj = self.__dict__[section.replace(' ', '_')]
            outstr += SECTIONS_TITLE[section] + '\n'
            outstr += section_obj.write() + '\n'

        with open(filename, 'w') as f:
            f.write(outstr)
        
        return

    def write_mow(self, filename):
        outstr = self.mow.write()
        with open(filename, 'w') as f:
            f.write(outstr)


    def __repr__(self):
        repr_str = f"Management\n"
        repr_str += f"  Simulation start: {datetime.strptime(self.simulation_controls['SDATE'], '%y%j').date()}\n"
        repr_str += f"  Planting date: {datetime.strptime(self.planting_details['PDATE'], '%y%j').date()}"
        return repr_str