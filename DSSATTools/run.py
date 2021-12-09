import subprocess
import shutil
from .exceptions import DSSATNotFound
import glob
import os
from datetime import datetime
import docker
import sys

__MODELS__ = { # Associates model name to file name (CUL, SPE, ECO)
    'PRFRM047':  'ALFRM047',
    'RICER047': 'RICER047'
}


class CSM():
    def __init__(self, DSSATimage='eusojk/dssat:v47', **kwargs):
        self.DSSATimage = DSSATimage
        self.client = docker.from_env()
        all_images = sum(list(map(lambda x: x.attrs['RepoTags'], self.client.images.list())), [])
        if DSSATimage not in all_images:
           raise OSError(f'{DSSATimage} image was not found on your docker client')
        # if not os.path.exists(os.path.join(tempfile.gettempdir(), 'dssat')):
        #     os.mkdir(os.path.join(tempfile.gettempdir(), 'dssat'))
        return



    def runFileX(self, experimental, crop):
        '''
        Crop is defined as it is indicated in: https://dssat.net/plant-growth-modules-in-dssat-csm/
        '''
        container = self.client.containers.run(
            self.DSSATimage, f'infinity', detach=True,
            volumes={os.path.dirname(experimental): {'bind': '/tmp/dssat', 'mode': 'rw'}},
            working_dir='/tmp/dssat', auto_remove=False, entrypoint='/bin/sleep',
        )
        exe_thr = container.exec_run(f'/dssat47/dscsm047 {crop} A {os.path.basename(experimental)}')
        if exe_thr.exit_code != 0:
            container.kill()
            container.remove()
            raise OSError(f'DSSAT execution failed  \n {exe_thr.output.decode("utf-8")}')
        else:
            sys.stdout.buffer.write(exe_thr.output)
        container.kill()
        container.remove()
        return
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
        # subprocess.run([
        #     'ln', '-sf', 
        #     os.path.join(self.GenotypePath, f'{__MODELS__[model]}.SPE'), 
        #     os.path.join(self.tmp_dir, f'{__MODELS__[model]}.SPE')
        # ])
        # if os.path.exists( os.path.join(self.GenotypePath, f'{__MODELS__[model]}.CUL')):
        #     subprocess.run([
        #         'ln', '-sf', 
        #          os.path.join(self.GenotypePath, f'{__MODELS__[model]}.CUL'), 
        #         os.path.join(self.tmp_dir, f'{__MODELS__[model]}.CUL')
        #     ])
        # if os.path.exists(os.path.join(self.GenotypePath, f'{__MODELS__[model]}.ECO')):
        #     subprocess.run([
        #         'ln', '-sf', 
        #          os.path.join(self.GenotypePath, f'{__MODELS__[model]}.ECO'), 
        #         os.path.join(self.tmp_dir, f'{__MODELS__[model]}.ECO')
        #     ])
        # # Save the current Path
        # prev_path = os.getcwd()
        # # Create ArgA based on run mode
        # if runmode in ['A', 'C', 'G']:
        #     argA = os.path.basename(self.Experimental)
        # os.chdir(self.tmp_dir) # Go to tmp_dir
        # subprocess.run([self.dssat, model, runmode, argA, argB, control_file])
        # os.chdir(prev_path) # Back to previous path
        