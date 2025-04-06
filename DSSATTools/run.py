'''
This module hosts the DSSAT class. This class represents the simulation environment, 
so per each DSSAT instance there's a directory where all the necesary files to 
run the model are allocated. To run the model there are 2 basic steps:

1. Create a new DSSAT instance. When DSSAT is instantiated, a simulation environment
is set. That enviroment is set at the path passed during the call:
    >>> dssat = DSSAT("/tmp/dssat_test")
2. Run the model by calling the run_treatment() method. This method receives as 
parameters the FileX sections' objects:
    >>> results = dssat.run_treatment(
    >>>     field=field, cultivar=crop, planting=planting,
    >>>     initial_conditions=initial_conditions, fertilizer=fertilizer,
    >>>     simulation_controls=simulation_controls
    >>> )
This call returns a dictionary that contains the values of the standard output 
of the model: FLO, MAT, TOPWT, HARWT, RAIN, etc. After running, the DSSAT instance
will have all the output files as strings in the output_files attribute, and the 
output timeseries tables in the output_tables attribute:
    >>> overview = dssat.output_files['OVERVIEW'] # Gets the overview file as a str
    >>> plantgro = dssat.output_tables['PlantGro'] # Gets the plant growth table
3. You can close the simulation environment by calling the close() method.
    >>> dssat.close
'''

import subprocess
import shutil
import os
import tempfile    
import random
import string
import pandas as pd
import sys
import warnings
import platform
import stat
import re
import io

# Libraries for second version
from . import __file__ as module_path
from . import VERSION
from .crop import Crop
from .filex import(
    Planting, Cultivar, Harvest, InitialConditions, Fertilizer,
    SoilAnalysis, Irrigation, Residue, Chemical, Tillage, Field,
    SimulationControls, Mow, create_filex
)
from .base.utils import detect_encoding

OS = platform.system().lower()
OUTPUTS = ['PlantGro', "Weather", "SoilWat", "SoilOrg", "SoilNi"]
OUTPUT_MAP = {
    "PlantGro": "GROUT",  "SoilWat": "WAOUT", "SoilOrg": "CAOUT",
    "Weather": "GROUT", "SoilNi": "NIOUT"
}
SOIL_LAYER_OUTPUTS = ["SoilNi"]

PERENIAL_FORAGES = ['Alfalfa', 'Bermudagrass', 'Brachiaria', 'Bahiagrass']
ROOTS = ['Potato']
PROTECTED_ATTRS = []
TMP_BASE = tempfile.gettempdir()

# Paths to DSSAT and Env variables
BASE_PATH = os.path.dirname(module_path)
STATIC_PATH = os.path.join(BASE_PATH, 'dssat-csm-os', 'Data')
TMP =  tempfile.gettempdir()
DSSAT_HOME = os.path.join(TMP, f"DSSAT{VERSION}"+os.sep)
STD_PATH = os.path.join(DSSAT_HOME, 'StandardData')
CRD_PATH = os.path.join(DSSAT_HOME, 'Genotype')
SLD_PATH = os.path.join(DSSAT_HOME, 'Soil')

# Creates a folder with DSSAT files. This is done to avoid long path names
# that exceed the defined lenght for path variables in DSSAT.
if not os.path.exists(DSSAT_HOME):
    os.mkdir(DSSAT_HOME)
for file in os.listdir(STATIC_PATH):
    file_link = os.path.join(DSSAT_HOME, file)
    if os.path.exists(file_link):
        os.remove(file_link)
    os.symlink(os.path.join(STATIC_PATH, file), file_link)

if 'windows'in OS:
    BIN_PATH = os.path.join(BASE_PATH, 'bin', 'dscsm048.exe')
    CONFILE = 'DSSATPRO.V48'
else: 
    BIN_PATH = os.path.join(BASE_PATH, 'bin', 'dscsm048')
    CONFILE = 'DSSATPRO.L48'

# function to handle windows permisions
def handleRemoveReadonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

if 'windows' in OS:
    WIN_SHUTIL_KWARGS = {'ignore_errors': False, 'onerror': handleRemoveReadonly}
    CHMOD_MODE = stat.S_IWRITE
else:
    WIN_SHUTIL_KWARGS = {}
    CHMOD_MODE = 111


class DSSAT:
    '''
    Class that represents the simulation environment for a single treatment. When
    initializing and seting up the environment, a new folder is created (usually
    in the tmp folder) to run the model there. 

    After the model runs, the output is saved in the output property. 
    '''
    run_path:str=None
    output_files:dict=None
    def __init__(self, run_path:str=None):   
        """
        Initializes the simulation environment. run_path is the only parameter. 
        That parameter is the path to the directory where the environment will
        be set, therefore, all simulations will be run in that environment.

        Arguments
        ----------
        run_path: str
            Working directory. The model will be run in that directory. 
            If None, then a tmp directory will be created.
        """
        if not run_path:
            run_path = os.path.join(
                TMP_BASE, 
                'dssat'+''.join(random.choices(string.ascii_lowercase, k=8))
            )
        if not os.path.exists(run_path):
            os.mkdir(run_path)
        if not os.path.exists(os.path.join(run_path, "Weather")):
            os.mkdir(os.path.join(run_path, "Weather"))
        sys.stdout.write(f'{run_path} created.\n')
        self.run_path = run_path
        self._output = {}


    def run_treatment(self, field:Field, cultivar:Cultivar, planting:Planting, 
                      simulation_controls:SimulationControls, harvest:Harvest=None,
                      initial_conditions:InitialConditions=None, 
                      fertilizer:Fertilizer=None, soil_analysis:SoilAnalysis=None, 
                      irrigation:Irrigation=None, residue:Residue=None, 
                      chemical:Chemical=None, tillage:Tillage=None, mow:Mow=None,
                      verbose=True):
        '''
        Run a single treatment. 

        Arguments
        ----------
        field:Field
        cultivar:Cultivar
        planting:Planting
        simulation_controls:SimulationControls
        harvest:Harvest
        initial_conditions:InitialConditions         
        fertilizer:Fertilizer
        soil_analysis:SoilAnalysis
        irrigation:Irrigation
        residue:Residue
        chemical:Chemical
        tillage:Tillage
        verbose: bool
            Whether to display the model std out or not
        ''' 
        assert isinstance(field, Field), "field parameter must be a Field instance."
        assert issubclass(type(cultivar), Crop), \
            "cultivar parameter must be a Crop instance."
        assert isinstance(planting, Planting), \
            "planting parameter must be a Planting instance."
        assert isinstance(simulation_controls, SimulationControls), \
            "simulation_controls parameter must be a SimulationControls instance."
        assert not harvest or isinstance(harvest, Harvest), \
            "harvest parameter must be a Harvest instance."
        assert not initial_conditions or isinstance(initial_conditions, InitialConditions), \
            "initial_conditions parameter must be a InitialConditions instance."
        assert not fertilizer or isinstance(fertilizer, Fertilizer), \
            "fertilizer parameter must be a Fertilizer instance."
        assert not soil_analysis or isinstance(soil_analysis, SoilAnalysis), \
            "soil_analysis parameter must be a SoilAnalysis instance."
        assert not irrigation or isinstance(irrigation, Irrigation), \
            "irrigation parameter must be a Irrigation instance."
        assert not residue or isinstance(residue, Residue), \
            "residue parameter must be a Residue instance."
        assert not chemical or isinstance(chemical, Chemical), \
            "chemical parameter must be a Chemical instance."
        assert not tillage or isinstance(tillage, Tillage), \
            "tillage parameter must be a Tillage instance."
        assert not mow or isinstance(mow, Mow), \
            "mow parameter must be a Mow instance"
        # Remove previous outputs and inputs
        OUTPUT_FILES = [i for i in os.listdir(self.run_path) if i[-3:] == 'OUT']
        INP_FILES = [i for i in os.listdir(self.run_path) if i[-3:] in ['INP', 'INH']]
        self.output_files = {}
        for file in (OUTPUT_FILES + INP_FILES):
            os.remove(os.path.join(self.run_path, file))

        # Assign a generic code for all elements
        # field["id_field"] = "ABCD0001"
        # field["wsta"]["insi"] = "ABCD"
        # field['id_soil'] = "ABCD000001"

        simulation_controls["general"]["smodel"] = cultivar.smodel
        # Check for Roots'parameters
        if type(cultivar).__name__ in ROOTS:
            assert not any((pd.isna(planting["plwt"]), pd.isna(planting["sprl"]))), \
                f"PLWT, SPRL transplanting parameters are mandatory for "+\
                f"{type(cultivar).__name__} crop, you must define those "+\
                "parameters in management.planting_details"
        
        # Write files
        # File X
        filex_name = field["id_field"][:4] +\
            simulation_controls["general"]["sdate"].strftime('%y01') +\
            f'.{cultivar.code}X'
        filex_name = os.path.join(self.run_path, filex_name.upper())
        with open(filex_name, "w") as f:
            lines = create_filex(
                field, cultivar, planting, simulation_controls, harvest, 
                initial_conditions, fertilizer, soil_analysis, irrigation,
                residue, chemical, tillage
            )
            f.write(lines)
        # Cultivar and ecotype
        cul_filename = os.path.join(self.run_path, cultivar.spe_file[:-3]+"CUL") 
        with open(cul_filename, "w") as f:
            lines = cultivar._write_cul()
            f.write(lines)
        eco_filename = os.path.join(self.run_path, cultivar.spe_file[:-3]+"ECO") 
        if cultivar.eco_dtypes:
            with open(eco_filename, "w") as f:
                lines = cultivar._write_eco()
                f.write(lines)
        # Soil
        sol_filename = os.path.join(self.run_path, "SOIL.SOL")
        with open(sol_filename, "w") as f:
            lines = field["id_soil"]._write_sol()
            f.write(lines)
        # Weather
        wth_year = field["wsta"].table[0]["date"].year
        wth_len = field["wsta"].table[-1]["date"].year - wth_year + 1
        wth_filename = f'{field["wsta"]["insi"]}{str(wth_year)[2:]}{wth_len:02d}.WTH'
        wth_filename = os.path.join(self.run_path, "Weather", wth_filename)
        with open(wth_filename, "w") as f:
            lines = field["wsta"]._write_wth()
            f.write(lines)
        # Mow
        if type(cultivar).__name__ in PERENIAL_FORAGES:
            if (not mow) or (len(mow.table) < 1):
                warnings.warn('Mow was not defined. It can be defined in the mow parameter.')
            else:
                mow_file_path = os.path.join(self.run_path, f'{filex_name[:-4]}.MOW')
                with open(mow_file_path, 'w') as f: 
                    file_str = mow._write_section()
                    f.write(file_str)
        # Configuration file
        with open(os.path.join(self.run_path, CONFILE), 'w') as f:
            f.write(f'WED    {os.path.join(self.run_path, "Weather")}\n')
            # if cultivar.code in ["WH", "BA"]:
            #     f.write(f'M{cultivar.code}    {self.run_path} dscsm048 CSCER{VERSION}\n')
            # else:
            f.write(f'M{cultivar.code}    {self.run_path} dscsm048 {cultivar.smodel}{VERSION}\n')
            f.write(f'CRD    {CRD_PATH}\n')
            f.write(f'PSD    {os.path.join(DSSAT_HOME, "Pest")}\n')
            f.write(f'SLD    {SLD_PATH}\n')
            f.write(f'STD    {STD_PATH}\n')

        # Run the model
        exc_args = [BIN_PATH, 'C', os.path.basename(filex_name), '1']
        excinfo = subprocess.run(exc_args, 
            cwd=self.run_path, capture_output=True, text=True,
            env={"DSSAT_HOME": DSSAT_HOME, }
        )
        excinfo.stdout = re.sub("\n{2,}", "\n", excinfo.stdout)
        excinfo.stdout = re.sub("\n$", "", excinfo.stdout)
        self.stdout = excinfo.stdout.strip()

        if verbose:
            for line in excinfo.stdout.split("\n"):
                sys.stdout.write(line + '\n')

        if excinfo.returncode != 0:
            with open(os.path.join(self.run_path, "ERROR.OUT"), "r") as f:
                for line in f:
                    print(line, end='')
            raise RuntimeError("DSSAT execution Failed. Check the ERROR.OUT file")

        # Get the output files
        self._fetch_output()
        # parse ouputs from files
        for fname, file_lines in self.output_files.items():
            # determine how many rows to skip in output file
            if fname not in OUTPUTS:
                continue
            table_start = -1
            init_lines = []
            for line in file_lines.split('\n'):
                table_start += 1
                init_lines.append(line)
                if "@" in init_lines[-1][:10]:
                    break
            try:
                df = pd.read_csv(
                    io.StringIO("".join(file_lines)),
                    skiprows=table_start,
                    sep=" ",
                    skipinitialspace=True,
                )
            except Exception:
                df = pd.read_csv(
                    io.StringIO("".join(file_lines[table_start:])),
                    skiprows=0,
                    sep=" ",
                    skipinitialspace=True,
                )
                break

            if all(("@YEAR" in df.columns, "DOY" in df.columns)):
                df["DOY"] = df.DOY.astype(int).map(lambda x: f"{x:03d}")
                df["@YEAR"] = df["@YEAR"].astype(str)
                df.index = pd.to_datetime((df["@YEAR"] + df["DOY"]), format="%Y%j")

            self._output[fname] = df

        out_dict = {
            k.lower(): int(v) if int(v) != -99 else None
            for k, v in zip(
                self.stdout.split("\n")[0][10:].split(),
                self.stdout.split("\n")[2][10:].split(),
            )
        }
        return out_dict

    def _fetch_output(self):
        files = os.listdir(self.run_path)
        files = filter(lambda x: x[-4:] == ".OUT", files)
        for file in files:
            encoding = detect_encoding(os.path.join(self.run_path, file))
            with open(os.path.join(self.run_path, file), "r", encoding=encoding) as f:
                self.output_files[file.split(".")[0]] = ''.join(f.readlines())


    def close(self):
        '''
        Removes the simulation environment (tmp folder and files).
        '''
        shutil.rmtree(self.run_path, **WIN_SHUTIL_KWARGS)
        sys.stdout.write(f'{self.run_path} and its content has been removed.\n')

    @property
    def output_tables(self):
        if len(self._output) < 1:
            warnings.warn("No output has been saved")
            return None
        return self._output

    def __setattr__(self, name, value):
        if name in PROTECTED_ATTRS:
            raise AttributeError(f"Can't modify {name} attribute")
        if (name == "run_path") and self.run_path:
            raise RuntimeError("run_path attribute can't be modified by the user")
        super().__setattr__(name, value)

    

