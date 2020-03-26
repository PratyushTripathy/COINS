import os, time, sys, random, multiprocessing
import numpy as np

os.chdir(r"C:\Users\pratyush-GIS\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\coins")
from .streetHierarchy import network

def timeTaken(t1, t2, stepName):
    print('It took %.2f seconds to %s' % ((t2 - t1), stepName))
    
t1 = time.time()
inFile = "F:\StreetNetworkLongest\QGISplugin\check\edges.shp"
outMergedFile = inFile.replace('.shp', '_strokes.shp')
outPreMergedFile = inFile.replace('.shp', '_preMerge.shp')

myNetwork = network(inFile)
#Split lines
myNetwork.splitLines()
t2 = time.time()
timeTaken(t1, t2, 'split lines')

#Create unique ID
myNetwork.uniqueID()
t3 = time.time()
timeTaken(t2, t3, 'assign unique ID')

#Compute connectivity table
myNetwork.getLinks()
t4 = time.time()
timeTaken(t3, t4, 'find links')

#Find best link at every point for both lines
myNetwork.bestLink()
t5 = time.time()
timeTaken(t4, t5, 'find best link')

#Cross check best links
myNetwork.crossCheckLinks(self.angleThreshold)
t6 = time.time()
timeTaken(t5, t6, 'cross check link')

#Merge finalised links
myNetwork.mergeLines()
t7 = time.time()
timeTaken(t6, t7, 'merge lines')

#Export lines
if self.dlg.preMergeCheckBox.isChecked():
    myNetwork.exportPreMerged(outPreMergedFile)
myNetwork.exportMerged(outMergedFile)

t8 = time.time()
print('Processing completed in %.2f' % (t8-t1))

