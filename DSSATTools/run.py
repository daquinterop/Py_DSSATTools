import subprocess
import shutil
from .exceptions import DSSATNotFound
import glob
import os
import tempfile
from datetime import datetime

__MODELS__ = { # Associates model name to file name (CUL, SPE, ECO)
    'PRFRM047':  'ALFRM047',
    'RICER047': 'RICER047'
}


class CSMRun():
    def __init__(self, DSSATPath, DSSATexec='dscsm047', **kwargs):
       return


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
        subprocess.run(['ln', '-sf', self.Experimental, os.path.join(self.tmp_dir, os.path.basename(self.Experimental))])
        # subprocess.run(['ln', '-sf', self.SPE, os.path.join(self.tmp_dir, os.path.basename(self.SPE))])
        # subprocess.run(['ln', '-sf', self.CUL, os.path.join(self.tmp_dir, os.path.basename(self.CUL))])
        subprocess.run(['ln', '-sf', self.SOL, os.path.join(self.tmp_dir, 'SOIL.SOL')])
        for WTH_file in self.WTH:
            subprocess.run(['ln', '-sf', WTH_file, os.path.join(self.tmp_dir, os.path.basename(WTH_file))])
        try:
            subprocess.run(['ln', '-sf', self.MOW, os.path.join(self.tmp_dir, os.path.basename(self.MOW))])
        except AttributeError:
            None


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
            os.path.join(self.GenotypePath, f'{__MODELS__[model]}.SPE'), 
            os.path.join(self.tmp_dir, f'{__MODELS__[model]}.SPE')
        ])
        if os.path.exists( os.path.join(self.GenotypePath, f'{__MODELS__[model]}.CUL')):
            subprocess.run([
                'ln', '-sf', 
                 os.path.join(self.GenotypePath, f'{__MODELS__[model]}.CUL'), 
                os.path.join(self.tmp_dir, f'{__MODELS__[model]}.CUL')
            ])
        if os.path.exists(os.path.join(self.GenotypePath, f'{__MODELS__[model]}.ECO')):
            subprocess.run([
                'ln', '-sf', 
                 os.path.join(self.GenotypePath, f'{__MODELS__[model]}.ECO'), 
                os.path.join(self.tmp_dir, f'{__MODELS__[model]}.ECO')
            ])
        # Save the current Path
        prev_path = os.getcwd()
        # Create ArgA based on run mode
        if runmode in ['A', 'C', 'G']:
            argA = os.path.basename(self.Experimental)
        os.chdir(self.tmp_dir) # Go to tmp_dir
        subprocess.run([self.dssat, model, runmode, argA, argB, control_file])
        os.chdir(prev_path) # Back to previous path