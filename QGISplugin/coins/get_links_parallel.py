import argparse, multiprocessing, math
from functools import partial
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Path to the input array")
parser.add_argument("--output", help="Path to the processed array")

a = parser.parse_args()

def getLinksMultiprocessing(n, tempArray):
    # Printing the progress bar
    total = tempArray.shape[0]
    if n%1000==0:
        """
        Dividing by two to have 50 progress steps
        Subtracting from 50, and not hundred to have less progress steps
        """
        currentProgress = math.floor(100*n/total/2)
        remainingProgress = 50 - currentProgress            
        print('>'*currentProgress + '-' * remainingProgress + ' [%d/%d] '%(n,total) + '%d%%'%(currentProgress*2), end='\r')
        
    # Create mask for adjacent edges as endpoint 1
    m1 = tempArray[:,1]==tempArray[n,1]
    m2 = tempArray[:,2]==tempArray[n,1]
    mask1 = m1 + m2

    # Create mask for adjacent edges as endpoint 2
    m1 = tempArray[:,1]==tempArray[n,2]
    m2 = tempArray[:,2]==tempArray[n,2]
    mask2 = m1 + m2

    # Use the tempArray to extract only the uniqueIDs of the adjacent edges at both ends
    mask1 = tempArray[:,0][~(mask1==0)]
    mask2 = tempArray[:,0][~(mask2==0)]

    # Links (excluding the segment itself) at both the ends are converted to list and added to the 'unique' attribute
    return(n, list(mask1[mask1 != n]), list(mask2[mask2 != n]))
    
if __name__ == '__main__':
    print('Finding adjacent links...\n')
    tempArray = np.load(a.input, allow_pickle=True)
    iterations = [n for n in range(0, tempArray.shape[0])]

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    constantParameterFunction = partial(getLinksMultiprocessing, tempArray=tempArray)
    result = pool.map(constantParameterFunction, iterations)
    pool.close()
    pool.join()
    iterations = None

    np.save(a.output, result)
