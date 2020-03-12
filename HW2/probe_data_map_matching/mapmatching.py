"""
_____________________ Notes _____________________
-- Zone is 32 for all probes
-- we can graph and use CNN to match points
"""

import numpy as np
from MapLink import MapLink
from ProbePoint import ProbePoint
from MatchedPoint import MatchedPoint
import matplotlib.pyplot as plt

import utm
from tkinter import *
from tkinter import filedialog
from sortedcontainers import SortedDict, SortedList

def binarySearch(data, val):
	low, high = 0, len(data)
	while low != high:
		mid = (low+high)//2
		if val < float(data[mid]): high = mid-1
		elif val > float(data[mid]): low = mid+1
		else: return mid
		#print("low={}, high={}".format(low,high), end="\n\n")
	#print("VALUE:", val, "type =",type(val))
	return mid
	#raise ValueError("list empty?")

def parseProbePoints(filename, maplinks=None, outfilepointer=None): #string arg 
	#data={} #dict of probepoints: data[sampleID] = list(probepoints with same sampleID)
	file = open(filename, "r")
	x=0
	while x<1000: 
		line = file.readline()
		if line:
			probe = ProbePoint(line) #get probe data
			print(probe)
			#if probe.sampleID not in data.keys(): data[probe.sampleID] = [probe] #cluster data by sampleID
			#else: data[probe.sampleID].append(probe)
			matchedpoint = match(probe, maplinks)
			if matchedpoint:
				outfilepointer.write(str(matchedpoint)+'\n')
		else:
			break
		x+=1
		print("Parsed", x, "Probe Points", end = "\r")
	file.close()
	print("Parsed all", x, "Probe Points")
	return True #data
	
def parseLinks(filename, plotting=False): #string arg
	def plotLinkPoint(link):
		x=[]
		y=[]
		for coor in link.shapeInfo:
			x.append(coor[0])
			y.append(coor[1])
		plt.plot(x,y,linewidth=1)
	################################
	data=SortedDict()
	file = open(filename, "r")
	x=0
	while x<1000: #(for testing)
		line = file.readline()
		if line:
			link = MapLink(line)
			if plotting: plotLinkPoint(link)
			#sort point by utm coordinate for ref node (x first, then y)
			if link.refX() not in data: data[link.refX()] = SortedDict({link.refY():link})
			else: (data[link.refX()])[link.refY()] = link
		else:
			break
		x+=1
		print("Read", x, "Map Links", end = "\r")
	file.close()
	print("Read all", x, "Map Links")
	#plt.savefig("Map_Links_Plot.png")
	#plt.show()
	return data


def match(probe, links, threshold =37): #threshold = 37 meters (which is 10 times average width of lane on highway)
	#find closest reference point then check shapepoints and nonref points for closest
	
	idx = binarySearch(list(links.keys()),float(probe.X()))
	closest200byX = {(k, links[k]) for k in links.keys[idx-100:idx+100]} #get subset of dict containing 200 closest links
	closestbyY = binarySearch(sorted(list(closest200byX.keys())), float(probe.Y())) #get the idx of key of closest link (in dict) by y coordinate in dict of closest 200 links 
	closestLink = closest200byX[closest200byX.keys()[closestbyY]] #store the closest link

	matched = MatchedPoint(probe, closestLink)

	return matched


#make main function thread-safe
if __name__ == "__main__": 
	#numThreads = os.cpu_count()*2 - 1
	#links must be read first
	rawLinkData = ".\\Partition6467LinkData.csv"#filedialog.askopenfilename(title = "Select Link Data",filetypes = (("comma-separated values","*.csv"),))
	mapLinks = parseLinks(rawLinkData, plotting=False)
	
	outfile = "Partition6467MatchedPoints.csv"
	output = open(outfile,"w")

	rawProbeData = ".\\Partition6467ProbePoints.csv"#filedialog.askopenfilename(title = "Select Probe Data",filetypes = (("comma-separated values","*.csv"),))
	probePoints = parseProbePoints(rawProbeData, maplinks=mapLinks, outfilepointer=output)

	#safe way to ensure resources close and we can view data later

	output.close()
