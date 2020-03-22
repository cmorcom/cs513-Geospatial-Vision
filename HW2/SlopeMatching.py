import utm
from tkinter import *
from tkinter import filedialog
from sortedcontainers import SortedDict, SortedList

import numpy as np
from MapLink import MapLink
from ProbePoint import ProbePoint
from MatchedPoint import MatchedPoint



"""
    GIVEN: Maplinks and ProbePoints Matched to the Links 
    FIND: Derive Slope between probe and ref point, and the error from the real data... (naive implementation assuming path is linear)
    PROCESS:
        First read maplinks again 
        for each matched point get the pvid of the link it matches to in the maplink.linkpvid (iterative)
        if the link does not have a slope, check next probe 
        else, match the probe based on distance to the most similar point to get real slope data
        using the refX and refY and altitude of the link, and the X and Y and altitude of the probe we get: slope=diff in altitude / euclidian distance
        note euclidian dist is given in the MatchedPoint.distFromRef 
"""

class SlopeData:
    def __init__(self,pvid, sampleID, derived, realslope):
        self.linkPVID = pvid
        self.sampleID = sampleID
        self.realslope = int(round(realslope))
        self.derivedslope = int(round(derived))
        self.error = abs(derived-realslope)/float(realslope)
    
    def __str__(self):
        a= \
            str(self.linkPVID)+',' + \
            str(self.sampleID)+',' + \
            str(self.realslope) + ',' + \
            str(self.derivedslope) + ',' + \
            str(self.error)
        return a

def parseLinks(filename): 
    def plotLinkPoint(link):
        x=[]
        y=[]
        for coor in link.shapeInfo:
            x.append(coor[0])
            y.append(coor[1])
        plt.plot(x,y,linewidth=1)
    data=SortedDict()
    file = open(filename, "r")
    x=0
    while x<1000:
        line = file.readline()
        if line:
            link = MapLink(line)
            #sort links by unique linkPVID
            if link.slopeInfo: 
                data[link.linkPVID] = link
        else:
            break
        x+=1
        print("Read", x, "Map Links", end = "\r")
    file.close()
    print("Read all", x, "Map Links", end = "\r")
    return data

def derive(mp, links):
    #given a matchedpoint (mp) and sorted (by PVID) dict of links
    if mp.linkPVID not in list(links.keys()):
        return None
    else:
        #derive slope
        xydist = mp.distFromRef
        #print("MapLink: ", links[mp.linkPVID])
        linkalt = float(links[mp.linkPVID].shapeInfo[0][-1])
        altdiff = mp.altitude - linkalt #negative means you are going downhill
        derivedslope = int(round(altdiff/xydist)) #get ans in meters
        #get real slope
        closest = 100000000
        for (dist,slope) in links[mp.linkPVID].slopeInfo:
            if abs(dist - xydist) < closest:
                closest = abs(dist - xydist)
                realslope = slope #gives us the slope of closest matching point
    return SlopeData(mp.linkPVID, mp.sampleID, derivedslope, realslope)

if __name__ == "__main__":
    linkfile = ".\\Partition6467LinkData.csv"
    data = parseLinks(linkfile)

    matchedpointsfile = ".\\Partition6467MatchedPoints.csv"
    matchedpoints = open(matchedpointsfile, "r")

    outname = ".\\Partition6467slopeData.csv" 
    out = open(outname, "w")
    x=0
    print("Parsing Slopes")
    while True: 
        line = matchedpoints.readline()
        if line:
            mp = MatchedPoint(attrs=line)
            outdatapoint = derive(mp, data)
            if outdatapoint: out.write(str(outdatapoint)+'\n')
        else:
            break
        x+=1
        print("Parsed Slope for", x, "Matched Points", end = "\r")
    matchedpoints.close()
    print("Parsed Slope for all", x, "Matched Points", end = "\r")
    out.close()
