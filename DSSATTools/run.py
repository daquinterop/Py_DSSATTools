import subprocess
import shutil

from numpy import isin
from .exceptions import DSSATNotFound, DSSATInputError
import os
import time
import docker
import sys
import tarfile
import tempfile    
import DSSATTools.dssatUtils as dssatUtils

# Libraries for second version
import DSSATTools
import random
import string
import shutil
import stat

class Dscsm():
    # TODO: Class implementation must allow to change Crop, Weather, Experiment(Management) and Soil. So, each of this must be defined as instances, and this class must keep track of those changes, so as to create new files only if the instance has changed.

    # TODO: Each crop model has to have it's own class. So far, I'll implement only CERES-MAIZE.

    # TODO: An option to run without definen input instances has to be implement as well. This will allow to use the class if the model is not implemented yet. For this case, the input will be initialized as a path (str) and not as an instance. 

    def __init__(self):
        '''
        
        '''
        BASE_PATH = os.path.dirname(DSSATTools.__file__)
        self._STATIC_PATH = os.path.join(BASE_PATH, 'static')
        self._BIN_PATH = os.path.join(self._STATIC_PATH, 'bin', 'dscsm048')
        self._STD_PATH = os.path.join(self._STATIC_PATH, 'StandardData')
        self._CRD_PATH = os.path.join(self._STATIC_PATH, 'Genotype')
        self._SLD_PATH = os.path.join(self._STATIC_PATH, 'Soil')

        self._SETUP = False
        self._INPUTS = {
            'crop': None, 'wheater': None, 'soil': None, 'management': None 
        }

    def setup(self, exp, cwd=None, overwrite=False, **kwargs):
        '''
        Setup a simulation environment.
        Creates a tmp folder to run the simulations and move all the required
        files to run the model. Some rguments are optional, if those aren't provided,
        then standard files location will be used.

        Arguments
        ----------
        exp: str
            Path to the experimental file (.CRX)
        cwd: str
            Working directory. All the model files would be moved to that directory.
            If None, then a tmp directory will be created and then removed.
        bin : str
            Path to the DSSAT executable file.
        std : str
            Path to the DSSAT StandardData folder.
        crd : str
            Path to the DSSAT Genotype folder.
        sld : str
            Path to the DSSAT Soil folder. It contains all the Soil files.
        overwrite: bool
            Whether to overwrite or not the current simulation environment. If
            true, then a new simulation environment will be created, and all the 
            outputs and inputs will be reseted.
        '''
        #
        # Create wd if it doesn't exist and move files to it.
        #
        # TODO: Check if this instance was already set-up. If it was, then stop, show warning, and ask to run the method with overwrite=True
        TMP_BASE = tempfile.gettempdir()
        if cwd:
            self._RUN_PATH = cwd
            if not os.path.exists(self._RUN_PATH):
                os.mkdir(self._RUN_PATH)
        else:
            self._RUN_PATH = os.path.join(
                TMP_BASE, 
                ''.join(random.choices(string.ascii_lowercase, k=8))
            )
            os.mkdir(self._RUN_PATH)
        
        # Move files
        shutil.copyfile(
            self._BIN_PATH, 
            os.path.join(self._RUN_PATH, os.path.basename(self._BIN_PATH))
        )
        os.chmod(
            os.path.join(self._RUN_PATH, os.path.basename(self._BIN_PATH)),
            mode=111
        )
        for file in os.listdir(self._STATIC_PATH):
            if file.endswith('.CDE'):
                shutil.copyfile(
                    self._BIN_PATH, 
                    os.path.join(self._RUN_PATH, file)
                )
        # TODO: All the inputs and outputs should be reseted when creating a new setup.
        
        def set_inputs(self, crop=None, wheater=None, soil=None, management=None):
            '''
            This function defines or overwrites the inputs in the folder.

            Arguments
            ----------
            TODO: DSSATTools.base.Input has to be implemented
            crop, wheater, soil, management: str, DSSATTools.base.Input
                It can be an input instance, or a string with the path to the input
                file.
            '''
            return


        def run(self):
            '''
            Start the simulation and runs until the end or failure.

            Arguments
            ----------
            '''
            # TODO: Write all the files.
            # TODO: Check if the weather, soil and crop instances matches the definitions in the management instance. 
            # TODO: Check for inputs.
            # TODO: Check for environment setup.
            # TODO: Print simulation outcome (Success or Error)
            return
        shutil.rmtree(self._RUN_PATH) # TODO: remember to remove this line



class CSM_EXE():
    '''
    A class to handle the DSSAT execution
    ...
    Attributes
    ----------------------
    results: dssatUtils.DSSATOutput object
        It is a dict-like type object. Upper level key is the treatment, nested keys are
        the results section (PlantGro, Summary, Etc.)
    '''
    def __init__(self, DSSATExe='/mnt/c/DSSAT47/DSCSM047.EXE', verbose=False):
        '''
        Initialization of the DSSAT environment
        ...
        Arguments
        ---------------------
        DSSATExe: str
            Path to the DSSAT Executable file
        verbose: bool
            Whether to print the DSSAT execution output or not.
        parallel: bool
            Is used during parallel runs to avoid permision errors during the reading
            and writing of files
        '''
        self.verbose = verbose
        self.DSSATExe = DSSATExe    
        self.DSSATFolder = os.path.dirname(DSSATExe)
        self.curdir = os.getcwd()
        # self.PARALLEL = parallel
        if os.path.exists(DSSATExe):
            print(f'DSSAT Executable at {self.DSSATExe}')
        else:
            raise DSSATNotFound(f'DSSAT Executable was not found on {self.DSSATExe}')
        return

    def __handleCopy(self, source, destination, move=False):
        '''A function to handle errors when copying files in parallel runs'''
        max_tries = 20
        try_n = 0
        if move:
            func = shutil.move
        else:
            func = shutil.copy
        while try_n < max_tries: # This forces to complete the operation until no PermissionError is raised
            try:
                func(source, destination)
                return
            except PermissionError:
                time.sleep(0.1)
                try_n += 1
        raise OSError(f'Something is going wrong when copying to {destination}')


    def __put_files(self, source_path, type='exp'):
        '''
        Move the files to run the model to the specific location.
        source_path: str, file path
        tpye: str, type, it could be {exp, wth, sol, crop}
        '''
        destinations = {
            'exp': self.wdir, 'wth': os.path.join(self.DSSATFolder, 'Weather'), 
            'sol': os.path.join(self.DSSATFolder, 'Soil'),
            'crop': os.path.join(self.DSSATFolder, 'Genotype'), 
        }
        
        if os.path.isdir(source_path): # This basically only for WTH
            files = os.listdir(source_path)
            for f in files:
                if not os.path.exists(os.path.join(destinations[type], f)):
                    self.__handleCopy(os.path.join(source_path, f), os.path.join(destinations[type], f))
                else:
                    break
            return
        if type == 'sol':
            self.__handleCopy(source_path, os.path.join(destinations['sol'], f'{os.path.basename(self.experimental)[:2]}.SOL'))
        else:
            self.__handleCopy(source_path, os.path.join(destinations[type], os.path.basename(source_path)))


    def __wrap_out(self, treat):
        treatOut = {}
        out_filenames = [f for f in os.listdir(self.wdir) if '.OUT' in f]
        for filename in out_filenames:
            treatOut[filename[:-4]] = dssatUtils.out_wrapper(os.path.join(self.wdir, filename))
        self.results.addTreatmentOut(treat, treatOut)
        return

    def __get_treatments(self):
        treatments = []
        flag = False
        with open(os.path.basename(self.experimental), 'r') as expfile:
            for line in expfile:
                if '*TREATMENTS' in line:
                    flag = True
                    continue
                if flag:
                    if len(line.strip()) < 1:
                        return treatments[1:]
                    treatments.append(line.split()[0])
        raise DSSATInputError(f'Treatments not detected on {os.path.basename(self.experimental)} file')

    # TODO: Return to cwd everytime it stops for whatever reason. I think it is done
    def runDSSAT(
        self, experimental, crop, treatments=None, 
        wth_folder=None, soil_profile=None, wdir=None,
        crop_file=None
    ): 
        '''
        Runs DSSAT based on the passed arguments to the function.
        ...
        Arguments
        ---------------------
        experimental: str
            Path to Exprimental File (.crX)
        wth_folder: str
            Path to weather files (.WTH). If None then the Weather files 
            are expected to be one of the default ones.
        soil_profile: str
            Path to soil file (.SOL). If none a Default soil is expected on 
            the Experimental File.
        crop_file: str
            Path to one of the crop files (.SPE, .ECO, .CUL). All of the crop
            files with that name on the same folder will be taken.
        wdir: str
            Path to working directory. If None, then it's current directory.
        treatements: list
            Any iterable listing the treatements to run. If None all treatements are run
        crop: str
            Two character crop code, defined as follows:
            +----------------+----+----------+----------------------+---------------+-------------+
            |    CROP        |DSSA|  ICASA   | Default Model        | Alt Model 1   | Alt Model 2 |
            +----------------+----+----------+----------------------+---------------+-------------+
            | Alfalfa        | AL | ALF      | FORAGE-alfalfa       |               |             |
            | Barley         | BA | BAR      | CROPSIM-CERES-barley | CSCRP-barley  |             |
            | Bahia          | BH | BHG      | CROPGRO-bahia        |               |             |
            | Bermudagrass   | BM | BMD      | FORAGE-bermuda       |               |             |
            | Dry bean       | BN | BND      | CROPGRO-drybean      |               |             |
            | Brachiaria     | BR | BRC      | FORAGE-brachiaria    |               |             |
            | Cabbage        | CB | CBG      | CROPGRO-cabbage      |               |             |
            | Chickpea       | CH | CHP      | CROPGRO-chickpea     |               |             |
            | Canola         | CN | CNL      | CROPGRO-canola       |               |             |
            | Cotton         | CO | COT      | CROPGRO-cotton       |               |             |
            | Cowpea         | CP | CWP      | CROPGRO-cowpea       |               |             |
            | Cassava        | CS | CSV      | CSYCA-cassava        | CSCAS-cassava |             |
            | Fallow         | FA | FAL      | CROPGRO              |               |             |
            | Faba bean      | FB | FBN      | CROPGRO-fababean     |               |             |
            | Generic forage | G0 | FRG      | CROPGRO ???          | FORAGE ???    |             |
            | Green bean     | GB | BNG      | CROPGRO-greenbean    |               |             |
            | Millet         | ML | FML      | CERES-millet         |               |             |
            | Maize          | MZ | MAZ      | CERES-maize          | IXIM-maize    |             |
            | Napier grass   | NP | NPG      | CROPGRO-napiergrass  |               |             |
            | Pineapple      | PI | PNA      | ALOHA-pineapple      |               |             |
            | Peanut         | PN | PNT      | CROPGRO-peanut       |               |             |
            | Pigeonpea      | PP | PGP      | CROPGRO-pigeonpea    |               |             |
            | Bellpepper     | PR | PPR      | CROPGRO-pepper       |               |             |
            | Potato         | PT | POT      | SUBSTOR-potato       |               |             |
            | Ryegrass       | RG | RGP      | FORAGE-ryegrass      |               |             |
            | Rice           | RI | RIC      | CERES-rice           |               |             |
            | Soybean        | SB | SBN      | CROPGRO-soybean      |               |             |
            | Sugarcane      | SC | SUC      | CANEGRO              | CASUPRO       | SAMUCA      |
            | Sugarbeet      | BS | SBT      | CERES-Sugarbeet      |               |             |
            | Safflower      | SF | SAF      | CROPGRO-safflower    |               |             |
            | Sorghum        | SG | SGG      | CERES-sorghum        |               |             |
            | Sunflower      | SU | SUN      | CROPGRO-sunflower    |               |             |
            | Sweetcorn      | SW | SWC      | CERES-sweetcorn      |               |             |
            | Tef            | TF | TEF      | NWHEAT-tef           |               |             |
            | Tomato         | TM | TOM      | CROPGRO-tomato       |               |             |
            | Tanier         | TN | TAN      | AROIDS               |               |             |
            | Taro           | TR | TAR      | AROIDS               |               |             |
            | Velvetbean     | VB | VBN      | CROPGRO-velvetbean   |               |             |
            | Wheat          | WH | WHB, WHD | CROPSIM-CERES-wheat  | NWHEAT        | CSCRP-wheat |
            +----------------+----+----------+----------------------+---------------+-------------+
        '''
        self.experimental = experimental
        if isinstance(wdir, type(None)):
            self.wdir = os.getcwd()
        else:
            self.wdir = wdir
            if not os.path.exists(self.wdir):
                os.mkdir(self.wdir)
        
        # Move crX File
        for f in os.listdir(os.path.dirname(experimental)):
            if os.path.basename(experimental).split('.')[0] in f:
                self.__put_files(os.path.join(os.path.dirname(experimental), f), type='exp')
        # Move WTH File
        if not isinstance(wth_folder, type(None)):
            self.__put_files(wth_folder, type='wth')
        # Move SOL File
        if not isinstance(soil_profile, type(None)):
            self.__put_files(soil_profile, type='sol')
        # Move SPE, CUL and ECO File
        if not isinstance(crop_file, type(None)):
            crop_file = crop_file[:-3]
            for file_type in ['SPE', 'CUL', 'ECO']:
                if os.path.exists(crop_file+file_type):
                    try:
                        shutil.copy(
                            os.path.join(self.DSSATFolder, 'Genotype', os.path.basename(crop_file+file_type)),
                            os.path.join(self.DSSATFolder, 'Genotype', 'bk_'+os.path.basename(crop_file+file_type)),
                        )
                        self.__put_files(crop_file+file_type, type='crop')
                    except shutil.SameFileError:
                        os.remove(
                            os.path.join(self.DSSATFolder, 'Genotype', os.path.basename('bk_'+crop_file+file_type))
                            )
                        shutil.copy(
                            os.path.join(self.DSSATFolder, 'Genotype', os.path.basename(crop_file+file_type)),
                            os.path.join(self.DSSATFolder, 'Genotype', os.path.basename('bk_'+crop_file+file_type))
                        )
                        self.__put_files(crop_file+file_type, type='crop')
        
        def recover_crop():
            '''This function moves the original crop Files back to its location'''
            if not isinstance(crop_file, type(None)):
                for file_type in ['SPE', 'CUL', 'ECO']:
                    bk_file = os.path.join(self.DSSATFolder, 'Genotype', os.path.basename('bk_'+crop_file+file_type))
                    if os.path.exists(bk_file):
                        try:
                            self.__handleCopy(
                                bk_file,
                                os.path.join(self.DSSATFolder, 'Genotype', os.path.basename(crop_file+file_type)),
                                move=True
                            )
                        except FileNotFoundError:
                            continue
        
        os.chdir(self.wdir)
        
        if not hasattr(treatments, '__iter__'):
            self.treatments = self.__get_treatments()
        else:
            self.treatments = list(map(str, treatments))
            treatments_on_file = self.__get_treatments()
            for treatment in self.treatments:
                if treatment not in treatments_on_file:
                    recover_crop()
                    os.chdir(self.curdir)
                    raise DSSATInputError(f'Treatment {treatment} not found in {os.path.basename(self.experimental)} file')
        self.results = dssatUtils.DSSATOutput(self.treatments)

        for treatment in self.treatments:
            DSSBatchLines = dssatUtils.writeDSSBATCH(
                crop=crop, wdir=self.wdir, 
                dssatExe=self.DSSATExe, exp=os.path.basename(self.experimental), treat=treatment
            )
            with open(os.path.join(wdir, 'DSSBatch.v47'), 'w') as f:
                f.writelines(DSSBatchLines)
            # Run the model handling keyboard interruption and errors in Parallel runs
            max_tries = 20
            try_n = 0
            while try_n < max_tries: 
                try:
                    exe_thr = subprocess.Popen([self.DSSATExe, crop, 'B', 'DSSBatch.v47'], stdout=subprocess.PIPE)
                    returncode = exe_thr.wait()
                except KeyboardInterrupt: # If it is keyboard interrumpted, then return to curdir
                    recover_crop()
                    os.chdir(self.curdir)
                if returncode == 0:
                    break
                else:
                    time.sleep(0.1)
                    try_n += 1
            

            if self.verbose:
                dssatUtils.printSysOut(exe_thr.stdout)
            if returncode != 0:
                self.__wrap_out(treatment)
                recover_crop()
                os.chdir(self.curdir)
                raise OSError(f'DSSAT execution failed')
            else:
                self.__wrap_out(treatment)
        os.chdir(self.curdir)
        recover_crop()
        
        return

    

class CSM_Docker():
    '''
    This is an implementation of DSSAT_Docker
    -----------------------------------------------------------------------------                                           
    DSSAT COMMAND LINE USAGE:                                                                                               
                                                                                                                            
    dscsm047 <model> runmode <argA> <argB> <control_file>                                                                 
                                                                                                                            
    -----------------------------------------------------------------------------                                           
    Details:                                                                                                                
    <model>   - OPTIONAL                                                                                                  
                - 8-character name of crop model (e.g., MZIXM047 or WHAPS047).                                              
                - If model name is blank or invalid, the default will be used.                                              
                                                                                                                            
    runmode   - REQUIRED                                                                                                  
                - 1-character run mode code                                                                                 
                - see table below for valid values of argA and argB                                                         
                                                                                                                            
    <control_file> - OPTIONAL                                                                                             
                - path + filename of external file which contains overrides for                                             
                    simulation controls.                                                                                    
                - This option is available with all run modes except D and I.                                               
                - Default file (DSCSM047.CTR) is found in DSSAT root directory.                                             
                - see https://dssat.net/using-an-external-simulation-control-file                                           
                - 120 characters maximum.                                                                                   
    run                                                                                                                     
    mode argA       argB  Description                                                                                       
    ---- ---------  ----- ------------------------------------------------------                                            
    A   FileX      NA    All: Run all treatments in the specified FileX.                                                   
    B   BatchFile  NA    Batch: Batchfile lists experiments and treatments.                                                
    C   FileX      TrtNo Command line: Run single FileX and treatment #.                                                   
    D   TempFile   NA    Debug: Skip input module and use existing TempFile.                                               
    E   BatchFile  NA    Sensitivity: Batchfile lists FileX and TrtNo.                                                     
    F   BatchFile  NA    Farm model: Batchfile lists experiments and treatments.                                           
    G   FileX      TrtNo Gencalc: Run single FileX and treatment #.                                                        
    I   NA         NA    Interactive: Interactively select FileX and TrtNo.                                                
    L   BatchFile  NA    Gene-based model (Locus): Batchfile for FileX and TrtNo                                           
    N   BatchFile  NA    Seasonal analysis: Batchfile lists FileX and TrtNo.                                               
    Q   BatchFile  NA    Sequence analysis: Batchfile lists FileX & rotation #.                                            
    S   BatchFile  NA    Spatial: Batchfile lists experiments and treatments.                                              
    T   BatchFile  NA    Gencalc: Batchfile lists experiments and treatments.                                              
    Y   BatchFile  NA    Yield forecast mode uses ensemble weather data.                                                   
                                                                                                                            
    BatchFile - Name of DSSAT batch file with list of exeriments and treatments                                           
                    (e.g., DSSBATCH.v47)                                                                                    
                - Current directory, 30 characters maximum                                                                  
                                                                                                                            
    FileX     - Name of Experimental file (e.g., UFGA7801.SBX)                                                            
                - Current directory, 12-character DSSAT naming convention                                                   
                                                                                                                            
    TempFile  - Name of temporary I/O file, normally generated by the input                                               
                    module (e.g., DSSAT47.INP)                                                                              
                - Current directory, 30 characters maximum                                                                  
                                                                                                                            
    TrtNo     - Treatment # (integer) in specified FileX to be simulated                                                  
                                                                                                                            
    -----------------------------------------------------------------------------                                           
    Example #1:                                                                                                            
    DSCSM047 B DSSBATCH.V47                                                                                                
    Effect: Run in batch mode. Name of the batch file is DSSBATCH.V47.                                                     
                                                                                                                            
    Example #2:                                                                                                            
    DSCSM047 MZIXM047 A UFGA8201.MZX                                                                                       
    Effect: Run all treatments in experiment UFGA8201.MZX using IXIM model.                                                
                                                                                                                            
    Example #3:                                                                                                            
    DSCSM047 Q DSSBATCH.V47 DSCSM047.CTR                                                                                   
    Effect: Run sequence simulation listed in DSSBATCH.V47 using the                                                       
            simulation control options specified by DSCSM047.CTR                                                         
    ----------------------------------------------------------------------------- 
    '''
    def __init__(self, DSSATimage='eusojk/dssat:v47', verbose=False, **kwargs):
        self.verbose = verbose
        self.DSSATimage = DSSATimage
        self.client = docker.from_env()
        all_images = sum(list(map(lambda x: x.attrs['RepoTags'], self.client.images.list())), [])
        if DSSATimage not in all_images:
           raise OSError(f'{DSSATimage} image was not found on your docker client')
        try:
            self.container = self.client.containers.run(
                self.DSSATimage, f'infinity', detach=True, entrypoint='/bin/sleep', **kwargs
            )
        except docker.errors.APIError:
            self.container = self.client.containers.get(kwargs['name'])
            self.container.stop()
            self.container.remove()
            self.container = self.client.containers.run(
                self.DSSATimage, f'infinity', detach=True, entrypoint='/bin/sleep', **kwargs
            )
        # if not os.path.exists(os.path.join(tempfile.gettempdir(), 'dssat')):
        #     os.mkdir(os.path.join(tempfile.gettempdir(), 'dssat'))
        return


    def put_folder(self, source_path, output_path=os.path.join(tempfile.gettempdir(), 'dssat.tar'), to='/tmp'):
        with tarfile.open(output_path, "w") as tar:
            tar.add(source_path, arcname='dssat')
        with open(output_path, 'r') as data:
            self.container.put_archive(to, data)
    

    def get_folder(self, output_path=os.path.join(tempfile.gettempdir(), 'dssat.tar')):
        path, stat = self.container.get_archive('/tmp/dssat')
        with open(output_path, 'wb') as data:
            for chunk in path:
                data.write(chunk)
        tar = tarfile.open(output_path)
        tar.extractall(os.path.dirname(output_path))
        tar.close()

    def __wrap_out(self):
        self.results = {}
        out_path = os.path.join(tempfile.gettempdir(), 'dssat')
        out_filenames = [f for f in os.listdir(out_path) if '.OUT' in f]
        for filename in out_filenames:
            file_path = os.path.join(tempfile.gettempdir(), 'dssat', filename)
            self.results[filename[:-4]] = dssatUtils.out_wrapper(file_path)
        return


    def runFileX(self, experimental, crop, wth_folder=None, rm_container=False, soil_profile=None):
        '''
        Crop is defined as it is indicated in: https://dssat.net/plant-growth-modules-in-dssat-csm/
        '''
        
        self.put_folder(os.path.dirname(experimental))
        if not isinstance(wth_folder, type(None)):
            self.put_folder(wth_folder, to='/dssat47/Weather/')
            wth_files = self.container.exec_run('ls /dssat47/Weather/dssat/').output.decode('utf-8').split()
            for wth_file in wth_files:
                self.container.exec_run(f'mv /dssat47/Weather/dssat/{wth_file} /dssat47/Weather/{wth_file}')
        if not isinstance(soil_profile, type(None)):
            self.put_folder(os.path.dirname(soil_profile))
            self.container.exec_run(
                f'mv /tmp/dssat/{os.path.basename(soil_profile)} /dssat47/Soil/{os.path.basename(experimental)[:2]}.SOL'
                )

        exe_thr = self.container.exec_run(
            f'/dssat47/dscsm047 {crop} A {os.path.basename(experimental)}',
            workdir='/tmp/dssat'
        )
        if exe_thr.exit_code != 0:
            self.get_folder()
            self.__wrap_out()
            if rm_container:
                self.container.kill()
                self.container.remove()
            raise OSError(f'DSSAT execution failed  \n {exe_thr.output.decode("utf-8")}')
        else:
            self.get_folder()
            if self.verbose:
                try:
                    sys.stdout.buffer.write(exe_thr.output)
                except AttributeError:
                    print(exe_thr.output.decode('utf-8'))

        if rm_container:
            self.container.kill()
            self.container.remove()
        self.__wrap_out()
        return
        
        