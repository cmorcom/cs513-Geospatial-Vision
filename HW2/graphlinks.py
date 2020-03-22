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

from sortedcontainers import SortedDict, SortedList

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
	if plotting:
		plt.savefig("Map_Links_Plot.png")
		plt.show()
	return data

if __name__ == "__main__": 
	rawLinkData = ".\\Partition6467LinkData.csv"#filedialog.askopenfilename(title = "Select Link Data",filetypes = (("comma-separated values","*.csv"),))
	mapLinks = parseLinks(rawLinkData, plotting=True)