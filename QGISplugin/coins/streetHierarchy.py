"""
This module is designed to read line type ESRI shapefiles,
mainly roads and find longest paths based on their
connectivity angle.

Author: PratyushTripathy
Date: 14 December 2018

"""

import os, sys, math, time, multiprocessing, json
from functools import partial
import numpy as np
from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import QVariant
import processing
from qgis.core import *
from PyQt5.QtGui import QFont

t1 = time.time()

#Set recurrsion depth limit to avoid error at a later stage
sys.setrecursionlimit(10000)
path = os.path.abspath(os.path.join(sys.exec_prefix, '../../bin/pythonw.exe'))
multiprocessing.set_executable(path)
sys.argv = [ None ]

def getPythonPath():
    path = os.__file__.split('\\')
    path.pop()
    path.pop()
    path = '\\'.join(path)
    return(path)

"""
The imported shapefile lines comes as tuple, whereas
the export requires list, this finction converts tuple
inside lines to list
"""
def tupleToList(line):
    for a in range(0,len(line)):
        line[a] = list(line[a])
    return(line)

def listToTuple(line):
    for a in range(0, len(line)):
        line[a] = tuple(line[a])
    return(tuple(line))
    
"""
This function rounds up the coordinates of the input
raw shapefile. The decimal places up to which round
up is expected can be changed from here.
"""
def roundCoordinates(x1, y1, x2, y2, decimal=4):
    x1 = round(x1, decimal)
    y1 = round(y1, decimal)
    x2 = round(x2, decimal)
    y2 = round(y2, decimal)
    return(x1, y1, x2, y2)
       
"""
The function below calculates the angle between two points in space.
"""
def computeAngle(point1, point2):
    height = abs(point2[1] - point1[1])
    base = abs(point2[0] - point1[0])
    angle = round(math.degrees(math.atan(height/base)), 3)
    return(angle)

"""
This function calculates the orientation of a line segment.
Point1 is the lower one on the y-axes and vice-cersa for
Point2.
"""
def computeOrientation(line):
    point1 = line[1]
    point2 = line[0]
    """
    If the latutide of a point is less and the longitude is more, or
    If the latitude of a point is more and the longitude is less, then
    the point is oriented leftward and wil have negative orientation.
    """
    if ((point2[0] > point1[0]) and (point2[1] < point1[1])) or ((point2[0] < point1[0]) and (point2[1] > point1[1])):
        return(-computeAngle(point1, point2))
    #If the latitudes are same, the line is horizontal
    elif point2[1] == point1[1]:
        return(0)
    #If the longitudes are same, the line is vertical
    elif point2[0] == point1[0]:
        return(90)
    else:
        return(computeAngle(point1, point2))

"""
This below function calculates the acute joining angle between
two given set of points.
"""
def pointsSetAngle(line1, line2):
    l1orien = computeOrientation(line1)
    l2orien = computeOrientation(line2)
    if ((l1orien>0) and (l2orien<0)) or ((l1orien<0) and (l2orien>0)):
        return(abs(l1orien)+abs(l2orien))
    elif ((l1orien>0) and (l2orien>0)) or ((l1orien<0) and (l2orien<0)):
        theta1 = abs(l1orien) + 180 - abs(l2orien)
        theta2 = abs(l2orien) + 180 - abs(l1orien)
        if theta1 < theta2:
            return(theta1)
        else:
            return(theta2)
    elif (l1orien==0) or (l2orien==0):
        if l1orien<0:
            return(180-abs(l1orien))
        elif l2orien<0:
            return(180-abs(l2orien))
        else:
            return(180 - (abs(computeOrientation(line1)) + abs(computeOrientation(line2))))
    elif (l1orien==l2orien):
        return(180)
        
"""
The below function calculates the joining angle between
two line segments.
"""
def angleBetweenTwoLines(line1, line2):
    l1p1, l1p2 = line1
    l2p1, l2p2 = line2
    l1orien = computeOrientation(line1)
    l2orien = computeOrientation(line2)
    """
    If both lines have same orientation, return 180
    If one of the lines is zero, exception for that
    If both the lines are on same side of the horizontal plane, calculate 180-(sumOfOrientation)
    If both the lines are on same side of the vertical plane, calculate pointSetAngle
    """
    if (l1orien==l2orien): 
        angle = 180
    elif (l1orien==0) or (l2orien==0): 
        angle = pointsSetAngle(line1, line2)
        
    elif l1p1 == l2p1:
        if ((l1p1[1] > l1p2[1]) and (l1p1[1] > l2p2[1])) or ((l1p1[1] < l1p2[1]) and (l1p1[1] < l2p2[1])):
            angle = 180 - (abs(l1orien) + abs(l2orien))
        else:
            angle = pointsSetAngle([l1p1, l1p2], [l2p1,l2p2])
    elif l1p1 == l2p2:
        if ((l1p1[1] > l2p1[1]) and (l1p1[1] > l1p2[1])) or ((l1p1[1] < l2p1[1]) and (l1p1[1] < l1p2[1])):
            angle = 180 - (abs(l1orien) + abs(l2orien))
        else:
            angle = pointsSetAngle([l1p1, l1p2], [l2p2,l2p1])
    elif l1p2 == l2p1:
        if ((l1p2[1] > l1p1[1]) and (l1p2[1] > l2p2[1])) or ((l1p2[1] < l1p1[1]) and (l1p2[1] < l2p2[1])):
            angle = 180 - (abs(l1orien) + abs(l2orien))
        else:
            angle = pointsSetAngle([l1p2, l1p1], [l2p1,l2p2])
    elif l1p2 == l2p2:
        if ((l1p2[1] > l1p1[1]) and (l1p2[1] > l2p1[1])) or ((l1p2[1] < l1p1[1]) and (l1p2[1] < l2p1[1])):
            angle = 180 - (abs(l1orien) + abs(l2orien))
        else:
            angle = pointsSetAngle([l1p2, l1p1], [l2p2,l2p1])
    return(angle)

    
class network():
    def __init__(self, inFile):
        self.fileWithPath = inFile
        self.directory, self.name = os.path.split(inFile)
        self.tempDirectory = os.path.join(self.directory, 'tempDirectory')
        if not os.path.exists(self.tempDirectory):
            os.mkdir(self.tempDirectory)
        self.pluginDirectory = os.path.dirname(__file__)
        self.pythonPath = getPythonPath()
        self.getProjection()
        
    def getProjection(self):
        with open(self.fileWithPath.replace('.shp', '')+".prj", "r") as stream:
            self.projection = stream.read()
            
    def splitLines(self):
        self.split = []
        self.tempArray = []
        
        input = self.fileWithPath
        layer = QgsVectorLayer(self.fileWithPath , "testlayer", "ogr")
        features = layer.getFeatures()
        
        n = 0
        for feat in features:
            geom = feat.geometry()
            if geom.type() == QgsWkbTypes.LineGeometry:
                line = geom.asMultiPolyline()
                for lineEdge in range(0, len(line[0])):
                    if not (len(line[0])-1) == lineEdge:
                        coor1, coor2 = line[0][lineEdge], line[0][lineEdge+1]
                    else:
                        coor1, coor2 = line[0][-2], line[0][-1]
                    x1, y1 = coor1
                    x2, y2 = coor2
                    x1, y1, x2, y2 = roundCoordinates(x1, y1, x2, y2)
                    part = [[x1, y1], [x2, y2]]
                    if part not in self.split:
                        self.split.append([part, computeOrientation(part), list(), list(), list(), list(), list(), list()])
                        # Merge the coordinates as string, this will help in finding adjacent edges in the function below
                        self.tempArray.append([n, '%.4f_%.4f'%(part[0][0], part[0][1]), '%.4f_%.4f'%(part[1][0], part[1][1])])
                        n += 1
        
    def uniqueID(self):
    #Loop through split lines, assign unique ID and
    #store inside a list along with the connectivity dictionary
        self.unique = dict(enumerate(self.split))

    def getLinks(self):
        self.tempArray = np.array(self.tempArray, dtype=object)
        
        # Defining all the file names to run from command prompt
        getLinksModulePath = os.path.join(self.pluginDirectory, 'get_links_parallel.py')
        inputTempArrayFile = os.path.join(self.pluginDirectory, 'array_to_link.npy')
        outputTempArrayFile = os.path.join(self.pluginDirectory, 'linked_array.npy')
        
        # Save the temporary array as hard file
        np.save(inputTempArrayFile, self.tempArray)
        
        # Run the parallel processing modult to get links from stored tempArray
        command = 'cd %s & python %s --input %s --output %s' % (self.pythonPath, getLinksModulePath, inputTempArrayFile, outputTempArrayFile)
        print(command)
        os.system(command)
        
        while True:
            if os.path.exists(outputTempArrayFile):
                break

        print('Loop broke')
        
        # Load the processed array
        result = list(np.load(outputTempArrayFile, allow_pickle=True))
        
        # Loop through the result and add it to unique dictionary
        for a in result:
            n = a[0]
            self.unique[n][2] = a[1]
            self.unique[n][3] = a[2]
        print('Links done', len(result))
            
    def bestLink(self):
        self.anglePairs = dict()
        for edge in range(0,len(self.unique)):
            p1AngleSet = []
            p2AngleSet = []

            """
            Instead of computing the angle between the two segments twice, the method calculates
            it once and stores in the dictionary for both the keys. So that it does not calculate
            the second time because the key is already present in the dictionary.
            """
            for link1 in self.unique[edge][2]:
                self.anglePairs["%d_%d" % (edge, link1)] = angleBetweenTwoLines(self.unique[edge][0], self.unique[link1][0])
                p1AngleSet.append(self.anglePairs["%d_%d" % (edge, link1)])
                
            for link2 in self.unique[edge][3]:
                self.anglePairs["%d_%d" % (edge, link2)] = angleBetweenTwoLines(self.unique[edge][0], self.unique[link2][0])
                p2AngleSet.append(self.anglePairs["%d_%d" % (edge, link2)])

            """
            Among the adjacent segments deflection angle values, check for the maximum value
            at both the ends. The segment with the maximum angle is stored in the attributes
            to be cross-checked later for before finalising the segments at both the ends.
            """
            if len(p1AngleSet)!=0:
                val1, idx1 = max((val, idx) for (idx, val) in enumerate(p1AngleSet))
                self.unique[edge][4] = self.unique[edge][2][idx1], val1
            else:
                self.unique[edge][4] = 'DeadEnd'
                
            if len(p2AngleSet)!=0:
                val2, idx2 = max((val, idx) for (idx, val) in enumerate(p2AngleSet))
                self.unique[edge][5] = self.unique[edge][3][idx2], val2
            else:
                self.unique[edge][5] = 'DeadEnd'

    def crossCheckLinks(self, angleThreshold=0):
        global edge, bestP1, bestP2
        print("Cross-checking and finalising the links...")
        for edge in range(0,len(self.unique)):
            bestP1 = self.unique[edge][4][0]
            bestP2 = self.unique[edge][5][0]
            
            if type(bestP1) == type(1) and \
               edge in [self.unique[bestP1][4][0], self.unique[bestP1][5][0]] and \
               self.anglePairs["%d_%d" % (edge, bestP1)] > angleThreshold:
                self.unique[edge][6] = bestP1
            else:
                self.unique[edge][6] = 'LineBreak'
                
            if type(bestP2) == type(1) and \
               edge in [self.unique[bestP2][4][0], self.unique[bestP2][5][0]] and \
               self.anglePairs["%d_%d" % (edge, bestP2)] > angleThreshold:
                self.unique[edge][7] = bestP2
            else:
                self.unique[edge][7] = 'LineBreak'

    def addLine(self, edge, parent=None, child='Undefined'):
        if child=='Undefined':
            self.mainEdge = len(self.merged)
        if not edge in self.assignedList:
            if parent==None:
                currentid = len(self.merged)
                self.merged[currentid] = set()
            else:
                currentid = self.mainEdge
            self.merged[currentid].add(listToTuple(self.unique[edge][0]))
            self.assignedList.append(edge)
            link1 = self.unique[edge][6]
            link2 = self.unique[edge][7]
            if type(1) == type(link1):
                self.addLine(link1, parent=edge, child=self.mainEdge)
            if type(1) == type(link2):
                self.addLine(link2, parent=edge, child=self.mainEdge)
        
    def mergeLines(self):
        print('Merging Lines...')
        self.mergingList = list()
        self.merged = list()

        # Defining all the file names to run from command prompt
        mergeLinesModulePath = os.path.join(self.pluginDirectory, 'merge_lines_parallel.py')
        inputDictionaryFile = os.path.join(self.pluginDirectory, 'unique_dict.json')
        outputDictionaryFile = os.path.join(self.pluginDirectory, 'unique_dict_merged_list.npy')
        
        # Save the dictionary as JSON file
        with open(inputDictionaryFile, 'w') as fp:
            json.dump(self.unique, fp)
        
        # Run the parallel processing modult to get links from stored tempArray
        command = 'cd %s & python %s --input %s --output %s' % (self.pythonPath, mergeLinesModulePath, inputDictionaryFile, outputDictionaryFile)
        os.system(command)
        print(command)

        """
        while True:
            if os.path.exists(outputDictionaryFile):
                break
        """
        
        # Load the list cntaining merged information
        result = list(np.load(outputDictionaryFile, allow_pickle=True))

        for tempList in result:
            if not tempList in self.mergingList:
                self.mergingList.append(tempList)
                self.merged.append({listToTuple(self.unique[key][0]) for key in tempList})

        self.merged = dict(enumerate(self.merged))
        print('>'*50 + ' [%d/%d] '%(len(self.unique),len(self.unique)) + '100%' + '\n', end='\r')
    
    def setProjection(self, outFile):
        outName, ext = os.path.splitext(outFile)
        with open(outName + ".prj", "w") as stream:
            stream.write(self.projection)           
           
    def exportMerged(self, outFileName):
        #Temporary merge is exported with the common ID
        #Temporary merge 1 is exported by dissolving the common ID
        #The final merged file is exported after calculating the lengths
        self.mergedFilename = outFileName
        tempMergedFilename = self.name.replace('.shp', '_tempMerge.shp')
        tempMergedFilename = os.path.join(self.tempDirectory, tempMergedFilename)
        tempMergedFilename_1 = tempMergedFilename.replace('.shp', '_1.shp')
        tempMergedFilename_2 = tempMergedFilename.replace('.shp', '_2.shp')
        
        #Define the fields
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.Int))
        
        writer = QgsVectorFileWriter(tempMergedFilename, "UTF-8", fields, QgsWkbTypes.LineString, driverName="ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            print("Error when creating shapefile: ",  writer.errorMessage())
        
        for a in range(0,len(self.merged)):
            feat = QgsFeature()
            linelist = list(self.merged[a])
            for part in linelist:
                coor1, coor2 = part
                feat.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(coor1[0], coor1[1]), QgsPointXY(coor2[0], coor2[1])]))
                feat.setAttributes([a])
                writer.addFeature(feat)
        self.setProjection(tempMergedFilename)
        del writer
        
        params = {'INPUT':tempMergedFilename,'OUTPUT':tempMergedFilename_1}
        processing.run("native:fixgeometries", params)
        
        params = {'FIELD' : ['ID'], 'INPUT' : tempMergedFilename_1, 'OUTPUT' : tempMergedFilename_2}
        processing.run('native:dissolve', params)
        self.setProjection(tempMergedFilename_2)
        
        params = {'INPUT':tempMergedFilename_2,'CALC_METHOD':0,'OUTPUT':self.mergedFilename}
        processing.run("qgis:exportaddgeometrycolumns", params)
        self.setProjection(self.mergedFilename)
        
#Export requires 3 brackets, all in list form,
#Whereas it reads in 3 brackets, inner one as tuple
    def exportPreMerged(self, outFileName):
        self.preMergeFileName = outFileName
        #The pre merge file contains the information from all the steps
        #that is lost in the merged file
        
        fields = QgsFields()
        fieldNames = ['UniqueID',  'Orientation', 'linksP1', 'linksP2', 'bestP1', 'bestP2', 'P1Final', 'P2Final']
        for var in fieldNames:
            fields.append(QgsField(var, QVariant.String))
            
        writer = QgsVectorFileWriter(self.preMergeFileName, "UTF-8", fields, QgsWkbTypes.LineString, driverName="ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            print("Error when creating shapefile: ",  writer.errorMessage())
        
        for a in range(0,len(self.unique)):
            feat = QgsFeature()
            part = tuple(self.unique[a][0])
            coor1, coor2 = part
            feat.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(coor1[0], coor1[1]), QgsPointXY(coor2[0], coor2[1])]))
            feat.setAttributes([a,
              str(self.unique[a][1]),
              str(self.unique[a][2]),
              str(self.unique[a][3]),
              str(self.unique[a][4]),
              str(self.unique[a][5]),
              str(self.unique[a][6]),
              str(self.unique[a][7])])
            writer.addFeature(feat)
        self.setProjection(self.preMergeFileName)
        del writer

