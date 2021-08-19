import subprocess
import shutil
from .exceptions import DSSATNotFound
import glob
import os
import tempfile
from datetime import datetime

class CSMRun():
    def __init__(self, DSSATPath, DSSATexec='dscsm047', **kwargs):
        ''' 
        Is the object that handles the execution of the DSSAT model, its
        initializated passing the exec arg, among other kwargs.

            DSSATexec: DSSAT Shell command | str
            DSSATPath: path were DSSAT source code is located | str
        '''
        self.dssat = DSSATexec
        # It checks whether DSSAT Shell command can't be found or not
        if shutil.which(self.dssat) != None:
            print(f'DSSAT found at {shutil.which(self.dssat)}')
            # Removes all the Out files from the previous execution
            # for ext in ['*.OUT', '*.LST', 'fort.*']:
            #     for f in glob.glob(ext):
            #         os.remove(f)

        else:
            raise DSSATNotFound(f'{self.dssat} was not found in your environment, please make sure it is compiled and added to $PATH and exec arg is well defined')
        self.DSSATPath = DSSATPath

        # Define attributes if those haven't been defined during the init
        # DataPath is the path that contains all DSSAT built data
        if 'DataPath' in kwargs.keys():
            self.DataPath = kwargs['DataPath']
        else:
            self.DataPath = os.path.join(self.DSSATPath, 'Data')
        # StandardData is a path than contains some of the required files to run the model
        if 'StandardData' in kwargs.keys():
            self.StandardDataPath = kwargs['StandardData']
        else:
            self.StandardDataPath = os.path.join(self.DataPath, 'StandardData')

        # Genotype is the folder that contains CUL, ECO and SPE files for the different crops
        if 'GenotypePath' in kwargs.keys():
            self.GenotypePath = kwargs['GenotypePath']
        else:
            self.GenotypePath = os.path.join(self.DataPath, 'Genotype')

        # Create a Temporary dir for working there
        self.tmp_dir = os.path.join(tempfile.gettempdir(), 'DSSATTools', datetime.now().strftime('%y%m%d%H%M%S'))
        os.makedirs(self.tmp_dir)
        print(f'{self.tmp_dir} Temporary working directory created')

        # Link necessary files for simulation on the temporary directory
        subprocess.run(['ln', '-sf', os.path.join(self.DataPath, 'MODEL.ERR'), os.path.join(self.tmp_dir, 'MODEL.ERR')])
        subprocess.run(['ln', '-sf', os.path.join(self.DataPath, 'DSSATPRO.L47'), os.path.join(self.tmp_dir, 'DSSATPRO.L47')])
        subprocess.run(['ln', '-sf', os.path.join(self.DataPath, 'SIMULATION.CDE'), os.path.join(self.tmp_dir, 'SIMULATION.CDE')])
        subprocess.run(['ln', '-sf', os.path.join(self.DataPath, 'DETAIL.CDE'), os.path.join(self.tmp_dir, 'DETAIL.CDE')])
        subprocess.run(['ln', '-sf', os.path.join(self.DataPath, 'DATA.CDE'), os.path.join(self.tmp_dir, 'DATA.CDE')])
        # Link StandardData directory to DSSAT Path
        subprocess.run(['ln', '-sf', self.StandardDataPath, os.path.join(self.DSSATPath, 'StandardData')])

        # If specific file locations are passed as args, then it will take those
        if 'RIX' in kwargs.keys():
            self.RIX = kwargs['RIX']
        else:
            None

        if 'WTH' in kwargs.keys():
            self.WTH = kwargs['WTH']
            if isinstance(self.WTH, str):
                self.WTH = [self.WTH]
        else:
            None

        # if 'SPE' in kwargs.keys():
        #     self.SPE = kwargs['SPE']
        # else:
        #     None

        # if 'CUL' in kwargs.keys():
        #     self.CUL = kwargs['CUL']
        # else:
        #     None

        if 'SOL' in kwargs.keys():
            self.SOL = kwargs['SOL']
        else:
            None

        # Link input files to temporary directory
        subprocess.run(['ln', '-sf', self.RIX, os.path.join(self.tmp_dir, os.path.basename(self.RIX))])
        # subprocess.run(['ln', '-sf', self.SPE, os.path.join(self.tmp_dir, os.path.basename(self.SPE))])
        # subprocess.run(['ln', '-sf', self.CUL, os.path.join(self.tmp_dir, os.path.basename(self.CUL))])
        subprocess.run(['ln', '-sf', self.SOL, os.path.join(self.tmp_dir, os.path.basename(self.SOL))])
        for WTH_file in self.WTH:
            subprocess.run(['ln', '-sf', WTH_file, os.path.join(self.tmp_dir, os.path.basename(WTH_file))])


    def run(self, model, runmode, argA, argB='', control_file=''):
        '''
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
        # Create Links to Crop Files
        subprocess.run([
            'ln', '-sf', 
            os.path.join(self.GenotypePath, f'{model}.SPE'), 
            os.path.join(self.tmp_dir, f'{model}.SPE')
        ])
        if os.path.exists( os.path.join(self.GenotypePath, f'{model}.CUL')):
            subprocess.run([
                'ln', '-sf', 
                 os.path.join(self.GenotypePath, f'{model}.CUL'), 
                os.path.join(self.tmp_dir, f'{model}.CUL')
            ])
        if os.path.exists(os.path.join(self.GenotypePath, f'{model}.ECO')):
            subprocess.run([
                'ln', '-sf', 
                 os.path.join(self.GenotypePath, f'{model}.ECO'), 
                os.path.join(self.tmp_dir, f'{model}.ECO')
            ])
        # Save the current Path
        prev_path = os.getcwd()
        # Create ArgA based on run mode
        if runmode in ['A', 'C', 'G']:
            argA = os.path.basename(self.RIX)
        os.chdir(self.tmp_dir) # Go to tmp_dir
        subprocess.run([self.dssat, model, runmode, argA, argB, control_file])
        os.chdir(prev_path) # Back to previous path