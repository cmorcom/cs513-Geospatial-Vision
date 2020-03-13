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

def flattenList(l):
	return [i for sl in l for i in sl]

def binarySearch(data, val):
	low, high = 0, len(data)-1
	while low <= high:
		#print("low={}, high={}".format(low,high), end="\n\n")
		mid = (low+high)//2
		if val < float(data[mid]): high = mid-1
		elif val > float(data[mid]): low = mid+1
		else: return mid
	return mid
	#raise ValueError("list empty?")

def linearSearch(data, val):
	closestIDX = 0
	closestdiff = 10000000
	for x in range(len(data)):
		if abs(float(data[x])-float(val)) < closestdiff:
			closestIDX = x
	return closestIDX

def parseProbePoints(filename, maplinks=None, outfilepointer=None, plotting=False): #string arg 
	#data={} #dict of probepoints: data[sampleID] = list(probepoints with same sampleID)
	file = open(filename, "r")
	x=0
	while True: 
		line = file.readline()
		if line:
			probe = ProbePoint(line) #get probe data
			if plotting: plt.plot(probe.X(),probe.Y())
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
	while True: #(for testing)
		line = file.readline()
		if line:
			link = MapLink(line)
			if plotting: plotLinkPoint(link)
			#sort point by utm coordinate for ref node (x first, then y)
			if link.refX() not in data: data[link.refX()] = [link]
			else: (data[link.refX()]).append(link)
		else:
			break
		x+=1
		print("Read", x, "Map Links", end = "\r")
	file.close()
	print("Read all", x, "Map Links")
	#if plotting:
	#plt.savefig("Map_Links_Plot.png")
	#plt.show()
	return data


def match(probe, links):
	idx = binarySearch(list(links.keys()),float(probe.X()))
	closest5byX = {}
	for k in list(links.keys())[max(0,idx-2):min(idx+2, len(links))]: #get subset of dict containing 200 closest links
		closest5byX[k] = links[k]
	#linear search for closest link
	closestLink = None
	closestdiff = 10000000
	for k,v in closest5byX.items():
		for ml in v: #ml short for maplunt
			diff = abs(probe.Y()-ml.refY())
			if diff < closestdiff:
				closestLink = ml
				closestdiff = diff

	#print(probe, "\n", closestLink)
	#print(closest5byX.items())
	#print("PROBE:\t{},{}\nBEST:\t{},{}".format(probe.X(), probe.Y(), closestLink.refX(),closestLink.refY()))

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

	output.close()

	#reopen closed output to read so we can calculate the slopes
	#matchedfile = open(outfile, "r")
	#sfile = ".\\Partition6467MatchedSlopes.csv"
	#slopefile = open(sfile, "w")

	#we have already read all the map links. now to scan the outfile for each probe.