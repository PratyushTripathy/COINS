import os, argparse, multiprocessing, math, json
from functools import partial
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Path to the input dictionary (JSON)")
parser.add_argument("--output", help="Path to the processed dictionary (JSON)")

a = parser.parse_args()

def mergeLinesMultiprocessing(n, uniqueDict):
    # Printing the progress bar
    total = len(uniqueDict)
    if n%1000==0:
        """
        Dividing by two to have 50 progress steps
        Subtracting from 50, and not hundred to have less progress steps
        """
        currentProgress = math.floor(100*n/total/2)
        remainingProgress = 50 - currentProgress            
        print('>'*currentProgress + '-' * remainingProgress + ' [%d/%d] '%(n,total) + '%d%%'%(currentProgress*2), end='\r')
    
    outlist = set()
    currentEdge1 = n

    outlist.add(currentEdge1)

    while True:
        if type(uniqueDict[currentEdge1][6]) == type(1) and \
           uniqueDict[currentEdge1][6] not in outlist:
            currentEdge1 = uniqueDict[currentEdge1][6]
            outlist.add(currentEdge1)
        elif type(uniqueDict[currentEdge1][7]) == type(1) and \
           uniqueDict[currentEdge1][7] not in outlist:
            currentEdge1 = uniqueDict[currentEdge1][7]
            outlist.add(currentEdge1)
        else:
            break
    currentEdge1 = n
    while True:
        if type(uniqueDict[currentEdge1][7]) == type(1) and \
           uniqueDict[currentEdge1][7] not in outlist:
            currentEdge1 = uniqueDict[currentEdge1][7]
            outlist.add(currentEdge1)
        elif type(uniqueDict[currentEdge1][6]) == type(1) and \
           uniqueDict[currentEdge1][6] not in outlist:
            currentEdge1 = uniqueDict[currentEdge1][6]
            outlist.add(currentEdge1)
        else:
            break

    outlist = list(outlist)
    outlist.sort()
    return(outlist)
    
if __name__ == '__main__':
    print('Merging segments to generate strokes...\n')
    with open(a.input, 'r') as fp:
        unique = json.load(fp)
    iterations = [n for n in range(0, len(unique))]
    
    new_unique = {int(key) : unique[key] for key in unique.keys()}
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    constantParameterFunction = partial(mergeLinesMultiprocessing, uniqueDict=new_unique)
    result = pool.map(constantParameterFunction, iterations)
    pool.close()
    pool.join()
    iterations = None
    
    np.save(a.output, result)
    