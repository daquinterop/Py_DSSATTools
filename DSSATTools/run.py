import subprocess
import shutil
from .exceptions import DSSATNotFound
import glob
import os

class CSMRun():
    def __init__(self, exec='dscsm047', **kwargs):
        ''' 
        Is the object that handles the execution of the DSSAT model, its
        initializated passing the exec arg, among other kwargs.

            exec: DSSAT Shell command | str
        '''
        self.dssat = exec
        if shutil.which(self.dssat) != None:
            print(f'DSSAT found at {shutil.which(self.dssat)}')
            for ext in ['*.OUT', '*.LST', 'fort.*']:
                for f in glob.glob(ext):
                    os.remove(f)

        else:
            raise DSSATNotFound(f'{self.dssat} was not found in your environment, please make sure it is compiled and added to $PATH and exec arg is well defined')
            