from MapLink import MapLink
import utm
from ProbePoint import ProbePoint
from tkinter import *
from tkinter import filedialog

def parseProbePoints(filename): #string arg 
	data={} #dict of probepoints: data[sampleID] = list(probepoints with same sampleID)
	probeCluster=[]
	file = open(filename, "r")
	clusterID = None
	prevclusterID = None
	x=0
	while True: #for x in range(100): #(for testing)
		line = file.readline()
		if line:
			probe = ProbePoint(line) #get probe data
			clusterID = probe.sampleID #note its clusterID
			if clusterID == prevclusterID: #check if it fits in previous cluster or make a new one
				probeCluster.append(probe) #store probe with key as Sample ID for search and sort
			else:
				data[clusterID] = probeCluster
				probeCluster = []
				prevclusterID = clusterID
		else:
			break
		x+=1
		print("Read", x, "Probe Points", end = "\r")
	file.close()
	print("Read all", x, "Probe Points")
	return data
	
def parseLinks(filename): #string arg
	data={}
	file = open(filename, "r")
	x=0
	while True: #for x in range(100): #(for testing)
		link = file.readline()
		if line:
			link = MapLink(line)
			data[link.linkPVID] = link #store link with key as unique linkPVID for search and sort
		else:
			break
		x+=1
		print("Read", x, "Map Links", end = "\r")
	file.close()
	print("Read all", x, "Map Links")
	return data

rawProbeData = filedialog.askopenfilename(title = "Select Probe Data",filetypes = (("comma-separated values","*.csv"),))
probePoints = parseProbePoints(rawProbeData)
#for x in probePoints: print(x)
print("len(ProbePoints) =", len(probePoints))

rawLinkData = filedialog.askopenfilename(title = "Select Link Data",filetypes = (("comma-separated values","*.csv"),))
mapLinks = parseLinks(rawLinkData)
#for x in mapLinks: print(x)
print("len(LinkData) =", len(mapLinks))

outfile = "Partition6467MatchedPoints.csv"
output = open(outfile,"w")
output.close()

