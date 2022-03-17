from tkinter import E
import pandas as pd

class outFile(list):
    def __init__(self, out):
        super().__init__(out)
        return
    
    def __str__(self) -> str:
        return ''.join(self)


class DSSATOutput(dict):
    def __init__(self, treatments):
        self.treatments = treatments
        super().__init__({treat: {} for treat in treatments})
        return

    def addTreatmentOut(self, treat, treatOut):
        self[treat] = treatOut
        for key in self[treat].keys():
            out = self[treat][key]
            if isinstance(out, list):
                self[treat][key] = outFile(out)
        return

    def listOutput(self):
        '''
        List the Variables included in the Output
        '''
        return list(self.get(self.treatments[0]).keys())

    def getOutput(self, outName, treat):
        '''
        Get the output for the specified OutName and treatment
        '''
        return self.get(treat).get(outName)
        

def writeDSSBATCH(crop, wdir, dssatExe, exp, treat):
    BatchStr = '''
        $BATCH(%(crop)s)
        !
        ! Directory    : %(wdir)s
        ! Command Line : %(dssatExe)s %(crop)s B DSSBatch.v47
        ! Crop         : %(crop)s         
        ! Experiment   : %(exp)s
        ! ExpNo        : %(treat)s
        ! Debug        : %(dssatExe)s %(crop)s " B DSSBatch.v47"
        !
        @FILEX                                                                                        TRTNO     RP     SQ     OP     CO''' \
            % {'crop': crop, 'wdir': wdir, 'exp': exp, 'treat': treat, 'dssatExe': dssatExe}
    lines = [line[8:] + '\n' for line in BatchStr[1:].split('\n')]
    filex_len = lines[-1].index('TRTNO')
    lines.append(f'{exp}{(filex_len - len(exp) + 4)*" "}{treat}      1      0      1      0')
    return lines

def out_wrapper(filename):
    '''
    Takes a file separated by spaces and return a df a list with
    the lines of the file.
    '''
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    copy_lines = list(lines)
    if len(lines) < 1:
        return lines
    for n, line in enumerate(lines):
        if '@' in line:   
            break
            
    lines = lines[n:]
    lines = [line.replace('\n', '') for line in lines]
    n_cols = len(lines[0].split())
    df = pd.DataFrame(
        [line.split() for line in lines[1:] if len(line.split()) == n_cols],
        columns=lines[0].split()
    )
    if len(df) == 0:
        return copy_lines
    else:
        return df


def printSysOut(sysOut):
    prev_line = ''
    for line in sysOut:
        line = line.decode('utf-8')
        if prev_line == line:
            pass
        else:
            print(line, end='')
        prev_line = line
    print()
    return