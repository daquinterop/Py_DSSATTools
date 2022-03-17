import pandas as pd

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