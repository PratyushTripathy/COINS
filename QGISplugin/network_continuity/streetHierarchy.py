"""
This module is designed to read line type ESRI shapefiles,
mainly roads and find longest paths based on their
connectivity angle.

Author: PratyushTripathy
Date: 14 December 2018

"""

import os, sys, math, time, shutil
import numpy as np
from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import QVariant
import processing
from qgis.core import *
from PyQt5.QtGui import QFont

t1 = time.time()

#Set recurrsion depth limit to avoid error at a later stage
sys.setrecursionlimit(10000)
"""
This function takes any layer as input and returns the total number
of features in the layer. This function serves in displaying the 
ongoing processes in the GUI.
"""
def getFeatureCount(inFile):
    layer = QgsVectorLayer(inFile, "testlayer", "ogr")
    features = layer.getFeatures()
    for n, feat in enumerate(features):
        pass
    return(n+1)


"""
The imported shapefile lines comes as tuple, whereas
the export requires list, this finction converts tuple
inside lines to list
"""
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
    #If the latutide of a point is less and the longitude is more, or
    #If the latitude of a point is more and the longitude is less, then
    #the point is oriented leftward and wil have negative orientation.
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
    if (l1orien==l2orien): #If both lines have same orientation, return 180
        angle = 180
    elif (l1orien==0) or (l2orien==0): #If one of the lines is zero, exception for that
        angle = pointsSetAngle(line1, line2)
    #If the lines form upper or lower facing angle, return 180-(sumOfOrientation)
    #If the lines form left or right facing angle, return pointSetAngle
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

def displayLineLog(cls, message):
    cls.dlg.logDisplayField.addItem(message)
                    
class network():
    def __init__(self, inFile):
        self.fileWithPath = inFile
        self.directory, self.name = os.path.split(inFile)
        self.tempDirectory = os.path.join(self.directory, 'tempDirectory')
        self.getProjection()
        if not os.path.exists(self.tempDirectory):
            os.mkdir(self.tempDirectory)
        
    def getProjection(self):
        with open(self.fileWithPath.replace('.shp', '')+".prj", "r") as stream:
            self.projection = stream.read()
            
    def splitLines(self, classInstance):
        classInstance.dlg.progressBar.setValue(0)
        classInstance.dlg.label_4.setFont(QFont("Times", 8, QFont.Bold))
        self.split = []
        input = self.fileWithPath
        """
        output = self.name.replace('.shp', '_splitted.shp')
        output = os.path.join(self.tempDirectory, output)
        
        params = {'INPUT' : input, 'LINES' : input, 'OUTPUT' : output}
        print(input, output)
        result = processing.run('native:splitwithlines', params)
        self.splitFileWithPath = result['OUTPUT']
        """
        layer = QgsVectorLayer(self.fileWithPath , "testlayer", "ogr")
        features = layer.getFeatures()
        total = getFeatureCount(input)
        for n, feat in enumerate(features):
            if (n%total*10) == int(n%total*10):
                status = (n%total*10)
                classInstance.dlg.progressBar.setValue(status)
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
                    tempLine = [[x1, y1], [x2, y2]]
                    if tempLine not in self.split:
                        self.split.append(tempLine)
        classInstance.dlg.progressBar.setValue(100)
        return(getFeatureCount(input))
        
    def uniqueID(self, classInstance):
    #Loop through split lines, assign unique ID and
    #store inside a list along with the connectivity dictionary
        classInstance.dlg.label_5.setFont(QFont("Times", 8, QFont.Bold))
        self.unique = dict()
        for edge in range(0,len(self.split)):
            self.unique[edge] = [self.split[edge], computeOrientation(self.split[edge]), list(), list(), list(), list(), list(), list()]
        #self.split = None

    def getLinks(self, classInstance):
        classInstance.dlg.progressBar.setValue(0)
        classInstance.dlg.label_6.setFont(QFont("Times", 8, QFont.Bold))
        print("Finding adjacent lines for each line.")
        tempArray = []
        for n in self.unique:
            tempArray.append([n, self.unique[n][0][0][0], self.unique[n][0][0][1], self.unique[n][0][1][0], self.unique[n][0][1][1]])
        tempArray = np.array(tempArray, dtype=object)
        for n in range(0, tempArray.shape[0]):
            if (n%tempArray.shape[0]*10) == int(n%tempArray.shape[0]*10):
                status = (n%tempArray.shape[0]*10)
                classInstance.dlg.progressBar.setValue(status)
            if n%1000==0:
                print(n, ' out of ', len(self.unique))
            m1 = tempArray[:,1]==tempArray[n,1]
            m2 = tempArray[:,2]==tempArray[n,2]
            m3 = tempArray[:,3]==tempArray[n,1]
            m4 = tempArray[:,4]==tempArray[n,2]
            mask1 = m1*m2 + m3*m4
            m1 = tempArray[:,1]==tempArray[n,3]
            m2 = tempArray[:,2]==tempArray[n,4]
            m3 = tempArray[:,3]==tempArray[n,3]
            m4 = tempArray[:,4]==tempArray[n,4]
            mask2 = m1*m2 + m3*m4
            mask1 = tempArray[~(mask1==0)]
            mask2 = tempArray[~(mask2==0)]
            for q in range(0,mask1.shape[0]):
                if not mask1[q][0] == n:
                    self.unique[n][2].append(mask1[q][0])
            for w in range(0,mask2.shape[0]):
                if not mask2[w][0] == n:
                    self.unique[n][3].append(mask2[w][0])
        classInstance.dlg.progressBar.setValue(100)
            
    def bestLink(self, classInstance):
        classInstance.dlg.progressBar.setValue(0)
        classInstance.dlg.label_7.setFont(QFont("Times", 8, QFont.Bold))
        self.anglePairs = dict()
        for edge in range(0,len(self.unique)):
            if (edge%len(self.unique)*10) == int(edge%len(self.unique)*10):
                status = (edge%len(self.unique)*10)
                classInstance.dlg.progressBar.setValue(status)
            p1AngleSet = []
            p2AngleSet = []
            for p1link in range(0,len(self.unique[edge][2])):
                link1 = self.unique[edge][2][p1link]
                self.anglePairs["%d_%d" % (edge, link1)] = angleBetweenTwoLines(self.unique[edge][0], self.unique[link1][0])
                p1AngleSet.append(self.anglePairs["%d_%d" % (edge, link1)])
            for p2link in range(0,len(self.unique[edge][3])):
                link2 = self.unique[edge][3][p2link]
                self.anglePairs["%d_%d" % (edge, link2)] = angleBetweenTwoLines(self.unique[edge][0], self.unique[link2][0])
                p2AngleSet.append(self.anglePairs["%d_%d" % (edge, link2)])
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
        classInstance.dlg.progressBar.setValue(100)

    def crossCheckLinks(self, classInstance, angleThreshold):
        classInstance.dlg.progressBar.setValue(0)
        classInstance.dlg.label_8.setFont(QFont("Times", 8, QFont.Bold))
        self.angleThreshold = angleThreshold
        print("Cross-checking and finalising the links..")
        for edge in range(0,len(self.unique)):
            if (edge%len(self.unique)*10) == int(edge%len(self.unique)*10):
                status = (edge%len(self.unique)*10)
                classInstance.dlg.progressBar.setValue(status)
            if edge%1000==0:
                print("Cross checking %d out of %d" %(edge, len(self.unique)))
            bestP1 = self.unique[edge][4][0]
            bestP2 = self.unique[edge][5][0]
            if type(bestP1) == type(1):
                if (self.unique[bestP1][4][0] == edge) or (self.unique[bestP1][5][0] == edge):
                    if self.anglePairs["%d_%d" % (edge, bestP1)] > self.angleThreshold:
                        self.unique[edge][6] = bestP1
                else:
                    self.unique[edge][6] = 'LineBreak'
            else:
                self.unique[edge][6] = 'LineBreak'
                
            if type(bestP2) == type(1):
                if (self.unique[bestP2][4][0] == edge) or (self.unique[bestP2][5][0] == edge):
                    if self.anglePairs["%d_%d" % (edge, bestP2)] > self.angleThreshold:
                        self.unique[edge][7] = bestP2
                else:
                    self.unique[edge][7] = 'LineBreak'
            else:
                self.unique[edge][7] = 'LineBreak'
        classInstance.dlg.progressBar.setValue(100)

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
        
    def mergeLines(self, classInstance):
        classInstance.dlg.progressBar.setValue(0)
        classInstance.dlg.label_9.setFont(QFont("Times", 8, QFont.Bold))
        self.merged = dict()
        self.assignedList = []
        print("Merging Lines..")
        for edge in range(0, len(self.unique)):
            if (edge%len(self.unique)*10) == int(edge%len(self.unique)*10):
                status = (edge%len(self.unique)*10)
                classInstance.dlg.progressBar.setValue(status)
            if edge%1000==0:
                print("Parent Line: ", edge)
            self.addLine(edge)
        classInstance.dlg.progressBar.setValue(100)
    
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
        if os.path.exists(self.tempDirectory):
            print(self.tempDirectory)
            #shutil.rmtree(self.tempDirectory)
        
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

"""
inFile = "F:\\StreetNetworkLongest\\QGISplugin\\sample.shp"
myStreet = network(inFile)
#Split lines
myStreet.splitLines()
#Create unique ID
myStreet.uniqueID()

print(len(myStreet.unique))

#Compute connectivity table
myStreet.getLinks()
#Find best link at every point for both lines
myStreet.bestLink()
#Cross check best links
myStreet.crossCheckLinks()
#Merge finalised links
myStreet.mergeLines()
#Export lines
myStreet.exportPreMerged()
myStreet.exportMerged()
temp = myStreet.tempDirectory
myStreet = None

os.rmdir(temp)
"""